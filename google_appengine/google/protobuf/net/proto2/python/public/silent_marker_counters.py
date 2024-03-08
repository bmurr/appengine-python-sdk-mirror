"""Wrapper to make silent marker logging a noop on unsupported platforms.

Certain uses, such as embedded python and exoblaze, are unable to use pybind11.
See go/redact-debug-string for details.
"""

try:
  # pylint: disable=g-import-not-at-top
  from google.net.proto2.python.public import silent_marker_counters_pybind
  import_success = True
except ImportError:
  import_success = False


def IncrementTextFormatParsingCounter():
  if import_success:
    silent_marker_counters_pybind.IncrementTextFormatParsingCounter()


def IncrementSilentMarkerDetectedCounter():
  if import_success:
    silent_marker_counters_pybind.IncrementSilentMarkerDetectedCounter()
