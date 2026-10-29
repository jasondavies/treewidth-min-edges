#!/usr/bin/env python3
"""Regenerate and verify the complete467 marked42-residue reconstruction.

Only source and the earlier classified family files are needed. The C
producer is untrusted; Python independently reconstructs every candidate and
checks every order/isomorphism. No large transcript is retained by default.
"""
import argparse
from contextlib import ExitStack
import json
import lzma
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import time

from marked_residue_common import EXCEPTION_G6, EXCEPTION_MASKS
from marked_residue_reconstruction import catalogue, verify_stream


class TeeReader:
    def __init__(self, source, destination=None):
        self.source, self.destination = source, destination

    def read(self, size=-1):
        data = self.source.read(size)
        if self.destination is not None:
            self.destination.write(data)
        return data


def regenerate(repository, *, native=False, compiler=None, output=None):
    repository = Path(repository)
    source = Path(__file__).resolve().parent
    output = None if output is None else Path(output)
    if output is not None and output.exists():
        raise FileExistsError(output)
    command = shlex.split(os.environ.get('CC', 'cc') if compiler is None else compiler)
    if not command:
        raise ValueError('The compiler command is empty.')
    started = time.monotonic()
    families = catalogue(repository)
    temporary_output = None
    try:
        with tempfile.TemporaryDirectory(prefix='marked-residue-') as directory, ExitStack() as stack:
            build = Path(directory)
            for name in ('marked_residue_proposer.c', 'marked_residue_exception_map.inc'):
                shutil.copyfile(source / name, build / name)
            shutil.copyfile(repository / 'scripts/treewidth.c', build / 'treewidth.c')
            (build / 'exception.h').write_text('static const M exception_graph[22] = {'
                + ','.join(str(mask) + 'u' for mask in EXCEPTION_MASKS) + '};\n')
            input_path = build / 'catalogue.g6'
            input_path.write_text(''.join(code + '\n' for r, code in families))
            executable = build / 'propose'
            compiled = subprocess.run(command + ['-O3'] + (['-march=native'] if native else [])
                                      + [str(build / 'marked_residue_proposer.c'), '-o', str(executable)],
                                      capture_output=True, text=True, check=False)
            if compiled.returncode:
                raise RuntimeError('Could not compile the untrusted producer:\n' + compiled.stderr)
            destination = None
            if output is not None:
                fd, name = tempfile.mkstemp(prefix=output.name + '.', suffix='.candidate', dir=output.parent)
                temporary_output = Path(name)
                raw = stack.enter_context(os.fdopen(fd, 'wb'))
                destination = (stack.enter_context(lzma.LZMAFile(raw, 'wb', preset=6))
                               if output.suffix == '.xz' else raw)
            errors = stack.enter_context(tempfile.TemporaryFile())
            inputs = stack.enter_context(input_path.open('rb'))
            child = subprocess.Popen([str(executable)], stdin=inputs, stdout=subprocess.PIPE, stderr=errors)
            try:
                checked = verify_stream(TeeReader(child.stdout, destination), families)
                code = child.wait()
                if code:
                    errors.seek(0)
                    raise RuntimeError('Untrusted producer failed:\n' + errors.read().decode(errors='replace'))
            finally:
                child.stdout.close()
                if child.poll() is None:
                    child.terminate()
                    try:
                        child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait()
            errors.seek(0)
            producer_report = errors.read().decode(errors='replace').strip()
        if output is not None:
            temporary_output.replace(output)
        return {'status': 'verified-relative-to-prior-classifications',
                'exception_graph6': EXCEPTION_G6, 'checked': checked,
                'producer': producer_report, 'seconds': time.monotonic() - started,
                'saved_transcript': None if output is None else str(output)}
    finally:
        if temporary_output is not None:
            temporary_output.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--native', action='store_true')
    parser.add_argument('--compiler')
    parser.add_argument('--output', type=Path, help='optional checked .bin or .xz transcript')
    args = parser.parse_args()
    result = regenerate(args.repository, native=args.native, compiler=args.compiler, output=args.output)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
