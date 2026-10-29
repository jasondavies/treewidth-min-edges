#!/usr/bin/env python3
"""Length-prefixed containers for independently checked branch certificates.

The outer container certifies no mathematics. Callers must verify every member
and independently establish coverage of the appropriate root catalogue.
"""
import io
import json
import lzma
from pathlib import Path

from branch_certificate_binary import (MAGIC as CERTIFICATE_MAGIC, decode,
                                       get_uint, put_uint, read_header, take)

MAGIC = b'TWBBC1\n'
MAX_COUNTS = {23: 425, 24: 364, 25: 40}
MAX_MEMBER_BYTES = 1 << 30


def write_header(stream, order, count):
    if type(order) is not int or order not in MAX_COUNTS:
        raise ValueError('Unknown bundle order.')
    if type(count) is not int or not 0 <= count <= MAX_COUNTS[order]:
        raise ValueError('Invalid bundle count.')
    stream.write(MAGIC + bytes([order]))
    put_uint(stream, count)


def read_bundle_header(stream, expected_order=None):
    if take(stream, len(MAGIC)) != MAGIC:
        raise ValueError('Unknown branch bundle format.')
    order = take(stream, 1)[0]
    if order not in MAX_COUNTS or (expected_order is not None and order != expected_order):
        raise ValueError('Wrong bundle order.')
    count = get_uint(stream)
    if count > MAX_COUNTS[order]:
        raise ValueError('Invalid bundle count.')
    return order, count


def member_prefix(data, expected_order=None):
    _, prefix = read_header(io.BytesIO(data))
    if expected_order is not None and prefix[0] != expected_order:
        raise ValueError('Member has the wrong graph order.')
    return prefix


def write_member(stream, data, expected_order):
    if not isinstance(data, bytes) or not 0 < len(data) <= MAX_MEMBER_BYTES:
        raise ValueError('Invalid member length.')
    member_prefix(data, expected_order)
    put_uint(stream, len(data))
    stream.write(data)


def iter_members(stream, expected_order=None):
    """Yield one raw certificate at a time; require complete outer-file EOF."""
    order, count = read_bundle_header(stream, expected_order)
    for _ in range(count):
        length = get_uint(stream)
        if not 0 < length <= MAX_MEMBER_BYTES:
            raise ValueError('Invalid member length.')
        data = take(stream, length)
        member_prefix(data, order)
        yield data
    if stream.read(1):
        raise ValueError('Trailing bundle bytes.')


def open_input(path):
    path = Path(path)
    return lzma.open(path, 'rb') if path.suffix == '.xz' else path.open('rb')


def selected_certificate(path, predicate):
    """Load only a selected binary member's tree for tests or conversion.

    The predicate receives a root prefix. This selection helper does not
    verify the selected proof, nor validate members skipped after a match.
    Legacy JSON bundles are supported for migration, but require JSON loading.
    """
    with open_input(path) as stream:
        marker = stream.read(len(MAGIC))
        stream.seek(0)
        if marker == MAGIC:
            for data in iter_members(stream):
                if predicate(member_prefix(data)):
                    return decode(io.BytesIO(data))
        elif marker.startswith(CERTIFICATE_MAGIC):
            data = stream.read(MAX_MEMBER_BYTES + 1)
            if len(data) > MAX_MEMBER_BYTES:
                raise ValueError('Invalid member length.')
            if predicate(member_prefix(data)):
                return decode(io.BytesIO(data))
        else:
            bundle = json.load(stream)
            cases = bundle.get('cases', [bundle])
            for case in cases:
                certificate = case.get('certificate', case)
                if predicate(certificate['prefix']):
                    return certificate
    raise ValueError('No matching certificate.')
