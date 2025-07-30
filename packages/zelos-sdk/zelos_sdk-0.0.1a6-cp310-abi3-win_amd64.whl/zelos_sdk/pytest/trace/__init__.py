"""
Zelos Cloud trace plugin

Use via:

  pytest_plugins = ["zelos_sdk.pytest.trace"]

"""

from pathlib import Path
from typing import Generator
import logging

from zelos_sdk import TracePublishClientConfig, TraceWriter
import pytest
import zelos_sdk

log = logging.getLogger(__name__)

DEFAULT_TRACE_FORWARD_URL = "grpc://localhost:2300"


def pytest_addhooks(pluginmanager):
    """This example assumes the hooks are grouped in the 'hooks' module."""
    from . import hooks  # pylint: disable=import-outside-toplevel

    pluginmanager.add_hookspecs(hooks)


def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Parses flags that can enable/disable specific event handlers.

    :param parser: A pytest Parser object to add the command-line options.
    """
    group = parser.getgroup("zelos", description="Zelos tracing plugin")
    group.addoption("--zelos-trace", action="store_true", help="Enable tracing to the zelos grpc-server")
    group.addoption("--zelos-trace-url", action="store", default=DEFAULT_TRACE_FORWARD_URL, help="Set the url")
    group.addoption("--zelos-trace-file", action="store_true", help="Enable tracing to a file")
    group.addoption(
        "--zelos-trace-file-scope",
        action="store",
        default="function",
        choices=["session", "module", "class", "function"],
        help="Set the scope for trace file recording (session, module, class, or function)",
    )
    group.addoption("--zelos-trace-log", action="store_true", default=False, help="Enable SDK logs")
    group.addoption("--zelos-trace-log-level", action="store", default="info", help="Set the log level")


@pytest.fixture(scope="session", autouse=True)
def trace_session(request) -> Generator[None, None, None]:
    """
    Initialize and manage trace handlers for the entire test session.

    :param request: The pytest request object.
    :yield: Manages the lifecycle of trace handlers without returning a value.
    """
    trace_scope = request.config.getoption("--zelos-trace-file-scope")
    if request.config.getoption("--zelos-trace-file") and trace_scope == "session":
        with _create_scoped_trace_writer(request):
            yield
    else:
        yield


@pytest.fixture(scope="module", autouse=True)
def trace_module(request) -> Generator[None, None, None]:
    """
    Initialize and manage trace handlers for each module.

    :param request: The pytest request object.
    :yield: Manages the lifecycle of trace handlers without returning a value.
    """
    trace_scope = request.config.getoption("--zelos-trace-file-scope")
    if request.config.getoption("--zelos-trace-file") and trace_scope == "module":
        with _create_scoped_trace_writer(request):
            yield
    else:
        yield


@pytest.fixture(scope="class", autouse=True)
def trace_class(request) -> Generator[None, None, None]:
    """
    Initialize and manage trace handlers for each test class.

    :param request: The pytest request object.
    :yield: Manages the lifecycle of trace handlers without returning a value.
    """
    trace_scope = request.config.getoption("--zelos-trace-file-scope")
    if request.config.getoption("--zelos-trace-file") and trace_scope == "class":
        with _create_scoped_trace_writer(request):
            yield
    else:
        yield


@pytest.fixture(scope="function", autouse=True)
def trace_function(request) -> Generator[None, None, None]:
    """
    Initialize and manage trace handlers for each test function.

    :param request: The pytest request object.
    :yield: Manages the lifecycle of trace handlers without returning a value.
    """
    trace_scope = request.config.getoption("--zelos-trace-file-scope")
    if request.config.getoption("--zelos-trace-file") and trace_scope == "function":
        with _create_scoped_trace_writer(request):
            yield
    else:
        yield


def _create_scoped_trace_writer(request):
    """
    Create a trace writer for the specified scope.

    :param request: The pytest request object.
    :return: A context manager for the trace writer.
    """
    if not request.config.zelos_local_artifacts_dir:
        raise RuntimeError("Local artifacts directory is not set")

    # Accept the user-provided file name through the hook or use the default
    trace_file_name = request.config.pluginmanager.hook.pytest_zelos_trace_file_name(request=request)
    if trace_file_name is None:
        artifact_basename = request.config.getoption("zelos_artifact_basename")

        # Sanitize nodeid for use in filenames
        nodeid_sanitized = request.node.nodeid
        nodeid_sanitized = nodeid_sanitized.replace(".py", "")
        nodeid_sanitized = nodeid_sanitized.replace("::", "-")
        nodeid_sanitized = nodeid_sanitized.translate(
            str.maketrans(
                {
                    "\\": None,
                    "/": "-",
                    ":": None,
                    "*": None,
                    "?": None,
                    '"': None,
                    ".": None,
                    "<": None,
                    ">": None,
                    "|": None,
                    " ": None,
                    ",": None,
                    "!": None,
                    "@": None,
                    "#": None,
                    "$": None,
                    "%": None,
                    "^": None,
                }
            )
        )
        trace_file_name = (
            f"{artifact_basename}-trace-{nodeid_sanitized}" if nodeid_sanitized else f"{artifact_basename}-trace"
        )

    # Create base path and handle filename collisions
    artifacts_dir = Path(request.config.zelos_local_artifacts_dir)
    base_path = artifacts_dir / trace_file_name
    trace_file_path = base_path.with_suffix(".trz")

    # Check if file exists and add numeric suffix if needed
    counter = 1
    while trace_file_path.exists():
        trace_file_path = base_path.with_suffix(f".{counter}.trz")
        counter += 1

    return TraceWriter(str(trace_file_path))


@pytest.fixture(scope="session", autouse=True)
def zelos_session(request):
    """Configures the zelos sdk for the entire test session"""
    trace_grpc_url = request.config.getoption("--zelos-trace-url")
    config = TracePublishClientConfig(url=trace_grpc_url)

    log_level = None
    if request.config.getoption("--zelos-trace-log"):
        log_level = request.config.getoption("--zelos-trace-log-level")

    log.debug(f"initializing the zelos sdk with: init(client_config={config}, log_level={log_level})")

    if request.config.getoption("--zelos-trace"):
        zelos_sdk.init(client_config=config, log_level=log_level)
    elif request.config.getoption("--zelos-trace-log"):
        zelos_sdk.enable_logging(log_level)

    yield
