from bs4 import BeautifulSoup

from routinepy.lib.scraper.models import RawClassRoutineTable


class ClassRoutineParser:
    """
    Parser for extracting class routine information from university HTML pages.

    This parser extracts three main components from the HTML structure:

        1. Metadata table (containing routine header information)
        2. Main routine table (containing schedule data)
        3. Faculty table (containing instructor information)
    """

    TABLE_META_SELECTOR = "table#HdtableRtn"
    """CSS selector for the metadata table (contains semester/program info)"""

    def __init__(self, html: str):
        """
        Initialize the :class:`ClassRoutineParser` with HTML content to be parsed.

        :param html: Raw HTML string containing the routine page content.
        :type html: str
        :raises ValueError: If the provided HTML is empty
        """
        if not html.strip():
            raise ValueError("HTML content cannot be empty")
        self.soup = BeautifulSoup(html, "lxml")

    def extract_routine_tables(self) -> list[RawClassRoutineTable]:
        """
        Extract and package all routine table parts from the HTML.

        This method locates and extracts three related HTML tables for each class routine:

            - Metadata table: Contains semester, program and section information.
            - Main routine table: Contains the class schedule.
            - Faculty table: Contains teacher and course details.

        :return: A list of :class:`RawClassRoutineTable` objects, each containing
            the metadata, routine, and faculty tables for a single class routine.
        :rtype: list[RawClassRoutineTable]
        """

        extracted_tables = []
        table_meta = self.soup.select(self.TABLE_META_SELECTOR)
        for table in table_meta:
            routine = table.find_next("table")
            faculty_table = routine.find_next("table")
            extracted_tables.append(
                RawClassRoutineTable(
                    meta=table, routine=routine, faculty_table=faculty_table
                )
            )

        return extracted_tables
