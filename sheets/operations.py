import time
import pandas as pd
from typing import List, Dict, Tuple, Optional

from sheets.auth import SheetsAuthenticator
from utils.logger import logger
import config


class SheetsOperations:

    def __init__(self):
        self.auth = SheetsAuthenticator()
        self.service = None
        self.sheet_ids: Dict[str, int] = {}

    def initialize(self):
        self.service = self.auth.authenticate()
        self.sheet_ids = self._get_sheet_ids()

    def _get_sheet_ids(self) -> Dict[str, int]:
        """
        Get sheet IDs for all configured sheets

        Returns:
            Dictionary mapping sheet name to sheet ID
        """
        metadata = (
            self.service.spreadsheets()
            .get(spreadsheetId=config.SPREADSHEET_ID)
            .execute()
        )

        sheet_ids = {}
        for sheet in metadata["sheets"]:
            title = sheet["properties"]["title"]
            if title in config.SHEET_NAMES:
                sheet_ids[title] = sheet["properties"]["sheetId"]

        return sheet_ids

    def get_sheet_data(self, sheet_name: str) -> List[List[str]]:
        """
        Get all data from a sheet

        Args:
            sheet_name: Name of the sheet

        Returns:
            2D list of cell values
        """
        result = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=config.SPREADSHEET_ID, range=f"{sheet_name}!A:D")
            .execute()
        )
        return result.get("values", [])

    def delete_rows(self, sheet_name: str, rows_to_delete: List[int]) -> None:
        """
        Delete specified rows from sheet

        Args:
            sheet_name: Name of the sheet
            rows_to_delete: List of 0-indexed row numbers to delete
        """
        if not rows_to_delete:
            return

        sheet_id = self.sheet_ids.get(sheet_name)
        if sheet_id is None:
            logger.error(f"Sheet '{sheet_name}' not found")
            return

        rows_to_delete = sorted(set(rows_to_delete), reverse=True)

        requests = []
        for row_index in rows_to_delete:
            requests.append(
                {
                    "deleteDimension": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "ROWS",
                            "startIndex": row_index,
                            "endIndex": row_index + 1,
                        }
                    }
                }
            )

        body = {"requests": requests}
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=config.SPREADSHEET_ID, body=body
        ).execute()

        # Only log from the caller with sheet name context
        time.sleep(2)

    def format_columns(self, sheet_name: str) -> None:
        """
        Format columns B and C with borders and left alignment

        Args:
            sheet_name: Name of the sheet
        """
        sheet_id = self.sheet_ids.get(sheet_name)
        if sheet_id is None:
            logger.error(f"Sheet '{sheet_name}' not found")
            return

        result = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=config.SPREADSHEET_ID, range=f"{sheet_name}!B:C")
            .execute()
        )
        values = result.get("values", [])

        if not values:
            return

        requests = []

        for row_idx, row in enumerate(values):
            for col_idx in range(min(2, len(row))):
                cell_value = row[col_idx].strip() if col_idx < len(row) else ""

                if not cell_value:
                    continue

                requests.append(
                    {
                        "updateCells": {
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": row_idx,
                                "endRowIndex": row_idx + 1,
                                "startColumnIndex": col_idx + 1,
                                "endColumnIndex": col_idx + 2,
                            },
                            "fields": "userEnteredFormat(horizontalAlignment,borders)",
                            "rows": [
                                {
                                    "values": [
                                        {
                                            "userEnteredFormat": {
                                                "horizontalAlignment": "LEFT",
                                                "borders": {
                                                    "left": {
                                                        "style": "SOLID",
                                                        "color": {
                                                            "red": 0,
                                                            "green": 0,
                                                            "blue": 0,
                                                        },
                                                    },
                                                    "right": {
                                                        "style": "SOLID",
                                                        "color": {
                                                            "red": 0,
                                                            "green": 0,
                                                            "blue": 0,
                                                        },
                                                    },
                                                    "top": {
                                                        "style": "SOLID",
                                                        "color": {
                                                            "red": 0,
                                                            "green": 0,
                                                            "blue": 0,
                                                        },
                                                    },
                                                    "bottom": {
                                                        "style": "SOLID",
                                                        "color": {
                                                            "red": 0,
                                                            "green": 0,
                                                            "blue": 0,
                                                        },
                                                    },
                                                },
                                            }
                                        }
                                    ]
                                }
                            ],
                        }
                    }
                )

        if requests:
            for i in range(0, len(requests), 50):
                batch = requests[i : i + 50]
                body = {"requests": batch}
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=config.SPREADSHEET_ID, body=body
                ).execute()
                time.sleep(1)

            logger.info(f"  ✅ Formatted {len(requests)} cells")


