import csv
import os


from ..utils.filers import copy_single_file_to_target_directory
from .report_utils.report_entities import call_records_statistics


def main(
    api: object,
    service_provider_id: str,
    group_id: str,
    start_date: str,
    end_date: str = None,
    start_time: str = "00:00:00",
    end_time: str = "23:59:59",
    time_zone: str = "Z",
):
    """Generates a CSV deatiling each users incoming and outgoing call statistics over 
        a specified period for a single group. Each row contains user extension, user ID, and call stats.

    Args:
        service_provider_id (str):  Service Provider/ Enterprise where group is hosted.
        group_id (str): Target Group you would like to know user statistics for.
        start_date (str): Start date of desired time period. Date must follow format 'YYYY-MM-DD'
        end_date (str, optional): End date of desired time period. Date must follow format 'YYYY-MM-DD'.\
            If this date is the same as Start date you do not need this parameter. Defaults to None.
        start_time (_type_, optional): Start time of desired time period. Time must follow formate 'HH:MM:SS'. \
            If you do not need to filter by time and want the whole day leave this parameter. Defaults to "00:00:00". MAX Request is 3 months.
        end_time (_type_, optional): End time of desired time period. Time must follow formate 'HH:MM:SS'. \
            If you do not need to filter by time and want the whole day leave this parameter. Defaults to "23:59:59". MAX Request is 3 months.
        time_zone (str, optional): A specified time you would like to see call records in. \
    """

    logger = api.logger

    # List of report_entities.call_records_statistics
    group_users_statistics = []

    logger.info(f"Fetching list of users in {group_id}")

    # Fetches complete list of users in group
    logger.info("fetching groups users")
    users = api.users.get_users(service_provider_id, group_id)
    failed_users = []

    # Pulls stats for each user, instantiates call_records_statistics, and append to group_users_statistics
    logger.info("Fetching users call statistics")
    for user in users:
        try:
            user_statistics = api.call_records.get_users_stats(
                user["userId"], start_date, end_date, start_time, end_time, time_zone
            )

            user_services = api.services.get_user_services(user_id=user["userId"])

        except Exception:
            logger.error(f"Failed to fetch {user} statistics - attempt 1/2")
            # attempt 2 in case of connection time out
            try:
                user_statistics = api.call_records.get_users_stats(
                    user["userId"],
                    start_date,
                    end_date,
                    start_time,
                    end_time,
                    time_zone,
                )

                user_services = api.services.get_user_services(user_id=user["userId"])

            except Exception:
                logger.error(f"Failed to fetch {user} statistics - attempt 2/2")
                failed_users.append(user)
                continue

        # Correction for API removing userId if no calls made by user
        if not user_statistics:
            user_statistics = {
                "userId": user["userId"],
                "total": 0,
                "totalAnsweredAndMissed": 0,
                "answeredTotal": 0,
                "missedTotal": 0,
                "busyTotal": 0,
                "redirectTotal": 0,
                "receivedTotal": 0,
                "receivedMissed": 0,
                "receivedAnswered": 0,
                "placedTotal": 0,
                "placedMissed": 0,
                "placedAnswered": 0,
            }

        user_statistics["servicePackServices"] = [
            service["serviceName"]
            for service in user_services["servicePackServices"]
            if service["assigned"]
        ]

        user_statistic_record = call_records_statistics.from_dict(
            user["firstName"], user["lastName"], user["extension"], user_statistics
        )
        group_users_statistics.append(user_statistic_record)

    output_directory = "./os_reports"
    file_name = os.path.join(
        output_directory,
        f"{group_id} User Call Statistics - {start_date} to {end_date}.csv",
    )
    logger.debug(f"Filename {file_name}")

    # Ensure the directory exists
    os.makedirs(output_directory, exist_ok=True)
    logger.debug("Directory exists")

    # Write statistics to csv
    logger.info("Writing report")
    with open(file_name, mode="w", newline="") as file:
        fieldnames = [
            field.name
            for field in call_records_statistics.__dataclass_fields__.values()
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for user in group_users_statistics:
            writer.writerow(user.__dict__)

        # Adds list of failed users to the bottom
        if failed_users:
            writer.writerow({})
            writer.writerow({fieldnames[1]: "Failed Users"})

            for failed_user in failed_users:
                writer.writerow({fieldnames[1]: failed_user["userId"]})

    # Add made_with_os.png for output
    copy_single_file_to_target_directory(
        "./odins_spear/assets/images/", "./os_reports/", "made_with_os.png"
    )
    logger.info(f"Report {file_name} saved to /os_reports")

    return True
