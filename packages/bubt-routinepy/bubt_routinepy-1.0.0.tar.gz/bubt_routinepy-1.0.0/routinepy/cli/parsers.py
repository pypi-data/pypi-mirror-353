import argparse

from routinepy.lib import RoutineType, SemesterType


def create_parser():
    parser = argparse.ArgumentParser(
        description="Fetch academic routine information of BUBT"
    )

    # Required arguments
    parser.add_argument(
        "--routine-type",
        type=str,
        required=True,
        choices=[rt.value for rt in RoutineType],
        help=f"Routine type ({','.join(RoutineType._member_names_)})",
    )

    # Optional arguments
    parser.add_argument(
        "--semester-type",
        default=SemesterType.CURRENT.value,
        type=str,
        choices=[st.value for st in SemesterType],
        help=f"Semester type ({','.join(SemesterType._member_names_)})",
    )
    parser.add_argument(
        "--faculty-code",
        type=str,
        help="Short code of the faculty member",
    )
    parser.add_argument(
        "--room",
        type=str,
        help="4 digit room number",
    )
    parser.add_argument(
        "--program-code",
        type=str,
        help="Program code to filter by",
    )
    parser.add_argument(
        "--intake",
        type=str,
        help="Student intake number",
    )
    parser.add_argument(
        "--section",
        type=str,
        help="Student section number. (requires intake)",
    )
    parser.add_argument(
        "--course-code",
        type=str,
        help="Course code to filter by",
    )

    # Output
    output_group = parser.add_argument_group("Output")
    output_group.add_argument(
        "--format",
        choices=["json", "html", "text"],
        default="text",
        help="Output format (json,html or text)",
    )
    output_group.add_argument("--output-dir", type=str, help="Path to the output file")
    output_group.add_argument(
        "--verbose", action="store_true", help="Enable verbose output"
    )

    return parser
