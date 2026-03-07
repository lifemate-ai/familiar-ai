#!/usr/bin/env python3
"""PyInstaller entrypoint for familiar-ai testflight builds."""

import os
import sys

from familiar_agent.main import main


if __name__ == "__main__":
    if "--gui" not in sys.argv and "--no-tui" not in sys.argv:
        sys.argv.append("--gui")
    main()
    # Packaged Windows builds can keep non-daemon worker threads alive after GUI close.
    # Force process termination so testers can relaunch immediately.
    os._exit(0)
