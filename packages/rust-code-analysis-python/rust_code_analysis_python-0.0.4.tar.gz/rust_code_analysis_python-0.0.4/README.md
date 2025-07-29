# rust-code-analysis-python
[![Build Status](https://img.shields.io/github/actions/workflow/status/luigig44/rust-code-analysis-python/release.yml)](https://github.com/luigig44/rust-code-analysis-python)
[![Docs Build Status](https://readthedocs.org/projects/rust-code-analysis-python/badge/)](https://rust-code-analysis-python.readthedocs.org)
[![PyPI - Version](https://img.shields.io/pypi/v/rust-code-analysis-python)](https://pypi.org/project/rust-code-analysis-python)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/rust-code-analysis-python)](https://pypistats.org/packages/rust-code-analysis-python)
![PyPI - License](https://img.shields.io/pypi/l/rust-code-analysis-python)

Python bindings for [rust-code-analysis](https://github.com/mozilla/rust-code-analysis), a Rust library to analyze and collect metrics on source code.


## Quick Start Guide

Full documentation available here: https://rust-code-analysis-python.readthedocs.org

```IPython Notebook
%pip install rust-code-analysis-python
from rust_code_analysis_python import compute_metrics, remove_comments

# Get code metrics
metrics_result = compute_metrics("example.rs", code_string, unit=True)

# Remove comments from code
code_without_comments = remove_comments("example.c", code_string)
```

## Developing

```bash
pip install -r dev_requirements.txt
# Must have rust installed (see rustup.rs)
# Run linting, build and test
tox run
```

## License

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/. 