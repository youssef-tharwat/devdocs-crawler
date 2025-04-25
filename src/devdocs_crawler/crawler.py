"""Core crawler logic for the DevDoc Crawler tool."""

import asyncio
import logging
import os
from typing import Optional, Tuple
from urllib.parse import urlparse

import aiofiles
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CrawlResult
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from pathvalidate import sanitize_filename

from .utils import url_to_filename

logger = logging.getLogger(__name__)


class DevDocCrawler:
    """Handles crawling and processing documentation websites."""

    def __init__(self, output_dir: str):
        """Initializes the crawler with the base output directory.

        Args:
            output_dir: Base directory to save crawl-specific subdirectories.
        """
        self.base_output_dir = os.path.abspath(output_dir)
        logger.info(
            f"Crawler initialized. Base output directory: {self.base_output_dir}"
        )

    async def _process_result(self, result: CrawlResult, crawl_output_dir: str) -> bool:
        """Processes a single crawl result, saving markdown if available.

        Args:
            result: CrawlResult object from crawl4ai.
            crawl_output_dir: The specific directory for the current crawl.

        Returns:
            True if markdown was saved successfully, False otherwise.
        """
        if not result.markdown:
            logger.warning(f"Skipped (no markdown): {result.url}")
            return False

        filepath = url_to_filename(result.url, crawl_output_dir)
        if not filepath:
            logger.warning(f"Skipped (bad filename): {result.url}")
            return False

        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            async with aiofiles.open(filepath, mode="w", encoding="utf-8") as f:
                await f.write(result.markdown)
            logger.info(f"Saved: {result.url} -> {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving file {filepath} for URL {result.url}: {e}")
            return False

    async def run_crawl(
        self,
        start_url: str,
        depth: int,
        stream: bool,
        max_pages: Optional[int],
        silent: bool,
    ) -> Tuple[int, int]:
        """Runs the crawl4ai crawler and saves markdown into a domain-specific sub-directory.

        Args:
            start_url: Initial URL to start crawling from.
            depth: Maximum crawl depth beyond the start URL.
            stream: If True, process results as they arrive.
            max_pages: Optional limit on the total number of pages to crawl.
            silent: If True, suppress informational logs and run crawl4ai quietly.

        Returns:
            Tuple containing (total_pages_processed, total_pages_saved).
        """
        try:
            parsed_start_url = urlparse(start_url)
            if not parsed_start_url.scheme or not parsed_start_url.netloc:
                raise ValueError(
                    f"Invalid start URL: {start_url}. Must include scheme (e.g., https://)."
                )

            allowed_domain = parsed_start_url.netloc
            sanitized_domain = sanitize_filename(allowed_domain)
            crawl_output_dir = os.path.join(self.base_output_dir, sanitized_domain)

            os.makedirs(crawl_output_dir, exist_ok=True)

            logger.info(
                f"Starting crawl for {start_url} (Domain: {allowed_domain}, "
                f"Depth: {depth}, Stream: {stream}, Max Pages: {max_pages or 'Unlimited'})"
                f" -> Saving to: {crawl_output_dir}"
            )

            deep_crawl_config = BFSDeepCrawlStrategy(
                max_depth=depth,
                include_external=False,
            )

            if max_pages is not None:
                if max_pages > 0:
                    deep_crawl_config.max_pages = max_pages
                    logger.info(f"Limiting crawl to a maximum of {max_pages} pages.")
                else:
                    logger.warning("max_pages specified as <= 0, ignoring limit.")

            crawl4ai_verbose = not silent
            logger.debug(f"Setting crawl4ai verbose mode to: {crawl4ai_verbose} (based on silent flag: {silent})")

            config = CrawlerRunConfig(
                deep_crawl_strategy=deep_crawl_config,
                stream=stream,
                verbose=crawl4ai_verbose,
            )

            page_count = 0
            saved_count = 0

            async with AsyncWebCrawler() as crawler:
                results_iterable = await crawler.arun(start_url, config=config)

                if stream:
                    logger.info(
                        "Streaming results enabled. Processing pages as they arrive..."
                    )
                    async for result in results_iterable:
                        page_count += 1
                        if await self._process_result(result, crawl_output_dir):
                            saved_count += 1
                    logger.info("Streaming finished.")
                else:
                    if not isinstance(results_iterable, list):
                        raise TypeError(
                            f"Expected a list when stream=False, but got {type(results_iterable)}. Cannot process."
                        )

                    total_results = len(results_iterable)
                    logger.info(
                        f"Crawling complete. Processing {total_results} pages..."
                    )
                    page_count = total_results
                    tasks = [
                        self._process_result(result, crawl_output_dir)
                        for result in results_iterable
                    ]
                    results_processed = await asyncio.gather(*tasks)
                    saved_count = sum(1 for success in results_processed if success)
                    logger.info("Batch processing finished.")

            logger.info(
                f"Finished crawl. Processed {page_count} pages. "
                f"Saved {saved_count} markdown files to {crawl_output_dir}"
            )
            return page_count, saved_count

        except ValueError as ve:
            logger.error(f"Invalid input: {ve}")
            return 0, 0
        except TypeError as te:
            logger.error(f"Type error during crawling: {te}")
            return 0, 0
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during crawling: {e}", exc_info=True
            )
            return 0, 0
