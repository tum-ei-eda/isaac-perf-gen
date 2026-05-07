#
# Copyright (c) 2026 TUM Department of Electrical and Computer Engineering.
#
# This file is part of ISAAC Perf Gen.
# See https://github.com/tum-ei-eda/isaac-perf-gen.git for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""ISAAC Perf Gen Script."""

import ast
import logging
import itertools
import tempfile
import argparse
from pathlib import Path
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, asdict, fields, replace

from typing import Optional, List, Union
from importlib_resources import files

# from importlib import resources  # Python 3.9+

import yaml
import pandas as pd
from mako.template import Template
from mako.lookup import TemplateLookup

from isaac_perf_common.config import VariantsConfig

pd.set_option("display.max_columns", None)


def filter_variants(variants_config: VariantsConfig, variants_filter: Union[str, List[int]] = None):
    assert variants_filter is not None
    if isinstance(variants_filter, str):
        variants_filter = list(map(int, variants_filter.split(",")))
    assert isinstance(variants_filter, list)  # TODO: allow sets?
    # assert all(isinstance(x, int) for x in variants_filter)
    filtered_variants = []
    for variant_config in variants_config.variants:
        if variant_config.idx in variants_filter or variant_config.name in variants_filter:
            filtered_variants.append(variant_config)
    ret = VariantsConfig(filtered_variants)
    return ret


def get_permutations(d):
    # return [
    #     {k: v for k, v in zip(sorted(d.keys()), list_prod_value)}
    #     for list_prod_value in itertools.product(*(d[k] for k in sorted(d.keys())))
    # ]
    return [
        tuple((k, v) for k, v in zip(sorted(d.keys()), list_prod_value))
        for list_prod_value in itertools.product(*(d[k] for k in sorted(d.keys())))
    ]


def get_templates_base(core: Optional[str] = None, part: bool = False):
    templates_path = files("isaac_perf_gen.templates")  # .joinpath("message.eml").read_text()
    # print("templates_path", templates_path)
    if core is not None:
        templates_path = templates_path.joinpath(core)
        # print("templates_path", templates_path)
    else:
        templates_path = templates_path.joinpath("/")
    if part:
        templates_path = templates_path.joinpath("parts")

    # print("templates_path", templates_path, type(templates_path))
    assert Path(templates_path).is_dir()
    return templates_path


