"""
Pulls current status for all tube lines and inserts one row per line
per poll into RawDisruptions table. When a line has multiple simultaneous
statuses, only the most severe is recorded.
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from dotenv import load_dotenv
import apiclient
import os
import sqlite3

BASE_URL = "https://api.tfl.gov.uk"
load_dotenv()
API_KEY = os.environ.get("TFL_API_KEY")
if not API_KEY:
    raise RuntimeError("TFL_API_KEY not set")
tfl_client = apiclient.APIClient(BASE_URL, API_KEY)

def create_table():
    """
    Establishes a connection to the TfL database and creates a table using the schema file
    """
    conn = sqlite3.connect("tfl.db")
    tfl_cursor = conn.cursor()
    schema = Path("schema.sql").read_text()
    tfl_cursor.execute(schema)
    conn.commit()
    conn.close()

def get_lines_disruptions():
    """
    Requests tube line statuses for each line, normalises into SQl rows and timestamps them
    """
    disruptions_list = tfl_client.fetch("/Line/Mode/tube/Status")
    current_time = datetime.now(ZoneInfo("Europe/London")).isoformat()

    disruption_conn = sqlite3.connect("tfl.db")
    d_cursor = disruption_conn.cursor()

    for line in disruptions_list:
        disruption_line = line.get("id")
        disruption_name = line.get("name")

        #Gets the worst disruptions status and outputs it for the selected line
        line_statuses = line.get("lineStatuses", [])
        worst_status = min(
            line_statuses,
            key=lambda ls: ls.get("statusSeverity", 10),
            default={"statusSeverity": 10, "statusSeverityDescription": "Good Service"}
        )

        disruption_severity = worst_status.get("statusSeverity")
        disruption_severity_description = worst_status.get("statusSeverityDescription")
        disruption_reason = worst_status.get("reason")

        disruption_created = None
        disruption_todate = None
        if disruption_severity_description != "Good Service":
            validity_periods = worst_status.get("validityPeriods") or [{}]
            first_period = validity_periods[0]
            disruption_created = first_period.get("fromDate")
            disruption_isnow = first_period.get("isNow")
            if not disruption_isnow: #If isnow = 0, the disruption is planned and TfL set an end time for it
                disruption_todate = first_period.get("toDate")

        d_cursor.execute('''
                         INSERT INTO RawDisruptions(LineID, LineName, ServiceQuality, ServiceQualityDescription,
                                                    Reason, FromDate, ToDate, FetchedAt)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                         ''', (
                             disruption_line, disruption_name, disruption_severity,
                             disruption_severity_description, disruption_reason,
                             disruption_created, disruption_todate, current_time))
        disruption_conn.commit()
    disruption_conn.close()

create_table()
get_lines_disruptions()


