from loguru import logger

from routinepy.consts import ROUTINE_PAGE_URL
from routinepy.lib.api.enums import ProgramCode
from routinepy.lib.models import ClassPeriod, TermExam
from routinepy.lib.scraper.parsers.html import ClassRoutineParser, RoutinePageParser
from routinepy.lib.scraper.parsers.pdf import BaseExamPdfParser
from routinepy.lib.scraper.scraper_utils import (
    filter_periods,
    get_shift_name,
    reverse_program_code,
)
from routinepy.lib.scraper.transformers import (
    BaseExamTableTransformer,
    ClassRoutineTableTransformer,
)
from routinepy.lib.utils.http import make_get_request


class ScraperClient:
    """
    Client for fetching routine data through web scraping the BUBT webpage
    """

    @logger.catch()
    async def get_routine_links(self):
        """
        Extract the links for class, exam, and supplementary exam routines from the
        `university's webpage <https://bubt.edu.bd/home/routines>`_

        :raises ValueError: Failed to get routine webpage
        :return: A dictionary containing three categories of routine links:

            - ``class``: A dictionary with a ``links`` key containing a list of dictionaries,
                each with ``program_code`` (str) and ``link`` (str) for class routines.

            - ``exam``: A dictionary with a ``links`` key containing a list of dictionaries,
                each mapping shift names to program-specific exam routine links.

            - ``sup_exam``: A dictionary with a ``links`` key containing a list of supplementary exam routine links.
        :rtype: dict
        """
        routine_html = await make_get_request(ROUTINE_PAGE_URL)
        if not routine_html:
            raise ValueError("Failed to get routine webpage")

        parser = RoutinePageParser(routine_html)

        class_links = parser.get_class_routine_links()
        exam_links = parser.get_exam_routine_links()
        sup_exam_links = parser.get_sup_exam_routine_links()

        return {"class": class_links, "exam": exam_links, "sup_exam": sup_exam_links}

    @logger.catch()
    async def get_class_routine(
        self,
        program_code: ProgramCode,
        course_code: str = None,
        faculty_code: str = None,
        intake: str = None,
        section: str = None,
    ) -> list[ClassPeriod] | None:
        """
        Get class routine data based on provided filters.

        :param program_code: The program code to filter by (e.g., `006`, `001`)
        :type program_code: ProgramCode
        :param course_code: The course code to filter by (e.g., `CSE 101`, `CSE 331`), defaults to None
        :type course_code: str, optional
        :param faculty_code: The faculty member code to filter by (e.g., `MDI`, `MAFI` ), defaults to None
        :type faculty_code: str, optional
        :param intake: The intake number to filter by (e.g., `49`, `50`), defaults to None
        :type intake: str, optional
        :param section: The section number to filter by (e.g., `1`, `2`), defaults to None
        :type section: str, optional
        :raises ValueError: If invalid or incompatible filter combinations are provided
        :return: A list of filtered ClassPeriod objects representing the class routine
        :rtype: list[ClassPeriod] | None

        .. note::
            - Program codes follow the university's standard numbering system
            - Filtering by room number is not implemented as we need to download the routines of all programs.
        """
        if section and not intake:
            raise ValueError("Intake is required when filtering by section")

        try:
            html = await self.get_class_routine_html(program_code)
        except Exception as e:
            msg = f"Failed to download routine HTML for program code {program_code}"
            logger.error(f"{msg}: {e}")
            raise ValueError(msg) from e

        if not html.strip():
            logger.error("Received empty response from BUBT")
            return None

        parser = ClassRoutineParser(html=html)
        table_htmls = parser.extract_routine_tables()
        if not table_htmls:
            logger.error(
                f"No routine raw HTML tables found for program code {program_code}"
            )
            return None

        tables = ClassRoutineTableTransformer().transform_to_models(
            table_htmls, program_code
        )
        if not tables:
            logger.error(f"No routine tables found for program code {program_code}")
            return None

        return filter_periods(tables, course_code, faculty_code, intake, section)

    @logger.catch()
    async def get_exam_routine(
        self,
        program_code: ProgramCode,
        course_code: str = None,
        faculty_code: str = None,
        intake: str = None,
        section: str = None,
    ) -> list[TermExam] | None:
        """
        Get exam routine data based on provided filters.

        :param program_code: The program code to filter by (e.g., `006`, `001`)
        :type program_code: ProgramCode
        :param course_code: The course code to filter by (e.g., `CSE 101`, `CSE 331`), defaults to None
        :type course_code: str, optional
        :param faculty_code: The faculty member code to filter by (e.g., `MDI`, `MAFI` ), defaults to None
        :type faculty_code: str, optional
        :param intake: The intake number to filter by (e.g., `49`, `50`), defaults to None
        :type intake: str, optional
        :param section: The section number to filter by (e.g., `1`, `2`), defaults to None
        :type section: str, optional
        :raises ValueError: If invalid or incompatible filter combinations are provided
        :return: A list of filtered TermExam objects representing the exam routine
        :rtype: list[TermExam] | None

        .. note::
            - Program codes follow the university's standard numbering system
            - Filtering by room number is not implemented as it's not possible *yet* to extract and parse varities of routine PDFs.
        .. warning::
            - Only `ProgramCode.CSE_DAY` is currently supported
        """
        if section and not intake:
            raise ValueError("Intake is required when filtering by section")

        # pdf_link = await self.get_exam_routine_pdf_link(program_code)
        pdf_link = "http://localhost:8001/CSE_DAY_4_3_2025.pdf"
        if not pdf_link:
            logger.error(f"No exam pdf link found for program code {program_code}")
            return

        try:
            pdf_path = await make_get_request(pdf_link, is_file=True)
            if not pdf_path:
                raise ValueError("Exam PDF download failed.")
        except Exception:
            logger.error(f"Failed to download the exam routine PDF: {pdf_link}")
            return

        pdf_raw_tables = BaseExamPdfParser().extract_raw_tables(program_code, pdf_path)
        if not pdf_raw_tables:
            raise NotImplementedError(
                f"Sorry, exam routine parser for program {program_code} is not implemented, Try using the API",
            )

        tables = BaseExamTableTransformer().transform_to_models(
            tables=pdf_raw_tables, program_code=program_code
        )
        if not tables:
            raise NotImplementedError(
                f"Sorry, exam routine pdf transformer for program {program_code} is not implemented, Try using the API",
            )

        return filter_periods(tables, course_code, faculty_code, intake, section)

    @logger.catch()
    async def get_class_routine_html(self, program_code: ProgramCode):
        """
        Get HTML content for a specific class routine

        :param program_code: The program code to filter by (e.g., `006`, `001`)
        :type program_code: ProgramCode
        :raises ValueError: no class routine links are found
        :raises ValueError: the routine cannot be downloaded
        :raises ValueError: class routine for program not found
        :return: HTML content of the class routine
        :rtype: str
        """
        logger.info(f"Fetching class routine HTML for program code {program_code}")

        routine_links = await self.get_routine_links()
        links = routine_links.get("class", {}).get("links")
        if not links:
            raise ValueError("No class routine links found")

        for i in links:
            if i["program_code"] == program_code:
                link = i["link"]
                if link.endswith(".pdf"):
                    raise ValueError(
                        f"Unsupported class routine url for program code {program_code}: {link}"
                    )

                return await make_get_request(link)

        raise ValueError(f"Class routine not found for program code {program_code}")

    @logger.catch()
    async def get_exam_routine_pdf_link(self, program_code: ProgramCode) -> str:
        """
        Get exam routine pdf link from the routine webpage

        :param program_code: The program code to filter by (e.g., `006`, `001`)
        :type program_code: ProgramCode
        :raises ValueError: No exam routine links found from the routine page
        :raises ValueError: No exam pdf link found for the given program code
        :return: the exam routine PDF link of the program
        :rtype: str
        """
        routine_links = await self.get_routine_links()
        links = routine_links.get("exam", {}).get("links")
        if not links:
            raise ValueError("No exam routine links found")

        shift_name = get_shift_name(program_code).value.lower()
        program_name_parts = (
            reverse_program_code(program_code=program_code).lower().split()
        )

        for shift in links:
            for program, program_links in shift.items():
                if shift_name in program.lower():
                    for i in program_links:
                        name, link = list(i.items())[0]
                        name = name.lower().replace("day", "").strip()
                        if name in program_name_parts:
                            return link

        raise ValueError("%s: PDF link not found.", program_code)
