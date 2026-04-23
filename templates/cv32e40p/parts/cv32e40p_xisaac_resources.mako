% for instr_name, instr_timing in instrs_timing.items():
<%
instr_cycles, = instr_timing
variant_prefix = f"{variant_name}_" if variant_name is not None else ""
%>\
Resource {${variant_prefix}${instr_name}(${instr_cycles})}
%endfor
