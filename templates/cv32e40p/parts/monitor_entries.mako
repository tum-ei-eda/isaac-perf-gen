% for instr_name, instr_operands in instr_operands_map.items():
<%
i = 0
%>\
   {"name": "${instr_name}_Type",
    "instructions": [{"name": "${instr_name}"}],
    "mappings": [
        {"traceValue": "code", "description": "$code"},
        {"traceValue": "pc", "description": "$pc"},
        {"traceValue": "assembly", "description": "$asm"},
    % for operand_name, data in instr_operands.items():
    <%
    operand_field, operand_type, _ = data
    i += 1
    %>\
    % if operand_type == "REG":
    % if i == len(instr_operands):
        {"traceValue": "${operand_name}_data", "description": "$reg{$bitfield{${operand_name}}}"}
    % else:
        {"traceValue": "${operand_name}_data", "description": "$reg{$bitfield{${operand_name}}}"},
    % endif
    % elif operand_type == "IMM":
    % if i == len(instr_operands):
        {"traceValue": "${operand_name}", "description": "$bitfield{${operand_name}}"}
    % else:
        {"traceValue": "${operand_name}", "description": "$bitfield{${operand_name}}"},
    % endif
    % endif
    % endfor
    ]
  },
%endfor
