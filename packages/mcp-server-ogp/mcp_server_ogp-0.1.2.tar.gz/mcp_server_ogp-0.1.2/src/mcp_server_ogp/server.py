import io
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from fastmcp import FastMCP, Image
from PIL import Image as PILImage
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS, INTERNAL_ERROR

# Create an MCP server instance
# This serves as a dedicated server for retrieving OGP information
mcp = FastMCP("OGP Information Server")


async def fetch_html(url: str) -> str:
    """
    Asynchronously fetch HTML content from a specified URL.

    This function sends an HTTP request to a web page and returns the HTML content
    as a string. It includes timeout handling and error management for robust operation.

    Args:
        url: The target URL to fetch content from

    Returns:
        HTML content as a string

    Raises:
        httpx.HTTPError: When HTTP-related errors occur
        Exception: For any other unexpected errors
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        return response.text


def extract_ogp_info(html: str, base_url: str) -> Dict[str, Any]:
    """
    Extract Open Graph Protocol (OGP) information from HTML content.

    This function parses HTML content to find OGP meta tags and returns
    the information in a structured dictionary format. If OGP tags are not found,
    it attempts to extract alternative information from basic HTML tags (like title).

    Args:
        html: The HTML content to parse
        base_url: Base URL for converting relative URLs to absolute URLs

    Returns:
        Dictionary containing OGP information with possible keys:
        - title: Page title
        - description: Page description
        - image: OGP image URL
        - url: Page URL
        - type: Content type
        - site_name: Site name
    """
    soup = BeautifulSoup(html, 'html.parser')
    ogp_data = {}

    # Search for OGP meta tags and extract information
    # We look for meta tags with property attributes starting with "og:"
    ogp_tags = soup.find_all(
        'meta', property=lambda x: x and x.startswith('og:'))

    for tag in ogp_tags:
        property_name = tag.get('property')
        content = tag.get('content')

        if property_name and content:
            # Remove "og:" prefix to create clean key names
            key = property_name.replace('og:', '')
            ogp_data[key] = content

    # Fallback processing when OGP tags are not found
    # Attempt to extract basic information from standard HTML tags
    if 'title' not in ogp_data:
        title_tag = soup.find('title')
        if title_tag:
            ogp_data['title'] = title_tag.get_text().strip()

    if 'description' not in ogp_data:
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            ogp_data['description'] = desc_tag.get('content', '').strip()

    # Convert relative image URLs to absolute URLs
    if 'image' in ogp_data:
        ogp_data['image'] = urljoin(base_url, ogp_data['image'])

    return ogp_data


async def fetch_image_data(image_url: str) -> Optional[Image]:
    """
    Fetch image data from a URL and return it as an optimized Image object.

    This function downloads an image file from the specified URL, processes it
    using PIL for optimization, and returns it as a FastMCP Image object.
    This approach is more memory-efficient than Base64 encoding and provides
    better integration with the MCP protocol.

    Args:
        image_url: The URL of the image to fetch

    Returns:
        FastMCP Image object containing optimized image data
        Returns None if fetching fails
    """
    try:
        # Download the image using a synchronous HTTP client within an async context
        # This pattern follows the established conventions from the YouTube server
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(image_url, follow_redirects=True)
            response.raise_for_status()

            # Process image data with PIL for optimization
            # Convert to RGB to ensure consistent color handling across formats
            image = PILImage.open(io.BytesIO(response.content)).convert('RGB')

            # Apply size constraints to prevent memory issues with very large images
            # Large images can cause performance problems, so we resize when necessary
            max_size = (1200, 1200)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, PILImage.Resampling.LANCZOS)

            # Optimize the image for efficient storage and transmission
            # JPEG format with 80% quality provides good balance of size and quality
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=80, optimize=True)

            # Return as FastMCP Image object for proper protocol compliance
            return Image(data=buffer.getvalue(), format="jpeg")

    except Exception as e:
        print(f"Image fetch error: {str(e)}")
        return None


@mcp.tool()
async def ogp_info(url: str) -> Dict[str, Any]:
    """
    Extract Open Graph Protocol (OGP) information from a specified URL.

    This function retrieves OGP metadata from web pages, which is commonly used
    for social media sharing previews. It extracts information like title,
    description, image URL, site name, and other OGP properties.

    Args:
        url: The URL of the web page to extract OGP information from

    Returns:
        Dictionary containing OGP metadata:
        - title: Page title
        - description: Page description
        - image: OGP image URL
        - url: Page URL
        - type: Content type
        - site_name: Site name
        - Other OGP properties as available

    Raises:
        McpError: When URL is invalid, fetching fails, or parsing errors occur
    """
    # Validate URL parameter
    if not url or not isinstance(url, str):
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="URL parameter is required and must be a non-empty string"
        ))

    # Basic URL validation
    if not (url.startswith('http://') or url.startswith('https://')):
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="URL must start with http:// or https://"
        ))

    try:
        # Fetch HTML content from the target URL
        html_content = await fetch_html(url)

        # Extract OGP information from the HTML
        ogp_data = extract_ogp_info(html_content, url)

        # Return the extracted OGP data
        return ogp_data

    except httpx.HTTPError as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Failed to fetch HTML from {url}: {e!r}"
        ))
    except Exception as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Unexpected error while extracting OGP info from {url}: {e!r}"
        ))


@mcp.tool()
async def ogp_image(url: str) -> Optional[Image]:
    """
    Retrieve the OGP image from a specified URL and return it as an optimized Image object.

    This function first extracts OGP information to locate the image URL,
    then downloads and processes the image using PIL for optimization.
    The result is returned as a FastMCP Image object.

    Args:
        url: The URL of the web page to extract the OGP image from

    Returns:
        FastMCP Image object containing the optimized OGP image data
        Returns None if no image is found or if an error occurs

    Raises:
        McpError: When URL is invalid, fetching fails, or image processing errors occur
    """
    # Validate URL parameter
    if not url or not isinstance(url, str):
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="URL parameter is required and must be a non-empty string"
        ))

    # Basic URL validation
    if not (url.startswith('http://') or url.startswith('https://')):
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="URL must start with http:// or https://"
        ))

    try:
        # First, extract OGP information to find the image URL
        html_content = await fetch_html(url)
        ogp_data = extract_ogp_info(html_content, url)

        # Check if OGP image URL exists
        image_url = ogp_data.get('image')
        if not image_url:
            return None

        # Fetch and process the image data, returning as FastMCP Image object
        image_data = await fetch_image_data(image_url)

        # Return the Image object directly
        return image_data

    except httpx.HTTPError as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Failed to fetch HTML from {url}: {e!r}"
        ))
    except Exception as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Unexpected error while extracting OGP image from {url}: {e!r}"
        ))
