CORE := cv32e40p
ARCH_NAME ?= XIsaac
ETISS_ARCH ?= XIsaacCore
UARCH_NAME := CV32E40PXISAAC
MONITOR_NAME := InstructionTrace_XISAAC

INDEX_FILE := $(INPUTS_DIR)/final_index.yml
HLS_DIR := $(INPUTS_DIR)/hls

INI_DL_URL := https://raw.githubusercontent.com/PhilippvK/isaac-artifacts/refs/heads/main/experiments/embench_iot/picojpeg/20250808T110607/run_compare_final/1/custom.ini
ELF_DL_URL := https://github.com/PhilippvK/isaac-artifacts/raw/refs/heads/main/experiments/embench_iot/picojpeg/20250808T110607/run_compare_final/1/generic_mlonmcu
ETISS_SRC_DL_URL := https://github.com/PhilippvK/isaac-artifacts/raw/refs/heads/main/experiments/embench_iot/picojpeg/20250808T110607/work/docker/etiss_final/etiss_source.zip
