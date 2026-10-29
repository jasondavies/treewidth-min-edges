#!/usr/bin/env python3
"""Merge JSON bundles and binary certificates into one compact binary bundle.

Only serialization and container structure are checked here. Verify all
mathematical proofs and catalogue coverage with the order-specific verifier.
"""
import argparse
import io
import json
import lzma
from pathlib import Path
import shutil
import tempfile

from branch_certificate_binary import (MAGIC as CERTIFICATE_MAGIC,
                                       SUPPORTED_VERSIONS, encode)
from branch_certificate_bundle import (MAGIC, MAX_COUNTS, MAX_MEMBER_BYTES,
                                       iter_members, open_input, write_header,
                                       write_member)


def input_members(path, order):
    with open_input(path) as stream:
        marker = stream.read(len(MAGIC))
        stream.seek(0)
        if marker == MAGIC:
            yield from iter_members(stream, order)
        elif marker.startswith(CERTIFICATE_MAGIC):
            data = stream.read(MAX_MEMBER_BYTES + 1)
            if len(data) > MAX_MEMBER_BYTES:
                raise ValueError('Invalid member length.')
            yield data
        else:
            value = json.load(stream)
            if value.get('format') == f'order{order}-refutations-v1':
                cases = value['cases']
            elif value.get('format') in tuple(
                    f'52-edge-branch-refutation-v{version}'
                    for version in SUPPORTED_VERSIONS):
                cases = [value]
            else:
                raise ValueError('Unknown JSON bundle or wrong order.')
            if not isinstance(cases, list):
                raise ValueError('Invalid bundle cases.')
            for case in cases:
                certificate = case.get('certificate', case)
                output = io.BytesIO()
                encode(certificate, output)
                yield output.getvalue()


def pack_members(raw_members, output, order):
    if type(order) is not int or order not in MAX_COUNTS:
        raise ValueError('Unknown bundle order.')
    output = Path(output)
    temporary = None
    count = 0
    try:
        # Spooling permits a count header without retaining all member bytes or
        # decoding any binary proof tree. Publication happens only at the end.
        with tempfile.TemporaryFile() as members:
            for data in raw_members:
                count += 1
                if count > MAX_COUNTS[order]:
                    raise ValueError('Too many bundle members.')
                write_member(members, data, order)
            members.seek(0)
            with tempfile.NamedTemporaryFile(dir=output.parent, prefix=output.name + '.',
                                             suffix='.tmp', delete=False) as raw:
                temporary = Path(raw.name)
                if output.suffix == '.xz':
                    with lzma.LZMAFile(raw, 'wb', preset=9) as compressed:
                        write_header(compressed, order, count)
                        shutil.copyfileobj(members, compressed)
                else:
                    write_header(raw, order, count)
                    shutil.copyfileobj(members, raw)
            temporary.replace(output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return count, output.stat().st_size


def pack(paths, output, order):
    members = (data for path in paths for data in input_members(path, order))
    return pack_members(members, output, order)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--order', type=int, choices=sorted(MAX_COUNTS), required=True)
    parser.add_argument('output', type=Path)
    parser.add_argument('inputs', type=Path, nargs='+')
    args = parser.parse_args()
    count, size = pack(args.inputs, args.output, args.order)
    print(f'Encoded {count} candidate proofs in {size:,} bytes. Independent verification required.')


if __name__ == '__main__':
    main()
