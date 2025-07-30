# torch-archs

PyTorch vision and language architectures.

## Overview

`torch-archs` is a collection of modern neural network architectures implemented in PyTorch, focusing on both computer vision and natural language processing models. This library provides clean, efficient implementations of state-of-the-art architectures that can be easily integrated into your projects.

## Features

- **Vision Architectures**: Vision Transformer (ViT) components and related architectures
- **Language Architectures**: Mixture of Experts (MoE) and other language model components
- **Clean Implementation**: Well-documented, modular code following PyTorch best practices
- **Easy Integration**: Simple APIs for incorporating architectures into your projects

## Installation

### From source

```bash
git clone https://github.com/your-username/torch-archs.git
cd torch-archs
pip install -e .
```

### Using uv (recommended)

```bash
uv add torch-archs
```

## Requirements

- Python >= 3.11
- PyTorch >= 2.4

## Usage

### Vision Architectures

```python
from torch_archs.vision.vit import Patchify2D
import torch

# Create a patch extraction layer
patchify = Patchify2D(patch_size=16, flatten_sequence=True)

# Input image tensor (batch_size=1, channels=3, height=224, width=224)
x = torch.randn(1, 3, 224, 224)
patches = patchify(x)
print(patches.shape)  # Output shape will depend on implementation
```

### Language Architectures

```python
from torch_archs.language import moe
# Implementation coming soon
```

## Architecture Components

### Vision (`torch_archs.vision`)

- **`Patchify2D`**: Extracts non-overlapping patches from 2D images for Vision Transformer models
  - Configurable patch size
  - Optional sequence flattening
  - Efficient tensor operations

### Language (`torch_archs.language`)

- **Mixture of Experts (MoE)**: Coming soon
- Additional language model components in development

## Project Structure

```
torch-archs/
├── torch_archs/
│   ├── vision/
│   │   └── vit.py          # Vision Transformer components
│   └── language/
│       └── moe.py          # Mixture of Experts components
├── main.py                 # Example usage and demos
├── pyproject.toml          # Project configuration
└── README.md              # This file
```

## Development

### Setting up development environment

```bash
# Clone the repository
git clone https://github.com/your-username/torch-archs.git
cd torch-archs

# Install in development mode
pip install -e .

# Or using uv
uv sync
```

### Running examples

```bash
python main.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

- Follow PyTorch coding conventions
- Add comprehensive docstrings to all public methods
- Include type hints
- Write tests for new architectures
- Update documentation as needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

- [ ] Complete Vision Transformer implementation
- [ ] Implement Mixture of Experts architectures
- [ ] Add more vision architectures (ResNet, EfficientNet, etc.)
- [ ] Add more language architectures (Transformer, BERT variants, etc.)
- [ ] Comprehensive test suite
- [ ] Performance benchmarks
- [ ] Pre-trained model weights

## Citation

If you use this library in your research, please cite:

```bibtex
@software{torch_archs,
  title = {torch-archs: PyTorch Vision and Language Architectures},
  author = {Javier Cervera Cordero},
  year = {2025},
  url = {https://github.com/javi22020/torch-archs}
}
```

## Acknowledgments

- PyTorch team for the excellent deep learning framework
- The research community for developing these architectures
- Contributors to this project