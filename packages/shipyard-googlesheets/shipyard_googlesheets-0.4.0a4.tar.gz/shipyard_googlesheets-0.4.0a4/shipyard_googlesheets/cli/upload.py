import argparse
import os
import socket
import sys

from shipyard_bp_utils import files as shipyard
from shipyard_templates import ShipyardLogger, Spreadsheets, ExitCodeException

from shipyard_googlesheets import exceptions, GoogleSheetsClient

logger = ShipyardLogger.get_logger()

socket.setdefaulttimeout(600)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-file-name", dest="source_file_name", required=True)
    parser.add_argument(
        "--source-folder-name", dest="source_folder_name", default="", required=False
    )
    parser.add_argument(
        "--destination-file-name", dest="file_name", default="", required=False
    )
    parser.add_argument(
        "--starting-cell", dest="starting_cell", default="A1", required=False
    )
    parser.add_argument("--tab-name", dest="tab_name", default=None, required=False)
    parser.add_argument(
        "--service-account",
        dest="gcp_application_credentials",
        default=None,
        required=False,
    )
    parser.add_argument("--drive", dest="drive", default=None, required=False)
    return parser.parse_args()


def main():
    try:
        args = get_args()
        file_name = shipyard.combine_folder_and_file_name(
            folder_name=args.source_folder_name,
            file_name=args.source_file_name,
        )

        tab_name = args.tab_name
        starting_cell = args.starting_cell or "A1"
        drive = args.drive

        if not os.path.isfile(file_name):
            raise FileNotFoundError(f"{file_name} does not exist")

        client = GoogleSheetsClient(args.gcp_application_credentials)

        spreadsheet_id = client.get_spreadsheet_id_by_name(
            file_name=file_name, drive=drive
        )
        if not spreadsheet_id:
            if len(file_name) >= 44:
                spreadsheet_id = file_name
            else:
                raise exceptions.InvalidSheetError(file_name)

        # check if workbook exists in the spreadsheet
        client.upload(
            file_name=file_name,
            source_full_path=file_name,
            spreadsheet_id=spreadsheet_id,
            tab_name=tab_name,
            starting_cell=starting_cell,
        )
    except FileNotFoundError as e:
        logger.error(e)
        sys.exit(Spreadsheets.EXIT_CODE_FILE_NOT_FOUND)
    except ExitCodeException as e:
        logger.error(e)
        sys.exit(e.exit_code)
    except Exception as e:
        logger.error(f"An unexpected error occurred\n{e}")
        sys.exit(Spreadsheets.EXIT_CODE_UNKNOWN_ERROR)


if __name__ == "__main__":
    main()
