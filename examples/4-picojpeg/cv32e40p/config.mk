CORE := cv32e40p
ARCH_NAME ?= XIsaac
ETISS_ARCH ?= XIsaacCore
UARCH_NAME := CV32E40PXISAAC
MONITOR_NAME := InstructionTrace_XISAAC

INDEX_FILE := $(INPUTS_DIR)/filtered_selected_index.yml
HLS_DIR := $(INPUTS_DIR)/hls

INI_DL_URL := https://raw.githubusercontent.com/PhilippvK/isaac-artifacts/refs/heads/main/experiments/embench_iot/picojpeg/20260522T170540/run_new_perf_filtered_selected/custom.ini
ELF_DL_URL := https://github.com/PhilippvK/isaac-artifacts/raw/refs/heads/main/experiments/embench_iot/picojpeg/20260522T170540/run_new_perf_filtered_selected/generic_mlonmcu
ETISS_SRC_DL_URL := https://github.com/PhilippvK/isaac-artifacts/raw/refs/heads/main/experiments/embench_iot/picojpeg/20260522T170540/work/local/etiss_perf_filtered_selected/etiss_perf_source.tar.gz
