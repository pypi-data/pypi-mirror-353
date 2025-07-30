"""
Report plugin for pytest.

Use via:

  pytest_plugins = ["zelos_sdk.pytest.report"]

"""

from pathlib import Path


def pytest_zelos_configure(config):
    """configure zelos report plugin"""
    # Configure pytest-html to output a report if it's been registered
    if not config.zelos_local_artifacts_dir:
        return

    # Generate the report name from the given format string
    artifact_basename_format = config.getoption("zelos_artifact_basename")
    report_name = artifact_basename_format + "-report"

    # Configure pytest-html to output a report if it's been registered
    if config.pluginmanager.hasplugin("html"):
        # Always generate a self-contained HTML file
        config.option.self_contained_html = True
        config.option.htmlpath = str((Path(config.local_artifacts_dir) / report_name).with_suffix(".html"))


def pytest_html_report_title(report):
    report.title = "Zelos Test Report"
