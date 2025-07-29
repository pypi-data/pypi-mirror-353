from fastmcp import FastMCP, Image
import io
import httpx
from PIL import Image as PILImage
from mcp_server_youtube_info.util import VideoInfoExtractor
mcp = FastMCP("MCP YouTube Info Server", dependencies=["httpx", "Pillow"])


@mcp.tool()
def youtube_metainfo(video_id: str) -> dict:
    """Retrieve meta info of YouTube video。

    Args:
        video_id (str): YouTube video ID

    Returns:
        dict: Video meta information
    """
    try:
        # Create extractor
        extractor = VideoInfoExtractor()

        # Get video information
        raw_info = extractor.get_video_info(video_id)

        return extractor.format_info(raw_info)
    except Exception as e:
        raise Exception(f"Failed to retrieve metadata: {str(e)}")


@mcp.tool()
def youtube_thumbnail_url(video_id: str) -> str:
    """Retrieve the thumbnail URL of a YouTube video.

    Args:
        video_id (str): YouTube Video ID

    Returns:
        str: Thumbnail URL
    """
    try:
        # Create extractor
        extractor = VideoInfoExtractor()
        # Get video information
        raw_info = extractor.get_video_info(video_id)
        thumbnail_url = raw_info.get('thumbnail')
        if not thumbnail_url:
            raise Exception("Cannot find thumbnail URL")
        return thumbnail_url
    except Exception as e:
        raise Exception(f"Failed to get thumbnail URL: {str(e)}")


@mcp.tool()
def youtube_thumbnail_image(video_id: str) -> Image:
    """
    Retrieve and download the thumbnail of a YouTube video as an Image.

    Args:
        video_id: YouTube Video ID
    Returns:
        Image: Image object containing the thumbnail data
    """
    try:
        # Create extractor
        extractor = VideoInfoExtractor()

        # Get video information
        raw_info = extractor.get_video_info(video_id)
        thumbnail_url = raw_info.get('thumbnail')
        if not thumbnail_url:
            raise Exception("Cannot find thumbnail URL")
    except Exception as e:
        raise Exception(f"Failed to get thumbnail URL: {str(e)}")

    try:
        with httpx.Client() as client:
            response = client.get(thumbnail_url)
            response.raise_for_status()

            image = PILImage.open(io.BytesIO(response.content)).convert('RGB')
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=60, optimize=True)

            return Image(data=buffer.getvalue(), format="jpeg")
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP Error: {e.response.status_code}")
    except PILImage.UnidentifiedImageError:
        raise Exception("Not a valid image format")
    except Exception as e:
        raise Exception(f"Failed to download image: {str(e)}")
