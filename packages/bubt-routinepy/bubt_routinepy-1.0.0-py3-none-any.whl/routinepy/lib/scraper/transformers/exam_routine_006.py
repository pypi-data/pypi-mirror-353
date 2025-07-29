import re
from datetime import datetime
from itertools import chain

from loguru import logger

from routinepy.lib.models import TermExam


class Program006ExamTableTransformer:
    """
    Transforms exam table data for the :attr:`ProgramCode.CSE_day`.

    This class processes raw exam table data and converts it into a structured format data.

    .. note::
        Till now, the exam routine PDF of CSE day (006) has been the most consistent structure which allowed
        to extract and transform data very easily.
    """

    def transform_to_models(
        self, tables: list, program_code: str = "006"
    ) -> list[list[TermExam]]:
        """
        Converts raw tables into a list of :class:`~routinepy.lib.models.TermExam` objects.
        """
        return [self.transform_to_model(i, program_code=program_code) for i in tables]

    def transform_to_model(
        self, rows: list, program_code: str = "006"
    ) -> dict[str, list[TermExam]]:
        """
        Converts a exam table rows into a list of :class:`~routinepy.lib.models.TermExam` objects.
        """

        exams = []
        intake_section = None
        for row in rows:
            if not row:
                continue
            if len(row) == 1:
                intake_section = self._extract_intake_section(row[0])
                continue
            if len(row) <= 2 or row[0].startswith("Day"):
                continue

            try:
                exam = self._parse_exam_row(row, program_code, intake_section)
                exams.append(exam)
            except (ValueError, IndexError) as e:
                logger.error(f"Failed to parse row {row}: {e}")
                continue

        return exams

    def _extract_intake_section(self, text) -> dict[str, str]:
        if not text:
            return {}

        match = re.search(
            r"Intake: (?P<intake>\d+).*Sec:(?P<section>\w+)",
            text,
            flags=re.IGNORECASE,
        )
        if not match:
            logger.error(f"Failed to extract intake/section from: {text}")
            return {}
        return match.groupdict()

    def _parse_time_cell(self, text: str):
        """
        Parses date string from format 'DD Mon YYYY' to 'YYYY-MM-DD'.
        """
        try:
            time = text.split("\n")[0].strip()
            if not time:
                return None

            return datetime.strptime(time, r"%d %b %Y").strftime(r"%Y-%m-%d")
        except (ValueError, IndexError):
            logger.error(f"Failed to parse time cell: {text}")
            return ""

    def _parse_room_cell(self, text: str):
        return (text[0], text[1:]) if text else ("-", "-")

    def _parse_exam_row(
        self,
        row: list[str],
        program_code: str,
        intake_section: dict[str, str],
    ) -> TermExam:
        """
        Creates a :class:`TermExam` from a single table row.
        """
        if len(row) < 7:
            logger.warning(
                f"Row too short, expected at least 7 columns got {len(row)}: {row}"
            )

        building, room = self._parse_room_cell(row[6] if len(row) > 6 else "")

        return TermExam(
            program_code=program_code,
            course_code=row[3],
            student_intake=intake_section.get("intake", ""),
            student_section=intake_section.get("section", ""),
            course_faculty=row[4],
            building=building,
            room_number=room,
            total_students=row[5],
            e_date=self._parse_time_cell(row[1]),
            slot_label=row[2].replace("\n", " "),
        )
