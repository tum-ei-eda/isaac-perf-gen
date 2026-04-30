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
"""ISAAC CoreDSL Loader Script."""

import sys
import yaml
import shutil
import tempfile
import argparse
import subprocess
from pathlib import Path
from typing import Optional, List


def cdsl_to_m2_model(
    file: str, out_file: Optional[str] = None, is_set: bool = True, includes: Optional[List[str]] = None
):
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        # if out_file is None:
        #     out_file = tmpdir / "temp.m2isarmodel"
        # else:
        #     out_file = Path(out_file)
        args = [
            "python3",
            "-m",
            "m2isar.frontends.coredsl2_set.parser" if is_set else "m2isar.frontends.coredsl2.parser",
            file,
            "-o",
            tmpdir,
        ]
        if includes:
            includes = list(map(lambda x: Path(x).resolve(), includes))
            includes_args = [f"-I{inc}" for inc in includes]
            args += includes_args
        subprocess.run(args, check=True)
        from m2isar.metamodel import load_model

        temp_file = tmpdir / f"{file.stem}.m2isarmodel"
        if out_file is not None:
            shutil.copy(temp_file, out_file)

        # print("out_file", out_file)
        # input("!!!")
        m2_model = load_model(temp_file)
        # print("m2_model", m2_model)
        return m2_model


def run_coredsl2_loader(
    file: str,
    out_file: Optional[str] = None,
    includes: Optional[List[str]] = None,
    set_name: str = "XIsaac",
    xlen: int = 32,
):
    resolved_file = Path(file).resolve()
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        m2_model = cdsl_to_m2_model(resolved_file, is_set=True, includes=includes)
        # print("m2_model", m2_model)
    assert len(m2_model.cores) == 0
    sets = m2_model.sets
    assert len(sets) > 0
    # print("sets", sets)
    assert set_name in sets, f"Set '{set_name}' not found!"
    set_def = sets[set_name]
    # print("set_def", set_def)
    instrs_data = []
    assert xlen in [32, 64]
    global_properties = {"xlen": xlen}
    for instr_def in set_def.instructions.values():
        instr_data = {}
        # print("instr_def", instr_def, dir(instr_def))
        instr_name = instr_def.name
        # print("instr_name", instr_name)

        def detect_operands(instr_def):
            # For now just use encoding field -> Use operands syntax in the future! (or infer from behav)
            from m2isar.metamodel import arch

            num_operands = 0
            operand_dirs = []
            operands_enc_bits = []
            operand_enc_bits_sum = 0
            operand_names = []
            operand_reg_classes = []
            operand_types = []
            # print("enc", instr_def.encoding)
            for enc in reversed(instr_def.encoding):
                if isinstance(enc, arch.BitVal):
                    continue
                assert isinstance(enc, arch.BitField)
                op_name = enc.name
                assert op_name not in operand_names
                operand_names.append(op_name)
                num_operands += 1
                range_spec = enc.range
                # print("range_spec", range_spec, dir(range_spec))
                assert range_spec.lower == 0
                op_bits = range_spec.upper + 1
                # print("op_bits", op_bits)
                operands_enc_bits.append(op_bits)
                operand_enc_bits_sum += op_bits
                lookup_dir = {
                    "rd": "OUT",
                    "rs1": "IN",
                    "rs2": "IN",
                    "rs3": "IN",
                    "rs4": "IN",
                    "rs5": "IN",
                    # TODO: support inout!
                }
                op_dir = lookup_dir.get(op_name)
                # print("op_dir", op_dir)
                operand_dirs.append(op_dir)
                if "imm" in op_name.lower():
                    op_type = "IMM"
                    op_reg_class = None
                else:
                    assert op_name.lower()[0] == "r"
                    op_type = "REG"
                    # TODO: check reg class
                    op_reg_class = "GPR"
                operand_types.append(op_type)
                operand_reg_classes.append(op_reg_class)
                # print("op_type", op_type)
                # print("op_reg_class", op_reg_class)
                assert op_dir is not None, "fUnable to infer op_dir from name: {op_name}"
            return (
                num_operands,
                operand_dirs,
                operands_enc_bits,
                operand_enc_bits_sum,
                operand_names,
                operand_reg_classes,
                operand_types,
            )

        (
            num_operands,
            operand_dirs,
            operands_enc_bits,
            operand_enc_bits_sum,
            operand_names,
            operand_reg_classes,
            operand_types,
        ) = detect_operands(instr_def)

        instr_data = {
            "InstrName": instr_name,
            "#Operands": num_operands,
            "OperandDirs": operand_dirs,
            "OperandEncBits": operands_enc_bits,
            "OperandEncBitsSum": operand_enc_bits_sum,
            "OperandNames": operand_names,
            "OperandRegClasses": operand_reg_classes,
            "OperandTypes": operand_types,
        }
        instrs_data.append({"properties": instr_data})
    # print("instrs_data", instrs_data, len(instrs_data))
    index_data = {
        "candidates": instrs_data,
        "global": {
            "properties": global_properties,
        },
    }
    # print("index_data", index_data)
    if out_file is not None:
        with open(out_file, "w") as f:
            yaml.dump(index_data, f)
    else:
        contents = yaml.dump(index_data)
        print(contents)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--set", default="XIsaac")
    parser.add_argument("--xlen", type=int, default=None, required=True)
    parser.add_argument("-I", dest="includes", action="append", default=[], help="Extra include directories")
    args = parser.parse_args()
    run_coredsl2_loader(args.file, out_file=args.output, includes=args.includes, set_name=args.set, xlen=args.xlen)


if __name__ == "__main__":
    main()
