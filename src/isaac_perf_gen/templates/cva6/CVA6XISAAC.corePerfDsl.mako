/*
 * Copyright 2025 Chair of EDA, Technical University of Munich
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/*********************************** Microaction Section ***********************************/
Connector {Pc_mp, Pc_pt, Pc_p, Pc_p_j, Pc_p_jr, Pc_c}
Connector {Ic_out, Ic_in}
Connector {Xa, Xb, Xd}
Connector {Cb_out, Cb_in}

Resource {PCGen, ICacheCtrl, IScan, IQInsert, Decoder, ALU, MUL_I, MUL_O}
Resource {ICache(iCacheModel)}
Resource {Issue(0)}
Resource {DIV(divider), DIVU(divider_u)}
Resource {LCtrl, DCache(dCacheModel), LUnit}
Resource {SCtrl, SUnit}
Resource {Commit}

// = XISAAC Resources =
<%include file="/cva6_xisaac_virtual_resources.part"/>
% for variant_name in variants:
% if variant_name is None:
<%include file="/cva6_xisaac_resources.part"/>
% else:
// Variant: ${variant_name}
<%include file="/${variant_name}/cva6_xisaac_resources.part"/>
% endif
% endfor
// --------------------

Microaction {
    uA_PCGen      (PCGen),
    uA_PcCorrect  (Pc_mp),
    uA_CacheBlock (Ic_out),

    uA_ICacheCtrl (ICacheCtrl),
    uA_PcPredict  (Pc_pt),
    uA_ICache     (ICache -> Ic_in),
    uA_IScan      (IScan),
    uA_IScan_br   (IScan -> Pc_p),
    uA_IScan_j    (IScan -> Pc_p_j),
    uA_IScan_jr   (IScan -> Pc_p_jr),

    uA_IQ (IQInsert),

    uA_Decode (Decoder),

    uA_Issue   (Issue),
    uA_Clobber (Cb_out),
    uA_OF_A    (Xa),
    uA_OF_B    (Xb),

    uA_ALU_def (ALU),
    uA_ALU_reg (ALU -> Xd),
    uA_ALU_br  (ALU -> Pc_c),
    uA_ALU_jr  (ALU -> {Xd, Pc_c}),
    uA_MUL_I   (MUL_I),
    uA_MUL_O   (MUL_O -> Xd),
    uA_DIV     (DIV),
    uA_DIVU    (DIVU),
    uA_LCtrl   (LCtrl),
    uA_DCache  (DCache),
    uA_LUnit   (LUnit -> Xd),
    uA_SCtrl   (SCtrl),
    uA_SUnit   (SUnit),

    uA_Commit (Commit),
    uA_Commit_Cb (Commit -> Cb_in)
}

// = XISAAC Microactions =
virtual Microaction {
<%include file="/cva6_xisaac_virtual_microactions.part"/>
}
% for variant_name in variants:
% if variant_name is None:
% else:
// Variant: ${variant_name}
% endif
Microaction {
% if variant_name is None:
<%include file="/cva6_xisaac_microactions.part"/>
% else:
<%include file="/${variant_name}/cva6_xisaac_microactions.part"/>
% endif
}
% endfor
// -----------------------

/************************************ Stages & Pipeline ************************************/

% if new:
% if variant_name is None:
<%include file="/cva6_xisaac_stages.part"/>
<%include file="/cva6_xisaac_pipelines.part"/>
% else:
<%include file="/${variant_name}/cva6_xisaac_stages.part"/>
<%include file="/${variant_name}/cva6_xisaac_pipelines.part"/>
% endif
% endif

// IF Substages
Stage {
    IF_substage_0 (uA_ICacheCtrl, uA_PcPredict),
    IF_substage_1 (uA_ICache),
    IF_substage_2 (uA_IScan, uA_IScan_br, uA_IScan_j, uA_IScan_jr)
}

// IF Subpipeline
Pipeline IF_subpipe (IF_substage_0 -> IF_substage_1 -> IF_substage_2)

// EX Substages
Stage {
    EX_substage_alu    (uA_ALU_def, uA_ALU_reg, uA_ALU_br, uA_ALU_jr),
    EX_substage_div    (uA_DIV, uA_DIVU),
    EX_substage_mul_i  (uA_MUL_I),
    EX_substage_mul_o  (uA_MUL_O),
    EX_substage_lCtrl  (uA_LCtrl),
    EX_substage_dCache (uA_DCache),
    EX_substage_lUnit  (uA_LUnit),
    EX_substage_sCtrl  (uA_SCtrl),
    EX_substage_sUnit  (uA_SUnit)
}

