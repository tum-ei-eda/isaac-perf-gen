<%
i = 0
%>\
% for group_idx, instr_names in sg2instrs.items():
  <%
  instrs = ", ".join(instr_name.lower() for instr_name in instr_names)
  i += 1
  new = False
  %>
  % if new:
  % if i == len(sg2instrs):
  XIsaac_SG${group_idx} (${instrs})\
  % else:
  XIsaac_SG${group_idx} (${instrs}),\
  % endif
  % else:
  % for j, instr_name in enumerate(instr_names):
  <%
  instr_name_lower = instr_name.lower()
  %>
  % if i == len(sg2instrs) and j == (len(instr_names) - 1):
  XIsaac_${instr_name} (${instr_name_lower})\
  % else:
  XIsaac_${instr_name} (${instr_name_lower}),\
  % endif
  % endfor
  % endif
% endfor
