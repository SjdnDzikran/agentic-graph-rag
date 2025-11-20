"""
Helper entry point to launch the SEPSES Cybersecurity Knowledge Graph MCP server.

This wrapper simply forwards all CLI arguments to the bundled FastMCP server
(`src/mcp-cskg-rdf/src/mcp-cskg-rdf/server.py`) so it can be started with `python -m`.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    """Resolve the server path and execute it with the provided CLI arguments."""
    repo_root = Path(__file__).resolve().parents[1]
    server_path = repo_root / "mcp-cskg-rdf" / "src" / "mcp-cskg-rdf" / "server.py"

    if not server_path.exists():
        raise FileNotFoundError(f"MCP server not found at {server_path}")

    # Preserve any user supplied CLI args while replacing argv[0] so argparse works.
    sys.argv = [str(server_path), *sys.argv[1:]]
    runpy.run_path(str(server_path), run_name="__main__")


if __name__ == "__main__":
    main()
