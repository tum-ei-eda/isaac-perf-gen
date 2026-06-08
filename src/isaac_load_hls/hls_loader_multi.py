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
"""ISAAC HLS Loader Script."""

import ast
import logging
import argparse
from pathlib import Path
from collections import defaultdict

import yaml
import pandas as pd

from isaac_perf_common.config import VariantsConfig, InstrConfig, VariantConfig


def load_hls_artifacts_multi(
    hls_dirs,
    drop_fallback_schedules: bool = True,
    isax_name: str = "XIsaac",
):
    # TODO: check that all dirs have the same instrs and SGs?
    assert isinstance(hls_dirs, list)
    variants_ = []
    for i, hls_dir in enumerate(hls_dirs):
        print("i,hls_dir", i, hls_dir)
        hls_schedules = Path(hls_dir) / "hls_schedules.csv"
        assert hls_schedules.is_file(), f"Missing: {hls_schedules}"
        hls_schedules_df = pd.read_csv(hls_schedules)
        if drop_fallback_schedules:
            hls_schedules_df = hls_schedules_df[~hls_schedules_df["Fallback"]]
        variants = {}
        variant_extras = {}
        if hls_schedules_df is not None:
            hls_schedules_df["SG"] = hls_schedules_df["config"].apply(lambda x: int(x.split("_")[1]))
        hls_selected_schedule_metrics_csv = Path(hls_dir) / "hls_selected_schedule_metrics.csv"
        assert hls_selected_schedule_metrics_csv.is_file(), f"Missing: {hls_selected_schedule_metrics_csv}"
        hls_variants_df = pd.read_csv(hls_selected_schedule_metrics_csv)
        assert len(hls_variants_df) == 1, "Only single-variant HLS dirs are allowed in load_hls_artifacts_multi"
        # num_variants = len(hls_variants_df)
        # print("hls_variants_df")
        # print("num_variants", num_variants)
        print("hls_variants_df")
        print(hls_variants_df)
        variant_row = hls_variants_df.iloc[0]
        # for idx, variant_row in hls_variants_df.iterrows():
        if True:
            # print("idx", idx)
            # print("variant_row", variant_row)
            variant_name = variant_row.get("Variant name")
            assert variant_name is None
            # print("variant_name", variant_name)
            # if variant_name is None:
            #     variant_name = f"V{idx}"
            # print("variant_name", variant_name)
            variant_details = variant_row.get("Variant details")
            assert variant_details is None
            variant_description = variant_row.get("Variant description")
            assert variant_description is None
            total_area_estimate = variant_row["total_area_estimate"]
            variant_extras[variant_name] = (
                variant_description,
                variant_details,
                total_area_estimate,
            )
            if variant_name is not None:
                selected_solutions_yaml = Path(hls_dir) / "output" / variant_name / "selected_solutions.yaml"
            else:
                selected_solutions_yaml = Path(hls_dir) / "output" / "selected_solutions.yaml"
            assert selected_solutions_yaml.is_file(), f"Missing: {selected_solutions_yaml}"
            with open(selected_solutions_yaml) as f:
                selected_solutions = yaml.safe_load(f)
            variant = selected_solutions
            variants[variant_name] = variant
            variant_instrs = []
            # print("variant", variant)
            selected_solutions = variant
            # if args.hls_yaml is None:
            #     assert args.hls_dir is not None
            #     hls_yaml = Path(args.hls_dir) / "ISAX_XIsaac.yaml"
            # else:
            #     hls_yaml = Path(args.hls_yaml)
            if variant_name is not None:
                hls_yaml = Path(hls_dir) / "output" / variant_name / f"ISAX_{isax_name}.yaml"
            else:
                hls_yaml = Path(hls_dir) / "output" / f"ISAX_{isax_name}.yaml"
            assert hls_yaml.is_file(), f"Missing: {hls_yaml}"
            with open(hls_yaml) as f:
                hls_data = yaml.safe_load(f)
                # print("hls_data", hls_data)

            def apply_selection(hls_schedules_df, selected_solutions):
                configs = [f"SG_{x['sharing_group']}_SOL_IDX_{x['solution_idx']}" for x in selected_solutions]
                # print("configs", configs)
                hls_schedules_df_ = hls_schedules_df[hls_schedules_df["config"].isin(configs)]
                return hls_schedules_df_

            hls_schedules_df_ = apply_selection(hls_schedules_df, selected_solutions)
            # print("hls_schedules_df_", hls_schedules_df_)
            instr_latencies = {}
            sg2ii = {}
            sg2instrs = defaultdict(list)
            instr_latencies2 = {}
            for instr_data in hls_data:
                if "instruction" not in instr_data:
                    break
                instr_name = instr_data["instruction"]
                schedule = instr_data["schedule"]
                stage_nums = [x["stage"] for x in schedule]
                # print("stage_nums", stage_nums)
                min_stage, max_stage = min(stage_nums), max(stage_nums)
                # print("instr_latencies", instr_latencies)
                # assert instr_latencies[instr_name] == (max_stage + 1)  # TODO: fix
                lat = max_stage - min_stage + 1
                # print("lat", lat)
                lat = max(1, lat)
                # print("lat_", lat)
                instr_latencies2[instr_name] = lat
            for _, row in hls_schedules_df_.iterrows():
                lats = row["Instruction latencies"]
                ii = row["II"]
                # print("ii", ii)
                # input("!!!")
                grp = row["SG"]
                assert grp not in sg2ii
                sg2ii[grp] = ii
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
                    assert len(lats) == 1, "Multi-instr sharing groups are unsupported!"
                for instr_name, lat in lats.items():
                    sg2instrs[grp].append(instr_name)
                    lat_ = lat
                    assert instr_name not in instr_latencies
                    instr_latencies[instr_name] = lat_
                lat = instr_latencies2[instr_name]
                ii = sg2ii[grp]
                variant_instr = InstrConfig(name=instr_name, cycles=lat, ii=ii, sg=grp)
                variant_instrs.append(variant_instr)
            # print("instr_latencies2", instr_latencies2)

            # input("!")
            variant_metrics = {}
            variant_metrics["total_area_estimate"] = float(total_area_estimate)
            variant_name = f"V{i}"
            variant_config = VariantConfig(
                name=variant_name,
                # idx=idx,
                idx=i,
                instrs=variant_instrs,
                details=variant_details,
                description=variant_description,
                metrics=variant_metrics,
            )
            variants_.append(variant_config)
    variants_config = VariantsConfig(variants=variants_)
    return variants_config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("hls_dir", nargs="+", help="Path to hls output dir")
    parser.add_argument("--isax-name", default="XIsaac")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output YAML file path. Prints to stdout if None",
    )
    args = parser.parse_args()

    variants_config = load_hls_artifacts_multi(args.hls_dir, isax_name=args.isax_name)
    if args.output is None:
        print(variants_config.to_yaml())
    else:
        logging.info("Writing YAML output to %s", args.output)
        variants_config.to_yaml_file(args.output)


if __name__ == "__main__":
    main()
