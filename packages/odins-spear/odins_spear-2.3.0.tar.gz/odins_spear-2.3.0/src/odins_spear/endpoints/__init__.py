from .administrators import Administrators
from .alternate_numbers import AlternateNumbers
from .announcements import Announcements
from .authentication import Authentication
from .auto_attendant import AutoAttendants
from .call_centers import CallCenters
from .call_forwarding_always import CallForwardingAlways
from .call_processing_policies import CallProcessingPolicies
from .call_pickup import CallPickup
from .call_fowarding_selective import CallForwardingSelective
from .call_forwarding_not_reachable import CallForwardingNotReachable
from .call_forwarding_no_answer import CallForwardingNoAnswer
from .call_forwarding_busy import CallForwardingBusy
from .call_records import CallRecords
from .devices import Devices
from .dns import DNs
from .groups import Groups
from .emergency_zones import EmergencyZones
from .do_not_disturb import DoNotDisturb
from .hunt_groups import HuntGroups
from .service_providers import ServiceProviders
from .services import Services
from .session import Session
from .shared_call_appearance import SharedCallAppearance
from .schedules import Schedules
from .reports import Reports
from .registration import Registration
from .password_generate import PasswordGenerate
from .trunk_groups import TrunkGroups
from .users import Users

__all__ = [
    "Administrators",
    "AlternateNumbers",
    "Announcements",
    "Authentication",
    "AutoAttendants",
    "CallCenters",
    "CallForwardingAlways",
    "CallProcessingPolicies",
    "CallPickup",
    "CallForwardingSelective",
    "CallForwardingNotReachable",
    "CallForwardingNoAnswer",
    "CallForwardingBusy",
    "CallRecords",
    "Devices",
    "DNs",
    "Groups",
    "EmergencyZones",
    "DoNotDisturb",
    "HuntGroups",
    "ServiceProviders",
    "Services",
    "Session",
    "SharedCallAppearance",
    "Schedules",
    "Reports",
    "Registration",
    "PasswordGenerate",
    "TrunkGroups",
    "Users",
]


# import importlib
# import pkgutil

# # Get the package name dynamically
# package_name = __name__

# # Iterate over all modules in the `endpoints` directory
# for _, module_name, _ in pkgutil.iter_modules(__path__):
#     if module_name != "base_endpoint":  # Exclude base_endpoint.py
#         importlib.import_module(f"{package_name}.{module_name}")
