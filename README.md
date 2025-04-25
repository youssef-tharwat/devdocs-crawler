# DevDoc Crawler

A CLI tool to crawl developer documentation websites and save each page as a Markdown file.

This tool uses [crawl4ai](https://github.com/unclecode/crawl4ai) to perform deep crawling and extract content suitable for ingestion into RAG pipelines or direct use with LLMs.

## Features

*   Crawls websites starting from a given URL.
*   Uses `crawl4ai`'s deep crawling (`BFSDeepCrawlStrategy` by default).
*   Stays within the original domain (does not follow external links).
*   Saves the markdown content of each successfully crawled page.
*   **Organizes output into a subdirectory named after the crawled domain** (e.g., `output_dir/docs_example_com/`).
*   Attempts to preserve the URL path structure within the domain subdirectory.
*   Offers a streaming mode (`--stream`, enabled by default) to process pages as they arrive.

## Installation (Recommended: pipx)

Using `pipx` is recommended as it installs the tool and its dependencies in an isolated environment, preventing conflicts with other Python projects.

```bash
# Ensure you have Python 3.12+ and pipx installed (pip install pipx)

pipx install devdocs-crawler

# To upgrade later:
pipx upgrade devdocs-crawler
```

### Alternative Installation (pip)

You can also install using `pip` directly (ideally within a virtual environment):

```bash
# Ensure you have Python 3.12+ installed

pip install devdocs-crawler
```

## Usage

```bash
# Basic usage (crawl depth 1, stream enabled by default)
# Saves to ./devdocs_crawler_output/<domain_name>/
# Example: Saves to ./devdocs_crawler_output/docs_python_org/
devdocs-crawler https://docs.python.org/3/

# Specify a different base output directory
# Example: Saves to ./python_docs/docs_python_org/
devdocs-crawler https://docs.python.org/3/ -o ./python_docs

# Example: Crawl Neo4j GDS docs (depth 2)
# Example: Saves to ./devdocs_crawler_output/neo4j_com/
devdocs-crawler https://neo4j.com/docs/graph-data-science/current/ -d 2

# Example: Disable streaming
devdocs-crawler https://docs.example.com --no-stream
```

**Options:**

*   `start_url`: (Required) The starting URL for the crawl (must include scheme like `https://`).
*   `-o, --output DIRECTORY`: Base directory to save crawl-specific subdirectories (default: `./devdocs_crawler_output`).
*   `-d, --depth INTEGER`: Crawling depth beyond the start URL (0 = start URL only, 1 = start URL + linked pages, etc.) (default: 1).
*   `--max-pages INTEGER`: Maximum total number of pages to crawl (default: no limit).
*   `--stream / --no-stream`: Streaming mode processes pages as they arrive. Enabled by default. Use `--no-stream` to disable it and process all pages after the crawl finishes.
*   `-v, --verbose`: Increase logging verbosity (-v for INFO, -vv for DEBUG). Default is WARNING.
*   `--version`: Show the package version and exit.
*   `-h, --help`: Show the help message and exit.

## Development

1.  Clone the repository: `git clone https://github.com/youssef-tharwat/devdocs-crawler` (Replace with your fork if contributing)
2.  Navigate to the project directory: `cd devdocs-crawler`
3.  **Install `uv`:** If you don't have it, install `uv` (e.g., `pip install uv` or see [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/)).
4.  **Create environment & Install:** Use `uv` to create an environment and install dependencies (including dev dependencies). Requires Python 3.12+.
    ```bash
    uv venv # Creates .venv
    uv sync --dev # Syncs based on pyproject.toml
    ```
    *(Alternatively, if you prefer manual venv: `python3.12 -m venv .venv`, `source .venv/bin/activate`, then `uv pip install -e .[dev]`)*
5.  **Activate the environment:**
    *   macOS/Linux: `source .venv/bin/activate`
    *   Windows: `.venv\Scripts\activate`

Now you can run the tool using `devdocs-crawler` from within the activated environment.

You can run linters and formatters:

```bash
ruff check .
ruff format .
```

And run tests (if/when tests are added):

```bash
pytest
```

### Building and Publishing (using uv)

1.  Ensure your `pyproject.toml` has the correct version number and author details.
2.  Build the distributions:
    ```bash
    uv build
    ```
    This creates wheel and source distributions in the `dist/` directory.
3.  Publish to PyPI (requires a PyPI account and an API token configured with `uv`):
    ```bash
    uv publish
    ```
    You can also publish to TestPyPI using `uv publish --repository testpypi`. See `uv publish --help` for more options, including providing tokens via environment variables or arguments.

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines (if one exists).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 