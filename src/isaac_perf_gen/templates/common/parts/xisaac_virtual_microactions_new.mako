% for i, instr_name in enumerate(instr_names):
    % if i == (len(instr_names) - 1):
    vuA_${instr_name}_I,
    vuA_${instr_name}_X,
    vuA_${instr_name}_O
    % else:
    vuA_${instr_name}_I,
    vuA_${instr_name}_X,
    vuA_${instr_name}_O,
    % endif
% endfor
