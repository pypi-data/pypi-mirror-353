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

# Stash key for tracking trace files across test execution
_zelos_trace_files = pytest.StashKey[dict]()


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


def pytest_configure(config):
    """Initialize trace file tracking when pytest starts"""
    # Initialize the trace files tracking dictionary
    config.stash[_zelos_trace_files] = {"session": [], "module": {}, "class": {}, "function": {}}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to inject trace file links into HTML reports.

    This hook runs after each test phase and adds trace file links
    to the HTML report if pytest-html is available.
    """
    outcome = yield
    report = outcome.get_result()

    # Only add extras during the "call" phase to avoid duplicates
    if report.when != "call":
        return

    # Check if pytest-html plugin is available
    pytest_html = item.config.pluginmanager.getplugin("html")
    if not pytest_html:
        return

    # Only proceed if trace files are enabled
    if not item.config.getoption("--zelos-trace-file"):
        return

    # Get trace files from stash
    trace_files = item.config.stash.get(_zelos_trace_files, {})

    # Collect relevant trace files for this test
    relevant_trace_files = []

    # Add session-level trace files (apply to all tests)
    relevant_trace_files.extend(trace_files.get("session", []))

    # Add module-level trace files
    module_name = item.module.__name__ if item.module else ""
    if module_name in trace_files.get("module", {}):
        relevant_trace_files.extend(trace_files["module"][module_name])

    # Add class-level trace files
    if item.cls:
        class_key = f"{module_name}::{item.cls.__name__}"
        class_files = trace_files.get("class", {})
        if class_key in class_files:
            relevant_trace_files.extend(class_files[class_key])

    # Add function-level trace files
    nodeid = item.nodeid
    if nodeid in trace_files.get("function", {}):
        relevant_trace_files.extend(trace_files["function"][nodeid])

    # Add trace file links to the report
    if relevant_trace_files:
        extras = getattr(report, "extras", [])

        for trace_file_info in relevant_trace_files:
            file_path = trace_file_info["path"]
            scope = trace_file_info["scope"]

            # Convert to absolute path and create file:// URL
            # This will open the file location in the system file manager when clicked
            absolute_path = Path(file_path).resolve()

            # Create a descriptive name for the link
            link_name = f"Trace File: {absolute_path.name}"

            # Use file:// URL to open file location in system file manager
            # TODO(tkeairns): Find a way to not have to redownload the file when the user clicks the link
            # maybe register a zelos:// URL that launches the app
            file_url = f"file://{absolute_path}"
            extras.append(pytest_html.extras.url(file_url, name=link_name))

        report.extras = extras


@pytest.fixture(scope="session", autouse=True)
def trace_session(request) -> Generator[None, None, None]:
    """
    Initialize and manage trace handlers for the entire test session.

    :param request: The pytest request object.
    :yield: Manages the lifecycle of trace handlers without returning a value.
    """
    trace_scope = request.config.getoption("--zelos-trace-file-scope")
    if request.config.getoption("--zelos-trace-file") and trace_scope == "session":
        with _create_scoped_trace_writer(request, "session"):
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
        with _create_scoped_trace_writer(request, "module"):
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
        with _create_scoped_trace_writer(request, "class"):
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
        with _create_scoped_trace_writer(request, "function"):
            yield
    else:
        yield


def _create_scoped_trace_writer(request, scope):
    """
    Create a trace writer for the specified scope and track it for HTML report integration.

    :param request: The pytest request object.
    :param scope: The scope of the trace writer (session, module, class, function).
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

    # Track the trace file for HTML report integration
    _track_trace_file(request, str(trace_file_path), scope)

    return TraceWriter(str(trace_file_path))


def _track_trace_file(request, file_path, scope):
    """
    Track a trace file for later inclusion in HTML reports.

    :param request: The pytest request object.
    :param file_path: Path to the trace file.
    :param scope: Scope of the trace file (session, module, class, function).
    """
    trace_files = request.config.stash.get(_zelos_trace_files, {})

    trace_file_info = {"path": file_path, "scope": scope}

    if scope == "session":
        trace_files["session"].append(trace_file_info)
    elif scope == "module":
        module_name = request.node.module.__name__ if request.node.module else ""
        module_files = trace_files.get("module", {})
        if module_name not in module_files:
            module_files[module_name] = []
        module_files[module_name].append(trace_file_info)
    elif scope == "class":
        module_name = request.node.module.__name__ if request.node.module else ""
        class_name = request.node.cls.__name__ if request.node.cls else ""
        class_key = f"{module_name}::{class_name}"
        class_files = trace_files.get("class", {})
        if class_key not in class_files:
            class_files[class_key] = []
        class_files[class_key].append(trace_file_info)
    elif scope == "function":
        nodeid = request.node.nodeid
        function_files = trace_files.get("function", {})
        if nodeid not in function_files:
            function_files[nodeid] = []
        function_files[nodeid].append(trace_file_info)


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
