from typing import Optional

from prettytable.colortable import ColorTable, Themes

from ..api.enums import RoutineType, Weekday
from ..models import ClassPeriod, FacultyPeriod, TermExam
from .dt_utils import sort_key_datetime
from .grouping import (
    group_by_intake_section,
    group_by_intake_section_and_weekday,
    group_by_weekday,
)


def create_routine_table(
    title: str,
    routine_data: list[Weekday, FacultyPeriod | ClassPeriod],
    is_faculty: bool = False,
):
    """
    Generate a formatted `ColorTable` from routine data.

    Args:
        title: title of the table
        routine_data: dict with weekday as key and periods as value
        is_faculty: Whether the data represents faculty schedule

    Returns:
        Formatted ColorTable object
    """
    table = ColorTable(theme=Themes.DEFAULT)
    table.align = "c"
    table.header = True
    table.title = title

    period_times = get_period_times(routine_data)
    table.add_column("Time", period_times)

    for day in routine_data:
        periods = routine_data[day]

        col_vals = [""] * len(period_times)
        for period in periods:
            col_vals[period_times.index(period.period_time)] = prepare_table_cell(
                period, is_faculty
            )

        table.add_column(day.value, col_vals)

    return table


def create_exam_routine_table(
    routine_type: RoutineType,
    data: list[TermExam],
):
    tables = []
    for intake_section in data:
        table = ColorTable(theme=Themes.DEFAULT)
        table.align = "c"
        table.header = False
        table.title = gen_table_title(
            routine_type=routine_type,
            intake_section=intake_section,
        )

        table.add_row(["Date", "Time", "Course Code", "Course Teacher", "Room"])

        for period in data[intake_section]:
            table.add_divider()
            table.add_row(
                [
                    period.exam_date,
                    period.period_time,
                    period.course_code,
                    period.faculty_code,
                    f"B{period.building}/{period.room}",
                ]
            )

        tables.append(table)

    return tables


def gen_tables(
    data: list[ClassPeriod | TermExam],
    routine_type: RoutineType = RoutineType.CLASS,
    faculty_code: Optional[str] = None,
    room: Optional[str] = None,
) -> list[ColorTable] | None:
    if faculty_code or room:
        grouped_data = group_by_weekday(data)
    elif routine_type != RoutineType.CLASS and not any([faculty_code, room]):
        # TermExam routines dont have week_day + different table layout
        grouped_data = group_by_intake_section(data)
        return create_exam_routine_table(routine_type, grouped_data)
    else:
        grouped_data = group_by_intake_section_and_weekday(data)

    tables = []
    key = list(grouped_data.keys())[0]

    if isinstance(key, Weekday):
        title = gen_table_title(
            routine_type=routine_type,
            faculty_code=faculty_code,
            room=room,
        )
        table = create_routine_table(
            routine_data=grouped_data, is_faculty=True, title=title
        )
        tables.append(table)
    elif isinstance(key, str):
        for intake_section in grouped_data:
            title = gen_table_title(
                routine_type=routine_type,
                faculty_code=faculty_code,
                room=room,
                intake_section=intake_section,
            )
            table = create_routine_table(
                title=title, routine_data=grouped_data[intake_section]
            )

            tables.append(table)

    return tables


def prepare_table_cell(
    period: FacultyPeriod | ClassPeriod | TermExam, is_faculty: bool = False
):
    cell = f"{period.course_code}\n"

    if hasattr(period, "faculty_code"):  # faculty routine got no faculty code.
        cell += f"{period.faculty_code}\n"

    if is_faculty:
        cell += f"{period.intake}-{period.section}\n"

    cell += f"B{period.building}/{period.room}"
    return cell


def get_period_times(data: dict[Weekday, FacultyPeriod | ClassPeriod | TermExam]):
    period_times = set()

    for day in data:
        periods = data[day]
        for period in periods:
            if period.period_time not in period_times:
                period_times.add(period.period_time)

    return sorted(period_times, key=sort_key_datetime)


def gen_table_title(
    routine_type: RoutineType,
    faculty_code: Optional[str] = None,
    room: Optional[str] = None,
    intake_section: Optional[str] = None,
):
    title = f"{routine_type.value.capitalize()} Routine"

    if room:
        return f"Schedule of Room {room}"

    if faculty_code:
        return f"{title} of Faculty {faculty_code.upper()}"

    if intake_section:
        title += f" ({intake_section})"

    return title
