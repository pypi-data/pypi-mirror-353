from dataclasses import dataclass
from enum import StrEnum, auto, IntEnum
import time
from typing import Iterable

from pytest import ExitCode
from balsa import get_logger
from ...__version__ import application_name

log = get_logger(application_name)


def _lines_per_second(duration: float, coverage: float) -> float:
    """
    Calculate the line coverage per second.
    """

    lines_per_second = coverage / max(duration, 1e-9)  # avoid division by zero
    return lines_per_second


@dataclass(frozen=True)
class ScheduledTest:
    """
    Represents a test that is scheduled to be run.
    """

    node_id: str  # unique identifier for the test
    singleton: bool  # True if the test is a singleton
    duration: float | None  # duration of the most recent run (seconds)
    coverage: float | None  # coverage of the most recent run, between 0.0 and 1.0 (1.0 = this tests covers all the code)

    def __gt__(self, other):
        """
        Compare two ScheduledTest objects. True if this object should be executed earlier than the other.
        """
        if self.singleton and not other.singleton:
            gt = True  # this object is a singleton, but the other is not, so this object should be executed later
        elif not self.singleton and other.singleton:
            gt = False  # this object is not a singleton, but the other is, so this object should be executed earlier
        elif self.duration is None or self.coverage is None or other.duration is None or other.coverage is None:
            # if either test has no duration or coverage, we just sort alphabetically
            gt = self.node_id > other.node_id
        else:
            # the test with the most effective coverage per second should be executed first
            gt = _lines_per_second(self.duration, self.coverage) > _lines_per_second(other.duration, other.coverage)
        return gt

    def __eq__(self, other):
        """
        Compare two ScheduledTest objects.
        """
        eq = self.singleton == other.singleton and self.duration == other.duration and self.coverage == other.coverage
        return eq


class ScheduledTests:
    """
    Represents a list of scheduled tests.
    """

    def __init__(self) -> None:
        self._tests_set = set()
        self._is_sorted = True
        self.tests = []  # list of scheduled (sorted) tests

    def add(self, test: ScheduledTest) -> None:
        """
        Add a test to the list of scheduled tests. (not called append since we'll sort later in the schedule method)
        """
        self._is_sorted = False  # mark the list as unsorted so we can sort it later
        self._tests_set.add(test)

    def schedule(self):
        """
        Put the test in order so they will run in scheduled order.
        """
        if not self._is_sorted:
            self.tests = sorted(self._tests_set)
            self._is_sorted = True

    def __iter__(self):
        """
        Iterate over the scheduled tests.
        """
        self.schedule()  # sort the tests before iterating
        return iter(self.tests)

    def __len__(self) -> int:
        """
        Get the number of scheduled tests.
        """
        return len(self.tests)


class RunMode(IntEnum):
    RESTART = 0  # rerun all tests
    RESUME = 1  # resume test run, and run tests that either failed or were not run
    CHECK = 2  # resume if program under test has not changed, otherwise restart


@dataclass
class RunParameters:
    """
    Parameters provided to the pytest runner.
    """

    run_guid: str  # unique identifier for the run
    run_mode: RunMode  # True to automatically determine the number of processes to run in parallel
    max_processes: int  # maximum number of processes to run in parallel (ignored if dynamic_processes is True)


class PytestProcessState(StrEnum):
    """
    Represents the state of a test process.
    """

    UNKNOWN = auto()  # unknown state
    QUEUED = auto()  # queued to be run by the scheduler
    RUNNING = auto()  # test is currently running
    FINISHED = auto()  # test has finished
    TERMINATED = auto()  # test was terminated


def state_order(pytest_process_state: PytestProcessState) -> int:
    # for sorting PytestProcessState, but keeping PytestProcessState as a str
    orders = {PytestProcessState.UNKNOWN: 0, PytestProcessState.QUEUED: 1, PytestProcessState.RUNNING: 2, PytestProcessState.FINISHED: 3, PytestProcessState.TERMINATED: 4}
    if pytest_process_state is None:
        order = orders[PytestProcessState.UNKNOWN]
    elif pytest_process_state in orders:
        order = orders[pytest_process_state]
    else:
        log.error(f"Unknown pytest_process_state: {pytest_process_state}")
        order = orders[PytestProcessState.UNKNOWN]
    return order


@dataclass
class PytestProcessInfo:
    """
    Information about a running test process, e.g. for the UI.
    """

    name: str  # test name
    singleton: bool  # True if the test is a singleton, False otherwise
    state: PytestProcessState | None = None  # state of the test process
    pid: int | None = None  # OS process ID of the pytest process
    exit_code: ExitCode | None = None  # exit code of the test
    output: str | None = None  # output (stdout, stderr) of the test
    start: float | None = None  # epoch when the test started (not when queued)
    end: float | None = None  # epoch when the test ended
    cpu_percent: float | None = None  # CPU utilization as a percentage (100.0 = 1 CPU)
    memory_percent: float | None = None  # memory utilization as a percentage (100.0 = 100% of RSS memory)
    run_with_coverage: bool = False  # True to run with test coverage
    test_coverage: float | None = None  # current coverage of the test (0.0 = no coverage, 1.0 = full coverage)
    time_stamp: float = time.time()  # timestamp when the data was last updated


# create a PytestProcessInfo from iterable
def pytest_process_info_from_iterable(t: Iterable) -> PytestProcessInfo:
    pytest_process_info = PytestProcessInfo(*t)
    return pytest_process_info


int_to_exit_code = {exit_code.value: exit_code for exit_code in ExitCode}


def exit_code_to_string(exit_code: ExitCode | int | None) -> str:
    if isinstance(exit_code, int):
        exit_code = int_to_exit_code[exit_code]
    if isinstance(exit_code, ExitCode):
        exit_code_string = exit_code.name
    else:
        exit_code_string = "unknown"
    return exit_code_string
