import os
import json
import tempfile
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from shipyard_templates import Spreadsheets, ExitCodeException


class GoogleSheetsClient(Spreadsheets):
    def __init__(self, service_account: str) -> None:
        """
        Initialize the Google Sheets client. Using either a file path or a JSON string for the service account.
        Args:
            service_account: The service account credentials. This can be a file path or a JSON string.
        """
        self.service_account = service_account

    def _set_env_vars(self):
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, "w") as tmp:
            tmp.write(self.service_account)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
        return path

    def connect(self):
        if is_existing_file_path(self.service_account):
            path = self.service_account
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.service_account
        elif is_json_string(self.service_account):
            path = self._set_env_vars()
        else:
            raise ExitCodeException(
                "Invalid service account credentials. Please provide a valid file path or JSON string.",
                self.EXIT_CODE_INVALID_TOKEN,
            )

        creds = service_account.Credentials.from_service_account_file(path)
        service = build("sheets", "v4", credentials=creds)
        drive_service = build("drive", "v3", credentials=creds)

        return service, drive_service

    def fetch(self):
        pass

    def upload(self):
        pass


def is_existing_file_path(string_value: str) -> bool:
    """Checks if the input string is a file path

    Args:
        string_value: The input string to check

    Returns: True if the string is a file path, False otherwise

    """
    return Path(string_value).is_file()


def is_json_string(string_value: str) -> bool:
    """Checks if the input string is a JSON string
    Args:
        string_value: The input string to check
    Returns: True if the string is a JSON string, False otherwise
    """
    string_value = string_value.strip()
    try:
        json.loads(string_value)
    except ValueError:
        return False

    return True
