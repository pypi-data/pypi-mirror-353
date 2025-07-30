# Pull in all fixtures, hooks, and markers by importing everything into the current namespace
# Formatters complain about the wildcard import, so we'll import the modules directly
# from zelos_sdk.pytest.report import pytest_zelos_configure,
from zelos_sdk.pytest.checker import check
from zelos_sdk.pytest.trace import trace_class, trace_function, trace_module, trace_session, zelos_session
import zelos_sdk.pytest.checker as checker
import zelos_sdk.pytest.config as config
import zelos_sdk.pytest.report as report
import zelos_sdk.pytest.trace as trace

_imported_modules = {
    "config": config,
    "report": report,
    "trace": trace,
    "checker": checker,
}


def pytest_addoption(parser):
    """Add options for plugin selection and delegate to enabled plugins"""
    # Delegate to enabled plugins
    for plugin_name, module in _imported_modules.items():
        if hasattr(module, "pytest_addoption"):
            try:
                module.pytest_addoption(parser)
            except Exception as e:
                print(f"Warning: Error calling pytest_addoption for plugin '{plugin_name}': {e}")


def pytest_configure(config):
    """Configure enabled plugins"""
    # Delegate to enabled plugins
    for plugin_name, module in _imported_modules.items():
        if hasattr(module, "pytest_configure"):
            try:
                module.pytest_configure(config)
            except Exception as e:
                print(f"Warning: Error calling pytest_configure for plugin '{plugin_name}': {e}")


def pytest_addhooks(pluginmanager):
    """Add hooks from enabled plugins"""
    # Delegate to enabled plugins
    for plugin_name, module in _imported_modules.items():
        if hasattr(module, "pytest_addhooks"):
            try:
                module.pytest_addhooks(pluginmanager)
            except Exception as e:
                print(f"Warning: Error calling pytest_addhooks for plugin '{plugin_name}': {e}")


__all__ = [
    "check",
    "pytest_addoption",
    "pytest_configure",
    "pytest_addhooks",
    "trace_session",
    "trace_module",
    "trace_function",
    "trace_class",
    "zelos_session",
]
