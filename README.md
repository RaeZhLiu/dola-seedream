# dola-seedream

Generate high-quality images from text prompts using BytePlus Seedream models. This project provides a robust Command Line Interface (CLI) and Python API to interact with Seedream 4.0, 4.5, and 5.0-lite models.

## Overview

dola-seedream simplifies the process of creating AI-generated artwork. Whether you need quick visualizations, high-detailed art, or batch generation, this tool wraps the complex API interactions into simple commands.

### Key Features

*   **Multi-Model Support**: Access to Seedream 4.0 (Fast), 4.5 (Detailed), and 5.0-lite (Creative).
*   **High Resolution**: Support for 1K, 2K, 3K, and 4K resolutions.
*   **Batch Generation**: Generate sequential images (up to 15) in a single request.
*   **Format Control**: Support for PNG and JPEG output formats (Version 5.0-lite specific).
*   **Image-to-Image**: Use reference images to guide generation.
*   **Reproducibility**: Control generation with a fixed random seed.

## Model Comparison

| Version | Resolution Support | Output Formats | Best For |
| :--- | :--- | :--- | :--- |
| **4.0** | 1K, 2K, 4K | JPEG | Quick daily generation, simple scenes, fast prototyping. |
| **4.5** | 2K, 4K | JPEG | Complex scenes requiring rich details and better style reproduction. |
| **5.0-lite** | 2K, 3K | JPEG, PNG | Professional grade quality, highest creative expression, and lossless (PNG) output. |

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/RaeZhLiu/dola-seedream.git
cd dola-seedream
```

### 2. Install Dependencies

Ensure you have Python 3.8+ installed.

```bash
pip install httpx
```

### 3. Configure Environment

You must provide your BytePlus API Key via an environment variable.

```bash
export ARK_DOLA_API_KEY="your-api-key-here"
```

## CLI Usage

The project includes a powerful CLI script at `scripts/seedream_image_generate.py`.

### Basic Example

Generate a simple image using the default model (5.0-lite):

```bash
python3 scripts/seedream_image_generate.py -p "A cyberpunk city at night with neon lights"
```

### Advanced Examples

**Using Version 4.5 with 4K resolution:**

```bash
python3 scripts/seedream_image_generate.py -p "A majestic mountain landscape" -v 4.5 -s 4K
```

**Batch Generation (Create 5 variations):**

```bash
python3 scripts/seedream_image_generate.py -p "Character design sheet" --group --max-images 5
```

**Generating PNG images (5.0-lite only) and without watermark:**

```bash
python3 scripts/seedream_image_generate.py -p "Logo of a new startup named 'Luminos'" -v 5.0-lite --output-format png --no-watermark
```

### Parameters Reference

| Argument | Shortcut | Default | Description |
| :--- | :--- | :--- | :--- |
| `--prompt` | `-p` | **Required** | The text description of the image to generate. |
| `--version` | `-v` | `5.0-lite` | Model version to use. Choices: `4.0`, `4.5`, `5.0-lite`, `5.0`. |
| `--size` | `-s` | `2K` | Image resolution. Accepts presets like `1K`, `2K`, `3K`, `4K` or dimensions `WxH`. |
| `--image` | `-i` | `None` | URL for a single reference image (Image-to-Image). |
| `--images` | - | `None` | Space-separated URLs for multiple reference images. |
| `--group` | `-g` | `False` | Enable batch image generation mode. |
| `--max-images` | - | `15` | Maximum number of images to generate in batch mode (1-15). |
| `--output-format` | - | `jpeg` | Output file format. Choices: `png`, `jpeg`. **(Only for 5.0-lite)**. |
| `--response-format`| - | `url` | Return format. Choices: `url` (download link) or `b64_json` (base64 data). |
| `--prompt-mode` | - | `None` | Optimization mode. `fast` (4.0 only) or `standard`. |
| `--timeout` | `-t` | `1200` | API request timeout in seconds. |
| `--no-watermark` | - | `False` | If set, disables the watermark on generated images. |
| `--stream` | - | `False` | Enable server-side streaming (non-blocking). |

## Python API Usage

You can import the core logic directly into your Python asyncio projects.

```python
import asyncio
from scripts.seedream_image_generate import seedream_generate

async def generate_art():
    # Define the task
    tasks = [{
        "prompt": "An astronaut riding a horse on Mars, photorealistic",
        "size": "2K",
        "output_format": "png",  # Only for 5.0-lite
        "watermark": True
    }]

    # Call the API
    result = await seedream_generate(
        tasks=tasks,
        version="5.0-lite",
        timeout=60
    )

    if result["status"] == "success":
        for success_item in result["success_list"]:
            for name, url in success_item.items():
                print(f"Generated {name}: {url}")
    else:
        print(f"Error: {result['error_list']}")

if __name__ == "__main__":
    asyncio.run(generate_art())
```

## License

This project is licensed under the **MIT License**.

## Disclaimer

This tool interacts with BytePlus Seedream API services. Please ensure your usage complies with BytePlus Terms of Service and applicable laws and regulations.
