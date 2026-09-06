from pathlib import Path
import apiclient
import os
import sqlite3

BASE_URL = "https://api.tfl.gov.uk"
API_KEY = os.environ.get("API_KEY")
tfl_client = apiclient.APIClient(BASE_URL, API_KEY)

conn = sqlite3.connect("tfl.db")
tfl_cursor = conn.cursor()
schema = Path("schema.sql").read_text()
tfl_cursor.execute(schema)
conn.commit()
conn.close()


def get_lines_disruptions():
    disruptions_list = tfl_client.fetch("/Line/Mode/tube/Status")
    rows = []

    for disruption in disruptions_list:
        disruption_line = disruption.get("line")
        disruption_name = disruption.get("name")

        for line_status in disruption["lineStatuses"]:
            disruption_severity = line_status["statusSeverity"]
            disruption_severity_description = line_status["statusSeverityDescription"]
            disruption_reason = line_status.get("reason")

            if disruption_severity_description != "Good Service":
                for validity_period in line_status["validityPeriods"]:
                    disruption_created = validity_period["fromDate"]
                    disruption_until = validity_period["toDate"]
                    disruption_is_now = validity_period["isNow"]
                    disruption_category = line_status["disruption"]["category"]
                    disruption_closure_text = line_status["disruption"]["closureText"]

                    rows.append({
                        "line_id": disruption_line,
                        "line_name": disruption_name,
                        "status_severity": disruption_severity,
                        "status_description": disruption_severity_description,
                        "reason": disruption_reason,
                        "category": disruption_category,
                        "closure_text": disruption_closure_text,
                        "valid_from": disruption_created,
                        "valid_to": disruption_until,
                        "is_now": disruption_is_now,
                    })

get_lines_disruptions()


