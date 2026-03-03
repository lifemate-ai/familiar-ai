#!/usr/bin/env python3
"""PyInstaller entrypoint for familiar-ai testflight builds."""

import sys

from familiar_agent.main import main


if __name__ == "__main__":
    if "--gui" not in sys.argv and "--no-tui" not in sys.argv:
        sys.argv.append("--gui")
    main()
