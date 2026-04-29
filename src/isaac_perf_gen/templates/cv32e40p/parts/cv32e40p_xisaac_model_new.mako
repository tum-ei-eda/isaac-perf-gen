<%
variant_prefix = f"{variant_name}_" if variant_name is not None else ""
variant_suffix = f"{variant_name}" if variant_name is not None else ""
%>
CorePerfModel ${uarch_name}${variant_suffix} (
  core : "${core_name}"
  use Pipeline : ${uarch_name}_pipeline
  use ConnectorModel : {regModel, staBranchPredModel}
  assign Resource : {
% for i, instr_name in enumerate(instr_names):
    % if i == (len(instr_names) - 1):
    v${instr_name}_I = ${variant_prefix}${instr_name}_I,
    v${instr_name}_X = ${variant_prefix}${instr_name}_X,
    v${instr_name}_O = ${variant_prefix}${instr_name}_O
    % else:
    v${instr_name}_I = ${variant_prefix}${instr_name}_I,
    v${instr_name}_X = ${variant_prefix}${instr_name}_X,
    v${instr_name}_O = ${variant_prefix}${instr_name}_O,
    % endif
% endfor
  }
  assign Microaction : {
% for i, instr_name in enumerate(instr_names):
    % if i == (len(instr_names) - 1):
    vuA_${instr_name}_I = uA_${variant_prefix}${instr_name}_I,
    vuA_${instr_name}_X = uA_${variant_prefix}${instr_name}_X,
    vuA_${instr_name}_O = uA_${variant_prefix}${instr_name}_O
    % else:
    vuA_${instr_name}_I = uA_${variant_prefix}${instr_name}_I,
    vuA_${instr_name}_X = uA_${variant_prefix}${instr_name}_X,
    vuA_${instr_name}_O = uA_${variant_prefix}${instr_name}_O,
    % endif
% endfor
  }
)
