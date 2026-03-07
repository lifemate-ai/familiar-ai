#!/usr/bin/env python3
"""PyInstaller entry point for familiar-ai packaged builds.

Packaged Windows builds can keep non-daemon worker threads alive after the GUI
closes.  The explicit os._exit(0) ensures the process exits cleanly so users
can relaunch immediately without a zombie process.
"""

from __future__ import annotations

import os
import sys

from familiar_agent.main import main

if __name__ == "__main__":
    # Default to GUI mode when launched as a packaged executable
    if "--gui" not in sys.argv and "--no-tui" not in sys.argv:
        sys.argv.append("--gui")
    main()
    os._exit(0)
