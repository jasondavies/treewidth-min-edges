#!/usr/bin/env python3
"""Lossless binary transport for explicitly supported branch-proof versions.

This changes only serialization. It introduces no inference rules. The bytes
after a fixed header encode the original tree in preorder, preserving every
node and therefore the checker's postorder reference numbering.
"""

MAGIC = b'TW11B\x01'
SUPPORTED_VERSIONS = (1, 2, 3, 4, 6, 7, 8, 9, 10)


def format_version(value):
    """Parse a canonical, explicitly supported JSON proof-format name."""
    prefix = '52-edge-branch-refutation-v'
    if type(value) is not str or not value.startswith(prefix):
        raise ValueError('Unknown proof format.')
    suffix = value[len(prefix):]
    if suffix not in tuple(str(v) for v in SUPPORTED_VERSIONS):
        raise ValueError('Unknown proof format.')
    return int(suffix)


def put_uint(stream, value):
    if type(value) is not int or not 0 <= value < 1 << 63:
        raise ValueError('Expected an unsigned integer below the transport limit.')
    while value >= 128:
        stream.write(bytes([(value & 127) | 128]))
        value >>= 7
    stream.write(bytes([value]))


def get_uint(stream):
    result = shift = 0
    while True:
        value = stream.read(1)
        if not value:
            raise ValueError('Truncated integer.')
        byte = value[0]
        result |= (byte & 127) << shift
        if byte < 128:
            if shift and byte == 0:
                raise ValueError('Noncanonical integer.')
            return result
        shift += 7
        if shift >= 63:
            raise ValueError('Integer exceeds transport limit.')


def take(stream, size):
    result = stream.read(size)
    if len(result) != size:
        raise ValueError('Truncated proof.')
    return result


def encode(certificate, stream):
    version = format_version(certificate['format'])
    if certificate['scope'] != 'minimum-order-counterexample':
        raise ValueError('Unknown proof scope.')
    prefix = certificate['prefix']
    if (not isinstance(prefix, list) or len(prefix) < 2
            or any(type(v) is not int for v in prefix)):
        raise ValueError('Invalid profile.')
    n, start, *masks = prefix
    if not 21 <= n <= 26 or not 0 <= start <= n or len(masks) != n:
        raise ValueError('Invalid profile dimensions.')
    stream.write(MAGIC + bytes([version, n, start]))
    for mask in masks:
        if not 0 <= mask < 1 << n:
            raise ValueError('Invalid profile mask.')
        put_uint(stream, mask)
    pending = [certificate['proof']]
    while pending:
        node = pending.pop()
        if not isinstance(node, list) or not node:
            raise ValueError('Invalid proof node.')
        tag = node[0]
        if tag == 'x' and len(node) == 1:
            stream.write(b'\x00')
        elif tag == 'r' and len(node) == 2:
            if not isinstance(node[1], list) or len(node[1]) > n:
                raise ValueError('Invalid trace length.')
            stream.write(b'\x01')
            put_uint(stream, len(node[1]))
            for step in node[1]:
                if not isinstance(step, list) or len(step) != 2:
                    raise ValueError('Invalid trace step.')
                operation, vertex = step
                if (operation not in ('delete', 'eliminate')
                        or type(vertex) is not int or not 0 <= vertex < n):
                    raise ValueError('Invalid trace operation.')
                stream.write(bytes([vertex + (32 if operation == 'eliminate' else 0)]))
        elif tag == 'b' and len(node) == 3:
            vertex, children = node[1:]
            if (type(vertex) is not int or not 0 <= vertex < n
                    or not isinstance(children, list)):
                raise ValueError('Invalid branch vertex.')
            stream.write(bytes([2, vertex]))
            put_uint(stream, len(children))
            pending.extend(reversed(children))
        elif tag == 's' and len(node) == 3 and version >= 2:
            reference, permutation = node[1:]
            if (not isinstance(permutation, list) or any(type(v) is not int for v in permutation)
                    or sorted(permutation) != list(range(n))):
                raise ValueError('Invalid reference permutation.')
            stream.write(b'\x03')
            put_uint(stream, reference)
            stream.write(bytes(permutation))
        elif tag == 'n' and len(node) in (2, 3) and version >= 3:
            vertex = node[1]
            if type(vertex) is not int or not 0 <= vertex < n:
                raise ValueError('Invalid neighborhood center.')
            stream.write(bytes([4 if len(node) == 3 else 5, vertex]))
            if len(node) == 3:
                pending.append(node[2])
        elif tag == 'g' and len(node) == 5 and version >= 3:
            from verify_branch_refutation import validate_program
            normalized, policy, first, switch = node[1:]
            if type(normalized) is not int or normalized not in (0, 1):
                raise ValueError('Invalid program mode.')
            validate_program(n, policy, first, switch)
            code = first + 32 * policy + (128 if switch >= 0 else 0)
            stream.write(bytes([6 + normalized, code]))
            if switch >= 0:
                stream.write(bytes([switch]))
        elif tag == 'u' and version >= 10 and len(node) in (1, 2):
            stream.write(bytes([22 if len(node) == 2 else 23]))
            if len(node) == 2:
                pending.append(node[1])
        elif tag == 'd' and version >= 8 and len(node) in (1, 2):
            stream.write(bytes([18 if len(node) == 2 else 19]))
            if len(node) == 2:
                pending.append(node[1])
        elif tag == 'm' and version >= 7 and len(node) in (1, 2):
            stream.write(bytes([16 if len(node) == 2 else 17]))
            if len(node) == 2:
                pending.append(node[1])
        elif tag == 'c' and version >= 6 and len(node) in (1, 2):
            stream.write(bytes([14 if len(node) == 2 else 15]))
            if len(node) == 2:
                pending.append(node[1])
        elif tag == 'e' and len(node) == 5 and (version == 4 or version >= 6):
            u, v = node[1:3]
            if type(u) is not int or type(v) is not int or not 0 <= u < v < n:
                raise ValueError('Invalid edge split endpoints.')
            stream.write(bytes([12, u, v]))
            pending.append(node[4])
            pending.append(node[3])
        else:
            raise ValueError('Invalid proof node.')


