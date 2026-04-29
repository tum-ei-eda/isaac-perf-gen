<%
known_names = {"pc", "code", "assembly", "imm", "rs1_data", "rs2_data", "rd_data", "jump_pc", "csr", "csr_reg", "mem_addr"}
names = set()
for instr_name, instr_operands in instr_operands_map.items():
    for operand_name, data in instr_operands.items():
        operand_field, operand_type, _ = data
        names.add(operand_name)
        if operand_type == "REG":
            names.add(f"{operand_name}_data")
unknown_names = sorted(list(names - known_names))
%>\
% for i, name in enumerate(unknown_names):
% if False and i == (len(unknown_names) - 1):
            {"name": "${name}"}
% else:
            {"name": "${name}"},
% endif
% endfor
