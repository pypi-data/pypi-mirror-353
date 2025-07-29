from dataclasses import dataclass

from bs4 import Tag


@dataclass
class TransformedClassPeriod:
    """
    This class holds the processed data about a specific class period after
    transformation from the HTML table.
    """

    course_code: str
    faculty_code: str
    building: str
    room: str


@dataclass
class RawClassRoutineTable:
    """
    This class is the container for raw HTML table fragments extracted during
    parsing for each sections.
    """

    meta: Tag
    routine: Tag
    faculty_table: Tag


@dataclass
class TransformedClassFacultyTable:
    """
    This class is holds the processed data of a faculty member and the course that
    will be taken after transformation from the HTML table.
    """

    course_code: str
    course_name: str
    faculty_code: str
    faculty_name: str
