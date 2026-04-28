% for instr_name, instr_operands in instr_operands_map.items():
<%
i = 0
reg_operands = {operand_name: data for operand_name, data in instr_operands.items() if data[1] == "REG"}
%>\
  XIsaac_${instr_name} : { \
    % for operand_name, data in reg_operands.items():
    <%
    operand_field, _, _ = data
    i += 1
    %>
    ${operand_name} = "$bitfield{${operand_field}}",
    % if i == len(reg_operands):
    ${operand_name}_data = "$reg{$bitfield{${operand_field}}}"
    % else:
    ${operand_name}_data = "$reg{$bitfield{${operand_field}}}",
    % endif
    % endfor
  },
%endfor
