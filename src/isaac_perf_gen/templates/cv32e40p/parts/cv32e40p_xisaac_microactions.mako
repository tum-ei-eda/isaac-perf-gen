<%
variant_prefix = f"{variant_name}_" if variant_name is not None else ""
%>\
% for i, instr_name in enumerate(instr_names):
    % if i == (len(instr_names) - 1):
    uA_${variant_prefix}${instr_name}    (${variant_prefix}${instr_name} -> Xd)
    % else:
    uA_${variant_prefix}${instr_name}    (${variant_prefix}${instr_name} -> Xd),
    % endif
% endfor
