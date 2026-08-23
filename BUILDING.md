# Building the Field Kit FX firmware

The original firmware was developed with **SW4STM32 / AC6** (System Workbench
for STM32). The Eclipse project files (`.project`, `.cproject`), the linker
script and the startup file were **not part of the public source release**, so
this repository as shipped cannot be built out of the box.

This tree recreates a working build with a plain **GNU Arm Embedded GCC**
toolchain.

## Target hardware

| Item          | Value |
|---------------|-------|
| MCU           | STM32F303VCT6 (LQFP100, Cortex-M4F) |
| Flash         | 256 KB @ `0x08000000` |
| SRAM          | 40 KB @ `0x20000000` + 8 KB CCM @ `0x10000000` |
| Audio codec   | WM8731, I2S slave mode, codec is clock master (SPI2 full-duplex + DMA) |
| Looper memory | 23LC1024 SPI SRAM |
| LEDs          | PCA9956B I2C LED driver |
| HAL version   | ST STM32F3xx HAL V1.4.0 (16-Dec-2016) |

## What was added on top of the original release

- `CMSIS/` — CMSIS device + core headers and the GCC startup file, taken from
  ST's [STM32CubeF3](https://github.com/STMicroelectronics/STM32CubeF3)
  (tag `v1.10.0`, Apache-2.0). These were referenced by the source but missing
  from the release.
- `STM32F303VCTx_FLASH.ld` — standard ST-style linker script for the
  STM32F303xC flash/RAM layout (recreated; the original AC6 script was not
  published).
- `Makefile` — see below.

Everything else is byte-identical to the original source. Two compatibility
measures are applied at build time (no source edits):

1. `-fcommon` — this 2016-era codebase defines global variables in headers
   (`adsr.h`, `looper.h`, `sequencer.h`, `UI.h`, …). GCC ≥ 10 defaults to
   `-fno-common`, which would fail at link time.
2. The ST `*_template.c` files in `HAL_Driver/Src/` are excluded from the
   build (they are copy-me templates and define conflicting symbols).

## Toolchain (macOS)

    brew install gcc-arm-embedded stlink dfu-util

(any recent `arm-none-eabi-gcc` works; the build was verified with 15.3)

## Build

    make                # release build (-O2), outputs in build/
    make OPT=-O0        # debug build
    make clean

Artifacts: `build/FieldKitFX.elf`, `.bin`, `.hex`, `.lst` (disassembly),
`.map` (linker map). Typical release size: ~74 KB flash / ~6 KB RAM.

## Flash

**DFU (stock system bootloader):** hold the LOOP button while powering on the
unit, then:

    make flash-dfu
    # equivalent to: dfu-util -a 0 -s 0x08000000:leave -D build/FieldKitFX.bin

**ST-Link (SWD, no bootloader mode needed):**

    make flash-stlink
    # equivalent to: st-flash write build/FieldKitFX.bin 0x08000000

STM32CubeProgrammer also works with either interface.
