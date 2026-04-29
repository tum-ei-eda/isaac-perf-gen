{"trace": {
    "name": "${monitor_name}",
    "core": "${core_name}",
    "setId": "Automatic",
    "separator": ",",
    "traceValues": [
	{"name": "pc"},
	{"name": "code"},
	{"name": "assembly", "type": "string", "size": 50},
	{"name": "imm"},
	{"name": "rs1_data"},
	{"name": "rs2_data"},
	{"name": "rd_data"},
	{"name": "jump_pc"},
	{"name": "csr"},
	{"name": "csr_reg"},
<%include file="/monitor_trace_values.mako"/>
	{"name": "mem_addr"}
    ],

    "instructions": [

	{"name": "_DEF", "mappings": [
	    {"traceValue": "code", "description": "$code"},
	    {"traceValue": "pc", "description": "$pc"},
	    {"traceValue": "assembly", "description": "$asm"}
	]},

	{"name": "JAL", "mappings":[
	    {"traceValue": "code", "description": "$code"},
	    {"traceValue": "pc", "description": "$pc"},
	    {"traceValue": "assembly", "description": "$asm"},
	    {"traceValue": "imm", "description": "$bitfield{imm}"},
	    {"traceValue": "rd_data", "description": "$reg{$bitfield{rd}}", "position": "post"},
	    {"traceValue": "jump_pc", "description": "$pc", "position": "post"}
	]},

	{"name": "JALR", "mappings":[
	    {"traceValue": "code", "description": "$code"},
	    {"traceValue": "pc", "description": "$pc"},
	    {"traceValue": "assembly", "description": "$asm"},
	    {"traceValue": "imm", "description": "$bitfield{imm}"},
	    {"traceValue": "rs1_data", "description": "$reg{$bitfield{rs1}}"},
	    {"traceValue": "rd_data", "description": "$reg{$bitfield{rd}}", "position": "post"},
	    {"traceValue": "jump_pc", "description": "$pc", "position": "post"}
	]}
    ],

    "instructionGroups": [

	{"name": "Reg_Reg_Type",
% if xlen == 64:
	"instructions": [{"name": "ADD"}, {"name": "SUB"}, {"name": "SLL"}, {"name": "SLT"}, {"name": "SLTU"}, {"name": "XOR"}, {"name": "SRL"}, {"name": "SRA"}, {"name": "OR"}, {"name": "AND"}, {"name": "ADDW"}, {"name": "SUBW"}, {"name": "SLLW"}, {"name": "SRLW"}, {"name": "SRAW"}, {"name": "MUL"}, {"name": "MULH"}, {"name": "MULHSU"}, {"name": "MULHU"}, {"name": "DIV"}, {"name": "DIVU"}, {"name": "REM"}, {"name": "REMU"}, {"name": "MULW"}, {"name": "DIVW"}, {"name": "DIVUW"}, {"name": "REMW"}, {"name": "REMUW"}],
% else:
	"instructions": [{"name": "ADD"}, {"name": "SUB"}, {"name": "SLL"}, {"name": "SLT"}, {"name": "SLTU"}, {"name": "XOR"}, {"name": "SRL"}, {"name": "SRA"}, {"name": "OR"}, {"name": "AND"}, {"name": "MUL"}, {"name": "MULH"}, {"name": "MULHSU"}, {"name": "MULHU"}, {"name": "DIV"}, {"name": "DIVU"}, {"name": "REM"}, {"name": "REMU"}],
% endif
	 "mappings": [
	     {"traceValue": "code", "description": "$code"},
	     {"traceValue": "pc", "description": "$pc"},
	     {"traceValue": "assembly", "description": "$asm"},
	     {"traceValue": "rs1_data", "description": "$reg{$bitfield{rs1}}"},
	     {"traceValue": "rs2_data", "description": "$reg{$bitfield{rs2}}"},
	     {"traceValue": "rd_data", "description": "$reg{$bitfield{rd}}", "position": "post"}
	 ]
	},
<%include file="/monitor_entries.mako"/>
	{"name": "Reg_Imm_Type",
% if xlen == 64:
		"instructions": [{"name": "ADDI"}, {"name": "SLTI"}, {"name": "SLTIU"}, {"name": "XORI"}, {"name": "ORI"}, {"name": "ANDI"}, {"name": "SLLI"}, {"name": "SRLI"}, {"name": "SRAI"}, {"name": "SLLIW"}, {"name": "SRLIW"}, {"name": "SRAIW"}],
% else:
		"instructions": [{"name": "ADDI"}, {"name": "SLTI"}, {"name": "SLTIU"}, {"name": "XORI"}, {"name": "ORI"}, {"name": "ANDI"}, {"name": "SLLI"}, {"name": "SRLI"}, {"name": "SRAI"}],
% endif
	 "mappings": [
	     {"traceValue": "code", "description": "$code"},
	     {"traceValue": "pc", "description": "$pc"},
	     {"traceValue": "assembly", "description": "$asm"},
	     {"traceValue": "imm", "description": "$bitfield{imm}"},
	     {"traceValue": "rs1_data", "description": "$reg{$bitfield{rs1}}"},
	     {"traceValue": "rd_data", "description": "$reg{$bitfield{rd}}", "position": "post"}
	 ]
	},

	{"name": "Load_Type",
% if xlen == 64:
	 "instructions": [{"name": "LB"}, {"name": "LH"}, {"name": "LW"}, {"name": "LBU"}, {"name": "LHU"}, {"name": "LWU"}, {"name": "LD"}],
% else:
	 "instructions": [{"name": "LB"}, {"name": "LH"}, {"name": "LW"}, {"name": "LBU"}, {"name": "LHU"}],
% endif
	 "mappings": [
	     {"traceValue": "code", "description": "$code"},
	     {"traceValue": "pc", "description": "$pc"},
	     {"traceValue": "assembly", "description": "$asm"},
	     {"traceValue": "imm", "description": "$bitfield{imm}"},
	     {"traceValue": "rs1_data", "description": "$reg{$bitfield{rs1}}"},
	     {"traceValue": "rd_data", "description": "$reg{$bitfield{rd}}", "position": "post"},
	     {"traceValue": "mem_addr", "description": "$reg{$bitfield{rs1}ULL} + $bitfield{imm}LL"}
	 ]
	},

	{"name": "Store_Type",
% if xlen == 64:
	 "instructions": [{"name": "SB"}, {"name": "SH"}, {"name": "SW"}, {"name": "SD"}],
% else:
	 "instructions": [{"name": "SB"}, {"name": "SH"}, {"name": "SW"}],
% endif
	 "mappings": [
	     {"traceValue": "code", "description": "$code"},
	     {"traceValue": "pc", "description": "$pc"},
	     {"traceValue": "assembly", "description": "$asm"},
	     {"traceValue": "imm", "description": "$bitfield{imm}"},
	     {"traceValue": "rs1_data", "description": "$reg{$bitfield{rs1}}"},
	     {"traceValue": "rs2_data", "description": "$reg{$bitfield{rs2}}"},
	     {"traceValue": "mem_addr", "description": "$reg{$bitfield{rs1}ULL} + $bitfield{imm}LL"}
	 ]
	},

	{"name": "CSR_Type",
	 "instructions": [{"name": "CSRRW"}, {"name": "CSRRS"}, {"name": "CSRRC"}],
	 "mappings": [
	     {"traceValue": "code", "description": "$code"},
	     {"traceValue": "pc", "description": "$pc"},
	     {"traceValue": "assembly", "description": "$asm"},
	     {"traceValue": "csr", "description": "$bitfield{csr}"},
	     {"traceValue": "rs1_data", "description": "$reg{$bitfield{rs1}}"},
	     {"traceValue": "rd_data", "description": "$reg{$bitfield{rd}}", "position": "post"},
	     {"traceValue": "csr_reg", "description": "$csr{$bitfield{csr}}", "position": "post"}
	 ]
	},

	{"name": "CSR_Imm_Type",
	 "instructions": [{"name": "CSRRWI"}, {"name": "CSRRSI"}, {"name": "CSRRCI"}],
	 "mappings": [
	     {"traceValue": "code", "description": "$code"},
	     {"traceValue": "pc", "description": "$pc"},
	     {"traceValue": "assembly", "description": "$asm"},
	     {"traceValue": "imm", "description": "$bitfield{imm}"},
	     {"traceValue": "csr", "description": "$bitfield{csr}"},
	     {"traceValue": "rd_data", "description": "$reg{$bitfield{rd}}", "position": "post"}
	 ]
	},

	{"name": "Branch_Type",
	 "instructions": [{"name": "BEQ"}, {"name": "BNE"}, {"name": "BLT"}, {"name": "BGE"}, {"name": "BLTU"}, {"name": "BGEU"}],
	 "mappings": [
	     {"traceValue": "code", "description": "$code"},
	     {"traceValue": "pc", "description": "$pc"},
	     {"traceValue": "assembly", "description": "$asm"},
	     {"traceValue": "imm", "description": "$bitfield{imm}"},
	     {"traceValue": "rs1_data", "description": "$reg{$bitfield{rs1}}"},
	     {"traceValue": "rs2_data", "description": "$reg{$bitfield{rs2}}"},
	     {"traceValue": "jump_pc", "description": "$pc", "position": "post"}
	 ]
	},

% if xlen == 64:
  {"name": "RegLoad_Type"
% else:
	{"name": "RegLoad_U_Type",
% endif
	 "instructions": [{"name": "LUI"}, {"name": "AUIPC"}],
	 "mappings": [
	     {"traceValue": "code", "description": "$code"},
	     {"traceValue": "pc", "description": "$pc"},
	     {"traceValue": "assembly", "description": "$asm"},
	     {"traceValue": "imm", "description": "$bitfield{imm}"},
	     {"traceValue": "rd_data", "description": "$reg{$bitfield{rd}}", "position": "post"}
	 ]
	}
    ]
}}