// EX Subpipeline
Pipeline {
    EX_subpipe_alu   (EX_substage_alu),
    EX_subpipe_mul   [blocks: EX_subpipe_alu] (EX_substage_mul_i -> EX_substage_mul_o),
    EX_subpipe_div   [blocks: {EX_subpipe_alu, EX_subpipe_mul}] (EX_substage_div),
    EX_subpipe_load  (EX_substage_lCtrl -> EX_substage_dCache -> EX_substage_lUnit),
    EX_subpipe_store (EX_substage_sCtrl -> EX_substage_sUnit)
}

// Main stages
Stage {
    PC_stage  (uA_PCGen, uA_PcCorrect, uA_CacheBlock),
    IF_stage  [capacity:3] (IF_subpipe),
    IQ_stage  [capacity: 7, output-buffer] (uA_IQ),
    ID_stage  (uA_Decode),
    IS_stage  (uA_Issue, uA_Clobber, uA_OF_A, uA_OF_B),
    EX_stage  [capacity: 8, output-buffer] (
        EX_subpipe_alu,
        // = XISAAC EX stage =
<%include file="/cva6_xisaac_ex_stages.part"/>
        // -------------------
        EX_subpipe_mul,
        EX_subpipe_div,
        EX_subpipe_load,
        EX_subpipe_store
    ),
    COM_stage [capacity:2] (uA_Commit, uA_Commit_Cb)
}

Pipeline ${uarch_name}_pipeline (PC_stage -> IF_stage -> IQ_stage -> ID_stage -> IS_stage -> EX_stage -> COM_stage)

/************************************* External Models *************************************/
TraceValue {rs1, rs2, rd, pc, addr, brTarget, imm, rs1_data, rs2_data}
// = XISAAC Trace Values =
<%include file="/cva6_xisaac_trace_values.part"/>
// -------------------

Model iCacheModel(
    link : "models/cva6/ICacheModel.h"
    trace : {pc}
    connectorIn : {Ic_in}
    connectorOut : {Ic_out}
)

ConnectorModel dynBranchPredModel (
    link : "models/cva6/BranchPredictionModel.h"
    trace : {pc, brTarget, rs1, rd, imm}
    connectorIn : {Pc_p, Pc_p_j, Pc_p_jr, Pc_c}
    connectorOut : {Pc_mp, Pc_pt}
)

ConnectorModel regModel (
    link : "models/common/StandardRegisterModel.h"
    trace : {rs1, rs2, rd}
    connectorIn : Xd
    connectorOut : {Xa, Xb}
)

ConnectorModel clobberModel (
    link : "models/cva6/ClobberModel.h"
    trace : {rd}
    connectorIn : Cb_in
    connectorOut : Cb_out
)

ResourceModel divider (
  link: "models/cva6/DividerModel.h"
  trace: {rs1_data, rs2_data}
)

ResourceModel divider_u (
  link: "models/cva6/DividerUnsignedModel.h"
  trace: {rs1_data, rs2_data}
)

ResourceModel dCacheModel (
    link: "models/cva6/DCacheModel.h"
    trace : addr
)

/**************************************** Variants *****************************************/
% for variant_name in variants:
% if variant_name is None:
<%include file="/cva6_xisaac_model.part"/>
% else:
// Variant: ${variant_name}
<%include file="/${variant_name}/cva6_xisaac_model.part"/>
% endif
% endfor
// --------------------

/*********************************** Instruction Section ***********************************/

InstrGroup {
    Default ([?]),
    Arith_0 (auipc, lui, csrrwi, csrrsi, csrrci),
    Arith_Rs1 (addi, xori, ori, andi, slti, sltiu, slli, srli, srai, csrrw, csrrs, csrrc, addiw, slliw, sraiw, srliw),
    Arith_Rs1_Rs2 (add, sub, xor, or, and, slt, sltu, sll, srl, sra, subw, addw),
    Branch (beq, bne, blt, bge, bltu, bgeu),
    Jump (jal),
    JumpR (jalr),
    Mul (mul, mulh, mulhu, mulhsu, mulw),
    Div (div, rem, divw, remw),
    DivU (divu, remu, divuw, remuw),
    Load (lw, lh, lhu, lb, lbu, ld, lwu),
    Store (sb, sh, sw, sd)
}

// = XISAAC Instr Groups =
InstrGroup {
<%include file="/cva6_xisaac_instr_groups.part"/>
}
// -----------------------