def should_delete_row(
    handle: str,
    contest_configs: List[Tuple[str, str, Optional[int]]],
    dfs: Dict[str, pd.DataFrame],
    global_threshold: int,
) -> Tuple[bool, Dict]:
    """
    Determine if a row should be deleted based on performance thresholds

    Args:
        handle: Participant handle
        contest_configs: List of contest configurations
        dfs: Dictionary mapping contest name to DataFrame
        global_threshold: Minimum total problems across all contests

    Returns:
        Tuple of (should_delete: bool, details: dict)
    """
    if not handle or not handle.strip():
        return True, {"error": "Empty handle"}

    handle = handle.strip()
    details = {}
    total_across_contests = 0
    failed_thresholds = []

    for contest_config in contest_configs:
        contest_name = contest_config[0]
        contest_threshold = contest_config[2] if len(contest_config) > 2 else None

        df = dfs[contest_name]

        if handle in df["Handle"].values:
            total_solved = df[df["Handle"] == handle].iloc[0]["Total_Solved"]
        else:
            total_solved = 0

        total_across_contests += total_solved

        meets_threshold = True
        if contest_threshold is not None:
            meets_threshold = total_solved >= contest_threshold
            if not meets_threshold:
                failed_thresholds.append(
                    (contest_name, total_solved, contest_threshold)
                )

        details[contest_name] = {
            "total_solved": total_solved,
            "threshold": contest_threshold,
            "meets_threshold": meets_threshold,
        }

    details["total_all_contests"] = total_across_contests
    details["failed_thresholds"] = failed_thresholds

    # Delete if failed any threshold OR total below global threshold
    should_delete = (len(failed_thresholds) > 0) or (
        total_across_contests < global_threshold
    )

    return should_delete, details


def clean_google_sheets(dfs: Dict[str, pd.DataFrame]) -> None:
    """
    Clean Google Sheets by deleting rows below thresholds

    Args:
        dfs: Dictionary mapping contest name to DataFrame
    """
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: CLEANING GOOGLE SHEETS")
    logger.info(f"Global Threshold: {config.GLOBAL_THRESHOLD}")
    logger.info("=" * 60)

    sheets = SheetsOperations()
    sheets.initialize()

    logger.info("✅ Authenticated\n")

    total_deleted = 0

    # Process each sheet
    for sheet_name in config.SHEET_NAMES:
        logger.info("\n" + "=" * 60)
        logger.info(f"Processing Sheet: '{sheet_name}'")
        logger.info("=" * 60)

        data = sheets.get_sheet_data(sheet_name)

        if not data or len(data) < 4:
            logger.warning("  ⚠️  No data rows")
            continue

        rows_to_delete = []

        # Check each row (skip first 3 header rows)
        for row_idx in range(3, len(data)):
            row = data[row_idx]

            handle = row[2].strip() if len(row) > 2 else None

            if not handle:
                continue

            should_delete, details = should_delete_row(
                handle, config.CONTESTS, dfs, config.GLOBAL_THRESHOLD
            )

            if should_delete:
                rows_to_delete.append(row_idx)

        if rows_to_delete:
            sheets.delete_rows(sheet_name, rows_to_delete)
            total_deleted += len(rows_to_delete)
            logger.info(f"  ✅ Deleted {len(rows_to_delete)} rows from '{sheet_name}'")
        else:
            logger.info(f"  ✅ No rows to delete in '{sheet_name}'")

    logger.info(f"\n✅ Total deleted: {total_deleted} rows\n")

    logger.info("=" * 60)
    logger.info("STEP 3: FORMATTING COLUMNS")
    logger.info("=" * 60)

    for sheet_name in config.SHEET_NAMES:
        logger.info(f"\n📋 Formatting '{sheet_name}'...")
        sheets.format_columns(sheet_name)

    logger.info("✅ Formatting complete!")
