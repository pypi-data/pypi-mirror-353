# nmn
Not the neurons we want, but the neurons we need

[![PyPI version](https://img.shields.io/pypi/v/nmn.svg)](https://pypi.org/project/nmn/)
[![Downloads](https://static.pepy.tech/badge/nmn)](https://pepy.tech/project/nmn)
[![Downloads/month](https://static.pepy.tech/badge/nmn/month)](https://pepy.tech/project/nmn)
[![GitHub stars](https://img.shields.io/github/stars/mlnomadpy/nmn?style=social)](https://github.com/mlnomadpy/nmn)
[![GitHub forks](https://img.shields.io/github/forks/mlnomadpy/nmn?style=social)](https://github.com/mlnomadpy/nmn)
[![GitHub issues](https://img.shields.io/github/issues/mlnomadpy/nmn)](https://github.com/mlnomadpy/nmn/issues)
[![PyPI - License](https://img.shields.io/pypi/l/nmn)](https://pypi.org/project/nmn/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nmn)](https://pypi.org/project/nmn/)

## Overview

**nmn** provides neural network layers for multiple frameworks (Flax, NNX, Keras, PyTorch, TensorFlow) that do not require activation functions to learn non-linearity. The main goal is to enable deep learning architectures where the layer itself is inherently non-linear, inspired by the paper:

> Deep Learning 2.0: Artificial Neurons that Matter: Reject Correlation - Embrace Orthogonality

## Supported Frameworks & Tasks

### Flax (JAX)
- `YatNMN` layer implemented in `src/nmn/linen/nmn.py`
- **Tasks:**
  - [x] Core layer implementation
  - [ ] Recurrent layer (to be implemented)

### NNX (Flax NNX)
- `YatNMN` layer implemented in `src/nmn/nnx/nmn.py`
- **Tasks:**
  - [x] Core layer implementation
  - [ ] Recurrent layer (to be implemented)

### Keras
- `YatNMN` layer implemented in `src/nmn/keras/nmn.py`
- **Tasks:**
  - [x] Core layer implementation
  - [ ] Recurrent layer (to be implemented)

### PyTorch
- `YatNMN` layer implemented in `src/nmn/torch/nmn.py`
- **Tasks:**
  - [x] Core layer implementation
  - [ ] Recurrent layer (to be implemented)

### TensorFlow
- `YatNMN` layer implemented in `src/nmn/tf/nmn.py`
- **Tasks:**
  - [x] Core layer implementation
  - [ ] Recurrent layer (to be implemented)

## Installation

```bash
pip install nmn
```

## Usage Example (Flax)

```python
from nmn.nnx.nmn import YatNMN
from nmn.nnx.yatconv import YatConv
# ... use as a Flax module ...
```

## Roadmap
- [ ] Implement recurrent layers for all frameworks
- [ ] Add more examples and benchmarks
- [ ] Improve documentation and API consistency

## License
GNU Affero General Public License v3
