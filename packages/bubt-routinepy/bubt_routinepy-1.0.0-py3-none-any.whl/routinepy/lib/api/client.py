from typing import List, Optional

from loguru import logger

from routinepy.lib.api.enums import (
    ProgramCode,
    RoutineType,
    SemesterType,
    SyncRoutineType,
)
from routinepy.lib.models import ClassPeriod, FacultyPeriod, TermExam, UpdateInfo
from routinepy.lib.utils.http import make_post_request


class ApiClient:
    """
    Client for fetching routine data using the BUBT routine APIs

    .. note::
        There are no public APIs provided by the university, I have to reverse engineer the
        `official routine webpage <https://routine.bubt.edu.bd>`_ to get the endpoints
    """

    async def get_class_routine(
        self,
        semester_type: SemesterType = SemesterType.CURRENT,
        faculty_code: str = None,
        program_code: ProgramCode = None,
        room: str = None,
        intake: str = None,
        section: str = None,
        course_code: str = None,
    ) -> list[ClassPeriod]:
        """
        Get class routine data based on provided filters

        Shortcut for method :meth:`.get_routine` with automatically filled parameter:

        - ``routine_type=RoutineType.CLASS``

        :return: A list of :class:`ClassPeriod` objects
        :rtype: list[ClassPeriod]
        """
        return await self.get_routine(
            routine_type=RoutineType.CLASS,
            semester_type=semester_type,
            faculty_code=faculty_code,
            program_code=program_code,
            room=room,
            intake=intake,
            section=section,
            course_code=course_code,
        )

    async def get_class_routine_update_info(
        self,
        semester_type: SemesterType = SemesterType.CURRENT,
    ) -> list[UpdateInfo] | None:
        """
        Get class routine update metadata.

        Shortcut for method :meth:`.get_last_update` with automatically filled parameter:

        - ``routine_type=RoutineType.CLASS``

        :return: A list of :class:`UpdateInfo` objects
        :rtype: list[UpdateInfo]
        """
        return await self.get_last_update(
            sync_routine_type=SyncRoutineType.CLASS,
            semester_type=semester_type,
        )

    async def get_mid_routine(
        self,
        semester_type: SemesterType = SemesterType.CURRENT,
        faculty_code: str = None,
        program_code: ProgramCode = None,
        room: str = None,
        intake: str = None,
        section: str = None,
        course_code: str = None,
    ) -> list[TermExam]:
        """
        Get mid-term routine data based on provided filters

        Shortcut for method :meth:`.get_routine` with automatically filled parameter:

        - ``routine_type=RoutineType.MID``

        :return: A list of :class:`TermExam` objects
        :rtype: list[TermExam]
        """

        return await self.get_routine(
            routine_type=RoutineType.MID,
            semester_type=semester_type,
            faculty_code=faculty_code,
            program_code=program_code,
            room=room,
            intake=intake,
            section=section,
            course_code=course_code,
        )

    async def get_mid_routine_update_info(
        self,
        semester_type: SemesterType = SemesterType.CURRENT,
    ) -> list[UpdateInfo] | None:
        """
        Get mid-term routine update metadata.

        Shortcut for method :meth:`.get_last_update` with automatically filled parameter:

        - ``routine_type=RoutineType.MID``

        :return: A list of :class:`UpdateInfo` objects
        :rtype: list[UpdateInfo]
        """
        return await self.get_last_update(
            sync_routine_type=SyncRoutineType.MID,
            semester_type=semester_type,
        )

    async def get_final_routine(
        self,
        semester_type: SemesterType = SemesterType.CURRENT,
        faculty_code: str = None,
        program_code: ProgramCode = None,
        room: str = None,
        intake: str = None,
        section: str = None,
        course_code: str = None,
    ) -> list[TermExam]:
        """
        Get final-term routine data based on provided filters

        Shortcut for method :meth:`.get_routine` with automatically filled parameter:

        - ``routine_type=RoutineType.FINAL``

        :return: A list of :class:`TermExam` objects
        :rtype: list[TermExam]
        """

        return await self.get_routine(
            routine_type=RoutineType.FINAL,
            semester_type=semester_type,
            faculty_code=faculty_code,
            program_code=program_code,
            room=room,
            intake=intake,
            section=section,
            course_code=course_code,
        )

    async def get_final_routine_update_info(
        self,
        semester_type: SemesterType = SemesterType.CURRENT,
    ) -> list[UpdateInfo] | None:
        """
        Get final-term routine update metadata.

        Shortcut for method :meth:`.get_last_update` with automatically filled parameter:

        - ``routine_type=RoutineType.FINAL``

        :return: A list of :class:`UpdateInfo` objects
        :rtype: list[UpdateInfo]
        """
        return await self.get_last_update(
            sync_routine_type=SyncRoutineType.FINAL,
            semester_type=semester_type,
        )

    @logger.catch()
    async def get_routine(
        self,
        routine_type: RoutineType,
        semester_type: SemesterType = SemesterType.CURRENT,
        faculty_code: str = None,
        program_code: ProgramCode = None,
        room: str = None,
        intake: str = None,
        section: str = None,
        course_code: str = None,
    ) -> List[ClassPeriod | TermExam | FacultyPeriod] | None:
        """
        Base method for getting routine data based on provided filters.


        :param routine_type: Type of routine (e.g., 'class', 'mid' )
        :type routine_type: RoutineType
        :param semester_type: Type of semester (e.g., 'past', 'present' ) (required for class routine only), defaults to SemesterType.CURRENT
        :type semester_type: SemesterType, optional
        :param faculty_code: The faculty member code to filter by (e.g., 'MDI', 'MAFI' ), defaults to None
        :type faculty_code: str, optional
        :param program_code: The program code to filter by (e.g., '006', '001'), defaults to None
        :type program_code: ProgramCode, optional
        :param room: The four digit room number to filter by (e.g., '2420', '2709'), defaults to None
        :type room: str, optional
        :param intake: The intake number to filter by (e.g., '49', '50'), defaults to None
        :type intake: str, optional
        :param section: The section number to filter by (e.g., '1', '2), defaults to None
        :type section: str, optional
        :param course_code: The course code to filter by (e.g., 'CSE 101', 'CSE 331'), defaults to None
        :type course_code: str, optional
        :raises ValueError: If invalid or incompatible filter combinations are provided, such as:

            - Invalid `routine_type`, `semester_type`, or `program_code` (not matching their respective `Enum` values).
            - Neither `program_code`, `faculty_code`, nor `room` provided.
            - `room` not being a four-digit string.
            - `section` provided without `intake`.
            - Empty or malformed `course_code`.

        :return: A list of routine objects or `None` if no data is found:

            - `List[ClassPeriod]` for ``routine_type=RoutineType.CLASS``.
            - `List[TermExam]` for exam-related `routine_type` (e.g., ``RoutineType.MID``).
            - `List[FacultyPeriod]` if `faculty_code` is provided.

        :rtype: List[ClassPeriod | TermExam | FacultyPeriod] | None

        .. note::
            The `room` parameter is split into building and room number for the payload.
        """

        # Input Validation
        if not isinstance(semester_type, SemesterType):
            raise ValueError(f"Invalid semester_type: {semester_type}")

        if not isinstance(routine_type, RoutineType):
            raise ValueError(f"Invalid routine_type: {routine_type}")

        if program_code and not isinstance(program_code, ProgramCode):
            raise ValueError(f"Invalid program_code: {program_code}")

        if room:
            if not (room.isdigit() and len(room) == 4):
                raise ValueError("Room must be a 4-digit string (e.g., '2317')")
        elif not program_code and not faculty_code:
            raise ValueError("room, program_code or faculty_code must be provided")

        if course_code and not course_code.strip():
            raise ValueError("course_code cannot be empty")

        if section and not intake:
            raise ValueError("section requires intake parameter")

        # Preparing payload
        payload = {}
        if semester_type:
            payload["semesterRoutine"] = semester_type
        if faculty_code:
            payload["facultyCode"] = faculty_code
        if program_code:
            payload["programCode"] = program_code.value
        if room:
            payload.update({"buildingNumber": room[0], "roomNumber": room[1:]})
        if course_code:
            payload["courseCode"] = course_code.strip()
        if intake:
            payload["intake"] = intake
        if section:
            payload["section"] = section

        # Building endpoint path
        base_endpoint = self._get_base_endpoint(routine_type, semester_type)
        endpoint = self._build_endpoint_path(
            base_endpoint,
            faculty_code=faculty_code,
            room=room,
            course_code=course_code,
            intake=intake,
            section=section,
        )

        logger.info(f"Getting {routine_type.value} routine")

        json = await make_post_request(endpoint=endpoint, data=payload)

        if not json:
            return

        if faculty_code:
            return [FacultyPeriod(**item) for item in json]

        if routine_type == RoutineType.CLASS:
            return [ClassPeriod(**item) for item in json]

        return [TermExam(**item) for item in json]

    async def get_last_update(
        self,
        sync_routine_type: SyncRoutineType,
        semester_type: Optional[SemesterType] = SemesterType.CURRENT,
    ) -> list[UpdateInfo] | None:
        """
        Base method of getting update information of a routine.

        :param sync_routine_type: Type of the routine to get information
        :type sync_routine_type: SyncRoutineType
        :param semester_type: Type of the routine to get information, defaults to :attr:`SemesterType.CURRENT`
        :type semester_type: Optional[SemesterType], optional
        :return: Update information of a routine containing last modified and when created.
        :rtype: list[UpdateInfo]

        **Example Output of Class Routine Update Metadata:**

        .. code-block:: python

            [
                UpdateInfo(
                    id="4",
                    routine="routine",
                    semester="present",
                    semseter_code="064",
                    hash="cd16a548f98a4bc5214f77c5d751f860",
                    minor_change="4",
                    major_change="6",
                    updated_at="2025-06-02 21:32:08",
                    created_at="2024-09-24 11:07:19",
                ),
                UpdateInfo(
                    id="3",
                    routine="routine",
                    semester="present",
                    semseter_code="610",
                    hash="822401605769ca575740327771176bbd",
                    minor_change="2",
                    major_change="7",
                    updated_at="2025-06-02 17:15:08",
                    created_at="2024-09-24 11:07:19",
                ),
            ]
        """
        payload = {"routine": sync_routine_type.value, "semester": semester_type.value}
        json = await make_post_request(endpoint="previousSyncCheck.php", data=payload)
        if not json:
            return

        return [UpdateInfo(**item) for item in json]

    # Helper functions
    def _get_base_endpoint(
        self,
        routine_type: RoutineType,
        semester_type: Optional[str] = None,
    ) -> str:
        """
        Get the base API endpoint path for the given routine type.

        :param routine_type: Type of routine (e.g., 'class', 'mid')
        :type routine_type: RoutineType
        :param semester_type: Type of semester (e.g., 'past', 'present' ) (required for class routine only), defaults to None
        :type semester_type: Optional[str], optional
        :raises ValueError: Missing semester type when routine type is `class`
        :raises ValueError: Unsupported type of routine
        :return: Base endpoint path string
        :rtype: str
        """
        if routine_type == RoutineType.CLASS:
            if not semester_type:
                raise ValueError("semester_type is required for CLASS routine type")
            return "class_routine"

        if routine_type == RoutineType.MID:
            return "exam_routine/mid"

        if routine_type == RoutineType.FINAL:
            return "exam_routine/final"

        raise ValueError(f"Unsupported routine type: {routine_type}")

    def _build_endpoint_path(
        self,
        base_endpoint: str,
        faculty_code: str = None,
        room: str = None,
        course_code: str = None,
        intake: str = None,
        section: str = None,
    ) -> str:
        """
        Construct the full API endpoint path based on parameters.

        :param base_endpoint: base API endpoint path for the given routine type
        :type base_endpoint: str
        :param faculty_code: The faculty member code to filter by (e.g., 'MDI', 'MAFI' ), defaults to None
        :type faculty_code: str, optional
        :param room: The four digit room number to filter by (e.g., '2420', '2709'), defaults to None
        :type room: str, optional
        :param course_code: The course code to filter by (e.g., 'CSE 101', 'CSE 331'), defaults to None
        :type course_code: str, optional
        :param intake: The intake number to filter by (e.g., '49', '50'), defaults to None
        :type intake: str, optional
        :param section: The section number to filter by (e.g., '1', '2), defaults to None
        :type section: str, optional
        :return: the full API endpoint path based on parameters
        :rtype: str
        """

        if faculty_code:
            return f"{base_endpoint}/withFacultyCode/filteredWithFacultyCode.php"

        if room:
            return f"{base_endpoint}/withRoomNumber/filteredWithRoomNumber.php"

        if course_code:
            return f"{base_endpoint}/program_intake_section/filteredWithCourseCode.php"

        if section:
            return f"{base_endpoint}/program_intake_section/filteredWithSection.php"

        if intake:
            return f"{base_endpoint}/program_intake_section/filteredWithIntake.php"

        return f"{base_endpoint}/program_intake_section/filteredWithProgram.php"
