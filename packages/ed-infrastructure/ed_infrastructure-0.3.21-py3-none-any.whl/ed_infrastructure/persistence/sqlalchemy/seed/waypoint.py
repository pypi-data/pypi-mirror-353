from datetime import UTC, datetime, timedelta

from ed_domain.core.aggregate_roots import Order, Waypoint
from ed_domain.core.aggregate_roots.waypoint import (WaypointStatus,
                                                     WaypointType)

from ed_infrastructure.common.generic import get_new_id


def get_waypoint(sequence: int, order: Order) -> Waypoint:
    return Waypoint(
        id=get_new_id(),
        order=order,
        expected_arrival_time=datetime.now(UTC) + timedelta(days=2),
        actual_arrival_time=datetime.now(UTC) + timedelta(days=2.2),
        sequence=sequence,
        waypoint_type=WaypointType.PICK_UP,
        waypoint_status=WaypointStatus.PENDING,
        create_datetime=datetime.now(UTC),
        update_datetime=datetime.now(UTC),
        deleted_datetime=datetime.now(UTC),
        deleted=False,
    )
