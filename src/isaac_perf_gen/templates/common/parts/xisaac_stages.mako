Stage {
% for i, instr_name in enumerate(instr_names):
    % if i == (len(instr_names) - 1):
    EX_substage_${instr_name}_I  (vuA_${instr_name}_I),
    EX_substage_${instr_name}_X  (vuA_${instr_name}_X),
    EX_substage_${instr_name}_O  (vuA_${instr_name}_O)
    % else:
    EX_substage_${instr_name}_I  (vuA_${instr_name}_I),
    EX_substage_${instr_name}_X  (vuA_${instr_name}_X),
    EX_substage_${instr_name}_O  (vuA_${instr_name}_O),
    % endif
% endfor
}
