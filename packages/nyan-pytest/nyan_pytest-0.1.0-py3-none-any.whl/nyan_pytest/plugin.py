"""Pytest plugin for Nyan Cat test reporter."""

import os
import sys
import time
import pytest
from typing import Dict, List, Optional, Tuple, Any

TERM_WIDTH = 80
try:
    # Get terminal width if supported
    from shutil import get_terminal_size
    TERM_WIDTH = get_terminal_size().columns
except (ImportError, AttributeError):
    pass

def is_interactive_terminal() -> bool:
    """Check if we're running in an interactive terminal."""
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


class NyanReporter:
    """Nyan Cat pytest reporter."""

    # ANSI escape codes for colors
    COLORS = {
        "reset": "\033[0m",
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "bright_black": "\033[90m",
        "bright_red": "\033[91m",
        "bright_green": "\033[92m",
        "bright_yellow": "\033[93m",
        "bright_blue": "\033[94m",
        "bright_magenta": "\033[95m",
        "bright_cyan": "\033[96m",
        "bright_white": "\033[97m",
        "bg_black": "\033[40m",
        "bg_red": "\033[41m",
        "bg_green": "\033[42m",
        "bg_yellow": "\033[43m",
        "bg_blue": "\033[44m",
        "bg_magenta": "\033[45m",
        "bg_cyan": "\033[46m",
        "bg_white": "\033[47m",
    }

    # Move cursor up n lines
    UP = "\033[{0}A"
    # Clear from cursor to end of screen
    CLEAR_SCREEN = "\033[0J"
    # Save cursor position
    SAVE_CURSOR = "\033[s"
    # Restore cursor position
    RESTORE_CURSOR = "\033[u"

    # Rainbow colors for the trail
    RAINBOW_COLORS = [
        "red", "yellow", "green", "cyan", "blue", "magenta"
    ]

    # Nyan cat frames
    NYAN_FRAMES = [
        # Frame 1
        [
            "≈≈≈≈≈≈≈≈≈≈≈≈≈≈",
            "≈≈≈≈≈≈≈≈≈≈≈≈≈≈",
            "╭━━━━╮┈┈┈┈┈┈┈┈",
            "┃ ∩ ∩ ┃┈┊┊┈┈┈┈",
            "┃∪(◕ᴥ◕)∪┊┊┈┈┈",
            "┃┈ ┈ ┈┃┊┊┈┈┈┈",
            "┃┈ ┈ ┈┃┊┊▃▃┈┈",
            "┗━━━━━┻━━━━━┈┈",
        ],
        # Frame 2
        [
            "≈≈≈≈≈≈≈≈≈≈≈≈≈≈",
            "≈≈≈≈≈≈≈≈≈≈≈≈≈≈",
            "┈┈┈┈┈┈┈┈╭━━━━╮",
            "┈┈┈┈┈┈┊┊┃ ∩ ∩ ┃",
            "┈┈┈┈┈┊┊∪(◕ᴥ◕)∪",
            "┈┈┈┈┈┊┊┃┈ ┈ ┈┃",
            "┈┈┈▃▃┊┊┃┈ ┈ ┈┃",
            "┈┈┈━━━━━┻━━━━┛",
        ]
    ]

    def __init__(self, config: pytest.Config) -> None:
        """Initialize the reporter."""
        self.config = config
        self.nyan_only = config.getoption("--nyan-only")
        self.interactive = is_interactive_terminal()
        self.width = min(TERM_WIDTH, 80)

        # Test counters
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.total = 0
        
        # Animation state
        self.tick = 0
        self.trail_length = 0
        self.max_trail_length = max(0, self.width - 20)  # Reserve space for cat
        
        self.started = False
        self.finished = False

    def pytest_configure(self, config: pytest.Config) -> None:
        """Configure the plugin."""
        if self.nyan_only:
            # Unregister other reporters
            standard_reporter = config.pluginmanager.getplugin('terminalreporter')
            config.pluginmanager.unregister(standard_reporter)

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        """Called after collection is finished."""
        self.total = len(session.items)
        if self.interactive:
            for _ in range(10):  # Reserve 10 lines for the nyan cat display
                sys.stdout.write("\n")
            # Move cursor back up and save position
            sys.stdout.write(self.UP.format(10))
            sys.stdout.write(self.SAVE_CURSOR)
            sys.stdout.flush()
            self.started = True

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        """Called for test setup/call/teardown."""
        if report.when != "call":
            return

        # Update counters
        if report.passed:
            self.passed += 1
        elif report.failed:
            self.failed += 1
        elif report.skipped:
            self.skipped += 1

        # Update display
        self.update_display()

    def update_display(self) -> None:
        """Update the display."""
        if not self.interactive or self.finished:
            return

        # Calculate progress percentage for trail length
        if self.total > 0:
            progress = min(1.0, (self.passed + self.failed + self.skipped) / self.total)
            self.trail_length = int(progress * self.max_trail_length)

        # Frame animation
        frame = self.NYAN_FRAMES[self.tick % len(self.NYAN_FRAMES)]
        self.tick += 1
        
        # Restore cursor position and clear screen
        sys.stdout.write(self.RESTORE_CURSOR)
        sys.stdout.write(self.CLEAR_SCREEN)
        
        # Draw rainbow trail and nyan cat
        for i, line in enumerate(frame):
            rainbow_segment = ""
            if 2 <= i <= 6:  # Draw rainbow only on middle lines
                for j in range(self.trail_length):
                    color_idx = (j + i + self.tick) % len(self.RAINBOW_COLORS)
                    color = self.RAINBOW_COLORS[color_idx]
                    rainbow_segment += f"{self.COLORS[color]}={self.COLORS['reset']}"
            
            # Print the line with rainbow trail
            sys.stdout.write(f"{rainbow_segment}{line}\n")
        
        # Print stats
        status = (
            f"Tests: {self.passed + self.failed + self.skipped}/{self.total} "
            f"✅ {self.passed} ❌ {self.failed} ⏭️  {self.skipped}"
        )
        sys.stdout.write(f"\n{status}\n")
        sys.stdout.flush()
        
        # Slow down animation to reduce CPU usage
        time.sleep(0.1)

    def pytest_terminal_summary(self, terminalreporter: Any, exitstatus: int) -> None:
        """Called at the end of the test session."""
        self.finished = True
        
        if self.interactive:
            # Print final status
            sys.stdout.write(self.RESTORE_CURSOR)
            sys.stdout.write(self.CLEAR_SCREEN)
            
            result = "passed" if exitstatus == 0 else "failed"
            color = "green" if exitstatus == 0 else "red"
            status = (
                f"{self.COLORS[color]}Tests {result}!{self.COLORS['reset']} "
                f"✅ {self.passed} ❌ {self.failed} ⏭️  {self.skipped}"
            )
            sys.stdout.write(f"{status}\n\n")
            sys.stdout.flush()


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add nyan-cat options to pytest."""
    group = parser.getgroup("nyan", "nyan cat reporting")
    group.addoption(
        "--nyan", 
        action="store_true", 
        help="Enable nyan cat output"
    )
    group.addoption(
        "--nyan-only", 
        action="store_true", 
        help="Enable nyan cat output and disable default reporter"
    )

def pytest_configure(config: pytest.Config) -> None:
    """Configure the pytest session."""
    # Only register if the option is enabled
    nyan_option = config.getoption("--nyan")
    nyan_only = config.getoption("--nyan-only")
    
    if nyan_option or nyan_only:
        nyan_reporter = NyanReporter(config)
        config.pluginmanager.register(nyan_reporter, "nyan-reporter")