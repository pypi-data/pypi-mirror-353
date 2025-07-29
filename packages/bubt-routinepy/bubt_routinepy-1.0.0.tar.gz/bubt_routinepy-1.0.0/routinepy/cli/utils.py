from json import dumps

from prettytable.colortable import ColorTable


def gen_filename(kwargs: dict):
    routine_config = kwargs["app"].__dict__
    output_config = kwargs["output"].__dict__

    routine_type = routine_config.get("routine_type")
    semester_type = routine_config.get("semester_type")
    room = routine_config.get("room")
    faculty_code = routine_config.get("faculty_code")
    program_code = routine_config.get("program_code")
    intake = routine_config.get("intake")
    section = routine_config.get("section")
    course_code = routine_config.get("course_code")

    title = f"{semester_type}_{routine_type.value}_schedule"

    parts = []
    if room:
        parts.append(f"_of_room_{room}")

    if faculty_code:
        parts.append(faculty_code.upper())
    if program_code:
        parts.append(program_code)
    if intake:
        parts.append(intake)
    if section:
        parts.append(section)
    if course_code:
        parts.append(course_code.replace(" ", ""))

    if parts:
        title += f"_{'_'.join(parts)}.{output_config.get('format', 'unknown')}"

    title = title.replace(".text", ".txt")

    return title


def gen_output(data, tables: list[ColorTable], format: str) -> str:
    if format == "json":
        return dumps([i.model_dump(exclude_none=True) for i in data])

    format_methods = {
        "html": lambda t: t.get_html_string(),
        "text": lambda t: t.get_formatted_string(),
    }

    if format not in format_methods:
        raise ValueError(f"Unsupported format: {format}")

    return "\n".join(format_methods[format](table) for table in tables)
