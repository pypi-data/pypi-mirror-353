from typing import Optional
from urllib.parse import urljoin, urlparse

from routinepy.consts import BASE_URL
from routinepy.lib.api.enums import ShiftTime, Weekday
from routinepy.lib.models import ClassPeriod


def normalize_url(url: str) -> str:
    """
    Convert relative URLs to absolute (thanks bubt dev -_-)
    """

    parsed = urlparse(url)
    return url if parsed.netloc else urljoin(BASE_URL, url)


def normalize_week_day(day: str) -> str:
    # better be named `normalize_day_name` but what to do gotta keep similar with the API :/
    """
    Normalize day name string to Weekday enum. (thanks bubt dev -_-)

    Args:
        day: Day name (case insensitive, can be partial like 'sun', 'tues')

    Returns:
        Corresponding Weekday enum member

    Raises:
        ValueError: If input cannot be matched to a weekday
    """

    day = day.strip().lower()
    day_map = {
        "sun": Weekday.SUNDAY,
        "mon": Weekday.MONDAY,
        "tue": Weekday.TUESDAY,
        "wed": Weekday.WEDNESDAY,
        "thu": Weekday.THURSDAY,
        "thr": Weekday.THURSDAY,
        "fri": Weekday.FRIDAY,
        "sat": Weekday.SATURDAY,
    }

    key = day[:3]
    if key in day_map:
        return day_map[key]

    raise ValueError(f"'{day}' is not a valid weekday name")


# https://www.bubt.edu.bd/Home/page_details/Undergraduate_Programs
# https://www.bubt.edu.bd/Home/page_details/Graduate_Programs
def reverse_program_code(program_code: str) -> str:
    program_map = {
        "001": "BBA",
        "004": "Executive MBA",
        "006": "B.Sc. in CSE",
        "007": "B.A (Hons) in English",
        "008": "MA in English",
        "009": "LL.B (Hons)",
        "013": "M.Sc in Economics",
        "014": "LL.M",
        "016": "MA in ELT",
        "019": "B.Sc. in CSE (Evening)",
        "020": "B.Sc. (Hons) in Economics",
        "021": "B.Sc. in EEE",
        "022": "B.Sc. in Textile Engg.",
        "023": "B.Sc. in EEE (Evening)",
        "024": "B.Sc. in Textile Engg. (Evening)",
        "027": "B.Sc. in Civil Engg.",
        "028": "B.Sc. in Civil Engg. (Evening)",
    }

    return program_map.get(program_code, "-1")


def get_shift_name(program_code: str) -> ShiftTime:
    program_name = reverse_program_code(program_code=program_code)
    return ShiftTime.EVENING if "evening" in program_name.lower() else ShiftTime.DAY


def filter_periods(
    tables: list[ClassPeriod],
    course_code: Optional[str] = None,
    faculty_code: Optional[str] = None,
    intake: Optional[str] = None,
    section: Optional[str] = None,
):
    if all(param is None for param in [course_code, faculty_code, intake, section]):
        return [period for table in tables for period in table]

    filtered_periods = []
    for table in tables:
        if not table:
            continue

        first_period = table[0]

        if intake and first_period.intake != intake:
            continue
        if section and first_period.section != section:
            continue

        for period in table:
            if faculty_code and period.faculty_code != faculty_code:
                continue
            if course_code and period.course_code != course_code:
                continue

            filtered_periods.append(period)

    return filtered_periods
