CORE := cv32e40p

SET_NAME := XCFU0
ARCH_NAME := RV32IMACFDXCFU0
UARCH_NAME := CV32E40PXCFU0
MONITOR_NAME := InstructionTrace_XCFU0

XLEN := 32

CDSL_IN := $(INPUTS_DIR)/wca.core_desc
RV_BASE := $(INPUTS_DIR)/rv_base

INDEX_FILE := $(OUTPUTS_DIR)/generated_index.yml

FAKE_HLS_LATS := 1,2,4

FAKE_HLS_STRATEGIES := \
	min_ii_min_lat(topk=1),\
	max_ii_min_lat(topk=1),\
	min_ii_max_lat(topk=1),\
	max_ii_max_lat(topk=1)
