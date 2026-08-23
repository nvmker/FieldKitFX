# shellcheck shell=sh disable=SC2034,SC2276,SC2283,SC2037,SC2068
###############################################################################
# KOMA Elektronik Field Kit FX — GNU Arm Embedded GCC Makefile
#
# The original firmware was built with SW4STM32/AC6 (Eclipse project files
# were not part of the public source release). This Makefile recreates the
# build with a plain arm-none-eabi toolchain:
#
#   make                -> build/FieldKitFX.{elf,.bin,.hex}
#   make flash-dfu      -> flash via stock USB DFU bootloader (hold LOOP while powering on)
#   make flash-stlink   -> flash via ST-Link SWD
#   make size / clean / objdump
#
# Toolchain: brew install gcc-arm-embedded stlink dfu-util
###############################################################################

TARGET=FieldKitFX
BUILD=build

PREFIX?=arm-none-eabi-
CC=$(PREFIX)gcc
AS=$(PREFIX)gcc -x assembler-with-cpp
CP=$(PREFIX)objcopy
SZ=$(PREFIX)size
OD=$(PREFIX)objdump

#######################################
# MCU / device
#######################################
# STM32F303VCT6 (LQFP100, 256K flash, 40K SRAM + 8K CCM), Cortex-M4F
CPU=-mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard
DEFS=$(CPU) -DUSE_HAL_DRIVER -DSTM32F303xC

#######################################
# Optimization (release default; override with OPT=-O0 ...)
#######################################
OPT?=-O2

#######################################
# Include paths / sources
#######################################
INCLUDES=-Iinc \
         -Isrc \
         -Ihardware \
         -Iengine \
         -IUI \
         -IdataUtils \
         -IHAL_Driver/Inc \
         -ICMSIS/Device/Include \
         -ICMSIS/Include

# ST ships *_template.c files in HAL_Driver/Src that are copy-me references —
# they must not be compiled (duplicate definitions of HAL_InitTick etc.)
HAL_TEMPLATE_FILES=$(wildcard HAL_Driver/Src/*_template.c)
SOURCES=$(wildcard src/*.c) \
        $(wildcard hardware/*.c) \
        $(wildcard engine/*.c) \
        $(wildcard UI/*.c) \
        $(wildcard dataUtils/*.c) \
        $(filter-out $(HAL_TEMPLATE_FILES),$(wildcard HAL_Driver/Src/*.c))

ASM_SOURCES=CMSIS/startup_stm32f303xc.s

LDSCRIPT=STM32F303VCTx_FLASH.ld

#######################################
# Flags
#######################################
# -fcommon: this 2016-era codebase defines globals in headers (e.g. adsr.h,
# looper.h, UI.h); GCC >= 10 defaults to -fno-common which would fail at link.
CFLAGS=$(DEFS) $(OPT) -g3 -std=gnu11 \
       -ffunction-sections -fdata-sections -fcommon \
       -Wall -fstack-usage

ASFLAGS=$(CPU) $(OPT) -g3 -x assembler-with-cpp

LDFLAGS=$(CPU) -specs=nano.specs -T$(LDSCRIPT) \
       -Wl,-Map=$(BUILD)/$(TARGET).map,--cref \
       -Wl,--gc-sections -Wl,--no-warn-rwx-segments \
       -lm

#######################################
# Objects
#######################################
OBJECTS=$(addprefix $(BUILD)/,$(notdir $(SOURCES:.c=.o)))
vpath %.c $(sort $(dir $(SOURCES)))
OBJECTS+=$(addprefix $(BUILD)/,$(notdir $(ASM_SOURCES:.s=.o)))
vpath %.s $(sort $(dir $(ASM_SOURCES)))

#######################################
# Rules
#######################################
.PHONY: all size clean flash-dfu flash-stlink objdump

all: $(BUILD)/$(TARGET).elf $(BUILD)/$(TARGET).bin $(BUILD)/$(TARGET).hex $(BUILD)/$(TARGET).lst size

$(BUILD)/%.o: %.c Makefile | $(BUILD)
	$(CC) -c $(CFLAGS) $(INCLUDES) $< -o $@

$(BUILD)/%.o: %.s Makefile | $(BUILD)
	$(AS) -c $(ASFLAGS) $< -o $@

$(BUILD)/$(TARGET).elf: $(OBJECTS) $(LDSCRIPT) Makefile
	$(CC) $(OBJECTS) $(LDFLAGS) -o $@
	$(SZ) $@

$(BUILD)/%.bin: $(BUILD)/%.elf
	$(CP) -O binary -S $< $@

$(BUILD)/%.hex: $(BUILD)/%.elf
	$(CP) -O ihex $< $@

$(BUILD)/$(TARGET).lst: $(BUILD)/$(TARGET).elf
	$(OD) -d $(BUILD)/$(TARGET).elf > $(BUILD)/$(TARGET).lst

$(BUILD):
	mkdir -p $@

size:
	$(SZ) $(BUILD)/$(TARGET).elf

objdump:
	$(OD) -d $(BUILD)/$(TARGET).elf | less

# USB DFU bootloader: hold LOOP button while powering the unit on, then run:
#   make flash-dfu
flash-dfu: $(BUILD)/$(TARGET).bin
	dfu-util -a 0 -s 0x08000000:leave -D $(BUILD)/$(TARGET).bin

# ST-Link SWD (no bootloader mode needed):
#   make flash-stlink
flash-stlink: $(BUILD)/$(TARGET).bin
	st-flash write $(BUILD)/$(TARGET).bin 0x08000000

clean:
	rm -rf $(BUILD)
