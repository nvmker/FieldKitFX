# Provenance — vendored CMSIS files

All files under `CMSIS/` are vendored **verbatim** (byte-identical, verified)
from STMicroelectronics' STM32CubeF3 repository:

- Upstream: <https://github.com/STMicroelectronics/STM32CubeF3>
- Tag: `v1.10.0` (tag object `d66c5ad9c9972856e0ed3fa87d306c8f95692722`)
- Fetched: 2026-08-23
- License: **BSD-3-Clause** — the CMSIS and CMSIS Device components of
  STM32CubeF3 `v1.10.0` are licensed BSD-3-Clause per the `License.md` shipped
  in that tag. (Upstream relicensed CMSIS to Apache-2.0 only in later
  releases; this tag predates that change.) Each vendored file retains its
  original copyright and license header.

**Do not modify** these files. If a patch is ever needed, do it here and
record the deviation in this file, or re-vendor from a newer tag and update
this manifest.

## Mapping to upstream paths

| File in this repo | Upstream path (under tag v1.10.0) |
| ----------------- | --------------------------------- |
| CMSIS/Device/Include/stm32f3xx.h | Drivers/CMSIS/Device/ST/STM32F3xx/Include/stm32f3xx.h |
| CMSIS/Device/Include/stm32f303xc.h | Drivers/CMSIS/Device/ST/STM32F3xx/Include/stm32f303xc.h |
| CMSIS/Device/Include/system_stm32f3xx.h | Drivers/CMSIS/Device/ST/STM32F3xx/Include/system_stm32f3xx.h |
| CMSIS/startup_stm32f303xc.s | Drivers/CMSIS/Device/ST/STM32F3xx/Source/Templates/gcc/startup_stm32f303xc.s |
| CMSIS/Include/core_cm4.h (and other core_*.h) | Drivers/CMSIS/Include/ |
| CMSIS/Include/cmsis_gcc.h, cmsis_armcc.h | Drivers/CMSIS/Include/ |

## SHA256 manifest

Verify with `shasum -a 256 -c` (run from repo root):

    b541fdf243bc4f24493ef20041a3603bfc49138294bb9c0fecebb2ba795b378b  CMSIS/Device/Include/stm32f3xx.h
    5a44affaff5b9890de234ae199e214807d41136c1d8ad39807feee65fbb944f4  CMSIS/Device/Include/stm32f303xc.h
    30b53db21a6b6f0927fee18b82ca5504dac4da8e95c11174c31ee63563e950f7  CMSIS/Device/Include/system_stm32f3xx.h
    2401d5b8d87bde74a1eba0413e6defcca052b6cec0da08df86d60a238dfa837c  CMSIS/Include/core_cm0.h
    1f0f7859d6355a7569799a9802560c55bc6a660be501ecbc45dedb77d85be3c9  CMSIS/Include/core_cm0plus.h
    03a80f17ff18c5d0e3b234009f98698cd402b8ea972df687a6cfafd8b8a78654  CMSIS/Include/core_cm3.h
    83c5d601dd5640a863fe4dc43cd228b46239bbf9f07b51102bf0c1c8f235cdfa  CMSIS/Include/core_cm4.h
    1fdd226d82bde2a90231ba47a59377158b8907e4cada2a6215f32dcf13ab35cd  CMSIS/Include/core_cmFunc.h
    c9b8e36d05097da5d493f197aa7f81ce517f4532536925b568ccbd6e2c01eb8a  CMSIS/Include/core_cmInstr.h
    5d338d36730ccbd138126078e17f69c308a015f0a88d85bd639af072e527d53d  CMSIS/Include/core_cmSimd.h
    6c7e75d09887cb3035f18bc6f4fdbd7392a50379cd556315deb3bcb762d99078  CMSIS/Include/cmsis_gcc.h
    9f1711b4c540a294c6ed57da21b6fca9eba032022899e1588c4ba3d3ac4105fb  CMSIS/Include/cmsis_armcc.h
    3dcc826e1e326fd3404a7af1f4b64f4b6c91a401887025033b2a7f3af6e979e1  CMSIS/startup_stm32f303xc.s

All 13 files were verified byte-identical against
`https://raw.githubusercontent.com/STMicroelectronics/STM32CubeF3/v1.10.0/<path>`
on 2026-08-23.