def lookup_template(inp: str, core: Optional[str] = None, suffix: Optional[str] = None, part: bool = False):
    # print("lookup_template", inp, core, suffix, part)
    assert inp is not None
    inp = str(inp)
    assert core is not None

    templates_path = get_templates_base(core=core, part=part)
    # print("templates_path", templates_path)
    # if part:
    #     template_path = templates_path.joinpath("parts")
    #     print("templates_path2", templates_path)
    if Path(inp).is_file():
        return Path(inp).resolve()
    assert isinstance(inp, str)
    if not inp.endswith(".mako"):
        if suffix is not None:
            assert suffix.startswith(".")
            if not inp.endswith(suffix):
                inp += suffix
        inp += ".mako"
    # print("inp", inp)
    template_path = templates_path.joinpath(inp)
    template_path = Path(template_path)
    # print("template_path", template_path)
    if not template_path.is_file():
        # if core is not None and core != "common":
        if core is not None and core != "common":
            return lookup_template(inp, core="common", suffix=suffix, part=part)
        assert False, f"Not a file: {template_path}"
    return str(Path(template_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--template", default=None, help="Base MAKO Template")
    parser.add_argument("-o", "--output", default=None, help="Output .core_perf_dsl file path")
    parser.add_argument("--monitor-template", default=None, help="Mako template for monitor description")
    parser.add_argument(
        "--monitor-dest",
        default=None,
        help="Directory containing generated Monitor descriptions",
    )
    parser.add_argument(
        "--ini-dest",
        default=None,
        help="Directory containing generated INI files (and mako templates)",
    )
    parser.add_argument("--uarchs-dest", default=None, help="Output CSV file for uarch names")
    parser.add_argument("-c", "--core", required=True, choices=["cv32e40p", "cva6"], help="Base core")
    parser.add_argument("-u", "--uarch", default=None, help="Perf model name")
    parser.add_argument("-a", "--etiss-arch", default="XIsaacCore", help="Base ETISS arch name")
    parser.add_argument("--temp-dir", default=None, help="Optional path to persistent temp dir")
    parser.add_argument("--hls-dir", default=None, help="Path to hls output dir")
    parser.add_argument("--variants-yaml", default=None, help="Path to variants YAML file")
    # parser.add_argument("--hls-schedules", default=None, help="Path to hls_schedules.csv")
    # parser.add_argument("--hls-yaml", default=None, help="Path to ISAX_XIsaac.yaml")
    # parser.add_argument("--selected-solutions", default=None, help="Path to selected_solutions.yaml")
    parser.add_argument("--variants-filter", default=None, help="Filter variants")
    parser.add_argument("--index-yaml", default=None, help="Path to XISAAC index.yml")
    parser.add_argument("--parts-only", action="store_true", help="Only generate parts")
    parser.add_argument("--render-only", action="store_true", help="Only render final output")
    args = parser.parse_args()
    core = args.core
    core_name = args.etiss_arch

    uarch_name = args.uarch
    if uarch_name is None:
        core is not None
        core_upper = core.upper()
        default_uarch_name = f"{core_upper}XISAAC"
        lookup_uarch_name = {}
        uarch_name = lookup_uarch_name.get("CV32E40PXISAAC", default_uarch_name)

    @contextmanager
    def temp_dir_content(enter_result=None):
        if args.temp_dir is not None:
            yield Path(args.temp_dir)
        else:
            with tempfile.TemporaryDirectory() as tmpdirname:
                yield Path(tmpdirname)

    templates_path = get_templates_base(core=core)
    common_path = get_templates_base(core="common")
    template_dirs = [".", "templates/", templates_path, f"{templates_path}/parts", common_path, f"{common_path}/parts"]
    lookup_dirs = defaultdict(list)
    lookup_dirs2 = []
    xlen = None
    variant_names = []
    with temp_dir_content() as temp_dir:
        # print("temp_dir", temp_dir)
        temp_dir.mkdir(exist_ok=True)
        content = None

        if args.render_only:
            assert args.temp_dir is not None, "Needs --temp-dir for input parts"
        else:
            assert args.index_yaml is not None
            with open(args.index_yaml) as f:
                index_data = yaml.safe_load(f)
            # print("index_data", index_data)
            candidates_data = index_data["candidates"]
            global_data = index_data["global"]
            global_properties = global_data["properties"]
            if isinstance(global_properties, list):
                assert len(global_properties) > 0
                global_properties = global_properties[0]
            xlen = global_properties["xlen"]
            instr_operands_map = {}
            for candidate_data in candidates_data:
                candidate_properties = candidate_data["properties"]
                instr_name = candidate_properties["InstrName"]
                operand_names = candidate_properties["OperandNames"]
                operand_types = candidate_properties["OperandTypes"]
                operand_dirs = candidate_properties["OperandDirs"]
                operands_map = {}
                for i, operand_name in enumerate(operand_names):
                    operand_type = operand_types[i]
                    operand_dir = operand_dirs[i]
                    assert operand_dir != "INOUT", "INOUT regs not supported!"
                    if operand_type == "REG":
                        assert operand_name in [
                            "rd",
                            "rs1",
                            "rs2",
                        ], f"Unsupported operand name: {operand_name}"
                    operand_field = operand_name
                    operands_map[operand_name] = (
                        operand_field,
                        operand_type,
                        operand_dir,
                    )
                instr_operands_map[instr_name] = operands_map
                instr_names = list(instr_operands_map.keys())
                trace_values = set()
                for instr_name, instr_operands in instr_operands_map.items():
                    reg_operands = {
                        operand_name: data for operand_name, data in instr_operands.items() if data[1] == "REG"
                    }
                    imm_operands = {
                        operand_name: data for operand_name, data in instr_operands.items() if data[1] == "IMM"
                    }
                    reg_names = list(reg_operands.keys()) + list(imm_operands.keys())
                    for reg_name in reg_names:
                        trace_values_ = {reg_name, f"{reg_name}_data"}
                        trace_values.update(trace_values_)
                print("trace_values", trace_values)
                # input("!")
            if args.hls_dir:
                # print("--hls-dir arg is deprecated, Please run isaac-load-hls first and pass --perf-yaml")
                # variants_config = load_hls_artifacts(args.hls_dir)
                raise RuntimeError("--hls-dir arg is deprecated, Please run isaac-load-hls first and pass --perf-yaml")
            else:
                assert args.variants_yaml is not None
                variants_config = VariantsConfig.from_yaml_file(args.variants_yaml)
            print("variants_config", variants_config.to_yaml())
            if args.variants_filter is not None:
                variants_config = filter_variants(variants_config, args.variants_filter)
            for variant_idx, variant_config in enumerate(variants_config.variants):
                variant_name = variant_config.name
                assert variant_name not in variant_names
                variant_names.append(variant_name)
                instrs_timing = {}
                # sgs = variant_config.sharing_groups
                sg2instrs = defaultdict(set)
                sg2iis = defaultdict(set)

                for instr_config in variant_config.instrs:
                    instr_name = instr_config.name
                    instr_cycles = instr_config.cycles
                    sg = instr_config.sg
                    sg2instrs[sg].add(instr_name)
                    ii = instr_config.ii
                    sg2iis[sg].add(ii)
                    instr_timing = (instr_cycles, ii)
                    instrs_timing[instr_name] = instr_timing

                sg2ii = {}
                for sg, iis in sg2iis.items():
                    assert len(iis) == 1, f"SG {sg} has multiple IIs: {iis}"
                    sg2ii[sg] = list(iis)[0]
                dest_dir = temp_dir
                lookup_dirs[variant_name].append(dest_dir)
                lookup_dirs2.append(temp_dir)
                cores_parts_map = {
                    "cv32e40p": {
                        "cv32e40p_xisaac_microactions.part": "xisaac_microactions_new.mako",
                        "cv32e40p_xisaac_resources.part": "xisaac_resources_new.mako",
                        "cv32e40p_xisaac_model.part": "cv32e40p_xisaac_model_new.mako",
                        "cv32e40p_xisaac_stages.part": "xisaac_stages.mako",
                        "cv32e40p_xisaac_pipelines.part": "xisaac_pipelines.mako",
                    },
                    "cva6": {
                        "cva6_xisaac_microactions.part": "xisaac_microactions_new.mako",
                        "cva6_xisaac_resources.part": "xisaac_resources_new.mako",
                        "cva6_xisaac_model.part": "cva6_xisaac_model_new.mako",
                        "cva6_xisaac_stages.part": "xisaac_stages.mako",
                        "cva6_xisaac_pipelines.part": "xisaac_pipelines.mako",
                    },
                }
                cores_parts_map2 = {
                    "cv32e40p": {
                        "cv32e40p_xisaac_microaction_mapping.part": "cv32e40p_xisaac_microaction_mapping_new.mako",
                        "cv32e40p_xisaac_ex_stages.part": "xisaac_ex_stages_new.mako",
                        "cv32e40p_xisaac_instr_groups.part": "xisaac_instr_groups.mako",
                        "cv32e40p_xisaac_trace_value_mapping.part": "xisaac_trace_value_mapping.mako",
                        "cv32e40p_xisaac_virtual_microactions.part": "xisaac_virtual_microactions_new.mako",
                        "cv32e40p_xisaac_virtual_resources.part": "xisaac_virtual_resources_new.mako",
                        "cv32e40p_xisaac_trace_values.part": "cv32e40p_xisaac_trace_values.mako",
                    },
                    "cva6": {
                        "cva6_xisaac_microaction_mapping.part": "cva6_xisaac_microaction_mapping_new.mako",
                        "cva6_xisaac_ex_stages.part": "xisaac_ex_stages_new.mako",
                        "cva6_xisaac_instr_groups.part": "xisaac_instr_groups.mako",
                        "cva6_xisaac_trace_value_mapping.part": "xisaac_trace_value_mapping.mako",
                        "cva6_xisaac_virtual_microactions.part": "xisaac_virtual_microactions_new.mako",
                        "cva6_xisaac_virtual_resources.part": "xisaac_virtual_resources_new.mako",
                        "cva6_xisaac_trace_values.part": "cva6_xisaac_trace_values.mako",
                    },
                }
                core_parts_map = cores_parts_map.get(args.core)
                core_parts_map2 = cores_parts_map2.get(args.core)
                assert core_parts_map is not None, f"Parts not found for core '{args.core}'"
                assert core_parts_map2 is not None, f"Parts not found for core '{args.core}'"
                for part_file, part_tmpl in core_parts_map.items():
                    # print("template_dirs", template_dirs)
                    mylookup = TemplateLookup(directories=template_dirs)
                    # part_template = Template(filename=f"{templates_path}/parts/{part_tmpl}", lookup=mylookup)
                    part_tmpl = lookup_template(part_tmpl, core=args.core, suffix=".corePerfDsl", part=True)
                    part_template = Template(filename=part_tmpl, lookup=mylookup)
                    assert part_tmpl is not None
                    part_content = part_template.render(
                        instr_names=instr_names,
                        instr_operands_map=instr_operands_map,
                        instrs_timing=instrs_timing,
                        sg2instrs=sg2instrs,
                        variant_name=variant_name,
                        uarch_name=uarch_name,
                        core_name=core_name,
                    )
                    if variant_name is not None:
                        subdir = dest_dir / variant_name
                    else:
                        subdir = dest_dir
                    subdir.mkdir(exist_ok=True)
                    part_dest = subdir / part_file
                    with open(part_dest, "w") as f:
                        f.write(part_content)
                for part_file, part_tmpl in core_parts_map2.items():
                    # print("part_file", part_file)
                    # print("part_tmpl", part_tmpl)
                    part_tmpl = lookup_template(part_tmpl, core=args.core, suffix=".corePerfDsl", part=True)
                    assert part_tmpl is not None
                    mylookup = TemplateLookup(directories=template_dirs)
                    # part_template = Template(filename=f"{templates_path}/parts/{part_tmpl}", lookup=mylookup)
                    part_template = Template(filename=part_tmpl, lookup=mylookup)
                    part_content = part_template.render(
                        instr_names=instr_names,
                        instr_operands_map=instr_operands_map,
                        instrs_timing=instrs_timing,
                        sg2instrs=sg2instrs,
                        uarch_name=uarch_name,
                        core_name=core_name,
                        trace_values=trace_values,
                    )
                    subdir = dest_dir
                    part_dest = subdir / part_file
                    with open(part_dest, "w") as f:
                        f.write(part_content)

        # all_content = ""
        # print("lookup_dirs", lookup_dirs)
        # print("lookup_dirs2", lookup_dirs2)
        # print("template_dirs", template_dirs)
        if not args.parts_only:
            # for variant_name, variant in variants.items():
            if True:
                # mylookup = TemplateLookup(directories=template_dirs + lookup_dirs[variant_name])
                # print("lookup_dirs2", lookup_dirs2)
                all_lookup = template_dirs + lookup_dirs2
                # print("all_lookup", all_lookup)
                mylookup = TemplateLookup(directories=all_lookup)
                # print("mylookup", mylookup)
                template = args.template
                if template is None:
                    assert core is not None
                    core2template = {"cv32e40p": "CV32E40PXISAAC", "cva6": "CVA6XISAAC"}
                    template = core2template.get(core)
                    assert template is not None, f"Could not find template for core {core}"
                template = lookup_template(template, core=args.core, suffix=".corePerfDsl")
                # print("template", template)
                assert template is not None
                mytemplate = Template(filename=template, lookup=mylookup)
                content = mytemplate.render(
                    variants=variant_names, new=True, uarch_name=uarch_name, core_name=core_name
                )
                # if variant_name is not None:
                #     header = f"// Variant: {variant_name}\n"
                # else:
                #     header = "// Default Variant\n"
                # all_content += header
                # all_content += content
                # content = all_content

    monitor_name = None
    if args.monitor_dest:
        monitor_template = args.monitor_template
        if monitor_template is None:
            assert core is not None
            core2monitor_template = {}
            monitor_template = core2monitor_template.get(core, "InstructionTrace_XISAAC")
            assert monitor_template is not None, f"Could not find monitor_template for core {core}"
        monitor_template = lookup_template(monitor_template, core=args.core, suffix=".json")
        # print("monitor_template", monitor_template)
        monitor_template = Path(monitor_template)
        assert monitor_template.is_file()
        monitor_dest = Path(args.monitor_dest)
        assert xlen is not None
        mylookup = TemplateLookup(directories=template_dirs)
        mytemplate = Template(filename=str(monitor_template), lookup=mylookup)
        monitor_name = monitor_dest.stem
        monitor_content = mytemplate.render(
            xlen=xlen,
            instr_operands_map=instr_operands_map,
            monitor_name=monitor_name,
            core_name=core_name,
        )
        # print("sg2instrs", sg2instrs)
        # print("instr_operands_map", instr_operands_map)
        with open(monitor_dest, "w") as f:
            f.write(monitor_content)
    if args.uarchs_dest:
        assert variant_config is not None
        uarchs_data = []
        for variant_idx, variant_config in enumerate(variants_config.variants):
            variant_name = variant_config.name
            variant_suffix = variant_name if variant_name is not None else ""
            uarch = f"{uarch_name}{variant_suffix}"
            uarch_lower = uarch.lower()
            new = {
                "uarch": uarch,
                "uarch_lower": uarch_lower,
                "variant": variant_name,
                "description": variant_config.description,
                "details": variant_config.details,
                **variant_config.metrics,
            }
            uarchs_data.append(new)

        uarchs_df = pd.DataFrame(uarchs_data)
        print("uarch_df")
        print(uarchs_df)
        uarchs_df.to_csv(args.uarchs_dest)

    if args.ini_dest:
        assert variant_config is not None
        uarchs_data = []
        assert monitor_name
        trace_modes = [False, True]
        for variant_idx, variant_config in enumerate(variants_config.variants):
            variant_name = variant_config.name
            for trace_mode in trace_modes:
                variant_suffix = variant_name if variant_name is not None else ""
                uarch = f"CV32E40PXISAAC{variant_suffix}"
                uarch_lower = uarch.lower()
                # instr_trace = "InstructionTrace_RV64IMF_Zicsr"
                instr_trace = monitor_name
                ini_content = f"""
[StringConfigurations]
arch.cpu={core_name}

[Plugin PerformanceEstimatorPlugin]
plugin.perfEst.uArch={uarch}
"""
                ini_dir = Path(args.ini_dest)
                if ini_dir.exists():
                    assert ini_dir.is_dir(), f"Not a directory: {ini_dir}"
                else:
                    ini_dir.mkdir()
                if trace_mode:
                    ini_content += f"""plugin.perfEst.print=1
plugin.perfEst.printDir=.

[Plugin TracePrinterPlugin]
plugin.tracePrinter.trace={instr_trace}
plugin.tracePrinter.stream.toFile=1
plugin.tracePrinter.stream.outDir=.
plugin.tracePrinter.stream.fileName=instr_trace
"""
                    ini_file = Path(ini_dir) / f"{uarch_lower}_trace.ini"
                else:
                    ini_file = Path(ini_dir) / f"{uarch_lower}.ini"
                with open(ini_file, "w") as f:
                    f.write(ini_content)

    if args.output is None:
        print(content)
    else:
        with open(args.output, "w") as f:
            f.write(content)


if __name__ == "__main__":
    main()
