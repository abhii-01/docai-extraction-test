"""
Vision LLM utilities for flowchart and diagram description
"""

import os
import base64
from typing import Dict, Optional
from dotenv import load_dotenv
from PIL import Image
import io


def describe_image_with_llm(
    image_bytes: bytes,
    prompt: str = "Describe this flowchart or diagram in detail.",
    image_type: str = "flowchart"
) -> str:
    """
    Get description of an image using Vision LLM
    
    Args:
        image_bytes: Image data as bytes
        prompt: Custom prompt for the vision model
        image_type: Type of image (flowchart, diagram, etc.)
        
    Returns:
        Text description of the image
    """
    load_dotenv()
    
    provider = os.getenv("LLM_PROVIDER", "openai")
    
    if provider == "openai":
        return _describe_with_openai_vision(image_bytes, prompt, image_type)
    else:
        return _describe_with_anthropic_vision(image_bytes, prompt, image_type)


def _describe_with_openai_vision(
    image_bytes: bytes,
    prompt: str,
    image_type: str
) -> str:
    """Describe image using GPT-4 Vision"""
    from openai import OpenAI
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in .env file")
    
    client = OpenAI(api_key=api_key)
    
    # Encode image to base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    # Build enhanced prompt
    enhanced_prompt = _build_vision_prompt(prompt, image_type)
    
    response = client.chat.completions.create(
        model="gpt-4o",  # GPT-4 with vision
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": enhanced_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=500,
        temperature=0.3
    )
    
    return response.choices[0].message.content.strip()


def _describe_with_anthropic_vision(
    image_bytes: bytes,
    prompt: str,
    image_type: str
) -> str:
    """Describe image using Claude 3.5 Sonnet Vision"""
    from anthropic import Anthropic
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in .env file")
    
    client = Anthropic(api_key=api_key)
    
    # Encode image to base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    # Determine media type
    media_type = "image/png"  # Assume PNG, adjust if needed
    
    enhanced_prompt = _build_vision_prompt(prompt, image_type)
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        temperature=0.3,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": enhanced_prompt
                    }
                ]
            }
        ]
    )
    
    return response.content[0].text.strip()


def _build_vision_prompt(base_prompt: str, image_type: str) -> str:
    """Build enhanced prompt for vision models"""
    
    type_specific = {
        "flowchart": """
This is a flowchart. Please describe:
1. The process flow from start to end
2. Key decision points and branches
3. Main steps in logical order
4. Overall purpose of the flow
""",
        "diagram": """
This is a diagram. Please describe:
1. Main components and their relationships
2. Labels and annotations
3. Overall structure and organization
4. Key concepts being illustrated
""",
        "chart": """
This is a chart/graph. Please describe:
1. Type of chart (bar, line, pie, etc.)
2. Axes labels and data ranges
3. Key trends or patterns
4. Main insights from the data
""",
        "table": """
This is a table. Please describe:
1. Column headers and row labels
2. Key data points
3. Patterns or trends in the data
4. Overall purpose of the table
"""
    }
    
    enhanced = base_prompt + "\n\n"
    enhanced += type_specific.get(image_type, "Describe this image in detail.")
    enhanced += "\n\nProvide a clear narrative description suitable for someone who cannot see the image."
    
    return enhanced


def extract_image_from_pdf(
    pdf_path: str,
    page_num: int,
    bbox: Dict[str, float]
) -> bytes:
    """
    Extract image region from PDF page
    
    Args:
        pdf_path: Path to PDF file
        page_num: Page number (0-indexed)
        bbox: Bounding box dict with keys: x_min, y_min, x_max, y_max (normalized 0-1)
        
    Returns:
        Image bytes (PNG format)
    """
    from pdf2image import convert_from_path
    
    # Convert PDF page to image
    images = convert_from_path(
        pdf_path,
        first_page=page_num + 1,
        last_page=page_num + 1,
        dpi=200
    )
    
    if not images:
        raise ValueError(f"Could not extract page {page_num} from PDF")
    
    page_image = images[0]
    
    # Calculate pixel coordinates from normalized bbox
    width, height = page_image.size
    x_min = int(bbox['x_min'] * width)
    y_min = int(bbox['y_min'] * height)
    x_max = int(bbox['x_max'] * width)
    y_max = int(bbox['y_max'] * height)
    
    # Crop image
    cropped = page_image.crop((x_min, y_min, x_max, y_max))
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    cropped.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.read()


def is_likely_diagram(
    image_bbox: Dict[str, float],
    page_text: str = ""
) -> bool:
    """
    Heuristic to determine if an image is likely a diagram/flowchart
    vs a photograph or decorative image
    
    Args:
        image_bbox: Bounding box of the image
        page_text: Text content near the image
        
    Returns:
        True if likely a diagram/flowchart
    """
    # Check if image is large enough (diagrams are usually significant)
    width = image_bbox['x_max'] - image_bbox['x_min']
    height = image_bbox['y_max'] - image_bbox['y_min']
    area = width * height
    
    if area < 0.05:  # Less than 5% of page - likely decorative
        return False
    
    # Check for diagram keywords in nearby text
    diagram_keywords = [
        'figure', 'diagram', 'flowchart', 'flow chart',
        'chart', 'graph', 'illustration', 'process',
        'step', 'fig.', 'algorithm'
    ]
    
    if page_text:
        text_lower = page_text.lower()
        if any(keyword in text_lower for keyword in diagram_keywords):
            return True
    
    # Default: assume it's a diagram if reasonably sized
    return area >= 0.05

