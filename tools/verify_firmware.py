#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validate the memory layout and reset vectors of a Field Kit FX ELF image."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

FLASH = (0x08000000, 0x08040000)
RAM = (0x20000000, 0x2000A000)
CCMRAM = (0x10000000, 0x10002000)
PT_LOAD = 1
EM_ARM = 40


def unpack_from(fmt: str, data: bytes, offset: int, label: str) -> tuple[int, ...]:
    size = struct.calcsize(fmt)
    if offset < 0 or offset + size > len(data):
        raise ValueError(f"{label} extends beyond the ELF file")
    return struct.unpack_from(fmt, data, offset)


def span_fits(start: int, size: int, region: tuple[int, int]) -> bool:
    return region[0] <= start <= region[1] and size <= region[1] - start


def region_for(start: int, size: int) -> str | None:
    for name, region in (("FLASH", FLASH), ("RAM", RAM), ("CCMRAM", CCMRAM)):
        if span_fits(start, size, region):
            return name
    return None


def c_string(table: bytes, offset: int) -> str:
    if offset >= len(table):
        raise ValueError("section name offset is outside the string table")
    end = table.find(b"\0", offset)
    if end == -1:
        raise ValueError("unterminated section name")
    return table[offset:end].decode("ascii", errors="strict")


def validate(path: Path) -> None:
    data = path.read_bytes()
    if len(data) < 52 or data[:4] != b"\x7fELF":
        raise ValueError("not an ELF file")
    if data[4] != 1 or data[5] != 1:
        raise ValueError("expected a 32-bit little-endian ELF image")

    header = unpack_from("<HHIIIIIHHHHHH", data, 16, "ELF header")
    (
        _elf_type,
        machine,
        _version,
        entry,
        program_offset,
        section_offset,
        _flags,
        _header_size,
        program_entry_size,
        program_count,
        section_entry_size,
        section_count,
        section_names_index,
    ) = header

    if machine != EM_ARM:
        raise ValueError(f"expected ARM machine type {EM_ARM}, got {machine}")
    if section_entry_size < 40 or section_names_index >= section_count:
        raise ValueError("invalid section-header table")
    if program_entry_size < 32:
        raise ValueError("invalid program-header table")

    sections: list[tuple[int, ...]] = []
    for index in range(section_count):
        offset = section_offset + index * section_entry_size
        sections.append(unpack_from("<IIIIIIIIII", data, offset, "section header"))

    names_header = sections[section_names_index]
    names_offset, names_size = names_header[4], names_header[5]
    if names_offset + names_size > len(data):
        raise ValueError("section-name string table extends beyond the ELF file")
    names = data[names_offset : names_offset + names_size]

    vector = None
    for section in sections:
        if c_string(names, section[0]) == ".isr_vector":
            vector = section
            break
    if vector is None:
        raise ValueError("missing .isr_vector section")

    vector_address, vector_offset, vector_size = vector[3], vector[4], vector[5]
    if vector_address != FLASH[0]:
        raise ValueError(
            f".isr_vector starts at 0x{vector_address:08x}, expected 0x{FLASH[0]:08x}"
        )
    if vector_size < 8:
        raise ValueError(".isr_vector does not contain initial SP and reset vectors")

    initial_sp, reset_vector = unpack_from(
        "<II", data, vector_offset, "initial vector table entries"
    )
    if not (RAM[0] < initial_sp <= RAM[1]) or initial_sp % 8:
        raise ValueError(f"initial SP 0x{initial_sp:08x} is not valid aligned SRAM")
    if reset_vector & 1 == 0:
        raise ValueError(
            f"reset vector 0x{reset_vector:08x} does not select Thumb state"
        )
    reset_address = reset_vector & ~1
    if not span_fits(reset_address, 2, FLASH):
        raise ValueError(f"reset vector 0x{reset_vector:08x} is outside FLASH")
    if entry != reset_vector:
        raise ValueError(
            f"ELF entry 0x{entry:08x} does not match reset vector 0x{reset_vector:08x}"
        )

    load_count = 0
    for index in range(program_count):
        offset = program_offset + index * program_entry_size
        program = unpack_from("<IIIIIIII", data, offset, "program header")
        kind, file_offset, virtual, physical, file_size, memory_size, _flags, _align = (
            program
        )
        if kind != PT_LOAD:
            continue
        load_count += 1
        if file_size > memory_size:
            raise ValueError(f"LOAD {index} has file size greater than memory size")
        if file_offset + file_size > len(data):
            raise ValueError(f"LOAD {index} extends beyond the ELF file")
        region = region_for(virtual, memory_size)
        if region is None:
            raise ValueError(
                f"LOAD {index} range 0x{virtual:08x}+0x{memory_size:x} is outside target memory"
            )
        if file_size and not span_fits(physical, file_size, FLASH):
            raise ValueError(
                f"LOAD {index} image 0x{physical:08x}+0x{file_size:x} is outside FLASH"
            )

    if load_count == 0:
        raise ValueError("ELF contains no loadable segments")

    print(
        f"verified {path}: vectors at 0x{vector_address:08x}, "
        f"SP=0x{initial_sp:08x}, reset=0x{reset_vector:08x}, {load_count} LOAD segments"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("elf", type=Path, help="firmware ELF image")
    args = parser.parse_args()
    try:
        validate(args.elf)
    except (OSError, ValueError, struct.error) as error:
        parser.exit(1, f"firmware verification failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
