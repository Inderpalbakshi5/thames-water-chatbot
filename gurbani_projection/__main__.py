"""
Main entry point for the Gurbani Projection System.

Usage:
    python -m gurbani_projection [--host HOST] [--port PORT]

Opens:
    - Projection display: http://localhost:8080/
    - Admin panel: http://localhost:8080/admin
"""

import argparse
import logging

import uvicorn

from .config import AppConfig


def main():
    parser = argparse.ArgumentParser(description="Gurbani Projection System")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    parser.add_argument("--reload", action="store_true", help="Auto-reload on code changes")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"])
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger = logging.getLogger("gurbani_projection")
    logger.info("Starting Gurbani Projection System")
    logger.info(f"Projection display: http://localhost:{args.port}/")
    logger.info(f"Admin panel:        http://localhost:{args.port}/admin")

    uvicorn.run(
        "gurbani_projection.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()
