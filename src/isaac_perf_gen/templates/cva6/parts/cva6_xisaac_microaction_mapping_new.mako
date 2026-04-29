<%
i = 0
%>\
% for instr_name, instr_operands in instr_operands_map.items():
<%
i += 1
%>
  XIsaac_${instr_name} : {\
uA_IScan, \
% for operand_name, data in instr_operands.items():
<%
operand_field, operand_type, operand_dir = data
%>\
% if operand_dir == "IN":
% if operand_type == "REG":
% if operand_name == "rs1":
uA_OF_A, \
% elif operand_name == "rs2":
uA_OF_B, \
% else:
<%
raise ValueError(f"Unsupported operand: {operand_name}")
%>
% endif
% endif
% endif
% endfor
uA_Clobber, \
vuA_${instr_name}_I, vuA_${instr_name}_X, vuA_${instr_name}_O\
, uA_Commit_Cb \
% if i == len(instr_operands_map):
}
% else:
},
% endif
%endfor
