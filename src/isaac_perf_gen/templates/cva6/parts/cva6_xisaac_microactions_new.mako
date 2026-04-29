<%
variant_prefix = f"{variant_name}_" if variant_name is not None else ""
%>\
% for i, instr_name in enumerate(instr_names):
    % if i == (len(instr_names) - 1):
    uA_${variant_prefix}${instr_name}_I    (${variant_prefix}${instr_name}_I),
    uA_${variant_prefix}${instr_name}_X    (${variant_prefix}${instr_name}_X),
    uA_${variant_prefix}${instr_name}_O    (${variant_prefix}${instr_name}_O -> Xd)
    % else:
    uA_${variant_prefix}${instr_name}_I    (${variant_prefix}${instr_name}_I),
    uA_${variant_prefix}${instr_name}_X    (${variant_prefix}${instr_name}_X),
    uA_${variant_prefix}${instr_name}_O    (${variant_prefix}${instr_name}_O -> Xd),
    % endif
% endfor
