"""Analytics modules."""
# Analytics are optional and may not be fully implemented
try:
    from .processor import ResultsProcessor
except ImportError:
    ResultsProcessor = None

try:
    from .reports import ReportGenerator
except ImportError:
    ReportGenerator = None

try:
    from .monitoring import MonitoringDashboard
except ImportError:
    MonitoringDashboard = None

__all__ = ['ResultsProcessor', 'ReportGenerator', 'MonitoringDashboard']
