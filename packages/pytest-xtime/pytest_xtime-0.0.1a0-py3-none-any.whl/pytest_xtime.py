"""
pytest-xtime: A pytest plugin for tracking test execution times with visual indicators.
Supports distributed testing with pytest-xdist.
"""

import json
import os
import shutil
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Literal

import pytest
from _pytest.config import Config
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.terminal import TerminalReporter

try:
    from xdist import get_xdist_worker_id
except ImportError:

    def get_xdist_worker_id(session_or_request):
        return None


def ensure_dir(dir_name: str) -> Path:
    """Ensures a directory exists and is empty of everything except a .gitignore file."""
    xtime_path = Path.cwd() / dir_name
    xtime_path.mkdir(exist_ok=True)
    for item in xtime_path.iterdir():
        if item.name == ".gitignore":
            continue
        if item.is_file() or item.is_symlink():
            item.unlink()
        if item.is_dir():
            shutil.rmtree(item)
    if not (xtime_path / ".gitignore").exists():
        with open(xtime_path / ".gitignore", "w") as f:
            f.write("*")
    return xtime_path


STATUS_ICON_MAP = {
    "passed": "✔",
    "failed": "✘",
    "skipped": "⚠",
}


@dataclass
class TestData:
    execution_result: Literal["passed", "failed", "skipped"]
    execution_time: float


class ExecutionTimeTracker:
    """Tracks execution times for tests marked with @pytest.mark.xtime."""

    def __init__(self) -> None:
        self.test_data: dict[str, TestData | float] = {}
        self.show_summary: bool = True
        self.top_count: int = 5
        self.json_path: Path | None = None
        self.temp_path: Path | None = None
        self.is_xdist_worker: bool = False
        self.worker_id: str | None = None

    def configure(self, config: Config) -> None:
        """Configure tracker for session config."""
        json_path = config.getoption("xtime_json_path", None)
        self.json_path = Path(json_path).absolute() if json_path else None

        # Create or clean temp directory and create .gitignore file
        self.temp_path = ensure_dir(".xtime")

        self.show_summary = not config.getoption("xtime_no_summary")
        self.top_count = config.getoption("xtime_top_count")

    def start_session(self, session: pytest.Session) -> None:
        """Configure tracker for xdist worker or controller."""
        worker_id = get_xdist_worker_id(session)
        self.worker_id = worker_id if worker_id != "master" else None
        self.is_xdist_worker = self.worker_id is not None

    def start_test(self, item: Item) -> None:
        """Record the start time of a test."""
        if item.get_closest_marker("xtime"):
            self.test_data[item.nodeid] = time.time()

    def finish_test(self, item: Item, report: TestReport) -> None:
        """Record the end time and calculate execution time."""
        if item.nodeid in self.test_data:
            execution_time = time.time() - self.test_data[item.nodeid]

            # Store data for JSON export and summary
            test_data = TestData(
                execution_result=report.outcome,
                execution_time=execution_time,
            )

            self.test_data[item.nodeid] = test_data

    def export_json(self, config: Config) -> None:
        """Export test data to JSON file if path is specified."""

        # For xdist workers, append worker ID to filename to avoid conflicts
        # For non-xdist (controller only), use the original filename
        json_path = (
            self.temp_path / f"results_{self.worker_id}.json"
            if (self.is_xdist_worker and self.worker_id)
            else self.json_path
        )

        if self.test_data and json_path:
            # Convert TestData objects to dictionaries for JSON serialization
            json_data = {k: asdict(v) for k, v in self.test_data.items()}

            try:
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=2)
            except Exception as e:
                if not self.is_xdist_worker:  # Only print once for controller
                    print(f"\nError exporting JSON: {e}")


# Global tracker instance
_tracker = ExecutionTimeTracker()


def pytest_addoption(parser: Any) -> None:
    """Add command line options for the plugin."""
    group = parser.getgroup("xtime")
    group.addoption(
        "--xtime-json",
        action="store",
        dest="xtime_json_path",
        help="Export execution times to JSON file at specified path",
    )
    group.addoption(
        "--xtime-top",
        action="store",
        type=int,
        default=5,
        dest="xtime_top_count",
        help="Number of slowest tests to show in summary (default: 5)",
    )
    group.addoption(
        "--xtime-no-summary",
        action="store_true",
        dest="xtime_no_summary",
        help="Disable the execution time summary output",
    )


def pytest_configure(config: Config) -> None:
    """Configure the plugin with command line options."""
    config.addinivalue_line("markers", "xtime: mark test to track execution time")

    # Configure options
    _tracker.configure(config)


def pytest_sessionstart(session: pytest.Session) -> None:
    """Hook called after the Session object has been created."""
    # Configure for xdist using session object
    _tracker.start_session(session)


def pytest_sessionfinish(session: pytest.Session) -> None:
    """Hook called when the test session finishes."""
    _tracker.export_json(session.config)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: Item) -> None:
    """Hook called before each test setup."""
    _tracker.start_test(item)


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item: Item) -> None:
    """Hook called after each test teardown."""
    # We need to wait for the report to be available
    pass


