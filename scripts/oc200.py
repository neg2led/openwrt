#!/usr/bin/python3

"""Script to generate firmware image for TP-Link OC200"""

import argparse
import hashlib
import struct

PT_OFFSET = 0x1000


struct_header = struct.Struct('>4I')
struct_img_part = struct.Struct('>32s5I')


def gen_checksum(data):
    img_data = bytearray(data)
    for i in range(0x10):
        img_data[0x10+1] = 0
    for i in range(0x80):
        img_data[0x130+1] = 0
    md5sum = hashlib.md5(data)
    print(md5sum.hexdigest())
    return (hashlib.md5(data).digest())

def gen_header(pt_offset, size):
    return struct_header.pack(int(0x00000001), int(0xaa55d98f), pt_offset, size)


def gen_pt(name, nand, fl_offset, fl_size, img_offset, img_size):
    return struct_img_part.pack(name.encode('ascii'), fl_offset, fl_size, img_offset, img_size, nand)


parser = argparse.ArgumentParser('generate TP-Link mvebu image')

parser.add_argument(
        '-d', '--dtb', help='read device tree image from <file>', required=True)

parser.add_argument(
        '-k', '--kernel', help='read kernel image from <file>', required=True)

parser.add_argument(
        '-r', '--rootfs', help='read rootfs image from <file>', required=True)

parser.add_argument(
        '-o', '--output', help='write image to <file>', required=True)

args = parser.parse_args()

img_dtb = open(args.dtb, "rb").read()
img_knl = open(args.kernel, "rb").read()
img_rfs = open(args.rootfs, "rb").read()



with open(args.output, 'wb') as img_factory:
    img_factory.seek(PT_OFFSET)
    img_factory.write(gen_pt("dtb", True, 0x70000, 0x1000, 0xd0000, len(img_dtb)))
    img_factory.seek(0xd0000)
    img_factory.write(img_dtb)

    img_factory.seek(PT_OFFSET + 1 * struct_img_part.size)
    img_factory.write(gen_pt("kernel", True, 0x80000, 0x1000000, 0xd0000 + len(img_dtb), len(img_knl)))
    img_factory.seek(0xd0000 + len(img_dtb))
    img_factory.write(img_knl)

    img_factory.seek(PT_OFFSET + 2 * struct_img_part.size)
    img_factory.write(gen_pt("rootfs", True, 0x2080000, 0x10000000, 0xd0000 + len(img_dtb) + len(img_knl), len(img_rfs)))
    img_factory.seek(0xd0000 + len(img_dtb) + len(img_knl))
    img_factory.write(img_rfs)

    img_factory.seek(0, 2)
    img_size = img_factory.tell()
    img_factory.seek(0)
    img_factory.write(gen_header(PT_OFFSET, img_size))

    img_factory.close()

with open(args.output, 'rb') as img_factory:
    img_data = bytearray(img_factory.read())
    img_factory.close()

with open(args.output, 'wb') as img_factory:
    img_factory.write(img_data)
    img_factory.seek(0x10)
    img_factory.write(gen_checksum(img_data))

    img_factory.close()
