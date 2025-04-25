"""Command Line Interface for the DevDoc Crawler tool."""

import asyncio
import logging
import sys

import click

from .crawler import DevDocCrawler


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("start_url", type=str)
@click.option(
    "--output",
    "-o",
    default="./devdocs_crawler_output",
    help="Directory to save markdown files.",
    type=click.Path(file_okay=False, writable=True, resolve_path=True),
    show_default=True,
)
@click.option(
    "--depth",
    "-D",
    default=1,
    type=click.IntRange(min=0),
    help="Crawling depth beyond the start URL (0 = start URL only).",
    show_default=True,
)
@click.option(
    "--max-pages",
    type=int,
    default=None,
    help="Maximum total number of pages to crawl (including start URL).",
    show_default="(no limit)",
)
@click.option(
    "--stream",
    is_flag=True,
    default=True,
    help=(
        "Enable streaming mode to process pages as they arrive. "
        "Use --no-stream to disable."
    ),
    show_default=True,
)
@click.option(
    "--silent",
    "-s",
    is_flag=True,
    default=False,
    help="Suppress informational messages (show only warnings/errors).",
)
@click.version_option(package_name="devdocs-crawler")
def main(
    start_url: str,
    output: str,
    depth: int,
    stream: bool,
    max_pages: int | None,
    silent: bool = False,
) -> None:
    """Crawls a developer documentation website starting from START_URL
    and saves each page as a markdown file in the --output directory.

    Default output includes informational messages about page processing.
    Use --silent to show only warnings and errors.
    Use --debug for maximum verbosity.

    Example:
        devdocs-crawler https://docs.example.com -o ./example_docs -D 2 \
        --no-stream --silent
    """

    log_level = logging.WARNING if silent else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )

    logger = logging.getLogger("devdocs_crawler")
    logger.info(f"Root logging level set to: {logging.getLevelName(log_level)}")

    if not (start_url.startswith("http://") or start_url.startswith("https://")):
        logger.error(
            f"Invalid start_url: {start_url}. Must start with 'http://' or 'https://'"
        )
        click.echo(
            f"Error: Invalid start_url: {start_url}. Must start with 'http://' or 'https://'",
            err=True,
        )
        sys.exit(1)

    try:
        crawler = DevDocCrawler(output_dir=output)
        asyncio.run(
            crawler.run_crawl(
                start_url=start_url,
                depth=depth,
                stream=stream,
                max_pages=max_pages,
                silent=silent,
            )
        )

    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)
        click.echo(f"An unexpected error occurred: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
