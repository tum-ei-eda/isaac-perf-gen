virtual Resource {
% for i, instr_name in enumerate(instr_names):
% if i == (len(instr_names) - 1):
    v${instr_name}_I,
    v${instr_name}_X,
    v${instr_name}_O
% else:
    v${instr_name}_I,
    v${instr_name}_X,
    v${instr_name}_O,
% endif
% endfor
}
