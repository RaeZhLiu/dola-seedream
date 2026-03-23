---
name: dola-seedream
description: Generate high-quality images from text prompts using BytePlus Seedream models. Supports multiple artistic styles and aspect ratios. Use this skill when users want to create images from text descriptions, generate artwork in various styles, create visual content for creative projects, or need AI-powered image generation capabilities.
license: MIT
tags: ["image-generation", "seedream", "dola", "byteplus", "ai-art", "text-to-image", "image-to-image"]
---

# dola-seedream

## Description

Generate high-quality images from text prompts using BytePlus Seedream models. This skill provides access to three powerful Seedream model versions (4.0, 4.5, and 5.0), each offering unique capabilities for different use cases.

## When to Use This Skill

Use this skill when:

- Users want to create images from text descriptions
- Users need to generate artwork in various artistic styles
- Users want to create visual content for creative projects
- Users need AI-powered image generation capabilities
- Users want to convert reference images to different styles
- Users need to generate multiple images in batch
- Users require high-quality, professional-looking images

## Model Versions

| Version  | Model Name          | Release Date  | Recommendation | Best For                                           |
| -------- | ------------------- | ------------- | -------------- | -------------------------------------------------- |
| 4.0      | seedream-4-0-250828 | August 2025   | ⭐⭐⭐         | Daily use, supports 1K/2K/4K and Fast prompt mode |
| 4.5      | seedream-4-5-251128 | November 2025 | ⭐⭐⭐⭐       | Detail-oriented for complex scenes, supports 2K/4K |
| 5.0-lite | seedream-5-0-260128 | January 2026  | ⭐⭐⭐⭐⭐     | Highest quality with breakthrough creative expression, supports 2K/3K and PNG/JPEG output |
| 5.0      | seedream-5-0-260128 | January 2026  | ⭐⭐⭐⭐⭐     | Alias for 5.0-lite, latest and most powerful version |

### Model Capabilities Comparison

| Feature | 5.0-lite | 4.5 | 4.0 |
|---------|----------|-----|-----|
| **Text-to-Image** | ✅ | ✅ | ✅ |
| **Single Image-to-Image** | ✅ | ✅ | ✅ |
| **Multi-Image Fusion (up to 14)** | ✅ | ✅ | ✅ |
| **Batch Generation (up to 15)** | ✅ | ✅ | ✅ |
| **Streaming Output** | ✅ | ✅ | ✅ |
| **Resolutions** | 2K, 3K | 2K, 4K | 1K, 2K, 4K |
| **Output Formats** | PNG, JPEG | JPEG | JPEG |
| **Prompt Modes** | standard | standard | standard, fast |
| **Pixel Range (width×height)** | 3.68M - 10.4M | 3.68M - 16.7M | 0.92M - 16.7M |
| **Max Images/Minute** | 500 | 500 | 500 |

## Features

- **Text-to-Image**: Generate images from detailed text descriptions
- **Image-to-Image**: Transform reference images (up to 14) into new creations
- **Batch Generation**: Create multiple related images in a single request (up to 15)
- **Flexible Resolution**: Support for resolution presets (1K, 2K, 3K, 4K) or custom sizes
- **Multiple Versions**: Choose from 4.0, 4.5, or 5.0-lite models
- **Watermark Control**: Option to disable watermarks
- **Output Formats**: PNG and JPEG formats (5.0-lite only)
- **Prompt Optimization**: Choose between `standard` and `fast` (for 4.0) modes

## Installation & Setup

### Prerequisites

```bash
# Required: API Key configuration (Get from BytePlus Console)
export ARK_DOLA_API_KEY="your-api-key-here"
```

## Usage

### Command Line

```bash
python scripts/seedream_image_generate.py -p "A cute kitten playing in a garden" --version 5.0
```

## Command Line Options

| Option              | Shortcut | Description                                     | Default      |
| ------------------- | -------- | ----------------------------------------------- | ------------ |
| `--prompt`          | `-p`     | Image description text (required)               | -            |
| `--version`         | `-v`     | Version selection: `4.0`, `4.5`, `5.0-lite`     | `5.0-lite`   |
| `--size`            | `-s`     | Image dimensions (1K/2K/3K/4K or WxH)           | `2K`         |
| `--image`           | `-i`     | Single reference image URL                      | -            |
| `--images`          | -        | Multiple reference image URLs (space separated) | -            |
| `--group`           | `-g`     | Enable batch image generation                   | `false`      |
| `--max-images`      | -        | Maximum images for batch generation             | `15`         |
| `--output-format`   | -        | Output format: `png` or `jpeg` (5.0-lite only)  | `jpeg`       |
| `--response-format` | -        | Response format: `url` or `b64_json`            | `url`        |
| `--prompt-mode`     | -        | Prompt optimization mode: `standard` or `fast`  | `standard`   |
| `--timeout`         | `-t`     | Timeout in seconds                              | `1200`       |
| `--no-watermark`    | -        | Disable watermark                               | `false`      |
| `--stream`          | -        | Enable server-side streaming                    | `false`      |

## Python API Usage

