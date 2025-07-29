from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from routinepy.lib import ProgramCode, RoutineType, SemesterType


@dataclass
class RoutineConfig:
    routine_type: RoutineType
    semester_type: Optional[SemesterType]
    room: Optional[str]
    faculty_code: Optional[str]
    program_code: Optional[ProgramCode]
    intake: Optional[str]
    section: Optional[str]
    course_code: Optional[str]


@dataclass
class OutputConfig:
    format: str
    output_dir: Optional[Path]
    verbose: bool
