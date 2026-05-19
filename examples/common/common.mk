SHELL := /usr/bin/env bash

EXAMPLE_DIR ?= $(CURDIR)

INPUTS_DIR := $(EXAMPLE_DIR)/inputs
OUTPUTS_DIR := $(EXAMPLE_DIR)/outputs
TEMP_DIR := $(EXAMPLE_DIR)/temp

mkdir_p = mkdir -p $(@D)

clean::
	rm -rf \
		$(TEMP_DIR) \
		$(OUTPUTS_DIR)/temp \
		$(OUTPUTS_DIR)/ini

cleanall:: | clean

.PHONY: clean
