COMMON_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

include $(COMMON_DIR)/common.mk

SIM_ENABLED := yes

ifndef ETISS_SRC_DL_URL
SIM_ENABLED := no
endif

ifndef ELF_DL_URL
SIM_ENABLED := no
endif

ifndef INI_DL_URL
SIM_ENABLED := no
endif

ifeq ($(SIM_ENABLED),yes)

ETISS_SRC_DIR := $(TEMP_DIR)/etiss_perf_source

ETISS_EXE := $(ETISS_SRC_DIR)/install/bin/bare_etiss_processor

ELF := $(TEMP_DIR)/$(notdir $(ELF_DL_URL))
INI := $(TEMP_DIR)/$(notdir $(INI_DL_URL))

ETISS_JIT ?= TCC

$(TEMP_DIR):
	mkdir -p $@

$(TEMP_DIR)/etiss_perf_source.tar.gz: | $(TEMP_DIR)
	wget $(ETISS_SRC_DL_URL) -O $@

$(ETISS_SRC_DIR)/build: $(TEMP_DIR)/etiss_perf_source.tar.gz
	mkdir -p $(ETISS_SRC_DIR)
	tar xf $< -C $(ETISS_SRC_DIR) || rm -rf $(ETISS_SRC_DIR)
	cmake \
		-S $(ETISS_SRC_DIR) \
		-B $(ETISS_SRC_DIR)/build \
		-DCMAKE_INSTALL_PREFIX=$(ETISS_SRC_DIR)/install \
		-DENABLE_JIT_LLVM=OFF \
		-DCMAKE_BUILD_TYPE=Release

$(ETISS_EXE): $(ETISS_SRC_DIR)/build
	cmake --build $(ETISS_SRC_DIR)/build -j$$(nproc)
	cmake --install $(ETISS_SRC_DIR)/build

$(ELF): | $(TEMP_DIR)
	wget $(ELF_DL_URL) -O $@

$(INI): | $(TEMP_DIR)
	wget $(INI_DL_URL) -O $@

simulate: $(ETISS_EXE) $(ELF) $(INI)
	$(ETISS_EXE) \
		-i$(INI) \
		--vp.elf_file=$(ELF) \
		--jit.type=$(ETISS_JIT)JIT \
		--arch.cpu=$(ETISS_ARCH)
else

simulate:
	@echo ""
	@echo "Simulation is not configured for this example."
	@echo ""
	@echo "Missing one or more required variables:"
	@echo "  ETISS_SRC_DL_URL"
	@echo "  ELF_DL_URL"
	@echo "  INI_DL_URL"
	@echo ""
	@exit 1

endif

clean::
	rm -rf \
		$(ETISS_SRC_DIR) \
		$(TEMP_DIR)/etiss_source.zip \
		$(ELF) \
		$(INI)

.PHONY: simulate
