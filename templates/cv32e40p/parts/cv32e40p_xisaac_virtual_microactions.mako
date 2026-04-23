% for i, instr_name in enumerate(instr_names):
    % if i == (len(instr_names) - 1):
    vuA_${instr_name}
    % else:
    vuA_${instr_name},
    % endif
% endfor
