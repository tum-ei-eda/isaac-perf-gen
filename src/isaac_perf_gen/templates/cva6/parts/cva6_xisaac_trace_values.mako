<%
known = ["rs1", "rs2", "rd", "pc", "addr", "brTarget", "imm", "rs1_data", "rs2_data"]
missing = set(trace_values) - set(known)
%>\
TraceValue {
% for i, name in enumerate(missing):
% if i == (len(missing) - 1):
  ${name}
% else:
  ${name},
% endif
% endfor
}
