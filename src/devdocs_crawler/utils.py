"""Utility functions for the devdocs_crawler tool."""

import logging
import os
from urllib.parse import urlparse

from pathvalidate import sanitize_filename

logger = logging.getLogger(__name__)


def url_to_filename(
    url: str, output_dir: str, default_filename: str = "index.md"
) -> str | None:
    """Converts a URL into a safe, structured filename within the output directory.

    Attempts to preserve the path structure from the URL.
    Handles potential filename collisions by adding a hash for URLs
    that differ only by query parameters or fragments.

    Args:
        url: The URL to convert.
        output_dir: The base directory to save the file.
        default_filename: The filename to use for directory index URLs (e.g., /docs/).

    Returns:
        The full, sanitized path for the output file, or None if the URL is invalid.
    """
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            logger.warning(f"Skipping invalid URL for filename generation: {url}")
            return None

        # Use only the path for directory/filename structure
        path_cleaned = parsed_url.path.strip("/")

        path_parts = [part for part in path_cleaned.split("/") if part]

        filename = default_filename
        dir_parts = []

        if path_parts:
            # Check if the last part looks like a file (contains a common extension)
            # A more robust check might be needed for edge cases
            last_part = path_parts[-1]
            common_extensions = {".html", ".htm", ".php", ".asp", ".aspx"}
            base, ext = os.path.splitext(last_part)
            # If it ends with a common web extension, treat it as a file
            if ext.lower() in common_extensions:
                # Sanitize and ensure it ends with .md
                sanitized_base = sanitize_filename(base)
                filename = f"{sanitized_base}.md"
                dir_parts = path_parts[:-1]  # Use preceding parts as directories
            # If it ends with / or has no extension, treat as directory index
            elif url.endswith("/") or not ext:
                filename = default_filename
                dir_parts = path_parts
            # Otherwise (e.g., a path component without extension), treat as directory
            else:
                filename = default_filename
                dir_parts = path_parts

        sanitized_path_parts = [sanitize_filename(part) for part in dir_parts]

        target_dir = os.path.join(output_dir, *sanitized_path_parts)

        try:
            os.makedirs(target_dir, exist_ok=True)
        except OSError as e:
            logger.error(f"Could not create directory {target_dir}: {e}")
            return None

        filepath = os.path.join(target_dir, filename)

        # Simple collision handling: If the path exists and the original URL
        # had query/fragment, append a hash of the query/fragment.
        # Content hashing is more robust but complex.
        if os.path.exists(filepath) and (parsed_url.query or parsed_url.fragment):
            query_fragment_hash = str(hash(parsed_url.query + parsed_url.fragment))[:8]
            base, ext = os.path.splitext(filename)
            # Ensure extension is .md
            if not ext:
                ext = ".md"
            elif ext != ".md":
                base = f"{base}{ext}"  # Keep original extension in base if not .md
                ext = ".md"

            unique_filename = f"{base}_{query_fragment_hash}{ext}"
            filepath = os.path.join(target_dir, unique_filename)
            logger.debug(
                f"Collision detected for {url}. Using unique filename: {filepath}"
            )

        return filepath

    except Exception as e:
        logger.error(f"Error converting URL {url} to filename: {e}", exc_info=True)
        return None
