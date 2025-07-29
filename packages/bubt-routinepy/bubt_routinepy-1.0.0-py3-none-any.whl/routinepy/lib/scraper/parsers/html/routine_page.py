from typing import Optional
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup, Tag
from loguru import logger

from ...scraper_utils import normalize_url


class RoutinePageParser:
    """
    A parser for extracting routine information from university web pages.

    This class contains CSS selectors used to locate and extract different types
    of routines (regular class, exams, supplementary exams) from the
    `university's webpage <https://bubt.edu.bd/home/routines>`_
    """

    # Container selectors
    ROUTINE_CONTAINER_SELECTOR = "div#accordion.panel-group"
    """CSS Selector of the main container element holding all routine sections"""
    CLASS_ACCORDION_SELECTOR = "div#accordionClassRoutine"
    """CSS Selector of the container specifically for class routine table"""
    EXAM_ACCORDION_SELECTOR = "div#Exam_Routine"
    """CSS Selector of the container specifically for exam routine table"""
    SUP_EXAM_ACCORDION_SELECTOR = "div#Sup_Exam_Routine"
    """CSS Selector of the container specifically for supplementary exam routine table"""

    # Cell selectors
    EXAM_NAME_CELL_SELECTOR = "td:nth-child(1)"
    """
    CSS selector for exam name cells in tables
    Targets the first column of exam routine tables for name
    """

    CLASS_LINK_SELECTOR = "a.btn.btn-primary"
    """
    CSS selector for class routine links
    Targets primary button-style link for getting `View` link
    """

    def __init__(self, html: str):
        """
        Initialize the :class:`RoutinePageParser` with HTML content to be parsed.

        :param html: Raw HTML string containing the routine page content.
        :type html: str
        :raises ValueError: If the provided HTML is empty
        """
        if not html.strip():
            raise ValueError("HTML content cannot be empty")
        self.soup = BeautifulSoup(html, "lxml")

    def get_class_routine_links(self):
        """
        Extract class routine links of all programs

        Parses the HTML table identified by :attr:`CLASS_ACCORDION_SELECTOR` to retrieve
        a title and a list of links of class routine.

        :return:
            A dictionary containing:
                - **title** (*str*) - The title of the class routine section.
                - **links** (*list[dict]*) - A list of dictionaries, each with:
                    - **program_code** (*str*) - The academic program code.
                    - **semester_code** (*str*) - The semester code.
                    - **link** (*str*) - The URL to the class routine.
        :rtype: dict[str, list[dict[str,str]]]

        **Example Output:**

        .. code-block:: python

            {
                "title": "Class Routine of Spring 2025",
                "links": [
                    {
                        "program_code": "001",
                        "semester_code": "610,064",
                        "link": "https://annex.bubt.edu.bd/global_file/routine.php?p=001&semNo=610,064",
                    },
                    {
                        "program_code": "006",
                        "semester_code": "610,064",
                        "link": "https://annex.bubt.edu.bd/global_file/routine.php?p=006&semNo=610,064",
                    },
                ],
            }
        """
        return self._parse_routine_table(self.CLASS_ACCORDION_SELECTOR, is_class=True)

    def get_exam_routine_links(self):
        """
        Extract exam routine links of all programs

        Parses the HTML table identified by :attr:`EXAM_ACCORDION_SELECTOR` to retrieve
        a title and a list of links to exam routine.

        :raises ValueError: Exam routine container is not found in the HTML
        :raises RuntimeError: Parsing fails due to invalid table structure or data
        :return:
            A dictionary containing:
                - **title** (*str*) - The title of the exam routine section.
                - **links** (*list[dict]*) - A list of dictionaries, each mapping an exam name
                    (str) to a list of dictionaries with link names and normalized URLs.
        :rtype: dict[str, list[dict]]

        **Example Output:**

        .. code-block:: python

            {
                "title": "Final Exam Schedule, Spring 2025",
                "links": [
                    {
                        "Day Program": [
                            {
                                "CSE Program": "https://www.bubt.edu.bd/assets/frontend/uploads/CSE_MODIFY_12_12_12.pdf"
                            },
                            {
                                "Other Programs": "https://www.bubt.edu.bd/assets/frontend/uploads/Semester_Final_Examination_Schedule_Fall_2024_-for_students-3rd_Revised_docx.pdf"
                            },
                        ]
                    },
                    {
                        "Evening Program": [
                            {
                                "Download": "https://www.bubt.edu.bd/assets/frontend/uploads/updated_Final_Examination_Schedule,_Spring_2025,_Evening_Program.pdf"
                            }
                        ]
                    },
                ],
            }
        """
        return self._parse_routine_table(self.EXAM_ACCORDION_SELECTOR)

    def get_sup_exam_routine_links(self):
        """
        Extract supplementary exam routine links for all programs.

        Parses the HTML table identified by :attr:`SUP_EXAM_ACCORDION_SELECTOR` to retrieve
        a title and a list of links to supplementary exam routine.

        :raises ValueError: Exam routine container is not found in the HTML
        :raises RuntimeError: Parsing fails due to invalid table structure or data
        :return:
            A dictionary containing:
                - **title** (*str*) - The title of the supplementary exam routine section.
                - **links** (*list[dict]*) - A list of dictionaries, each mapping an exam name
                    (str) to a list of dictionaries with link names and normalized URLs.
        :rtype: dict[str, list[dict]]

        **Example Output:**

        .. code-block:: python

            {
                "title": "Supplementary Mid-Term Exam Schedule, Spring 2025",
                "links": [
                    {
                        "Day Program": [
                            {
                                "Click here": "https://www.bubt.edu.bd/assets/frontend/uploads/Day_Program_Supplementry_Mid-Terml_Routine_Spring,_2025.pdf"
                            }
                        ]
                    },
                    {
                        "Evening Program": [
                            {
                                "Click here": "https://www.bubt.edu.bd/assets/frontend/uploads/Supplementary_Spring,_2025_Mid-Term_Examination_Evening_(NB)_.pdf"
                            }
                        ]
                    },
                ],
            }
        """

        return self._parse_routine_table(self.SUP_EXAM_ACCORDION_SELECTOR)

    @staticmethod
    def _extract_prog_and_sem_no(query_params: dict) -> dict[str, str]:
        """
        Extract program and semester codes from URL query parameters.

        :param query_params: Parsed query parameters from a URL (from parse_qs)
        :type query_params: dict
        :return:
            A dictionary containing:
        :rtype: dict[str, str]

        **Example**:

        .. code-block:: python

            >>> self._extract_prog_and_sem_no({'p': ['006'], 'semNo': ['610,064']})
            {'program_code': '006', 'semester_code': '610,064'}
        """
        program_code = query_params.get("p", [""])[0]
        semester_code = query_params.get("semNo", [""])[0]
        return {"program_code": program_code, "semester_code": semester_code}

    @staticmethod
    def _extract_title(container: Tag) -> str:
        """
        Extract the title of a routine table.

        Args:
            container (Tag): A BeautifulSoup Tag object containing the table.

        Returns:
            str: The text of the h2 tag within the container, or "Untitled" if not found.
        """

        title_tag = container.select_one("h2")
        return title_tag.get_text(strip=True) if title_tag else "Untitled"

    @logger.catch()
    def _parse_routine_table(
        self,
        container_id: str,
        is_class: bool = False,
    ) -> dict[str, str]:
        """
        Parse a routine table to extract its title and links.

        Args:
            container_id (str): CSS selector for the table container (e.g., `div#accordionClassRoutine`).
            is_class (bool, optional): If True, parse as class routine table; otherwise, parse as exam routine table. Defaults to False.

        Returns:
            dict: A dictionary containing:
                - title (str): The title of the routine table.
                - links (list[dict]): A list of link data dictionaries (structure depends on is_class).

        Raises:
            ValueError: If the specified container is not found in the HTML.
        """

        container = self.soup.select_one(container_id)
        if not container:
            raise ValueError(f"Routine container {container_id} not found")

        title = self._extract_title(container)
        links = self._parse_links(container, is_class=is_class)

        return {"title": title, "links": links}

    def _parse_links(
        self,
        container: Tag,
        is_class: bool = False,
    ) -> list[dict[str, str]]:
        """
        Extract and normalize links from a routine table.

        Args:
            container (Tag): A BeautifulSoup Tag object containing the table.
            is_class (bool, optional): If True, parse links as class routines; otherwise, parse as exam routines. Defaults to False.

        Returns
        -------
        list
            A list of dictionaries containing link data:
                - For class routines, each dictionary has program_code, semester_code, and link.
                - For exam routines, each dictionary maps an exam name to a list of name-URL pairs.
        """

        links = []
        for row in container.select("table > tbody > tr"):
            if is_class:
                link = self._parse_class_row_link(row)
            else:
                link = self._parse_exam_row_link(row)

            if link:
                links.append(link)
        return links

    def _parse_class_row_link(self, row: Tag) -> Optional[dict[str, str]]:
        """
        Parse a class routine table row to extract link data.

        Args:
            row (Tag): A BeautifulSoup Tag object representing a table row.

        Returns
        -------
        dict
            A dictionary with keys:
                - program_code (str): The academic program code.
                - semester_code (str): The semester code.
                - link (str): The URL to the class routine.
        None
            if the row lacks a valid link or query parameters.
        """

        link_tag = row.select_one(self.CLASS_LINK_SELECTOR)
        if not link_tag or not (link := link_tag.get("href")):
            return None

        parsed_url = urlparse(link)
        if not parsed_url.query:
            return None
        query_params = parse_qs(parsed_url.query)
        if not query_params:
            return None

        meta = self._extract_prog_and_sem_no(query_params)
        meta["link"] = link

        return meta

    def _parse_exam_row_link(
        self,
        row: Tag,
    ) -> dict[str, str]:
        """
        Parse an exam routine table row to extract link data.

        Args:
            row (Tag): A BeautifulSoup Tag object representing a table row.

        Returns
        -------
        dict
            A dictionary mapping the exam name (str) to a list of dictionaries, each
            containing a link name and its normalized URL.
        None
            if the row lacks a valid name cell.
        """

        name_cell = row.select_one(self.EXAM_NAME_CELL_SELECTOR)
        if not name_cell:
            return None
        name_cell = name_cell.get_text(strip=True)

        links = row.find_all("a")
        urls = list()
        for i in links:
            link = i.get("href")
            name = i.get_text(strip=True).split()
            name = " ".join(name)
            if link:
                urls.append({name: normalize_url(link)})

        return {name_cell: urls}
