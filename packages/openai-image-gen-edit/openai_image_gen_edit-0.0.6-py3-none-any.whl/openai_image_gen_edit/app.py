import base64
import os
import uuid
from pathlib import Path
from typing import Annotated
import tempfile
import io

from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent
from openai import OpenAI
from pydantic import Field

mcp = FastMCP("openai-image-generation")
client = OpenAI()
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-image-1")


@mcp.tool(
    description="Generate an image with OpenAI model and display the image."
)
def generate_image(
    prompt: Annotated[str, Field(description="A text description of the desired image(s).")],
    background: Annotated[
        str | None,
        Field(
            description="Allows to set transparency for the background of the generated image(s). "
            "This parameter is only supported for `gpt-image-1`. "
            "Must be one of `transparent`, `opaque` or `auto` (default value). "
            "When `auto` is used, the model will automatically determine the best background for the image.",
        ),
    ] = None,
    n: Annotated[
        int | None,
        Field(
            description="The number of images to generate. Must be between 1 and 10. For `dall-e-3`, "
            "only `n=1` is supported.",
        ),
    ] = 1,
    quality: Annotated[
        str | None,
        Field(
            description="""The quality of the image that will be generated.

- `auto` (default value) will automatically select the best quality for the given model.
- `high`, `medium` and `low` are supported for `gpt-image-1`.
- `hd` and `standard` are supported for `dall-e-3`.
- `standard` is the only option for `dall-e-2`.
"""
        ),
    ] = "auto",
    model: Annotated[
        str,
        Field(
            description='Should be one of ["dall-e-2", "dall-e-3", "gpt-image-1"]',
        ),
    ] = DEFAULT_MODEL,
    output_format: Annotated[
        str,
        Field(
            description="The format in which the generated images are returned. "
            "This parameter is only supported for `gpt-image-1`. Must be one of `png`, `jpeg`, or `webp`.",
        ),
    ] = "png",
    size: Annotated[
        str,
        Field(
            description="The size of the generated images. "
            "Must be one of `1024x1024`, `1536x1024` (landscape), "
            "`1024x1536` (portrait), or `auto` (default value) for `gpt-image-1`, "
            "one of `256x256`, `512x512`, or `1024x1024` for `dall-e-2`, "
            "and one of `1024x1024`, `1792x1024`, or `1024x1792` for `dall-e-3`.",
        ),
    ] = "auto",
) -> ImageContent | list[ImageContent] | dict:
    response = client.images.generate(
        prompt=prompt,
        background=background,
        n=n,
        quality=quality,
        model=model,
        output_format=output_format,
        size=size,
    )
    if not response.data:
        return {"generated_images": [], "message": "No images generated"}

    case_id = uuid.uuid4().hex
    result = []
    for count, image in enumerate(response.data):
        image_base64 = image.b64_json
        result.append(
            ImageContent(
                type="image",
                data=image_base64,
                mimeType=f"image/{output_format}",
                annotations={"case_id": case_id, "count": count, "prompt": prompt},
            )
        )
    if len(result) == 1:
        result = result[0]
    return result


# TODO: Edit, inpainting,


@mcp.tool(
    description="Edit an image from base64-encoded string using an OpenAI model and return the edited image."
    "The client is expected to provide base64-encoded data as a string."
)
def edit_image(
    prompt: Annotated[
        str,
        Field(
            description="The prompt to generate the image.",
        ),
    ],
    image_data: Annotated[
        str,
        Field(
            description="Base64-encoded image data for the image we want edit. The value of this field is in the `source.data` field when `type` is `image` or `result` field when the type is`image_generation_call`.",
        ),
    ],
    image_type: Annotated[
        str,
        Field(
            description="The type of image sent. Must be a mime-type (e.g. 'image/png', 'image/jpeg')",
        ),
    ],
    mask_data: Annotated[
        str | None,
        Field(
            description="Base64-encoded image data for a mask to apply to the image.",
        ),
    ] = None,
    background: Annotated[
        str | None,
        Field(
            description="Allows to set transparency for the background of the generated image(s). "
            "This parameter is only supported for `gpt-image-1`. "
            "Must be one of `transparent`, `opaque` or `auto` (default value). "
            "When `auto` is used, the model will automatically determine the best background for the image.",
        ),
    ] = None,
    quality: Annotated[
        str | None,
        Field(
            description="""The quality of the image that will be generated.

- `auto` (default value) will automatically select the best quality for the given model.
- `high`, `medium` and `low` are supported for `gpt-image-1`.
- `hd` and `standard` are supported for `dall-e-3`.
- `standard` is the only option for `dall-e-2`.
"""
        ),
    ] = "auto",
    model: Annotated[
        str,
        Field(
            description='Should be one of ["dall-e-2", "dall-e-3", "gpt-image-1"]',
        ),
    ] = DEFAULT_MODEL,
    output_format: Annotated[
        str,
        Field(
            description="The format in which the generated images are returned. "
            "This parameter is only supported for `gpt-image-1`. Must be one of `png`, `jpeg`, or `webp`.",
        ),
    ] = "png",
    size: Annotated[
        str,
        Field(
            description="The size of the generated images. "
            "Must be one of `1024x1024`, `1536x1024` (landscape), "
            "`1024x1536` (portrait), or `auto` (default value) for `gpt-image-1`, "
            "one of `256x256`, `512x512`, or `1024x1024` for `dall-e-2`, "
            "and one of `1024x1024`, `1792x1024`, or `1024x1792` for `dall-e-3`.",
        ),
    ] = "auto",
) -> ImageContent | dict:
    def _b64_to_tempfile(b64data: str, ext: str) -> tempfile.NamedTemporaryFile:
        temp = tempfile.NamedTemporaryFile(delete=True, suffix=ext)
        temp.write(base64.b64decode(b64data))
        temp.seek(0)
        return temp

    mime_to_ext = {
        "image/png": ".png",
        "image/jpeg": ".jpeg",
        "image/jpg": ".jpg",
        "image/webp": ".webp",
    }
    image_file = None
    mask_file = None
    try:
        ext = mime_to_ext.get(image_type, ".img")
        image_file = _b64_to_tempfile(image_data, ext)
        if mask_data:
            mask_file = _b64_to_tempfile(mask_data, ".png")
        response = client.images.edit(
            image=image_file,
            prompt=prompt,
            background=background,
            mask=mask_file,
            quality=quality,
            model=model,
            response_format=output_format,
            size=size,
        )
        if not response.data:
            return {"generated_images": [], "message": "No images generated"}
        case_id = uuid.uuid4().hex
        image_base64 = response.data[0].b64_json
        return ImageContent(
            type="image",
            data=image_base64,
            mimeType=f"image/{output_format}",
            annotations={"case_id": case_id, "prompt": prompt},
        )
    finally:
        if image_file:
            try:
                image_file.close()
            except Exception:
                pass
        if mask_file:
            try:
                mask_file.close()
            except Exception:
                pass
