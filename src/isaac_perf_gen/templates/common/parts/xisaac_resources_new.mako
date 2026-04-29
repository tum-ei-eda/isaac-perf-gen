% for instr_name, instr_timing in instrs_timing.items():
<%
instr_cycles, instr_ii = instr_timing
variant_prefix = f"{variant_name}_" if variant_name is not None else ""

t_i = instr_ii
t_x = 0 if (2 * instr_ii) >= instr_cycles else instr_ii
t_o = instr_cycles - t_i - t_x

%>\
Resource {${variant_prefix}${instr_name}_I(${t_i}), ${variant_prefix}${instr_name}_X(${t_x}), ${variant_prefix}${instr_name}_O(${t_o})}
%endfor
