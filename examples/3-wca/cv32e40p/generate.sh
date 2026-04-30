#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-${(%):-%N}}" )" &> /dev/null && pwd )

CORE=cv32e40p
SET_NAME=XCFU0
ARCH_NAME=RV32IMACFDXCFU0
UARCH_NAME=CV32E40PXCFU0
MONITOR_NAME=InstructionTrace_XCFU0
XLEN=32

INPUTS_DIR=$SCRIPT_DIR/inputs
OUTPUTS_DIR=$SCRIPT_DIR/outputs

CDSL_IN=$INPUTS_DIR/wca.core_desc
RV_BASE=$INPUTS_DIR/rv_base
INDEX_FILE=$OUTPUTS_DIR/generated_index.yml
HLS_DIR=$INPUTS_DIR/hls
TEMP_OUT=$OUTPUTS_DIR/temp
INI_OUT=$OUTPUTS_DIR/ini
CDSL_PERF_OUT=$OUTPUTS_DIR/$UARCH_NAME.corePerfDsl
UARCHS_OUT=$OUTPUTS_DIR/uarchs.csv
MONITOR_OUT=$OUTPUTS_DIR/$MONITOR_NAME.json
EXTRA_ARGS=""

FAKE_HLS_LATS="1,2,4"
FAKE_HLS_STRATEGIES="min_ii_min_lat(topk=1),max_ii_min_lat(topk=1),min_ii_max_lat(topk=1),max_ii_max_lat(topk=1)"

# TODO: check submodule!

isaac-load-cdsl $CDSL_IN -o $INDEX_FILE -I $RV_BASE --xlen $XLEN --set $SET_NAME

isaac-fake-hls $INDEX_FILE -o $HLS_DIR --set $SET_NAME --lats "$FAKE_HLS_LATS" --strategies "$FAKE_HLS_STRATEGIES"



# TODO: fake hls

isaac-perf-gen -c $CORE \
    --index $INDEX_FILE --hls-dir $HLS_DIR \
    --temp-dir $TEMP_OUT -o $CDSL_PERF_OUT \
    --ini-dest $INI_OUT --uarchs-dest $UARCHS_OUT \
    --monitor-dest $MONITOR_OUT $EXTRA_ARGS
    # --monitor-template $MONITOR_IN

isaac-perf-verify $CDSL_PERF_OUT
