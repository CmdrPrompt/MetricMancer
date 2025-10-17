"""Cross-cutting coordination modules.

This module handles coordination between different analysis aspects:
- HotspotCoordinator: Hotspot analysis coordination
- ReportCoordinator: Report generation coordination
- ReviewCoordinator: Review strategy coordination
"""

from src.app.coordination.hotspot_coordinator import HotspotCoordinator
from src.app.coordination.report_coordinator import ReportCoordinator
from src.app.coordination.review_coordinator import ReviewCoordinator

__all__ = ['HotspotCoordinator', 'ReportCoordinator', 'ReviewCoordinator']
