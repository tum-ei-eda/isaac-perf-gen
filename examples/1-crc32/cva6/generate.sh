#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-${(%):-%N}}" )" &> /dev/null && pwd )

CORE=cva6
ARCH_NAME=XIsaac
UARCH_NAME=CVA6XISAAC
MONITOR_NAME=InstructionTrace_XISAAC

INPUTS_DIR=$SCRIPT_DIR/inputs
OUTPUTS_DIR=$SCRIPT_DIR/outputs

INDEX_FILE=$INPUTS_DIR/final_index.yml
# TEMPLATE_FILE=...
HLS_DIR=$INPUTS_DIR/hls
TEMP_OUT=$OUTPUTS_DIR/temp
INI_OUT=$OUTPUTS_DIR/ini
CDSL_PERF_OUT=$OUTPUTS_DIR/$UARCH_NAME.corePerfDsl
UARCHS_OUT=$OUTPUTS_DIR/uarchs.csv
# MONITOR_IN=...
MONITOR_OUT=$OUTPUTS_DIR/$MONITOR_NAME.json
EXTRA_ARGS=""

isaac-perf-gen -c $CORE \
    --index $INDEX_FILE --hls-dir $HLS_DIR \
    --temp-dir $TEMP_OUT -o $CDSL_PERF_OUT \
    --ini-dest $INI_OUT --uarchs-dest $UARCHS_OUT \
    --monitor-dest $MONITOR_OUT $EXTRA_ARGS
    # --monitor-template $MONITOR_IN

isaac-perf-verify $CDSL_PERF_OUT
