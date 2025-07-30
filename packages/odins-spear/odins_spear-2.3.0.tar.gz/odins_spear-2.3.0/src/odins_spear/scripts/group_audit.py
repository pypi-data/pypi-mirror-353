def main(api, service_provider_id: str, group_id: str):
    """Audits a group for chargeable services this will return all feature packs
    assigned and count for all broadwork entities such as users, call centers, hunt groups etc.
    Additionaly this will return all DID/DDI's and their active status.

    :param service_provider_id: Service provider or Enterprise ID that contains group being audited.
    :param group_id: Group that is to be audited.

    :return r:
    """

    # save logger from api
    logger = api.logger

    # all Services
    logger.info("Fetching all group services")
    service_report = api.services.get_group_services(group_id, service_provider_id)

    assigned_user_services = []
    assigned_group_services = []
    assigned_service_pack_services = []

    logger.info("Analysing user services")
    for us in service_report["userServices"]:
        if us["usage"] > 0:
            del us["authorized"]
            del us["assigned"]
            del us["limited"]
            del us["quantity"]
            del us["licensed"]
            del us["allowed"]
            del us["userAssignable"]
            del us["groupServiceAssignable"]
            del us["tags"]
            del us["alias"]

            logger.info(f"Fetching users assigned {us}")
            users = api.services.get_group_services_user_assigned(
                group_id, service_provider_id, us["serviceName"], "serviceName"
            )
            userIDs = [u["userId"] for u in users["users"]]
            us["users"] = userIDs

            assigned_user_services.append(us)

    logger.info("Analysing group services")
    for gs in service_report["groupServices"]:
        if gs["usage"] > 0:
            del gs["authorized"]
            del gs["assigned"]
            del gs["limited"]
            del gs["quantity"]
            del gs["licensed"]
            del gs["allowed"]
            del gs["instanceCount"]
            del gs["alias"]
            assigned_group_services.append(gs)

    logger.info("Analysing service packs")
    for sps in service_report["servicePackServices"]:
        if sps["usage"] > 0:
            del sps["authorized"]
            del sps["assigned"]
            del sps["limited"]
            del sps["allowed"]
            del sps["serviceName"]
            del sps["quantity"]
            del sps["alias"]

            logger.info(f"Fetching users assigned {us}")
            users = api.services.get_group_services_user_assigned(
                group_id, service_provider_id, sps["servicePackName"], "servicePackName"
            )
            userIDs = [u["userId"] for u in users["users"]]
            sps["users"] = userIDs

            assigned_service_pack_services.append(sps)

    # Group DNs
    logger.info("Fetching group dns")
    dn_report = api.dns.get_group_dns(service_provider_id, group_id)
    all_dns = {
        "assigned": {"activated": [], "deactivated": []},
        "unassigned": {"activated": [], "deactivated": []},
    }

    logger.info("Analysing group dns")
    for dn in dn_report["dns"]:
        if dn["assigned"] and dn["activated"]:
            all_dns["assigned"]["activated"] += dn["list"]
        elif dn["assigned"] and not dn["activated"]:
            all_dns["assigned"]["deactivated"] += dn["list"]
        elif not dn["assigned"] and dn["activated"]:
            all_dns["unassigned"]["activated"] += dn["list"]
        elif not dn["assigned"] and not dn["activated"]:
            all_dns["unassigned"]["deactivated"] += dn["list"]

    total_assigned_activated = len(all_dns["assigned"]["activated"])
    total_assigned_deactivated = len(all_dns["assigned"]["deactivated"])
    total_unassigned_activated = len(all_dns["unassigned"]["activated"])
    total_unassigned_deactivated = len(all_dns["unassigned"]["deactivated"])
    total_dns = (
        total_assigned_activated
        + total_assigned_deactivated
        + total_unassigned_activated
        + total_unassigned_deactivated
    )

    all_dns["totalDNs"] = total_dns
    all_dns["assigned"]["totalAssignedDNs"] = (
        total_assigned_activated + total_assigned_deactivated
    )
    all_dns["unassigned"]["totalUassignedDNs"] = (
        total_unassigned_activated + total_unassigned_deactivated
    )

    # Group Detail
    group_detail = api.groups.get_group(service_provider_id, group_id)

    # Trunking detail
    logger.info("Fetching trunking capacity")
    try:
        trunk_detail = api.trunk_groups.get_group_trunk_groups_call_capacity(
            service_provider_id, group_id
        )
        del trunk_detail["serviceProviderId"]
        del trunk_detail["groupId"]
    except Exception:
        trunk_detail = []

    group_audit = {
        "groupDetail": group_detail,
        "licenceBreakdown": {
            "userServices": assigned_user_services,
            "groupServices": assigned_group_services,
            "servicePackServices": assigned_service_pack_services,
        },
        "groupDNs": all_dns,
        "groupTrunking": trunk_detail,
    }

    return group_audit
