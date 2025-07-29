# Artifex

[![Static Badge](https://img.shields.io/pypi/v/artifex?logo=pypi&logoColor=%23fff&color=%23006dad&label=Pypi)](https://pypi.org/project/artifex/)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/tanaos/artifex/python-publish.yml?logo=github&logoColor=%23fff&label=Tests)](https://github.com/tanaos/artifex/actions/workflows/python-publish.yml)
[![Documentation](https://img.shields.io/badge/%20Docs-Read%20the%20docs-orange?logo=docusaurus&logoColor=white)](https://docs.tanaos.com)

Artifex is a Python library for training small AI models in 1 line of code and **WITHOUT DATA**. How is it even possible, you may ask? Because synthetic training data is automatically generated under the hood through our [synthex library](https://github.com/tanaos/synthex-python).

## Documentation

See the [full Artifex documentation](https://docs.tanaos.com/).

## Installation

You only need acces to this source code if you want to modify the package. We do welcome contributions. To find out how you can contribute, see [CONTRIBUTING.md](CONTRIBUTING.md).

If you just want to **use** the package, simply run

```bash
pip install --upgrade artifex
```

## Use cases

Artifex can be used to easily generate *pre-trained* AI models for specific use-cases, such as:

- Chatbot Guardrail models
- RAG re-rankers
