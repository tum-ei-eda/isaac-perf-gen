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
"""ISAAC Perf Gen Script (old)."""

import ast
import itertools
import tempfile
import argparse
from pathlib import Path
from collections import defaultdict
from contextlib import contextmanager

import yaml
import pandas as pd
from mako.template import Template
from mako.lookup import TemplateLookup

pd.set_option("display.max_columns", None)


def get_permutations(d):
    # return [
    #     {k: v for k, v in zip(sorted(d.keys()), list_prod_value)}
    #     for list_prod_value in itertools.product(*(d[k] for k in sorted(d.keys())))
    # ]
    return [
        tuple((k, v) for k, v in zip(sorted(d.keys()), list_prod_value))
        for list_prod_value in itertools.product(*(d[k] for k in sorted(d.keys())))
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--template", default=None, required=True, help="Base MAKO Template"
    )
    parser.add_argument(
        "-o", "--output", default=None, help="Output .core_perf_dsl file path"
    )
    parser.add_argument(
        "--monitor-template", default=None, help="Mako template for monitor description"
    )
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
    parser.add_argument(
        "--uarchs-dest", default=None, help="Output CSV file for uarch names"
    )
    parser.add_argument(
        "-c", "--core", required=True, choices=["cv32e40p", "cva6"], help="Base core"
    )
    parser.add_argument(
        "--temp-dir", default=None, help="Optional path to persistent temp dir"
    )
    parser.add_argument("--hls-dir", default=None, help="Path to hls output dir")
    # parser.add_argument("--hls-schedules", default=None, help="Path to hls_schedules.csv")
    # parser.add_argument("--hls-yaml", default=None, help="Path to ISAX_XIsaac.yaml")
    # parser.add_argument("--selected-solutions", default=None, help="Path to selected_solutions.yaml")
    parser.add_argument("--variants", default=None, help="Filter variants")
    parser.add_argument("--index-yaml", default=None, help="Path to XISAAC index.yml")
    parser.add_argument("--parts-only", action="store_true", help="Only generate parts")
    parser.add_argument(
        "--render-only", action="store_true", help="Only render final output"
    )
    args = parser.parse_args()
    core_name = "XIsaacCore"

    @contextmanager
    def temp_dir_content(enter_result=None):
        if args.temp_dir is not None:
            yield Path(args.temp_dir)
        else:
            with tempfile.TemporaryDirectory() as tmpdirname:
                yield Path(tmpdirname)

    template_dirs = [".", "templates/"]
    lookup_dirs = defaultdict(list)
    lookup_dirs2 = []
    xlen = None
    variants = None
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
            # if args.hls_schedules is None:
            #     assert args.hls_dir is not None
            #     hls_schedules = Path(args.hls_dir) / ".." / "hls_schedules.csv"
            # else:
            #     hls_schedules = Path(args.hls_schedules)
            hls_schedules = Path(args.hls_dir) / "hls_schedules.csv"
            assert hls_schedules.is_file(), f"Missing: {hls_schedules}"
            hls_schedules_df = pd.read_csv(hls_schedules)
            drop_fallback_schedules = True
            if drop_fallback_schedules:
                hls_schedules_df = hls_schedules_df[~hls_schedules_df["Fallback"]]
            print("hls_schedules_df", hls_schedules_df)
            # input("123")
            # assert args.selected_solutions is not None
            variants_filter = args.variants
            if variants_filter is not None:
                if isinstance(variants_filter, str):
                    variants_filter = list(map(int, variants_filter.split(",")))
                assert isinstance(variants_filter, list)  # TODO: allow sets?
            variants = {}
            variant_extras = {}
            if hls_schedules_df is not None:
                hls_schedules_df["SG"] = hls_schedules_df["config"].apply(
                    lambda x: int(x.split("_")[1])
                )
            hls_selected_schedule_metrics_csv = (
                Path(args.hls_dir) / "hls_selected_schedule_metrics.csv"
            )
            assert (
                hls_selected_schedule_metrics_csv.is_file()
            ), f"Missing: {hls_selected_schedule_metrics_csv}"
            hls_variants_df = pd.read_csv(hls_selected_schedule_metrics_csv)
            num_variants = len(hls_variants_df)
            print("hls_variants_df")
            print(hls_variants_df)
            print("num_variants", num_variants)
            if variants_filter:
                hls_variants_df = hls_variants_df[
                    hls_variants_df["Variant idx"].isin(variants_filter)
                ]
            print("hls_variants_df")
            print(hls_variants_df)
            for _, variant_row in hls_variants_df.iterrows():
                print("variant_row", variant_row)
                variant_name = variant_row["Variant name"]
                print("variant_name", variant_name)
                variant_details = variant_row["Variant details"]
                variant_description = variant_row["Variant description"]
                total_area_estimate = variant_row["total_area_estimate"]
                variant_extras[variant_name] = (
                    variant_description,
                    variant_details,
                    total_area_estimate,
                )
                if variant_name is not None:
                    selected_solutions_yaml = (
                        Path(args.hls_dir)
                        / "output"
                        / variant_name
                        / "selected_solutions.yaml"
                    )
                else:
                    selected_solutions_yaml = (
                        Path(args.hls_dir) / "output" / "selected_solutions.yaml"
                    )
                assert (
                    selected_solutions_yaml.is_file()
                ), f"Missing: {selected_solutions_yaml}"
                with open(selected_solutions_yaml) as f:
                    selected_solutions = yaml.safe_load(f)
                variant = selected_solutions
                variants[variant_name] = variant
            print("variants", variants)
            # input(">>>")
            sg2instrs = defaultdict(list)
            for variant_name, variant in variants.items():
                print("variant", variant)
                selected_solutions = variant
                # if args.hls_yaml is None:
                #     assert args.hls_dir is not None
                #     hls_yaml = Path(args.hls_dir) / "ISAX_XIsaac.yaml"
                # else:
                #     hls_yaml = Path(args.hls_yaml)
                if variant_name is not None:
                    hls_yaml = (
                        Path(args.hls_dir)
                        / "output"
                        / variant_name
                        / "ISAX_XIsaac.yaml"
                    )
                else:
                    hls_yaml = Path(args.hls_dir) / "output" / "ISAX_XIsaac.yaml"
                assert hls_yaml.is_file(), f"Missing: {hls_yaml}"
                with open(hls_yaml) as f:
                    hls_data = yaml.safe_load(f)
                    # print("hls_data", hls_data)

                def apply_selection(hls_schedules_df, selected_solutions):
                    configs = [
                        f"SG_{x['sharing_group']}_SOL_IDX_{x['solution_idx']}"
                        for x in selected_solutions
                    ]
                    # print("configs", configs)
                    hls_schedules_df_ = hls_schedules_df[
                        hls_schedules_df["config"].isin(configs)
                    ]
                    return hls_schedules_df_

                hls_schedules_df = apply_selection(hls_schedules_df, selected_solutions)
                # print("hls_schedules_df_", hls_schedules_df)
                instr_latencies = {}
                for _, row in hls_schedules_df.iterrows():
                    lats = row["Instruction latencies"]
                    grp = row["SG"]
                    if lats in ["None", None]:
                        instr_names = ["unknown"]  # TODO
                        assert "Overall latency" in row
                        default_lat = row["Overall latency"]
                        lats = {}
                        for instr_name in instr_names:
                            lats[instr_name] = default_lat
                    else:
                        lats = ast.literal_eval(lats)
                        # print("lats", lats, type(lats))
                        assert (
                            len(lats) == 1
                        ), "Multi-instr sharing groups are unsupported!"
                    for instr_name, lat in lats.items():
                        sg2instrs[grp].append(instr_name)
                        lat_ = lat
                        instr_latencies[instr_name] = lat_
                instr_latencies2 = {}
                print("sg2instrs", sg2instrs)
                # print("instr_latencies", instr_latencies)
                for instr_data in hls_data:
                    if "instruction" not in instr_data:
                        break
                    instr_name = instr_data["instruction"]
                    schedule = instr_data["schedule"]
                    stage_nums = [x["stage"] for x in schedule]
                    print("stage_nums", stage_nums)
                    min_stage, max_stage = min(stage_nums), max(stage_nums)
                    print("instr_latencies", instr_latencies)
                    # assert instr_latencies[instr_name] == (max_stage + 1)  # TODO: fix
                    lat = max_stage - min_stage + 1
                    print("lat", lat)
                    lat = max(1, lat)
                    print("lat_", lat)
                    instr_latencies2[instr_name] = lat
                print("instr_latencies2", instr_latencies2)

                # input("!")
                instr_operands_map = {}
                instrs_timing = {}
                for candidate_data in candidates_data:
                    candidate_properties = candidate_data["properties"]
                    instr_name = candidate_properties["InstrName"]
                    # print("instr_name", instr_name)
                    operand_names = candidate_properties["OperandNames"]
                    # print("operand_names", operand_names)
                    operand_types = candidate_properties["OperandTypes"]
                    # print("operand_types", operand_types)
                    operand_dirs = candidate_properties["OperandDirs"]
                    # print("operand_dirs", operand_dirs)
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
                    print("instr_name", instr_name)
                    print("instr_latencies2", instr_latencies2)
                    instr_cycles = instr_latencies2[instr_name]
                    instr_timing = (instr_cycles,)
                    instrs_timing[instr_name] = instr_timing
                instr_names = list(instr_operands_map.keys())
                # if variant_name is not None:
                #     dest_dir = temp_dir / variant_name
                #     dest_dir.mkdir(exist_ok=True)
                # else:
                #     dest_dir = temp_dir
                dest_dir = temp_dir
                lookup_dirs[variant_name].append(dest_dir)
                lookup_dirs2.append(temp_dir)
                cores_parts_map = {
                    "cv32e40p": {
                        "cv32e40p_xisaac_microactions.part": "cv32e40p_xisaac_microactions.mako",
                        "cv32e40p_xisaac_resources.part": "cv32e40p_xisaac_resources.mako",
                        "cv32e40p_xisaac_model.part": "cv32e40p_xisaac_model.mako",
                    },
                }
                cores_parts_map2 = {
                    "cv32e40p": {
                        "cv32e40p_xisaac_microaction_mapping.part": "cv32e40p_xisaac_microaction_mapping.mako",
                        "cv32e40p_xisaac_ex_stages.part": "cv32e40p_xisaac_ex_stages.mako",
                        "cv32e40p_xisaac_instr_groups.part": "cv32e40p_xisaac_instr_groups.mako",
                        "cv32e40p_xisaac_trace_value_mapping.part": "cv32e40p_xisaac_trace_value_mapping.mako",
                        "cv32e40p_xisaac_virtual_microactions.part": "cv32e40p_xisaac_virtual_microactions.mako",
                        "cv32e40p_xisaac_virtual_resources.part": "cv32e40p_xisaac_virtual_resources.mako",
                    },
                }
                core_parts_map = cores_parts_map.get(args.core)
                core_parts_map2 = cores_parts_map2.get(args.core)
                assert (
                    core_parts_map is not None
                ), f"Parts not found for core '{args.core}'"
                assert (
                    core_parts_map2 is not None
                ), f"Parts not found for core '{args.core}'"
                for part_file, part_tmpl in core_parts_map.items():
                    mylookup = TemplateLookup(directories=template_dirs)
                    part_template = Template(
                        filename=f"templates/{part_tmpl}", lookup=mylookup
                    )
                    part_content = part_template.render(
                        instr_names=instr_names,
                        instr_operands_map=instr_operands_map,
                        instrs_timing=instrs_timing,
                        sg2instrs=sg2instrs,
                        variant_name=variant_name,
                    )
                    subdir = dest_dir / variant_name
                    subdir.mkdir(exist_ok=True)
                    part_dest = subdir / part_file
                    with open(part_dest, "w") as f:
                        f.write(part_content)
                for part_file, part_tmpl in core_parts_map2.items():
                    mylookup = TemplateLookup(directories=template_dirs)
                    part_template = Template(
                        filename=f"templates/{part_tmpl}", lookup=mylookup
                    )
                    part_content = part_template.render(
                        instr_names=instr_names,
                        instr_operands_map=instr_operands_map,
                        instrs_timing=instrs_timing,
                        sg2instrs=sg2instrs,
                    )
                    subdir = dest_dir
                    part_dest = subdir / part_file
                    with open(part_dest, "w") as f:
                        f.write(part_content)

        # all_content = ""
        print("lookup_dirs", lookup_dirs)
        print("lookup_dirs2", lookup_dirs2)
        print("template_dirs", template_dirs)
        if not args.parts_only:
            # for variant_name, variant in variants.items():
            if True:
                # mylookup = TemplateLookup(directories=template_dirs + lookup_dirs[variant_name])
                mylookup = TemplateLookup(directories=template_dirs + lookup_dirs2)
                mytemplate = Template(filename=args.template, lookup=mylookup)
                content = mytemplate.render(variants=variants, new=False)
                # if variant_name is not None:
                #     header = f"// Variant: {variant_name}\n"
                # else:
                #     header = "// Default Variant\n"
                # all_content += header
                # all_content += content
                # content = all_content

    monitor_name = None
    if args.monitor_dest:
        assert args.monitor_template
        monitor_template = Path(args.monitor_template)
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
        assert variants is not None
        uarchs_data = []
        for variant_name in variants:
            variant_suffix = variant_name if variant_name is not None else ""
            extras = variant_extras[variant_name]
            variant_description, variant_details, total_area_estimate = extras
            uarch = f"CV32E40PXISAAC{variant_suffix}"
            uarch_lower = uarch.lower()
            new = {
                "uarch": uarch,
                "uarch_lower": uarch_lower,
                "variant": variant_name,
                "description": variant_description,
                "details": variant_details,
                "total_area_estimate": total_area_estimate,
            }
            uarchs_data.append(new)

        uarchs_df = pd.DataFrame(uarchs_data)
        print("uarch_df")
        print(uarchs_df)
        uarchs_df.to_csv(args.uarchs_dest)

    if args.ini_dest:
        assert variants is not None
        assert monitor_name
        trace_modes = [False, True]
        for variant_name in variants:
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
                assert ini_dir.is_dir(), f"Not a directory: {ini_dir}"
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
