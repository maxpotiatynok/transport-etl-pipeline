from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import apiclient
import os
import sqlite3

BASE_URL = "https://api.tfl.gov.uk"
API_KEY = os.environ.get("API_KEY")
tfl_client = apiclient.APIClient(BASE_URL, API_KEY)
db_path = Path("~/PycharmProjects/transport-etl-pipeline/tfl.db")

def create_table():
    """
    Establishes a connection to the TfL database and creates a table using the schema file
    """
    conn = sqlite3.connect(db_path)
    tfl_cursor = conn.cursor()
    schema = Path("schema.sql").read_text()
    tfl_cursor.execute(schema)
    conn.commit()
    conn.close()

def get_lines_disruptions():
    """
    All TfL lines statutes are pulled from the API using the APIClient, the data is sorted to columns and rows in the table
    """
    disruptions_list = tfl_client.fetch("/Line/Mode/tube/Status")

    current_time = datetime.now(ZoneInfo("Europe/London")).isoformat()

    for disruption in disruptions_list:
        disruption_line = disruption.get("id")
        disruption_name = disruption.get("name")
        for line_status in disruption["lineStatuses"]:
            disruption_severity = line_status["statusSeverity"]
            disruption_severity_description = line_status["statusSeverityDescription"]
            disruption_reason = line_status.get("reason")
            # Only display disrupted lines
            if disruption_severity_description != "Good Service":
                for validity_period in line_status["validityPeriods"]:
                    disruption_created = validity_period["fromDate"]
                    disruption_isnow = validity_period["isNow"]
                    if disruption_isnow: #isNow is True if the disruption is planned
                        disruption_todate = ""
                    else:
                        disruption_todate = validity_period["toDate"] #End of the planned disruption
                    disruption_closure_text = line_status["disruption"]["closureText"]

                    disruption_conn = sqlite3.connect(db_path)
                    d_cursor = disruption_conn.cursor()
                    d_cursor.execute(
                    '''
                        INSERT INTO RawDisruptions(Line, LineName, StatusSeverity, SeverityDescription,
                            Reason, FromDate, IsPlanned, ToDate, DisruptionClosureText, FetchedAt
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                                     disruption_line, disruption_name, disruption_severity,
                                     disruption_severity_description, disruption_reason,
                                     disruption_created, disruption_isnow, disruption_todate, disruption_closure_text, current_time))
                    disruption_conn.commit()
                    disruption_conn.close()

create_table()
get_lines_disruptions()


