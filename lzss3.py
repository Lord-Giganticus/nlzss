#!/usr/bin/env python3

import sys
from sys import stdin, stdout, stderr, exit
from os import SEEK_SET, SEEK_CUR, SEEK_END
from errno import EPIPE
from struct import pack, unpack

__all__ = ('decompress', 'decompress_file', 'decompress_bytes',
           'decompress_overlay', 'DecompressionError')

class DecompressionError(ValueError):
    pass

def bits(byte):
    return ((byte >> 7) & 1,
            (byte >> 6) & 1,
            (byte >> 5) & 1,
            (byte >> 4) & 1,
            (byte >> 3) & 1,
            (byte >> 2) & 1,
            (byte >> 1) & 1,
            (byte) & 1)

def decompress_raw_lzss10(indata, decompressed_size, _overlay=False):
    """Decompress LZSS-compressed bytes. Returns a bytearray."""
    data = bytearray()

    it = iter(indata)

    disp_extra = 1

    def writebyte(b):
        data.append(b)
    def readbyte():
        return next(it)
    def readshort():
        # big-endian
        a = next(it)
        b = next(it)
        return (a << 8) | b
    def copybyte():
        data.append(next(it))

    while len(data) < decompressed_size:
        b = readbyte()
        flags = bits(b)
        for flag in flags:
            if flag == 0:
                copybyte()
            elif flag == 1:
                sh = readshort()
                count = (sh >> 0xc) + 3
                disp = (sh & 0xfff) + disp_extra

                for _ in range(count):
                    writebyte(data[-disp])
            else:
                raise ValueError(flag)

            if decompressed_size <= len(data):
                break

    if len(data) != decompressed_size:
        raise DecompressionError("decompressed size does not match the expected size")

    return data

def decompress(obj):
    """Decompress LZSS-compressed bytes or a file-like object.

    Shells out to decompress_file() or decompress_bytes() depending on
    whether or not the passed-in object has a 'read' attribute or not.

    Returns a bytearray."""
    if hasattr(obj, 'read'):
        return decompress_file(obj)
    else:
        return decompress_bytes(obj)

def decompress_bytes(data):
    """Decompress LZSS-compressed bytes. Returns a bytearray."""
    header = data[8:12]
    if header[0] == 0x10:
        decompress_raw = decompress_raw_lzss10
    else:
        raise DecompressionError("not a lzss10-compressed file")

    decompressed_size, = unpack("<L", header[1:] + b'\x00')

    data = data[4:]
    return decompress_raw(data, decompressed_size)

def decompress_file(f):
    """Decompress an LZSS-compressed file. Returns a bytearray.

    This isn't any more efficient than decompress_bytes, as it reads
    the entire file into memory. It is offered as a convenience.
    """
    
    f.read(8) # ignore first 8 bytes, this is file-format-specific
    header = f.read(4)
    if header[0] == 0x10:
        decompress_raw = decompress_raw_lzss10
    else:
        raise DecompressionError("not a lzss10-compressed file")

    decompressed_size, = unpack("<L", header[1:] + b'\x00')

    data = f.read()
    return decompress_raw(data, decompressed_size)

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    try:
        f = open(args[0], "rb")
    except IOError as e:
        print(e, file=stderr)
        return 2

    if len(args) > 1:
        try:
            out = open(args[1], "wb")
        except IOError as e:
            print(e, file=stderr)
            return 3
    else:
        out = sys.stdout
        if hasattr(stdout, 'buffer'):
            # grab the underlying binary stream
            stdout = stdout.buffer

    try:
        out.write(decompress_file(f))
    except IOError as e:
        if e.errno == EPIPE:
            # don't complain about a broken pipe
            pass
        else:
            raise
    except (DecompressionError,) as e:
        print(e, file=stderr)
        return 1

    return 0



if __name__ == '__main__':
    exit(main())