```python
import asyncio
from scripts.seedream_image_generate import seedream_generate

async def main():
    # Generate image using 5.0 version
    result = await seedream_generate([
        {
            "prompt": "A futuristic city landscape",
            "size": "2048x2048",
            "output_format": "png"
        }
    ], version="5.0")

    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Version Selection Guide

### Choose 4.0 if:

- You need quick daily generation
- Quality requirements are not extremely high
- You need faster generation speed
- Simple scenes and styles

### Choose 4.5 if:

- You want richer details
- You're working with complex scenes
- You need better style reproduction
- You have moderate quality requirements

### Choose 5.0 (Recommended) if:

- You want the highest quality
- You need breakthrough creative expression
- You have extreme detail requirements
- **You need tools parameter (like web search)** ⭐
- **You need custom output format (png/jpeg)** ⭐
- Important projects and work

**When in doubt, use 5.0!** ⭐

## Prompt Engineering Tips

### Basic Prompt Structure

```
[Subject Description] + [Style/Art Movement] + [Lighting/Atmosphere] + [Quality/Resolution]
```

### Advanced Prompts (Optimized for 5.0)

```
[Subject Description], [Creative Style/Art Movement], [Unique Perspective/Composition], [Special Lighting/Atmosphere], [Emphasizing 5.0 creative expression]
```

## Parameter Support by Version

| Parameter                           | Seedream 4.0 | Seedream 4.5 | Seedream 5.0 | Description                        |
| ----------------------------------- | ------------ | ------------ | ------------ | ---------------------------------- |
| **model** (required)                | ✅           | ✅           | ✅           | Model ID (seedream-x-x-xxxxxx)   |
| **prompt** (required)               | ✅           | ✅           | ✅           | Text prompt (recommended ≤ 600 words) |
| **image**                           | ✅           | ✅           | ✅           | Reference image(s) (URL or Base64, up to 14) |
| **size**                            | ✅           | ✅           | ✅           | Image dimensions (preset: 1K/2K/3K/4K or WxH) |
| **sequential_image_generation**     | ✅           | ✅           | ✅           | Batch generation: "auto" or "disabled" |
| **sequential_image_generation_options** | ✅       | ✅           | ✅           | Batch config: {max_images: 1-15} |
| **response_format**                 | ✅           | ✅           | ✅           | Response format: "url" (24h valid) or "b64_json" |
| **watermark**                       | ✅           | ✅           | ✅           | Watermark: true (default) or false |
| **stream**                          | ✅           | ✅           | ✅           | Streaming output: true or false (default) |
| **optimize_prompt_options**         | ✅           | ✅           | ✅           | Prompt optimization: {mode: "standard"} |
| **output_format**                   | ❌           | ❌           | **✅**       | Output format: "png" or "jpeg" (5.0-lite only) |

### Important Notes

- **Reference Images**: Up to 14 images supported. Reference images + generated images ≤ 15.
- **Image Formats**: JPEG, PNG (5.0-lite also supports WEBP, BMP, TIFF, GIF)
- **Image Size**: Max 10MB, ≤ 6000×6000 pixels, aspect ratio [1/16, 16]
- **Prompt Length**: Recommended ≤ 600 English words to avoid detail loss
- **URL Validity**: Generated URLs are valid for 24 hours
- **Token Calculation**: output_tokens = sum(width × height) / 256 (rounded down)


## FAQ

### Q: What's the difference between the versions?

A: 
- **4.0**: Quick daily use, supports 1K/2K/4K resolution and fast prompt mode
- **4.5**: Improved detail for complex scenes, supports 2K/4K resolution
- **5.0-lite/5.0**: Highest quality with breakthrough creative expression, supports 2K/3K resolution and PNG/JPEG output

**When in doubt, use 5.0!** ⭐

### Q: How long are generated URLs valid?

A: URLs are valid for 24 hours. Please download and save your images promptly.

### Q: What image formats are supported for references?

A: 
- 4.0/4.5: JPEG, PNG
- 5.0-lite: JPEG, PNG, WEBP, BMP, TIFF, GIF
- All versions support URL or Base64 encoding

### Q: Can I use multiple versions in one call?

A: Currently, only one version per call. For comparisons, make separate calls for different versions.

### Q: What's the maximum number of reference images?

A: Up to 14 reference images. Note: reference images + generated images ≤ 15.

### Q: What's the maximum image size for references?

A: Max 10MB, ≤ 6000×6000 pixels, aspect ratio between 1/16 and 16.

### Q: How are tokens calculated?

A: output_tokens = sum(width × height) / 256 (rounded down). total_tokens = output_tokens.

### Q: What's the maximum generation rate?

A: All versions support up to 500 images per minute.

### Q: Can I disable the watermark?

A: Yes, set `watermark: false` to disable the "AI generated" watermark.

### Q: What's the difference between "standard" and "fast" prompt modes?

A: 
- "standard": Higher quality, longer generation time (default for all versions)
- "fast": Faster but lower quality (only available for 4.0)


## License

This skill is licensed under the Apache License 2.0. See the LICENSE file for details.

## Notice

Please comply with BytePlus's terms of service and relevant laws and regulations when using this skill.