@pytest.hookimpl(trylast=True)
def pytest_runtest_logreport(report: TestReport) -> None:
    """Hook called when a test report is available."""
    if report.when == "call":  # Only process the main test execution phase
        # Find the item by nodeid (this is a bit of a workaround)
        # In a real implementation, you might want to store the item reference
        item_nodeid = report.nodeid
        if item_nodeid in _tracker.test_data:
            # Create a minimal item-like object for compatibility
            class MockItem:
                def __init__(self, nodeid: str):
                    self.nodeid = nodeid
                    self._markers = []

                def get_closest_marker(self, name: str):
                    # This is a simplified version - in practice you'd need to
                    # store the actual marker information
                    return True if name == "xtime" else None

            mock_item = MockItem(item_nodeid)
            _tracker.finish_test(mock_item, report)


def pytest_terminal_summary(
    terminalreporter: TerminalReporter, exitstatus: int, config: Config
) -> None:
    """Add a summary section to the terminal output."""
    # Only show summary on controller (not on xdist workers)
    if _tracker.is_xdist_worker:
        return

    # For xdist: try to merge data from workers, for non-xdist: use local data
    all_test_data = _merge_xdist_results(config)

    if not all_test_data or not _tracker.show_summary:
        return

    # Sort tests by execution time (slowest first)
    sorted_tests = sorted(
        all_test_data, key=lambda k: all_test_data[k].execution_time, reverse=True
    )

    # Initialize counter values
    total_time = 0
    counts = dict.fromkeys(STATUS_ICON_MAP, 0)

    for test in all_test_data.values():
        total_time += test.execution_time
        counts[test.execution_result] += 1

    # Calculate statistics
    total_tests = len(all_test_data)
    avg_time = total_time / total_tests if total_tests > 0 else 0
    slowest_test = sorted_tests[0] if sorted_tests else None
    fastest_test = sorted_tests[-1] if sorted_tests else None

    # Write summary section
    terminalreporter.write_sep("=", "execution time summary", bold=True)
    terminalreporter.write_line(f"Total tracked tests: {total_tests}")
    terminalreporter.write_line(f"Total execution time: {total_time:.4f}s")
    terminalreporter.write_line(f"Average execution time: {avg_time:.4f}s")
    terminalreporter.write_line(
        f"Status breakdown: {counts['passed']} passed, {counts['failed']} failed, {counts['skipped']} skipped"
    )

    if slowest_test:
        terminalreporter.write_line(
            f"Slowest test: {slowest_test} ({all_test_data[slowest_test].execution_time:.4f}s)"
        )
    if fastest_test and fastest_test != slowest_test:
        terminalreporter.write_line(
            f"Fastest test: {fastest_test} ({all_test_data[fastest_test].execution_time:.4f}s)"
        )

    if total_tests > 0:
        if total_tests > _tracker.top_count:
            top_count = min(_tracker.top_count, total_tests)
            summary_line = f"Top {top_count} slowest tests:"
            selected_tests = sorted_tests[:top_count]
        elif total_tests > 0:
            summary_line = "All tracked tests (by execution time):"
            selected_tests = sorted_tests

        terminalreporter.write_line("")
        terminalreporter.write_line(summary_line)
        for i, test in enumerate(selected_tests, 1):
            test_data = all_test_data[test]
            status_icon = STATUS_ICON_MAP[test_data.execution_result]
            terminalreporter.write_line(
                f"  {i}. {status_icon} {test}: {test_data.execution_time:.4f}s"
            )

    terminalreporter.write_line("")  # Add blank line for better readability


def _merge_xdist_results(config: Config) -> dict[str, TestData]:
    """Merge results from all xdist workers."""
    all_data = _tracker.test_data  # Start with controller data
    temp_path = _tracker.temp_path

    # Look for worker JSON files
    try:
        # Find all worker files (they have the pattern: filename_gw0.json, filename_gw1.json, etc.)
        worker_files = list(temp_path.glob("results_gw*.json"))

        for json_file in worker_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    worker_data_dicts = json.load(f)
                    # Convert dictionaries back to TestData objects
                    worker_data = {
                        data["test_name"]: TestData(**data)
                        for data in worker_data_dicts
                    }
                    all_data.update(worker_data)
            except Exception:
                continue  # Skip problematic files

        for json_file in worker_files:
            try:
                os.remove(json_file)
            except Exception:
                print("Unable to clean up worker JSON file:", json_file)

        if _tracker.json_path and all_data and not _tracker.is_xdist_worker:
            try:
                # Convert TestData objects to dictionaries for JSON serialization
                json_data = sorted(
                    [asdict(test) for test in all_data.values()],
                    key=lambda x: x["test_name"],
                )
                with open(_tracker.json_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=2)
            except Exception as e:
                print(f"Error merging xdist results: {e}")

    except Exception:
        pass  # Fall back to controller data only

    return all_data


# Make the xtime marker available
xtime = pytest.mark.xtime
