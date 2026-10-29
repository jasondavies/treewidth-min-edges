#!/usr/bin/env python3
"""Restore and audit saved eleven checkpoints in an isolated Linux mount layout.

Requires bubblewrap, nauty, and an x86 CPU with POPCNT. This checks selected
saved searches, not all earlier classifications. See proof-eleven.md.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile

from reproduce_eleven import SNAPSHOT, check_bundle
from replay_cache import atomic_json, digest

HISTORICAL_ROOT = '/home/ttuser/open-problems'
HISTORICAL_WORK = '/tmp/treewidth11'
SYSTEM_PYTHON = '/usr/bin/python3'


def resolve_checkpoint_archive():
    """Hash-check the selected square-search archive before extraction."""
    name = 'treewidth-eleven-quartic-complete-checkpoints.tar.gz'
    archive = SNAPSHOT / 'sources' / name
    if not archive.is_file():
        raise RuntimeError(f'Missing required checkpoint archive: {name}')
    expected = json.loads((SNAPSHOT / 'SHA256.json').read_text())['sources/' + name]
    if digest(archive) != expected:
        raise RuntimeError(f'Archive checksum mismatch: {archive}')
    return archive


def restore(archive, destination, executables):
    print(f'Restoring {archive.name}', flush=True)
    with tarfile.open(archive, 'r|gz') as stream:
        for member in stream:
            path = PurePosixPath(member.name)
            if path.is_absolute() or '..' in path.parts or not (member.isfile() or member.isdir()):
                raise RuntimeError(f'Unexpected archive member: {member.name}')
            # Only regular files/directories are accepted. No links or devices.
            stream.extract(member, destination, set_attrs=True)
            if member.isfile() and (member.mode & 0o111 or member.name.endswith(".so")):
                executables[member.name] = digest(destination / member.name)


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: assertions are verification steps.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Directory for restored checkpoints, local replay receipts, and reports.')
    parser.add_argument('--scope', choices=['quartic'], default='quartic',
                        help='Replay the five selected order-26 square families.')
    parser.add_argument('--resume', action='store_true', help='Reuse this output directory and its completed checks.')
    parser.add_argument('--seconds', type=float, help='Replay scheduling budget; partial checks are saved for --resume.')
    parser.add_argument('--workers', type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument('--replay-terminals', action='store_true', help='Quartic only: also rerun every adaptive and cooperative terminal search.')
    args = parser.parse_args()
    if args.workers < 1 or (args.seconds is not None and args.seconds <= 0):
        parser.error('Workers and time budget must be positive.')
    bubblewrap = shutil.which('bwrap')
    if bubblewrap is None:
        parser.error('Install bubblewrap (Linux) to preserve recorded paths without changing manifests.')
    if not Path(SYSTEM_PYTHON).is_file():
        parser.error('Replay requires the system Python at /usr/bin/python3.')
    check_bundle()
    archives = [('quartic-complete', resolve_checkpoint_archive())]
    # Test namespace support before extracting hundreds of thousands of files.
    subprocess.run([bubblewrap, '--ro-bind', '/', '/', '/bin/true'], check=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=args.resume)
    lock = (output / '.replay.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        parser.error('Another replay is using this output directory.')
    marker = output / 'restore.json'
    if args.resume:
        if not marker.exists():
            parser.error('No restoration manifest here; use a new output directory.')
        restored = json.loads(marker.read_text())
        if restored.get('format') != 1:
            parser.error('Unsupported restoration manifest.')
    else:
        restored = {'format': 1, 'archives': {}, 'executables': {}}
        atomic_json(marker, restored)
    work = output / 'treewidth11'
    work.mkdir(exist_ok=args.resume)
    for name, expected in restored['executables'].items():
        if digest(work / name) != expected:
            raise RuntimeError(f'Changed restored executable: {name}; use a new output directory.')
    for tag, archive in archives:
        checksum = digest(archive)
        if tag in restored['archives']:
            if restored['archives'][tag] != checksum:
                raise RuntimeError('Changed archive; use a new output directory.')
            print(f'Reusing extracted {tag}', flush=True)
        else:
            restore(archive, work, restored['executables'])
            restored['archives'][tag] = checksum
            atomic_json(marker, restored)
    # Keep the host read-only; hide its /tmp and historical research checkout.
    # Only the fresh checkpoint directory is writable inside the namespace.
    prefix = [bubblewrap, '--die-with-parent', '--ro-bind', '/', '/',
              '--tmpfs', '/tmp', '--bind', str(work), HISTORICAL_WORK,
              '--tmpfs', '/home', '--dir', '/home/ttuser',
              '--tmpfs', '/opt', '--ro-bind', str(Path(__file__).resolve().parent), '/opt/treewidth-reproduction',
              '--ro-bind', str(SNAPSHOT), HISTORICAL_ROOT,
              '--chdir', HISTORICAL_ROOT, '--setenv', 'PYTHONDONTWRITEBYTECODE', '1']
    extra = ['--replay-terminals'] if args.replay_terminals else []
    if args.seconds is not None:
        extra += ['--seconds', str(args.seconds)]
    command = prefix + [SYSTEM_PYTHON, '/opt/treewidth-reproduction/audit_eleven_replays.py',
                        '--snapshot', HISTORICAL_ROOT, '--work', HISTORICAL_WORK,
                        '--scope', args.scope, '--workers', str(args.workers), *extra]
    result = subprocess.run(command)
    if result.returncode not in (0, 2):
        result.check_returncode()
    report_path = work / ('resumable-' + args.scope) / 'summary.json'
    report = json.loads(report_path.read_text())
    expected_status = 'partial_replay' if result.returncode == 2 else 'required_replays_verified'
    if (report['status'] != expected_status or report['scope'] != args.scope
            or report['terminal_replays'] != args.replay_terminals
            or report['verifier']['auditor'] != digest(Path(__file__).with_name('audit_eleven_replays.py'))
            or report['verifier']['cache'] != digest(Path(__file__).with_name('replay_cache.py'))
            or report['counts']['complete'] != (result.returncode == 0)):
        raise RuntimeError('Replay report does not match this verification run.')
    if result.returncode == 2:
        print(f'Partial replay saved in {output}; repeat this command with --resume.', flush=True)
        return 2
    reports = [work / 'resumable-quartic/summary.json']
    atomic_json(output / ('verified-' + args.scope + '.json'),
                {'status': 'verified', 'scope': args.scope, 'replay_terminals': args.replay_terminals,
                 'reports': {str(p.relative_to(output)): digest(p) for p in reports}})
    print(f'PASS: {args.scope} audit. Restored files and reports: {work}')


if __name__ == '__main__':
    raise SystemExit(main())
