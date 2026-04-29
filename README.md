# isaac-perf-gen
[![pypi package](https://badge.fury.io/py/isaac-perf-gen.svg)](https://pypi.org/project/isaac-perf-gen)
[![readthedocs](https://readthedocs.org/projects/isaac-perf-gen/badge/?version=latest)](https://isaac-perf-gen.readthedocs.io/en/latest/?version=latest)
![coverage](https://byob.yarr.is/tum-ei-eda/isaac-perf-gen/coverage)
[![GitHub license](https://img.shields.io/github/license/tum-ei-eda/isaac-perf-gen.svg)](https://github.com/tum-ei-eda/isaac-perf-gen/blob/main/LICENSE)

[![cicd workflow](https://github.com/tum-ei-eda/isaac-perf-gen/actions/workflows/docs.yml/badge.svg)](https://github.com/tum-ei-eda/isaac-perf-gen/actions/workflows/docs.yml)
[![lint workflow](https://github.com/tum-ei-eda/isaac-perf-gen/actions/workflows/style.yml/badge.svg)](https://github.com/tum-ei-eda/isaac-perf-gen/actions/workflows/style.yml)
[![demo workflow](https://github.com/tum-ei-eda/isaac-perf-gen/actions/workflows/test.yml/badge.svg)](https://github.com/tum-ei-eda/isaac-perf-gen/actions/workflows/test.yml)
[![bench workflow](https://github.com/tum-ei-eda/isaac-perf-gen/actions/workflows/release.yml/badge.svg)](https://github.com/tum-ei-eda/isaac-perf-gen/actions/workflows/release.yml)

Generating CorePerfDSL Performance Models for ISE candidates

https://tum-ei-eda.github.io/isaac-perf-gen

## Features

This project ships multiple sub-projects:
- `isaac_perf_gen`: Emits CorePerfDSL and auxiliary files based on provides GenIE and HLS files.
- `isaac_perf_verify`: Wrapper for CorePerfDSL API to check if the syntax of the generated files is ok.
- `isaac_fake_hls`: WIP! Sample many possible uarchs for a given ISE to design space exploration without actually running a HLS backend.
- `isaac_load_cdsl`: WIP! Allows passing `.core_desc` inputs instead of a GenIE-specific `index.yaml`

## Prerequisites

```
pip install -e .

# Optional:
pip install -e ".[dev]"
pip install -e ".[verify]"
```

## Usage

### `isaac_perf_gen`

TODO

### `isaac_perf_verify`

TODO

### ...

## Examples

```sh
cd examples/1-crc32/cv32e40p
./generate.sh

cd examples/1-crc32/cva6
./generate.sh
```

## Development

TODO
