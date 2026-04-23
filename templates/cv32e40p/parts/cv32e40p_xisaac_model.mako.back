<%
variant_prefix = f"{variant_name}_" if variant_name is not None else ""
variant_suffix = f"{variant_name}" if variant_name is not None else ""
%>
CorePerfModel CV32E40PXISAAC${variant_suffix} (
  core : "XIsaacCore"
  use Pipeline : CV32E40PXISAAC_pipeline
  use ConnectorModel : {regModel, staBranchPredModel}
  assign Resource : {
% for i, instr_name in enumerate(instr_names):
    % if i == (len(instr_names) - 1):
    v${instr_name} = ${variant_prefix}${instr_name}
    % else:
    v${instr_name} = ${variant_prefix}${instr_name},
    % endif
% endfor
  }
  assign Microaction : {
% for i, instr_name in enumerate(instr_names):
    % if i == (len(instr_names) - 1):
    vuA_${instr_name} = uA_${variant_prefix}${instr_name}
    % else:
    vuA_${instr_name} = uA_${variant_prefix}${instr_name},
    % endif
% endfor
  }
)

