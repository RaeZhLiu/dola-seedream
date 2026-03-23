#!/usr/bin/env python3
# MIT License
# Copyright (c) 2026
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
dola-seedream - Generate high-quality images from text prompts
using BytePlus Seedream models (4.0, 4.5, and 5.0).

Documentation: https://docs.byteplus.com/en/docs/ModelArk/1399008
"""

import argparse
import asyncio
import json
import os
import sys
import logging
from typing import Dict, List, Tuple, Optional

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Configuration constants
API_KEY = os.getenv("ARK_DOLA_API_KEY")
API_BASE = os.getenv(
    "ARK_DOLA_API_BASE", 
    "https://ark.ap-southeast.bytepluses.com/api/v3"
).rstrip("/")

# Model names for each version (official model IDs from BytePlus documentation)
MODELS = {
    "4.0": "seedream-4-0-250828",
    "4.5": "seedream-4-5-251128",
    "5.0-lite": "seedream-5-0-260128",
    "5.0": "seedream-5-0-260128",
}

# Resolution presets (from official documentation)
RESOLUTION_PRESETS = {
    "1K": "1024x1024",
    "2K": "2048x2048",
    "3K": "3072x3072",
    "4K": "4096x4096",
}

# Pixel range limits per version (width * height)
# From official documentation:
# - 5.0-lite: [3,686,400, 10,404,496]
# - 4.5: [3,686,400, 16,777,216]
# - 4.0: [921,600, 16,777,216]
PIXEL_RANGES = {
    "4.0": (921600, 16777216),
    "4.5": (3686400, 16777216),
    "5.0-lite": (3686400, 10404496),
    "5.0": (3686400, 10404496),
}

# Supported output formats per version
OUTPUT_FORMATS = {
    "4.0": ["jpeg"],
    "4.5": ["jpeg"],
    "5.0-lite": ["png", "jpeg"],
    "5.0": ["png", "jpeg"],
}

# Supported prompt modes per version
PROMPT_MODES = {
    "4.0": ["standard", "fast"],
    "4.5": ["standard"],
    "5.0-lite": ["standard"],
    "5.0": ["standard"],
}

# Supported resolutions per version (presets)
SUPPORTED_RESOLUTIONS = {
    "4.0": ["1K", "2K", "4K"],
    "4.5": ["2K", "4K"],
    "5.0-lite": ["2K", "3K"],
    "5.0": ["2K", "3K"],
}

# Supported fields per version (based on official documentation)
SUPPORTED_FIELDS = {
    "4.0": ["size", "response_format", "watermark", "image", "sequential_image_generation", "sequential_image_generation_options", "stream", "optimize_prompt_options"],
    "4.5": ["size", "response_format", "watermark", "image", "sequential_image_generation", "sequential_image_generation_options", "stream", "optimize_prompt_options"],
    "5.0-lite": ["size", "response_format", "watermark", "image", "sequential_image_generation", "sequential_image_generation_options", "stream", "optimize_prompt_options", "output_format"],
    "5.0": ["size", "response_format", "watermark", "image", "sequential_image_generation", "sequential_image_generation_options", "stream", "optimize_prompt_options", "output_format"],
}

# Version descriptions (from official documentation)
VERSION_DESCRIPTIONS = {
    "4.0": "Seedream 4.0 - Stable for daily use, supports 1K/2K/4K resolution and fast prompt mode.",
    "4.5": "Seedream 4.5 - Improved detail for complex scenes, supports 2K/4K resolution.",
    "5.0-lite": "Seedream 5.0-lite - Highest quality with breakthrough creative expression, supports 2K/3K resolution and PNG/JPEG output.",
    "5.0": "Seedream 5.0 (alias for 5.0-lite) - Latest and most powerful version.",
}

def _parse_size(size_str: str) -> Tuple[int, int]:
    """
    Parse size string into width and height.
    Supports: "2048x2048", "2K", "3K", "4K", etc.
    """
    size_str = size_str.strip().upper()
    
    # Check if it's a preset
    if size_str in RESOLUTION_PRESETS:
        size_str = RESOLUTION_PRESETS[size_str]
    
    # Parse WxH format
    if "x" in size_str:
        try:
            w, h = size_str.split("x", 1)
            return int(w.strip()), int(h.strip())
        except ValueError:
            raise ValueError(f"Invalid size format: {size_str}. Expected format: '2048x2048' or '2K'")
    
    raise ValueError(f"Invalid size: {size_str}. Expected format: '2048x2048' or '2K'")

def _validate_size(size_str: str, version: str) -> str:
    """
    Validate and normalize size for a given version.
    Returns normalized size string (WxH).
    """
    width, height = _parse_size(size_str)
    min_pixels, max_pixels = PIXEL_RANGES.get(version, (0, float('inf')))
    total_pixels = width * height
    
    if total_pixels < min_pixels:
        raise ValueError(
            f"Size {width}x{height} ({total_pixels:,} pixels) too small for {version}. "
            f"Minimum: {min_pixels:,} pixels."
        )
    if total_pixels > max_pixels:
        raise ValueError(
            f"Size {width}x{height} ({total_pixels:,} pixels) too large for {version}. "
            f"Maximum: {max_pixels:,} pixels."
        )
    
    return f"{width}x{height}"

def _validate_output_format(output_format: str, version: str) -> str:
    """Validate output format for a given version."""
    supported = OUTPUT_FORMATS.get(version, ["jpeg"])
    if output_format not in supported:
        raise ValueError(
            f"Output format '{output_format}' not supported for {version}. "
            f"Supported formats: {', '.join(supported)}"
        )
    return output_format

def _validate_prompt_mode(prompt_mode: str, version: str) -> str:
    """Validate prompt mode for a given version."""
    supported = PROMPT_MODES.get(version, ["standard"])
    if prompt_mode not in supported:
        raise ValueError(
            f"Prompt mode '{prompt_mode}' not supported for {version}. "
            f"Supported modes: {', '.join(supported)}"
        )
    return prompt_mode

def _validate_max_images(max_images: int) -> int:
    """Validate max_images parameter (1-15)."""
    if not (1 <= max_images <= 15):
        raise ValueError(f"max_images must be between 1 and 15, got {max_images}")
    return max_images

def _validate_image_count(image_count: int, max_images: int) -> None:
    """Validate that reference images + generated images <= 15."""
    if image_count + max_images > 15:
        raise ValueError(
            f"Reference images ({image_count}) + generated images ({max_images}) = {image_count + max_images}, "
            f"which exceeds the limit of 15."
        )

def _get_headers() -> dict:
    if not API_KEY:
        raise ValueError("Missing ARK_DOLA_API_KEY environment variable.")
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

def _build_request_body(item: dict, model_name: str, version: str) -> dict:
    """
    Build and validate the request body according to official BytePlus documentation.
    """
    # Validate required prompt
    prompt = item.get("prompt", "")
    if not prompt:
        raise ValueError("Prompt is required")
    
    body = {
        "model": model_name,
        "prompt": prompt,
    }

    # Validate and add size
    if "size" in item and item["size"]:
        normalized_size = _validate_size(item["size"], version)
        body["size"] = normalized_size

    # Add response format
    if "response_format" in item and item["response_format"]:
        body["response_format"] = item["response_format"]

    # Add watermark
    if "watermark" in item and item["watermark"] is not None:
        body["watermark"] = bool(item["watermark"])

    # Add stream
    if "stream" in item and item["stream"]:
        body["stream"] = True

    # Add reference image(s) - support up to 14 images
    if "image" in item and item["image"]:
        images = item["image"]
        if isinstance(images, list):
            if len(images) > 14:
                raise ValueError(f"Maximum 14 reference images allowed, got {len(images)}")
            body["image"] = images
        else:
            body["image"] = images

    # Validate and add output format (5.0-lite only)
    if "output_format" in item and item["output_format"]:
        if version in ["5.0-lite", "5.0"]:
            validated_format = _validate_output_format(item["output_format"], version)
            body["output_format"] = validated_format

    # Batch generation
    if item.get("sequential_image_generation") == "auto":
        body["sequential_image_generation"] = "auto"
        
        max_images = item.get("max_images", 15)
        validated_max = _validate_max_images(max_images)
        
        # Check reference images count
        image_count = 0
        if "image" in item and item["image"]:
            images = item["image"]
            image_count = len(images) if isinstance(images, list) else 1
        
        _validate_image_count(image_count, validated_max)
        
        body["sequential_image_generation_options"] = {
            "max_images": validated_max
        }
    else:
        # Default: disabled
        body["sequential_image_generation"] = "disabled"

    # Prompt optimization options
    if "prompt_mode" in item and item["prompt_mode"]:
        validated_mode = _validate_prompt_mode(item["prompt_mode"], version)
        body["optimize_prompt_options"] = {"mode": validated_mode}

    return body

async def _call_image_api(client: httpx.AsyncClient, item: dict, model_name: str, version: str) -> dict:
    url = f"{API_BASE}/images/generations"
    body = _build_request_body(item, model_name, version)
    
    response = await client.post(url, headers=_get_headers(), json=body)
    if response.status_code != 200:
        try:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", response.text)
        except Exception:
            error_msg = response.text
        raise RuntimeError(f"API Error ({response.status_code}): {error_msg}")
    
    return response.json()

async def handle_single_task(
    client: httpx.AsyncClient,
    idx: int,
    item: dict,
    model_name: str,
    version: str,
    semaphore: asyncio.Semaphore
) -> Tuple[List[dict], List[str], List[dict], Optional[dict]]:
    """
    Handle a single image generation task.
    Returns: (success_list, error_list, error_detail_list, usage_info)
    """
    async with semaphore:
        success_list = []
        error_list = []
        error_detail_list = []
        usage_info = None

        try:
            response = await _call_image_api(client, item, model_name, version)

            # Extract usage information if available
            if "usage" in response:
                usage_info = response["usage"]

            if "error" not in response:
                data_list = response.get("data", [])
                for i, image_data in enumerate(data_list):
                    image_name = f"task_{idx}_image_{i}"

                    if "error" in image_data:
                        error_list.append(image_name)
                        error_detail_list.append({"task_idx": idx, "image_name": image_name, "error": image_data.get("error")})
                        continue

                    image_url = image_data.get("url")
                    if image_url:
                        success_list.append({image_name: image_url})
                    else:
                        b64 = image_data.get("b64_json")
                        if b64:
                            output_format = item.get("output_format", "jpeg")
                            mime_type = f"image/{output_format}"
                            success_list.append({image_name: f"data:{mime_type};base64,{b64}"})
                        else:
                            error_list.append(image_name)
                            error_detail_list.append({"task_idx": idx, "image_name": image_name, "error": "missing data (no url/b64)"})
            else:
                error_info = response.get("error", {})
                error_list.append(f"task_{idx}")
                error_detail_list.append({"task_idx": idx, "error": error_info})

        except Exception as e:
            error_list.append(f"task_{idx}")
            error_detail_list.append({"task_idx": idx, "error": str(e)})

        return success_list, error_list, error_detail_list, usage_info

async def seedream_generate(
    tasks: List[dict],
    version: str = "5.0",
    timeout: int = 1200,
    concurrency: int = 5
) -> Dict:
    """
    Main function to generate images using Seedream models.
    
    Args:
        tasks: List of task dictionaries, each containing prompt and parameters
        version: Model version ("4.0", "4.5", "5.0-lite", "5.0")
        timeout: Timeout in seconds for each request
        concurrency: Maximum concurrent requests
    
    Returns:
        Dictionary with results, including success_list, error_list, usage info, etc.
    """
    if version not in MODELS:
        return {
            "status": "error", 
            "error_list": [f"Unsupported version: {version}. Supported versions: {', '.join(MODELS.keys())}"]
        }

    if not API_KEY:
        return {
            "status": "error", 
            "error_list": ["Missing ARK_DOLA_API_KEY environment variable. Please set it with your BytePlus API key."]
        }

    model_name = MODELS[version]
    semaphore = asyncio.Semaphore(concurrency)
    
    async with httpx.AsyncClient(timeout=float(timeout)) as client:
        coroutines = [handle_single_task(client, idx, item, model_name, version, semaphore) for idx, item in enumerate(tasks)]
        results = await asyncio.gather(*coroutines, return_exceptions=True)

    success_list = []
    error_list = []
    error_detail_list = []
    all_usage_info = []

    for res in results:
        if isinstance(res, Exception):
            error_list.append("exception")
            error_detail_list.append({"error": str(res)})
        else:
            s, e, ed, usage = res
            success_list.extend(s)
            error_list.extend(e)
            error_detail_list.extend(ed)
            if usage:
                all_usage_info.append(usage)

    # Aggregate usage information
    total_usage = None
    if all_usage_info:
        total_generated = sum(u.get("generated_images", 0) for u in all_usage_info)
        total_output_tokens = sum(u.get("output_tokens", 0) for u in all_usage_info)
        total_tokens = sum(u.get("total_tokens", 0) for u in all_usage_info)
        total_usage = {
            "generated_images": total_generated,
            "output_tokens": total_output_tokens,
            "total_tokens": total_tokens,
        }

    result = {
        "status": "success" if success_list else "error",
        "success_list": success_list,
        "error_list": error_list,
        "error_detail_list": error_detail_list,
        "model": model_name,
        "version": version,
    }
    
    if total_usage:
        result["usage"] = total_usage

    return result

def main():
    parser = argparse.ArgumentParser(
        description="dola-seedream - Generate images using BytePlus Seedream models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Versions:\n" + "\n".join([f"  {k}: {v}" for k, v in VERSION_DESCRIPTIONS.items()])
    )
    parser.add_argument("--prompt", "-p", help="Image description text")
    parser.add_argument("--version", "-v", choices=list(MODELS.keys()), default="5.0-lite", help="Model version (default 5.0-lite)")
    parser.add_argument("--size", "-s", help="Image dimensions (e.g., 2048x2048 or resolution 1K/2K/3K/4K)")
    parser.add_argument("--image", "-i", help="Reference image URL")
    parser.add_argument("--images", nargs="+", help="Multiple reference image URLs")
    parser.add_argument("--group", "-g", action="store_true", help="Enable batch generation")
    parser.add_argument("--max-images", type=int, default=15, help="Max images for batch (1-15)")
    parser.add_argument("--output-format", choices=["png", "jpeg"], default="jpeg", help="Output format (5.0-lite only)")
    parser.add_argument("--response-format", choices=["url", "b64_json"], default="url", help="Response format")
    parser.add_argument("--prompt-mode", choices=["standard", "fast"], help="Prompt optimization mode (fast only for 4.0)")
    parser.add_argument("--timeout", "-t", type=int, default=1200, help="Timeout in seconds")
    parser.add_argument("--no-watermark", action="store_true", help="Disable watermark")
    parser.add_argument("--stream", action="store_true", help="Enable streaming request (non-blocking server side)")
    
    args = parser.parse_args()

    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    # Set default size based on version (from official documentation)
    size = args.size
    if not size:
        if args.version in ["5.0-lite", "5.0"]:
            size = "2K"  # 5.0-lite supports 2K and 3K
        elif args.version == "4.5":
            size = "2K"  # 4.5 supports 2K and 4K
        elif args.version == "4.0":
            size = "2K"  # 4.0 supports 1K, 2K, and 4K
        else:
            size = "2048x2048"

    task = {
        "prompt": args.prompt,
        "size": size,
        "response_format": args.response_format,
        "watermark": not args.no_watermark,
        "stream": args.stream
    }

    if args.version in ["5.0", "5.0-lite"]:
        task["output_format"] = args.output_format
    
    if args.prompt_mode:
        task["prompt_mode"] = args.prompt_mode
    
    if args.images:
        task["image"] = args.images
    elif args.image:
        task["image"] = args.image

    if args.group:
        task["sequential_image_generation"] = "auto"
        task["max_images"] = max(1, min(15, args.max_images))

    result = asyncio.run(seedream_generate([task], version=args.version, timeout=args.timeout))
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
