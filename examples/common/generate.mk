COMMON_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

include $(COMMON_DIR)/common.mk

TEMP_OUT ?= $(OUTPUTS_DIR)/temp
INI_OUT ?= $(OUTPUTS_DIR)/ini

CDSL_PERF_OUT ?= $(OUTPUTS_DIR)/$(UARCH_NAME).corePerfDsl
UARCHS_OUT ?= $(OUTPUTS_DIR)/uarchs.csv
MONITOR_OUT ?= $(OUTPUTS_DIR)/$(MONITOR_NAME).json

VARIANTS_YAML_OUT ?= $(OUTPUTS_DIR)/variants.yml
INDEX_FILE ?= $(INPUTS_DIR)/final_index.yml
ISAX_NAME ?= XIsaac

EXTRA_ARGS ?=

HLS_DIR ?= $(INPUTS_DIR)/hls
HLS_DIRS ?= $(HLS_DIR)
CDSL_IN ?=
RV_BASE ?=

EXISTING_HLS_DIRS := $(wildcard $(HLS_DIRS))
NUM_HLS_DIRS := $(words $(EXISTING_HLS_DIRS))
# HAS_HLS := $(wildcard $(HLS_DIR))

HAS_VARIANTS := $(wildcard $(VARIANTS_YAML_OUT))
HAS_CDSL := $(wildcard $(CDSL_IN))
HAS_INDEX := $(wildcard $(INDEX_FILE))

ifeq ($(HAS_INDEX),)

# No index.yml exists

ifeq ($(HAS_CDSL),)
$(error No variants.yml, index YAML, or CoreDSL input found)
endif

$(INDEX_FILE): $(CDSL_IN)
	@echo "Generating index from CoreDSL..."
	@$(mkdir_p)

	isaac-load-cdsl \
		$(CDSL_IN) \
		-o $@ \
		-I $(RV_BASE) \
		--xlen $(XLEN) \
		--set $(SET_NAME)
endif

ifeq ($(HAS_VARIANTS),)

# No variants.yml exists


# ifeq ($(HAS_HLS),)
ifeq ($(NUM_HLS_DIRS),0)

# No HLS dir exists

# CoreDSL -> fake HLS


$(VARIANTS_YAML_OUT): $(INDEX_FILE)
	@echo "Generating fake HLS variants..."
	@$(mkdir_p)

	isaac-fake-hls2 \
		$(INDEX_FILE) \
		-o $@ \
		--set $(SET_NAME) \
		--lats "$(FAKE_HLS_LATS)" \
		--strategies "$(FAKE_HLS_STRATEGIES)"

else ifeq ($(NUM_HLS_DIRS),1)
# single HLS dir -> variants

$(VARIANTS_YAML_OUT):
	@echo "Loading HLS variants..."
	@$(mkdir_p)

	isaac-load-hls \
		$(HLS_DIRS) \
		-o $@ \
    --isax-name $(ISAX_NAME)

else

$(VARIANTS_YAML_OUT):
	@echo "Loading HLS variants (multi)..."
	@$(mkdir_p)

	isaac-load-hls-multi \
		$(HLS_DIRS) \
		-o $@ \
    --isax-name $(ISAX_NAME)

endif
endif

$(CDSL_PERF_OUT): $(VARIANTS_YAML_OUT) $(INDEX_FILE)
	@echo "Generating performance model..."
	@$(mkdir_p)

	isaac-perf-gen \
		-c $(CORE) \
		--index $(INDEX_FILE) \
		--variants-yaml $(VARIANTS_YAML_OUT) \
		--temp-dir $(TEMP_OUT) \
		-o $@ \
		--ini-dest $(INI_OUT) \
		--uarchs-dest $(UARCHS_OUT) \
		--monitor-dest $(MONITOR_OUT) \
		$(EXTRA_ARGS)

generate: $(CDSL_PERF_OUT)

verify: $(CDSL_PERF_OUT)
	isaac-perf-verify $(CDSL_PERF_OUT)

load_hls: $(VARIANTS_YAML_OUT)

load_cdsl: $(INDEX_FILE)

# TODO: add clean_temp vs. cleanall

clean::
	rm -rf \
		$(TEMP_OUT) \

cleanall::
	rm -rf \
    $(UARCHS_OUT) \
    $(CDSL_PERF_OUT) \
    $(MONITOR_OUT) \
    $(INI_OUT)

.PHONY: \
	generate \
	verify \
	load_hls \
	load_cdsl
