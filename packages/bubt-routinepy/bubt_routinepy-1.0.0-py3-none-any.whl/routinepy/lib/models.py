from json import JSONDecodeError, loads
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .api.enums import ProgramCode, ShiftTime, Weekday


class UpdateInfo(BaseModel):
    """
    Represents a single update metadata of a routine.
    """

    id: str
    routine: str
    semester: str
    semseter_code: str = Field(alias="semseterCode")
    hash: str
    minor_change: str = Field(alias="minorChange")
    major_change: str = Field(alias="majorChange")
    updated_at: str
    created_at: str


class ClassPeriod(BaseModel):
    """
    Represents a single class period in Class routine.
    """

    week_day: Weekday = Field(alias="classDay")
    period_time: str = Field(alias="timeSlotLabel", examples=["12:00 PM to 01:30 PM"])
    intake: str = Field(alias="studentIntake", examples=["48", "49", "50"])
    section: str = Field(alias="studentSection", examples=["1", "2", "3"])
    faculty_code: str = Field(alias="teacherShortCode")
    faculty_name: Optional[str] = Field(
        alias="teacherFullName", exclude=True, default=None
    )
    building: str = Field(alias="buildingId", examples=["1", "2", "3", "4"])
    room: str = Field(alias="roomNo")
    course_code: str = Field(alias="courseNo", examples=["CSE 101", "CSE 201"])
    course_name: Optional[str] = Field(alias="courseName", exclude=True, default=None)
    shift_time: ShiftTime = Field(alias="shiftTime")


class FacultyPeriod(BaseModel):
    """
    Represents a single class period in Faculty routine.
    """

    week_day: Weekday = Field(alias="dayName")
    period_time: str = Field(alias="timeSlotLabel", examples=["12:00 PM to 01:30 PM"])
    intake: str = Field(alias="intake", examples=["48", "49", "50"])
    section: str = Field(alias="section", examples=["1", "2", "3"])
    building: str = Field(alias="buildingId", examples=["1", "2", "3", "4"])
    room: str = Field(alias="roomNumber")
    course_code: str = Field(alias="courseNumber", examples=["CSE 101", "CSE 201"])
    shift_time: ShiftTime = Field(alias="shiftName")


class TermExam(BaseModel):
    """
    Represents a single exam period in Exam routine.
    """

    program_code: ProgramCode = Field(alias="program_code")
    course_code: str = Field(alias="course_code", examples=["CSE 101", "CSE 201"])
    intake: str = Field(alias="student_intake", examples=["48", "49", "50"])
    section: str = Field(alias="student_section", examples=["1", "2", "3"])
    faculty_code: str = Field(alias="course_faculty", examples=["AQO", "MDI", "MMRH"])
    building: str = Field(alias="building", examples=["1", "2", "3", "4"])
    room: str = Field(alias="room_number", examples=['["906"]'])
    total_students: Optional[str] = None
    exam_date: str = Field(alias="e_date", examples=["2025-03-12 00:00:00"])
    period_time: str = Field(alias="slot_label", examples=["12:00 PM to 01:30 PM"])

    # Why? Because for some *good* reason developer thought of sending
    # room number as an array of str e.g, '["801"]' ¯\_(ツ)_/¯
    @field_validator("room")
    def parse_room(cls, value):
        try:
            return loads(value)[0]
        except (JSONDecodeError, IndexError, TypeError):
            return value

    @field_validator("exam_date")
    def parse_exam_date(cls, value):
        try:
            return value.split()[0]
        except (JSONDecodeError, IndexError):
            return value