MicroactionMapping {
    [ALL] : {uA_PCGen, uA_PcCorrect, uA_CacheBlock, uA_ICacheCtrl, uA_PcPredict, uA_ICache, uA_IQ, uA_Decode, uA_Issue},
    Default : {uA_IScan, uA_ALU_def, uA_Commit},
    Arith_0 : {uA_IScan, uA_ALU_reg, uA_Commit_Cb},
    Arith_Rs1 : {uA_IScan, uA_OF_A, uA_Clobber, uA_ALU_reg, uA_Commit_Cb},
    Arith_Rs1_Rs2 : {uA_IScan, uA_OF_A, uA_OF_B, uA_Clobber, uA_ALU_reg, uA_Commit_Cb},
    Branch : {uA_IScan_br, uA_OF_A, uA_OF_B, uA_ALU_br, uA_Commit},
    Jump : {uA_IScan_j, uA_Clobber, uA_ALU_reg, uA_Commit_Cb},
    JumpR : {uA_IScan_jr, uA_OF_A, uA_Clobber, uA_ALU_jr, uA_Commit_Cb},
    Mul : {uA_IScan, uA_OF_A, uA_OF_B, uA_Clobber, uA_MUL_I, uA_MUL_O, uA_Commit_Cb},
    Div : {uA_IScan, uA_OF_A, uA_OF_B, uA_Clobber, uA_DIV, uA_Commit_Cb},
    DivU : {uA_IScan, uA_OF_A, uA_OF_B, uA_Clobber, uA_DIVU, uA_Commit_Cb},
    Load : {uA_IScan, uA_OF_A, uA_Clobber, uA_LCtrl, uA_DCache, uA_LUnit, uA_Commit_Cb},
    Store : {uA_IScan, uA_OF_A, uA_OF_B, uA_SCtrl, uA_SUnit, uA_Commit}
}

// = XISAAC Microaction Mapping =
MicroactionMapping {
<%include file="/cva6_xisaac_microaction_mapping.part"/>
}
// ------------------------------

/*********************************** Monitor Description ***********************************/

TraceValueMapping {

    [ALL] : {
        pc = "$resolved{$pc}"
    },
    Arith_0 : {
        rd = "$bitfield{rd}"
    },
    Arith_Rs1 : {
        rs1 = "$bitfield{rs1}",
        rd = "$bitfield{rd}"
    },
    Arith_Rs1_Rs2 : {
        rs1 = "$bitfield{rs1}",
        rs2 = "$bitfield{rs2}",
        rd = "$bitfield{rd}"
    },
    // = XISAAC Trace Value Mapping =
<%include file="/cva6_xisaac_trace_value_mapping.part"/>
    // ------------------------------
    Branch : {
        rs1 = "$bitfield{rs1}",
        rs2 = "$bitfield{rs2}",
        brTarget = "$resolved{$pc + (((int16_t)($bitfield{imm} << 3)) >> 3)}",
        imm = "$resolved{(((int16_t)($bitfield{imm} << 3)) >> 3)}"
    },
    Jump : {
        rd = "$bitfield{rd}",
        brTarget = "$resolved{$pc + (((int32_t)($bitfield{imm} << 11)) >> 11)}",
        imm = "$resolved{(((int32_t)($bitfield{imm} << 11)) >> 11)}"
    },
    JumpR : {
        rs1 = "$bitfield{rs1}",
        rd = "$bitfield{rd}",
        brTarget = "($reg{$bitfield{rs1}} + $resolved{(((int16_t)($bitfield{imm} << 4)) >> 4)}) & -2U",
        imm = "$resolved{(((int16_t)($bitfield{imm} << 4)) >> 4)}"
    },
    Mul : {
        rs1 = "$bitfield{rs1}",
        rs2 = "$bitfield{rs2}",
        rd  = "$bitfield{rd}"
    },
    Div : {
        rs1 = "$bitfield{rs1}",
        rs2 = "$bitfield{rs2}",
        rd  = "$bitfield{rd}",
        rs1_data = "$reg{$bitfield{rs1}}",
        rs2_data = "$reg{$bitfield{rs2}}"
    },
    DivU : {
        rs1 = "$bitfield{rs1}",
        rs2 = "$bitfield{rs2}",
        rd  = "$bitfield{rd}",
        rs1_data = "$reg{$bitfield{rs1}}",
        rs2_data = "$reg{$bitfield{rs2}}"
    },
    Load : {
        rs1 = "$bitfield{rs1}",
        rd  = "$bitfield{rd}",
        addr = "($reg{$bitfield{rs1}} + $bitfield{imm})"
    },
    Store: {
        rs1 = "$bitfield{rs1}",
        rs2 = "$bitfield{rs2}"
    }
}
