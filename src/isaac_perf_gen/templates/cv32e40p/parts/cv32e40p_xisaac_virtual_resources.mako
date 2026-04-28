virtual Resource {
% for i, instr_name in enumerate(instr_names):
% if i == (len(instr_names) - 1):
    v${instr_name}
% else:
    v${instr_name},
% endif
% endfor
}
