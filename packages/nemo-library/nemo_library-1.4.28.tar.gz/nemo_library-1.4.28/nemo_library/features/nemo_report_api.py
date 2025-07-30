from nemo_library.features.nemo_persistence_api import getProjectID
from nemo_library.utils.config import Config
from nemo_library.utils.utils import log_error

import pandas as pd
import requests


import json
import logging


def LoadReport(
    config: Config,
    projectname: str,
    report_guid: str = None,
    report_name: str = None,
    data_types: dict[str] = None,
) -> pd.DataFrame:
    """
    Loads a report from a specified project and returns the data as a Pandas DataFrame.

    Args:
        config (Config): Configuration object containing connection details and headers.
        projectname (str): The name of the project from which to load the report.
        report_guid (str): The unique identifier (GUID) of the report to be loaded.
        max_pages (int, optional): Reserved for future use to limit the number of pages in the report.

    Returns:
        pd.DataFrame: The report data as a Pandas DataFrame.

    Raises:
        RuntimeError: If the report initialization or data download fails.
        ValueError: If the downloaded data cannot be processed into a DataFrame.

    Notes:
        - Fetches the project ID using `getProjectID`.
        - Sends an HTTP POST request to initialize the report and retrieve a CSV download URL.
        - Downloads the CSV file and converts it into a Pandas DataFrame.
        - Removes the `_RECORD_COUNT` column if present in the dataset.
        - Logs errors and raises exceptions for failed requests or data processing issues.
    """

    project_id = getProjectID(config=config, projectname=projectname)
    headers = config.connection_get_headers()

    # if name was given, we have to resolve this into a guid
    if report_name:
        response = requests.get(
            config.get_config_nemo_url()
            + "/api/nemo-persistence/metadata/Reports/project/{projectId}/reports".format(
                projectId=project_id
            ),
            headers=headers,
        )
        resultjs = json.loads(response.text)
        df = pd.json_normalize(resultjs)
        df = df[df["displayName"] == report_name]
        if df.empty:
            log_error(f"could not find report '{report_name}' in project {projectname}")
        report_guid = df.iloc[0]["id"]

    logging.info(f"Loading report: {report_guid} from project {projectname}")

    # INIT REPORT PAYLOAD (REQUEST BODY)
    report_params = {"id": report_guid, "project_id": project_id}

    response_report = requests.post(
        config.get_config_nemo_url() + "/api/nemo-report/report_export",
        headers=headers,
        json=report_params,
    )

    if response_report.status_code != 200:
        log_error(
            f"Request failed. Status: {response_report.status_code}, error: {response_report.text}"
        )

    # Extract download URL from response
    csv_url = response_report.text.strip('"')
    logging.info(f"Downloading CSV from: {csv_url}")

    # Download the file into pandas
    result = pd.DataFrame()
    try:
        # if parameter data_types is given, we add it to the "read_csv" call
        if data_types:
            result = pd.read_csv(
                csv_url,
                sep=",",
                quotechar='"',
                escapechar="\\",
                dtype=data_types,
                keep_default_na=False,
            )
        else:
            # if no data_types are given, we read the csv without dtype
            result = pd.read_csv(csv_url, sep=",", quotechar='"', escapechar="\\")
        if "_RECORD_COUNT" in result.columns:
            result.drop(columns=["_RECORD_COUNT"], inplace=True)
    except Exception as e:
        log_error(f"Download failed. Status: {e}")
    return result
