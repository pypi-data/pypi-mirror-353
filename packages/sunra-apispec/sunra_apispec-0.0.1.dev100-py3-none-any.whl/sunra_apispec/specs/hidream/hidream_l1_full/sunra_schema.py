# Schema for Text-to-Image generation
from pydantic import BaseModel, Field
from typing import Literal

from sunra_apispec.base.output_schema import ImageOutput


class TextToImageInput(BaseModel):
    """Text to image input for HiDream L1 Full model"""

    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="Text prompt for image generation"
    )
    
    aspect_ratio: Literal["1:1", "2:3", "3:4", "9:16", "3:2", "4:3", "16:9"] = Field(
        "1:1",
        json_schema_extra={"x-sr-order": 401},
        description="Aspect ratio of the generated image"
    )
    
    seed: int = Field(
        default=None,
        json_schema_extra={"x-sr-order": 206},
        description="Random seed for generation. Use -1 for random seed"
    )


class HiDreamL1FullOutput(ImageOutput):
    predict_time: float = Field(
        ...,
        description="Time taken to generate the image",
    )
