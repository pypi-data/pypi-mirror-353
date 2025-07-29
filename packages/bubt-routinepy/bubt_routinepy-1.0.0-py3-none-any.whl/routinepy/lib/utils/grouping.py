from collections import defaultdict

from routinepy.lib.api.enums import Weekday
from routinepy.lib.models import ClassPeriod, FacultyPeriod, TermExam


def group_by_weekday(
    data: list[FacultyPeriod | ClassPeriod | TermExam],
) -> dict[Weekday, list[FacultyPeriod | ClassPeriod | TermExam]]:
    """
    Groups periods by weekday.

    Returns: dict[Weekday: list[FacultyPeriod | ClassPeriod | TermExam]]
    """
    # leaving here, in case in future the bubt dev decides to do something stupid.
    # sorted_data = sorted(data, key=attrgetter('intake', 'section'))

    grouped = defaultdict(list)
    for item in data:
        key1 = item.week_day
        grouped[key1].append(item)

    return grouped


def group_by_intake_section(
    data: list[FacultyPeriod | ClassPeriod | TermExam],
) -> dict[str, dict[Weekday : list[FacultyPeriod | ClassPeriod | TermExam]]]:
    """
    Groups periods by intake-section combination.

    Returns: dict[intake-section: dict[Weekday: list[FacultyPeriod | ClassPeriod | TermExam]]]
    """
    # leaving here, in case in future the bubt dev decides to do something stupid.
    # sorted_data = sorted(data, key=attrgetter('intake', 'section'))

    grouped = defaultdict(list)
    for item in data:
        key1 = f"{item.intake}-{item.section}"
        grouped[key1].append(item)

    return dict(
        sorted(grouped.items(), key=lambda x: [int(num) for num in x[0].split("-")]),
    )


def group_by_intake_section_and_weekday(
    data: list[FacultyPeriod | ClassPeriod | TermExam],
) -> dict[str, dict[Weekday : list[FacultyPeriod | ClassPeriod | TermExam]]]:
    """
    Groups periods by intake-section combination and then by weekday.

    Returns: dict[intake-section: dict[Weekday: list[FacultyPeriod | ClassPeriod | TermExam]]]
    """
    # leaving here, in case in future the bubt dev decides to do something stupid.
    # sorted_data = sorted(data, key=attrgetter('intake', 'section'))

    grouped = defaultdict(lambda: defaultdict(list))
    for item in data:
        key1 = f"{item.intake}-{item.section}"
        key2 = item.week_day
        grouped[key1][key2].append(item)

    return dict(
        sorted(grouped.items(), key=lambda x: [int(num) for num in x[0].split("-")]),
    )
