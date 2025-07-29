import asyncio
from pathlib import Path
from sys import exit as sys_exit
from sys import stderr

from loguru import logger

from routinepy.cli.dataclasses import OutputConfig, RoutineConfig
from routinepy.cli.parsers import create_parser
from routinepy.cli.utils import gen_filename, gen_output
from routinepy.lib import ApiClient, ProgramCode, RoutineType, SemesterType
from routinepy.lib.utils.table_generator import gen_tables


def parse_args() -> dict[str, RoutineConfig | OutputConfig]:
    parser = create_parser()
    args = parser.parse_args()

    # input to enum magic -,-
    routine_type = RoutineType(args.routine_type.lower())
    semester_type = (
        SemesterType(args.semester_type.lower()) if args.semester_type else None
    )
    program_code = ProgramCode(args.program_code.upper()) if args.program_code else None

    return {
        "app": RoutineConfig(
            routine_type=routine_type,
            semester_type=semester_type,
            room=args.room,
            faculty_code=args.faculty_code,
            program_code=program_code,
            intake=args.intake,
            section=args.section,
            course_code=args.course_code,
        ),
        "output": OutputConfig(
            format=args.format,
            output_dir=args.output_dir,
            verbose=args.verbose,
        ),
    }


def setup_logger(is_verbose: bool = False):
    logger.remove()
    level = "DEBUG" if is_verbose else "INFO"
    logger.add(stderr, level=level)


async def main():
    try:
        kwargs = parse_args()

        routine_config: RoutineConfig = kwargs["app"]
        output_config: OutputConfig = kwargs["output"]

        setup_logger(output_config.verbose)

        data = await ApiClient().get_routine(**routine_config.__dict__)
        if not data:
            logger.error("No routine found.")
            return

        tables = gen_tables(
            data=data,
            routine_type=routine_config.routine_type,
            faculty_code=routine_config.faculty_code,
            room=routine_config.room,
        )

        output_str = gen_output(data=data, tables=tables, format=output_config.format)
        output_dir = output_config.output_dir
        if output_dir:
            file_name = gen_filename(kwargs)
            path = Path(output_dir) / file_name
            path.write_text(output_str)
            logger.info(f"Saved to {path}")
        else:
            print(output_str)
    except ValueError as e:
        logger.error(f"Failed to process routine: {type(e).__name__}: {e}")
        sys_exit(1)


def cli():
    asyncio.run(main())


if __name__ == "__main__":
    cli()
