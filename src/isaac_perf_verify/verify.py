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
"""ISAAC Fake HLS Script."""

import sys
import tempfile
import argparse
import subprocess
from pathlib import Path
from typing import Optional


def run_verify(file: str, full: bool = False, out_dir: Optional[str] = None):
    resolved_file = Path(file).resolve()
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        if out_dir is None:
            out_dir = tmpdir
        else:
            out_dir = Path(out_dir)
        args = [
            "python3",
            "-m",
            "m2isar_perf.run",
            resolved_file,
            "-c",
            # "-i",
            "-o",
            "out_dir",
        ]
        if full:
            dump_dir = out_dir / "dump"
            args += ["-m", "-d", dump_dir]
        try:
            subprocess.run(args, cwd=tmpdir, check=True)
        except subprocess.CalledProcessError:
            print("Check FAILED!")
            sys.exit(1)
        print("Check successfull!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--full", "-f", action="store_true")
    parser.add_argument("--output", "-o", default=None)
    args = parser.parse_args()
    run_verify(args.file, full=args.full, out_dir=args.output)


if __name__ == "__main__":
    main()