def read_header(stream):
    if take(stream, len(MAGIC)) != MAGIC:
        raise ValueError('Unknown binary transport.')
    version, n, start = take(stream, 3)
    if version not in SUPPORTED_VERSIONS or not 21 <= n <= 26 or not 0 <= start <= n:
        raise ValueError('Invalid profile header.')
    masks = [get_uint(stream) for _ in range(n)]
    if any(mask >= 1 << n for mask in masks):
        raise ValueError('Invalid profile mask.')
    return version, [n, start, *masks]


def read_node(stream, version, n):
    tag = take(stream, 1)[0]
    if tag == 0:
        return ['x']
    if tag == 1:
        length = get_uint(stream)
        if length > n:
            raise ValueError('Invalid trace length.')
        trace = []
        for code in take(stream, length):
            if (code & 31) >= n or code >= 64:
                raise ValueError('Invalid trace byte.')
            trace.append(['eliminate' if code & 32 else 'delete', code & 31])
        return ['r', trace]
    if tag == 2:
        vertex = take(stream, 1)[0]
        if vertex >= n:
            raise ValueError('Invalid branch vertex.')
        return ['b', vertex, get_uint(stream)]
    if tag == 3 and version >= 2:
        reference = get_uint(stream)
        permutation = list(take(stream, n))
        if sorted(permutation) != list(range(n)):
            raise ValueError('Invalid reference permutation.')
        return ['s', reference, permutation]
    if tag in (4, 5) and version >= 3:
        vertex = take(stream, 1)[0]
        if vertex >= n:
            raise ValueError('Invalid neighborhood center.')
        return ['n', vertex, int(tag == 4)]
    if tag in (6, 7) and version >= 3:
        from verify_branch_refutation import validate_program
        code = take(stream, 1)[0]
        value = code & 127
        policy, first = value >> 5, value & 31
        switch = take(stream, 1)[0] if code & 128 else -1
        validate_program(n, policy, first, switch)
        return ['g', tag - 6, policy, first, switch]
    if tag in (22, 23) and version >= 10:
        return ['u', int(tag == 22)]
    if tag in (18, 19) and version >= 8:
        return ['d', int(tag == 18)]
    if tag in (16, 17) and version >= 7:
        return ['m', int(tag == 16)]
    if tag in (14, 15) and version >= 6:
        return ['c', int(tag == 14)]
    if tag == 12 and (version == 4 or version >= 6):
        u, v = take(stream, 2)
        if not 0 <= u < v < n:
            raise ValueError('Invalid edge split endpoints.')
        return ['e', u, v]
    raise ValueError('Unknown proof opcode.')


def decode(stream):
    version, prefix = read_header(stream)

    def subtree():
        node = read_node(stream, version, prefix[0])
        if node[0] == 'b':
            node[2] = [subtree() for _ in range(node[2])]
        elif node[0] == 'n':
            node = ['n', node[1], subtree()] if node[2] else ['n', node[1]]
        elif node[0] in ('c', 'm', 'd', 'u'):
            node = [node[0], subtree()] if node[1] else [node[0]]
        elif node[0] == 'e':
            node.extend([subtree(), subtree()])
        return node

    proof = subtree()
    if stream.read(1):
        raise ValueError('Trailing proof bytes.')
    return {'format': f'52-edge-branch-refutation-v{version}',
            'scope': 'minimum-order-counterexample', 'prefix': prefix,
            'proof': proof}

def binary_events(stream, version, n):
    pending = 1
    while pending:
        node = read_node(stream, version, n)
        pending -= 1
        if node[0] in ('b', 'n'):
            pending += node[2]
        elif node[0] in ('c', 'm', 'd', 'u'):
            pending += node[1]
        elif node[0] == 'e':
            pending += 2
        yield node
    if stream.read(1):
        raise ValueError('Trailing proof bytes.')

def verify_stream(stream, expected_prefix=None):
    from collections import Counter
    from verify_branch_refutation import verify_events
    version, prefix = read_header(stream)
    needed = Counter()
    if version >= 2:
        needed.update(node[1] for node in binary_events(stream, version, prefix[0])
                      if node[0] == 's')
        stream.seek(0)
        read_header(stream)
    return verify_events(binary_events(stream, version, prefix[0]), version,
                         prefix, needed, expected_prefix)
