from loguru import logger

from routinepy.lib.api.enums import ProgramCode
from routinepy.lib.models import TermExam

from .exam_routine_006 import Program006ExamTableTransformer


class BaseExamTableTransformer:
    """
    Factory class that routes exam table transformations to program-specific parsers.

    Provides the main interface for converting raw exam HTML table into :class:`~routinepy.lib.models.TermExam` objects,
    moving the actual transformation to program-specific implementations.

    .. note::
        Specific program codes need to have their own implementation.

    .. seealso::
        For an example implementation, see the source code of :class:`Program006ExamTableTransformer`.
    """

    def transform_to_models(
        self, tables: list, program_code: ProgramCode
    ) -> list[TermExam]:
        """
        Transforms raw exam table data into structured :class:`~routinepy.lib.models.TermExam` models.

        Data is transformed using program-specific parser based on the
        program code and returns a list of standardized :class:`~routinepy.lib.models.TermExam` objects.

        :param rows: list of table rows
        :type rows: list
        :param program_code: Program code of the routine (e.g., '006', '001')
        :type ProgramCode: str
        :return: List of `TermExam` extracted from the table or None if no parser exists
            for the specified program code
        :rtype: list[TermExam] | None
        """

        parser = None
        match program_code:
            case ProgramCode.CSE_Day:
                parser = Program006ExamTableTransformer()

            case _:
                logger.warning(
                    f"Exam PDF Table transformer for program {program_code.name} is not available"
                )
                return

        return parser.transform_to_models(tables, program_code=program_code)
