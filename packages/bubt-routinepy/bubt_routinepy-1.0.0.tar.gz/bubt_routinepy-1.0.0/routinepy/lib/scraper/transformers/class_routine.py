import re

from bs4 import Tag
from loguru import logger

from routinepy.lib.api.enums import ShiftTime
from routinepy.lib.models import ClassPeriod
from routinepy.lib.scraper.models import (
    RawClassRoutineTable,
    TransformedClassFacultyTable,
    TransformedClassPeriod,
)
from routinepy.lib.scraper.scraper_utils import get_shift_name, normalize_week_day


class ClassRoutineTableTransformer:
    """
    Transforms raw HTML class routine tables into structured routine data.

    This class handles the conversion of class routine HTML into
    organized collections of :class:`~routinepy.lib.models.ClassPeriod` objects, including:

        1. Parsing table metadata (program, intake, semester)
        2. Extracting faculty information
        3. Building 2D matrix of class routine
        4. Converting raw HTML into structured objects
    """

    # (I initially asked Gemini but it didn't provide a working one, so I took that broken regex as base and modified on top of it)
    # first pattern        : ^(?P<ccode>[A-Z]{2,} \d{3,}),FC:,?(?P<fcode>[A-Z]+)(?:,B:,?(?P<bnum>\d+) ⇒)?,R:,?(?P<rnum>\d+.\w?)$
    # (2991 matches, 99,758 steps, 615.21ms)
    #
    # second pattern (grok): ^(?P<ccode>[A-Z]{2,} \d{3,}),FC:,(?P<fcode>[A-Z]+)(?:,B:,(?P<bnum>\d+)(?: ⇒)?)?,R:,(?P<rnum>[\d\w-]+)$
    # (2991 matches, 93,338 steps, 184.19ms)

    CELL_TEXT_REGEX = r"^(?P<ccode>[A-Z]{2,} \d{3,}),FC:,(?P<fcode>[A-Z]+)(?:,B:,(?P<bnum>\d+)(?: ⇒)?)?,R:,(?P<rnum>[\d\w-]+)$"
    """
    Regular expression pattern to parse structured cell text with named groups.

    Sample cell texts:

    - ``CE 417,FC:,SRB,R:,4904``
    - ``GED 1105,FC:,MSBN,R:,1504-B``
    - ``CSE 232,FC:,MAFI,B:,2 ⇒,R:,418``
    """

    def __init__(self):
        self.CELL_TEXT_REGEX = re.compile(self.CELL_TEXT_REGEX, re.IGNORECASE)

    def transform_to_models(
        self, tables: list[RawClassRoutineTable], program_code: str
    ) -> list[ClassPeriod]:
        """
        Transform multiple HTML routine tables into :class:`~routinepy.lib.models.ClassPeriod` models.

        :param tables: List of extracted HTML routine tables to transform
        :type tables: list[RawClassRoutineTable]
        :param program_code: Program code of the routine (e.g., '006', '001')
        :type program_code: str
        :return: List of transformed class periods
        :rtype: list[ClassPeriod]
        """
        shift_time = get_shift_name(program_code=program_code)

        return [
            self.transform_to_model(
                data=table, program_code=program_code, shift_time=shift_time
            )
            for table in tables
        ]

    @logger.catch()
    def transform_to_model(
        self,
        data: RawClassRoutineTable,
        program_code: str,
        shift_time: ShiftTime = None,
    ) -> list[ClassPeriod]:
        """
        Transform a single HTML routine table into :class:`~routinepy.lib.models.ClassPeriod` models.

        :param data: Extracted HTML routine table data
        :type data: RawClassRoutineTable
        :param program_code: Program code of the routine (e.g., '006', '001')
        :type program_code: str
        :param shift_time: Pre-determined shift time if available, defaults to None
        :type shift_time: ShiftTime, optional
        :raises ValueError: the routine data cannot be transformed
        :return: List of ClassPeriod extracted from the table
        :rtype: list[ClassPeriod]

        **Transformation Steps**:

        1. Extracts routine metadata (program, semester, intake and section)
        2. Builds 2D matrix from the routine HTML table
        3. Extracts faculty information from the faculty table
        4. Constructs ClassPeriod objects from the generated 2D matrix
        """

        shift_time = shift_time or get_shift_name(program_code=program_code)

        try:
            meta = self.extract_routine_meta(data.meta)
            routine_matrix = self.build_2D_routine_matrix(data.routine)
            faculty_table = self.extract_faculty_table(data.faculty_table)

            intake, section = self._parse_intake_section(meta["intake_section"])

            logger.debug(
                f"Transforming routine: program={meta.get('program')}, "
                f"intake={intake}, section={section}, semester={meta.get('semester')}"
            )

            return self._build_periods(
                intake, section, routine_matrix, faculty_table, shift_time
            )
        except Exception as e:
            raise ValueError(f"Routine transformation failed: {str(e)}") from e

    def _build_periods(
        self,
        intake: str,
        section: str,
        routine_matrix: list[list[TransformedClassPeriod]],
        faculty_table: dict[str, TransformedClassFacultyTable],
        shift_time: ShiftTime = ShiftTime.DAY,
    ) -> list[ClassPeriod]:
        """
        Construct :class:`~routinepy.lib.models.ClassPeriod` objects from the processed routine data.

        Transforms the 2D routine matrix into a structured list of :class:`~routinepy.lib.models.ClassPeriod` objects
        by combining routine data with faculty information for a complete period information.

        :param intake: Intake number (e.g., '49', '50')
        :type intake: str
        :param section: Section number (e.g., '1', '2')
        :type section: str
        :param routine_matrix: 2D routine matrix where:

            - First row contains time slot labels
            - Subsequent rows represent days with periods
            - Format: [['Time', '08:00 AM to 09:15 AM', ...], ['SAT', 'CSE101 FC:MAFI R:2320', ...]]
        :type routine_matrix: list[list[TransformedClassPeriod]]
        :param faculty_table: Mapping of course codes to faculty information containing:

            - Faculty codes (e.g., 'MDI', 'HHS')
            - Faculty names
            - Course titles
        :type faculty_table: dict[str, TransformedClassFacultyTable]
        :param shift_time: Shift type of the program, defaults to :class:`ShiftTime.DAY`
        :type shift_time: ShiftTime, optional
        :return: List of fully constructed class periods with:

            - Course information
            - Faculty details
            - Time slots
            - Room locations
        :rtype: list[ClassPeriod]

        :raises ValueError: If the routine matrix cannot be parsed into valid periods


        **Processing Workflow**:

        1. Extracts time slot headers from first matrix row
        2. Processes each subsequent row as a day's schedule:

            a. Normalizes day name (e.g., 'sun' → 'Sunday') (to make data of API and Website consistent)
            b. Matches each period with corresponding time slot
            c. Merges with course and faculty data from faculty table (course title and faculty full name)

        3. Constructs ClassPeriod objects with complete period information
        """
        if not routine_matrix:
            return []

        time_slots = routine_matrix[0]  # First row contains time slots
        time_slots_len = len(time_slots)

        default_faculty = TransformedClassFacultyTable("-", "-", "-", "-")

        periods = []
        for day_row in routine_matrix[1:]:
            if not day_row:
                continue

            normalized_day = normalize_week_day(day_row[0])

            for period_no, period_meta in enumerate(day_row[1:], start=1):
                if not period_meta:
                    continue

                time_slot = (
                    time_slots[period_no]
                    if period_no < time_slots_len
                    else "Unknown Time"
                )

                course_meta = faculty_table.get(
                    period_meta.course_code, default_faculty
                )

                periods.append(
                    ClassPeriod(
                        classDay=normalized_day,
                        courseNo=period_meta.course_code,
                        courseName=course_meta.course_name,
                        teacherShortCode=period_meta.faculty_code,
                        teacherFullName=course_meta.faculty_name,
                        roomNo=period_meta.room,
                        studentIntake=intake,
                        studentSection=section,
                        buildingId=period_meta.building,
                        timeSlotLabel=time_slot,
                        shiftTime=shift_time,
                    )
                )

        return periods

    @logger.catch()
    def _parse_intake_section(self, intake_section: str) -> tuple[str, str]:
        """
        Parse intake and section numbers from a combined intake-section string.

        :param intake_section: Combined intake-section string in format "XX-YY" where:

            - XX represents the intake number (e.g., '49', '50')
            - YY represents the section number or more text (e.g., '1', '2', '1 (Major: Finance)')
        :type intake_section: str
        :return: Tuple containing (intake, section) as strings
        :rtype: tuple[str, str]
        :raises ValueError: If the input string:
            - Is empty or None
            - Doesn't match expected "XX-YY" format

        **Expected Formats**:
        - Valid: "49-1", "50-2", "57 - 1 (Major: Finance)"
        - Invalid: "49", "49-", "-1", "49-1-2"

        **Examples**:

        .. code-block:: python

            >>> self._parse_intake_section("49-1")
            ('49', '1')
            >>> self._parse_intake_section("50-2")
            ('50', '2')
            >>> self._parse_intake_section("57 - 1 (Major: Finance)")
            ('57', '1 (Major: Finance)')
        """
        if not intake_section or not intake_section.strip():
            error_msg = "Empty intake-section string"
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            parts = intake_section.split("-")
            intake, section = parts[0].strip(), parts[1].strip()
            return intake, section
        except ValueError as e:
            logger.error(f"Invalid intake-section format '{intake_section}': {str(e)}")
            raise ValueError(f"Invalid intake-section format: {str(e)}") from e

    def extract_routine_meta(self, tag: Tag) -> dict[str, str]:
        """
        Extract metadata from routine HTML header table.

        Parses program name, intake-section combination, and semester information
        from a :class:`BeautifulSoup.Tag` object representing a routine table header.

        :param tag: :class:`BeautifulSoup.Tag` containing the routine header table
        :type tag: bs4.Tag
        :return: Dictionary containing extracted metadata with keys:

            - program: Name of academic program
            - intake_section: Combined intake and section numbers
            - semester: Semester name and year
        :rtype: dict[str, str]

        **HTML Structure Expected**:

        The method expects a table row (``<tr>``) with three ``<td>`` elements containing:

        1. Left-aligned: Program name (e.g., "Program: B.Sc. Engg. in CSE")
        2. Center-aligned: Intake-section (e.g., "Intake: 49 - 3")
        3. Right-aligned: Semester info (e.g., "Semester: Spring, 2023")

        **Text Processing Examples**:

        .. code-block:: python

            # Program examples
            "<td align='left'>Program: B.Sc. Engg. in CSE</td>"
            > {"program": "B.Sc. Engg. in CSE"}

            # Intake-section examples
            "<td align='center'>Intake:60  -  7</td>"
            > {"intake_section": "60 - 7"}

            "<td align='center'>Intake:53  -  1\\n\\t\\t\\t(Major: HR)</td>"
            > {"intake_section": "53 - 1 (Major: HR)"}

            # Semester examples
            "<td align='right'>Semester:Spring, 2025</td>"
            > {"semester": "Spring, 2025"}

        """
        text = {"program": "", "intake_section": "", "semester": ""}

        row = tag.select_one("tr:nth-child(2)")
        if not row:
            return text

        program_td = row.select_one('td[align="left"]')
        intake_section_td = row.select_one('td[align="center"]')
        semester_td = row.select_one('td[align="right"]')

        text = dict()
        if program_td:
            text["program"] = program_td.get_text(strip=True).split(":")[-1].strip()
        if intake_section_td:
            temp = intake_section_td.get_text(strip=True).removeprefix("Intake:")
            temp = " ".join(temp.split())
            text["intake_section"] = temp
        if semester_td:
            text["semester"] = semester_td.get_text(strip=True).split(":")[-1].strip()

        return text

    def extract_faculty_table(
        self, tag: Tag
    ) -> dict[str, TransformedClassFacultyTable]:
        """
        Extract faculty information from an HTML table into structured data.

        Parses a faculty information table where each row represents a course and its
        associated faculty members, converting it into a dictionary mapping course codes
        to faculty data objects. Mapping is done to get the data easily during the period
        construction.

        :param tag: `BeautifulSoup.Tag` containing the faculty table
        :type tag: bs4.Tag
        :return: Dictionary mapping course codes to :class:`TransformedClassFacultyTable` objects containing:

            - course_code: The course identifier (e.g., "CSE 317")
            - course_name: Full course name (e.g., "System Analysis & Design")
            - faculty_code: Faculty code (e.g., "MDI")
            - faculty_name: Full faculty name (e.g., "MD. Masudul Islam")
        :rtype: dict[str, TransformedClassFacultyTable]

        **Expected Table Structure**:

        Each table row (<tr>) should contain exactly 4 cells (<td>) with:

        1. Course code
        2. Course name
        3. Faculty short code
        4. Faculty full name

        .. code-block:: html

            <tr>
                <td>CSE 317</td>
                <td>System Analysis And Design</td>
                <td>MDI</td>
                <td>MD. Masudul Islam</td>
            </tr>
        """
        rows = dict()

        for i in tag.find_all("tr", recursive=False):
            cells = i.find_all("td", recursive=False)
            if not cells:
                continue

            if len(cells) != 4:
                logger.warning(f"Require exactly 4 cells but got {len(cells)}: {cells}")

            course_code = cells[0].get_text(strip=True)
            if course_code:
                rows[course_code] = TransformedClassFacultyTable(
                    course_code=course_code,
                    course_name=cells[1].get_text(strip=True),
                    faculty_code=cells[2].get_text(strip=True),
                    faculty_name=cells[3].get_text(strip=True),
                )

        return rows

    @logger.catch()
    def build_2D_routine_matrix(self, tag: Tag) -> list[list[TransformedClassPeriod]]:
        """
        Build a structured 2D matrix from the routine HTML table.

        :param tag: `BeautifulSoup.Tag` containing the routine table
        :type tag: bs4.Tag
        :return: 2D schedule matrix where:

            - First row contains time slot headers (from <th> elements)
            - Subsequent rows represent days with class periods (from <td> elements)
            - Each cell contains :class:`TransformedClassPeriod` object with parsed data
        :rtype: list[list[TransformedClassPeriod]]
        :raises ValueError: Provided table tag is invalid

        **Expected Table Structure**:

        - First row: Time slot headers (<th> elements)
        - Subsequent rows: Period information (<td> elements)

        **Example Output Structure**:

        .. code-block:: python

            [
                ['Day/Time', '08:00 AM to 09:15 AM', ...]  # First row is time slots
                ['SAT', ...],
                ['SUN', '', '', TransformedClassPeriod(course_code='CSE 407', faculty_code='WMO', building='2', room='709'), ...],
                ...,
                ...,
                ...,
                ['FRI', ...]
            ]
        """

        if not tag:
            raise ValueError("Invalid routine table tag")

        mat = []
        for row in tag.find_all("tr", recursive=False):
            cells = row.find_all(["th", "td"], recursive=False)
            mat.append(self.parse_routine_row(cells=cells))

        return mat

    @logger.catch()
    def parse_routine_row(self, cells: list[Tag]) -> list[TransformedClassPeriod]:
        """
        Parse a row of HTML table cells into routine period metadata.

        Converts a list of HTML table cells into a row of routine data, with each cell
        either containing a :class:`TransformedClassPeriod` object for occupied periods
        or an empty string to preserve the period index.

        :param cells: List of :class:`BeautifulSoup.Tag` representing table cells
        :type cells: list[Tag]
        :return: List containing either:

            - :class:`TransformedClassPeriod` objects for valid class periods
            - Empty strings for empty cells (empty periods)
            - Raw text for the cells which doesn't match the regex
        :rtype: list[TransformedClassPeriod]

        **Cell Parsing Logic**:

        1. Extracts and cleans cell text content
        2. For non-empty cells, attempts pattern matching with :attr:`CELL_TEXT_REGEX`
        3. On successful match, creates :class:`TransformedClassPeriod` with:
            - Course code
            - Faculty code
            - Building number
            - Room number
        4. Handles legacy building/room number formats
        5. Preserves original text for unparseable cells

        **Example Input Tags**:

        .. code-block:: html

            [<th><em>Day</em>/<em>Time</em></th>, <th>08:00 AM to 09:15 AM</th>, ... ,<th>05:15 PM to 06:30 PM</th>]
            [<th>SUN</th>, ... , <td style="background: #fff ;"> <strong>CSE 417</strong><br/><strong>FC:</strong> SWL   <br/><strong>R:</strong> 2710     </td>, ... , <td style="background:  #FFF ;"> </td>]
            [<th>THR</th>, .. ,<td style="background: #fff ;"> <strong>CSE 476</strong><br/><strong>FC:</strong> SPS   <br/><strong>B:</strong> 2 ⇒ <strong>R:</strong> 419     </td>, ... , <td style="background:  #FFF ;"> </td>]

        **Example Output**:

        .. code-block:: python

            ['Day/Time', '08:00 AM to 09:15 AM', ... , '05:15 PM to 06:30 PM']
            ['THR', ... , TransformedClassPeriod(course_code='CSE 417', faculty_code='SWL', building='2', room='710'), ... , '']
            ['THR', ... , TransformedClassPeriod(course_code='CSE 476', faculty_code='SPS', building='2', room='419'), ... , '']
        """
        new_row = []
        for cell in cells:
            text = cell.get_text(strip=True)
            if not text:
                new_row.append("")  # preserving period index
                continue

            try:
                parts = cell.get_text(separator="\n", strip=True).split("\n")
                _parts = ",".join(parts)
                match = self.CELL_TEXT_REGEX.match(_parts)
                if not match:
                    new_row.append(text)
                    continue

                match_dict = match.groupdict()

                building = match_dict["bnum"]
                room = match_dict["rnum"]

                # Building number fallback logic
                # (older routines used to have building and room number separated)
                if not building and len(room) >= 4:
                    building, room = room[0], room[1:]

                new_row.append(
                    TransformedClassPeriod(
                        course_code=match_dict["ccode"].strip(),
                        faculty_code=match_dict["fcode"].strip(),
                        building=building,
                        room=room,
                    )
                )

            except IndexError as e:
                logger.warning(f"Failed to parse cell content {parts}: {e}")
                new_row.append(text)
                # idk but adding (i mean atleast you can see the half-baked content?)

        return new_row
