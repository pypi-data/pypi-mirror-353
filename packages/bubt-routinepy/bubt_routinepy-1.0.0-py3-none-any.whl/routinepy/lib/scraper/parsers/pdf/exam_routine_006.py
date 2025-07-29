from io import BytesIO
from itertools import chain
from pathlib import Path

import pdfplumber
from loguru import logger


class Program006ExamPdfParser:
    """
    Extract raw exam table data for the ProgramCode 006 / CSE day from PDF.

    This class extracts the raw exam table data and cleans the empty row cells.

    .. note::
        Till now, the exam routine PDF of CSE day (006) has been the most consistent structure which allowed
        to extract data very easily.
    """

    @logger.catch()
    def extract_raw_tables(self, path: Path | BytesIO) -> list[list[list[str]]]:
        """
        Returns cleaned raw table data from a PDF
        """

        extracted_tables = []
        with pdfplumber.open(path) as pdf:
            logger.info("Started processing exam pdf of CSE day")
            current_table = []
            for page in pdf.pages:
                try:
                    # the default table settings just works ╮(￣_￣)╭
                    page_tables = page.extract_tables()
                    for i in page_tables:
                        table = self._clean_empty_row_cell(i)
                        if not table or len(table) == 0:
                            continue

                        # Gotta handle table break down to multiple pages :/
                        if table[0][0].startswith(("Intake")):
                            if current_table:
                                extracted_tables.append(current_table)
                            current_table = []

                        current_table.extend(table)
                except Exception as e:
                    logger.error(f"Failed to process page {page.page_number}: {e}")

            # almost forgot the last table ~_~
            if current_table:
                extracted_tables.append(current_table)

        logger.info("Finished processing exam pdf of CSE day")

        return extracted_tables

    def _clean_empty_row_cell(self, rows: str) -> list[list[str]]:
        """
        Remove empty cells (None or "") from each row in a 2D list.

        Args:
            rows: 2D list containing values

        Returns:
            List of rows with empty cells removed
        """

        for i, row in enumerate(rows):
            rows[i] = [cell for cell in row if cell not in {None, ""}]
        return rows
