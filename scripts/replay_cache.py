"""Local, content-addressed receipts for successfully checked search replays.

Receipts accelerate repeat verification on a trusted local machine; they are
not certificates to distribute to an independent verifier. Only checked
successful subprocesses receive receipts. Changed inputs or tools miss cache.
"""
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(value, stream, sort_keys=True)
            stream.write('\n')
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def executable_identity(path):
    """Bind dynamically linked checkers to their actual library bytes as well."""
    path = Path(path).resolve()
    output = subprocess.run(['ldd', str(path)], text=True, capture_output=True)
    if output.returncode:
        raise RuntimeError(f'Cannot identify runtime libraries for {path}: {output.stderr or output.stdout}')
    if 'not found' in output.stdout:
        raise RuntimeError(f'Missing runtime library: {output.stdout}')
    dependencies = {str(path): digest(path)}
    for name in re.findall(r'(/[^\s()]+)', output.stdout):
        library = Path(name).resolve()
        dependencies[str(library)] = digest(library)
    return dependencies


def verify_adaptive_terminal(stdout, stderr, kind):
    """Check a fresh exhaustive run, including imported historical terminals.

    Imported records may have used a different kernel. We require a complete
    exclusion under this stage's kernel, rather than matching old node counts.
    """
    reports = [json.loads(line.removeprefix('TEMPLATE_RESULT '))
               for line in stderr.splitlines() if line.startswith('TEMPLATE_RESULT ')]
    if stdout or len(reports) != 1:
        raise RuntimeError('Adaptive replay emitted graphs or lacked one final report.')
    row = reports[0]
    counters = ('kind', 'nodes', 'patterns', 'leaves', 'covers', 'filtered',
                'residues', 'isomorphism_covers')
    if (not isinstance(row, dict)
            or any(type(row.get(k)) is not int or row[k] < 0 for k in counters)
            or row['kind'] != kind or row['patterns'] != 0 or row['residues'] != 0):
        raise RuntimeError('Adaptive replay did not certify a complete exclusion.')


class ReplayCache:
    def __init__(self, directory, identity):
        self.directory = Path(directory)
        self.identity = identity

    def verify(self, task, parse_run):
        prefix = task['prefix']
        mode = task.get('mode', 'cooperative')
        if mode not in ('cooperative', 'adaptive-terminal'):
            raise ValueError(f'Unknown replay mode: {mode}')
        expected = task['stdout']
        report = task['report']
        command = (['run'] if mode == 'adaptive-terminal'
                   else ['replay', str(report['cut'])])
        binding = {'format': 2, 'mode': mode, 'command': command, 'verifier': self.identity,
                   'executable': task['executable_identity'],
                   'state_sha256': task['state_sha256'],
                   'record_sha256': task['record_sha256'],
                   'prefix': prefix, 'stdout': expected, 'report': report}
        key = hashlib.sha256(encoded(binding)).hexdigest()
        receipt = {'key': key, 'status': 'verified'}
        path = self.directory / key[:2] / (key + '.json')
        try:
            if json.loads(path.read_text()) == receipt:
                return 'cached'
        except (FileNotFoundError, ValueError):
            pass  # Incomplete or damaged receipt: replay instead of trusting it.
        result = subprocess.run([task['executable'], *command],
                                input=prefix + '\n', text=True, capture_output=True, check=True)
        if mode == 'adaptive-terminal':
            verify_adaptive_terminal(result.stdout, result.stderr, int(prefix.split()[0]))
        elif result.stdout != expected or parse_run(result.stdout, result.stderr)[2] != report:
            raise RuntimeError(f'Replay mismatch for {task["executable"]}: {task["key"]}')
        atomic_json(path, receipt)
        return 'replayed'


def verify_tasks(tasks, cache, parse_run, workers, seconds=None):
    """Bound in-flight work; save each success before reporting progress."""
    started = time.monotonic()
    counts = {'cached': 0, 'replayed': 0, 'total': len(tasks)}
    next_task = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        active = set()
        try:
            while True:
                expired = seconds is not None and time.monotonic() - started >= seconds
                while not expired and next_task < len(tasks) and len(active) < workers:
                    active.add(pool.submit(cache.verify, tasks[next_task], parse_run))
                    next_task += 1
                if not active:
                    break
                done, active = wait(active, return_when=FIRST_COMPLETED)
                for future in done:
                    counts[future.result()] += 1
                completed = counts['cached'] + counts['replayed']
                if completed % 20 < len(done) or completed == len(tasks):
                    print(f'Checked {completed}/{len(tasks)} ({counts["cached"]} cached, {counts["replayed"]} replayed)', flush=True)
        except BaseException:
            for future in active:
                future.cancel()
            raise
    counts['complete'] = counts['cached'] + counts['replayed'] == len(tasks)
    counts['seconds'] = time.monotonic() - started
    return counts
