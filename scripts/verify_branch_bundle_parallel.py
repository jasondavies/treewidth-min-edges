#!/usr/bin/env python3
"""Independently check a binary branch-proof bundle with isolated workers.

Root coverage is established by the ordinary independent catalogues. Each
fresh worker checks one exact member with the standard Python verifier. Exit
2 means all supplied proofs passed but catalogue coverage is incomplete.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import time

from verify_branch_refutation import PREMISE_NOTICE
from branch_certificate_binary import verify_stream
from branch_certificate_bundle import iter_members, member_prefix, open_input, read_bundle_header
from order25_profiles import enumerate_profiles, profile_key


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, value):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + '.',
                                         suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(json.dumps(value, indent=2).encode() + b'\n')
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def check_member(job):
    started, cpu_started = time.monotonic(), time.process_time()
    result = {key: value for key, value in job.items() if key != 'path'}
    try:
        raw = Path(job['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != job['sha256']:
            raise ValueError('Extracted member changed before verification.')
        result['statistics'] = verify_stream(io.BytesIO(raw), job['prefix'])
        result['verified'] = True
    except Exception as error:
        result['verified'] = False
        result['error'] = f'{type(error).__name__}: {error}'
    result['wall_seconds'] = time.monotonic() - started
    result['cpu_seconds'] = time.process_time() - cpu_started
    try:
        import resource
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        result['peak_rss_kib'] = peak / 1024 if sys.platform == 'darwin' else peak
    except ImportError:
        result['peak_rss_kib'] = None
    return result


def verify_parallel(path, reports_directory, workers=1, catalogue=None, coverage=None):
    if type(workers) is not int or workers < 1:
        raise ValueError('Worker count must be positive.')
    started, parent_cpu = time.monotonic(), time.process_time()
    reports_directory = Path(reports_directory)
    reports_directory.mkdir(parents=True, exist_ok=True)
    digest = sha256_file(path)
    with tempfile.TemporaryDirectory(prefix='tw11-verify-members-') as directory:
        directory = Path(directory)
        with open_input(path) as stream:
            order, count = read_bundle_header(stream)
            if order not in (23, 24, 25):
                raise ValueError('Unsupported bundle order.')
            stream.seek(0)
            if order == 25:
                catalogue_roots = enumerate_profiles()

                def identify(prefix):
                    key = profile_key(prefix)
                    if key not in catalogue_roots:
                        raise ValueError('Unknown order25 root.')
                    return key, ''.join(map(str, key))
            elif order == 24:
                from verify_order24_catalogue import read_certificate, verify
                if catalogue is None:
                    raise ValueError('Order24 verification requires a catalogue certificate.')
                profiles = verify(read_certificate(catalogue))['profiles']
                indices = {tuple(prefix): index for index, prefix in enumerate(profiles)}
                if len(indices) != len(profiles):
                    raise ValueError('Duplicate verified catalogue roots.')
                catalogue_roots = set(range(len(profiles)))

                def identify(prefix):
                    index = indices.get(tuple(prefix))
                    if index is None:
                        raise ValueError('Unknown order24 root.')
                    return index, str(index)

            else:
                from verify_order23_refutations import read_json
                from verify_order23_coverage import verify
                if coverage is None:
                    raise ValueError('Order23 verification requires a coverage certificate.')
                cover = read_json(Path(coverage))
                checked = verify(cover)
                profiles = cover['catalogue']
                indices = {tuple(prefix): index for index, prefix in enumerate(profiles)}
                if len(indices) != len(profiles):
                    raise ValueError('Duplicate order23 catalogue roots.')
                catalogue_roots = set(checked['referenced_indices'])

                def identify(prefix):
                    index = indices.get(tuple(prefix))
                    if index is None:
                        raise ValueError('Unknown order23 catalogue root.')
                    return index, str(index)

            jobs, seen = [], set()
            for index, raw in enumerate(iter_members(stream, order)):
                prefix = member_prefix(raw, order)
                key, code = identify(prefix)
                if key in seen:
                    raise ValueError('Duplicate root in bundle.')
                seen.add(key)
                member_path = directory / f'{index}.bin'
                member_path.write_bytes(raw)
                jobs.append({'index': index, 'code': code, 'prefix': prefix,
                             'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                             'path': str(member_path)})
        if len(jobs) != count:
            raise ValueError('Bundle count changed while extracting members.')
        results = []
        # Large jobs first minimizes idle time near the end. One task per child
        # makes each resource report independent of previously checked members.
        with ProcessPoolExecutor(max_workers=workers, max_tasks_per_child=1) as pool:
            futures = {pool.submit(check_member, job) for job in sorted(jobs, key=lambda j: j['bytes'], reverse=True)}
            for future in as_completed(futures):
                futures.remove(future)
                result = future.result()
                results.append(result)
                write_json(reports_directory / f"{result['index']:03d}-{result['code']}.json", result)
                status = 'PASS' if result['verified'] else 'FAIL'
                print(f"{status} {result['code']}: {result['wall_seconds']:.3f}s, {result['peak_rss_kib']} KiB", flush=True)
    missing = sorted(set(catalogue_roots) - seen)
    if order == 25:
        missing = [''.join(map(str, key)) for key in missing]
    all_verified = all(result['verified'] for result in results)
    report = {'order': order, 'bundle_sha256': digest, 'supplied_members': count,
              'required_roots': len(catalogue_roots), 'missing_roots': missing,
              'required_roots_supplied': len(set(catalogue_roots) & seen),
              'all_supplied_verified': all_verified,
              'members': sorted(results, key=lambda result: result['index']),
              'wall_seconds': time.monotonic() - started,
              'worker_cpu_seconds': sum(result['cpu_seconds'] for result in results),
              'parent_cpu_seconds': time.process_time() - parent_cpu,
              'max_worker_peak_rss_kib': max((result['peak_rss_kib'] or 0 for result in results), default=0),
              'workers': workers}
    write_json(reports_directory / 'summary.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--reports', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--catalogue', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'sources/eleven-order24-catalogue.bin.xz')
    parser.add_argument('--coverage', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'sources/eleven-order23-coverage.json.xz')
    args = parser.parse_args()
    report = verify_parallel(args.bundle, args.reports, args.workers, args.catalogue, args.coverage)
    print(f"Verified {sum(result['verified'] for result in report['members'])}/{report['supplied_members']} supplied proofs.")
    print(PREMISE_NOTICE)
    if not report['all_supplied_verified']:
        return 1
    if report['missing_roots']:
        print(f"INCOMPLETE: {len(report['missing_roots'])} catalogue roots remain missing.")
        return 2
    print('PASS: all catalogue roots are independently excluded.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
