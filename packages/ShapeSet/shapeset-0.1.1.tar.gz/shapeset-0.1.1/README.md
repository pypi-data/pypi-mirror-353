# ShapeSet

[![ShapeSet PyPI Publish](https://github.com/enugalamanideepreddy/ShapeSet/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/enugalamanideepreddy/ShapeSet/actions/workflows/pypi-publish.yml)

SHapeSet is a package designed to simplify and streamline your workflow for [briefly describe the main purpose or functionality of your package, e.g., "data processing", "API integration", etc.].

## Features

- Easy to use
- Lightweight and efficient
- Flexible data generation
- Scalable in data size

## Installation

```bash
pip install ShapeSet
```
<!-- _Replace with the correct command for your package manager._ -->

## Usage

```python
from ShapeSet import dataset

# Example usage
dataset.generate(
        class_names,
        num_train,
        num_val,
        image_size,
        output_dir,
        seed
)
```

## Note

Therefore, the minimum allowable image size is **80x80 pixels**.  
If you use a smaller size, you may get a `ValueError: empty range for randrange()`.

**Recommendation:**  
Use `image_size >= 80` in your tests and dataset generation.

<!-- _Replace with a relevant code snippet for your package._ -->

<!-- ## Documentation

See the [official documentation](link-to-docs) for detailed usage and API reference. -->

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE).
