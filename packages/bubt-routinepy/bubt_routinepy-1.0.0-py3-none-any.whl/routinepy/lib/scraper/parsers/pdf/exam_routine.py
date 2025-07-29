from pathlib import Path

from loguru import logger

from routinepy.lib.api.enums import ProgramCode

from .exam_routine_006 import Program006ExamPdfParser


class BaseExamPdfParser:
    """
    Factory class that routes exam table extractions to program-specific extractors.

    This class provides the main interface for extracting raw exam table from PDF into
    a workable list for further processing.

    .. note::
        Specific program codes need to have their own implementation.

    .. seealso::
        For an example implementation, see the source code of :class:`Program006ExamPdfParser`.
    """

    @staticmethod
    def extract_raw_tables(program_code: ProgramCode, path: Path) -> list:
        """
        Extracts and returns cleaned raw table data from a PDF file based on the specified program code.

        This method selects an appropriate parser for the given program code and uses it to extract
        table data from the provided PDF file.

        :param program_code: The program code (e.g., '006', '001') to determine the parser to use.
        :type program_code: ProgramCode
        :param path: The file path to the PDF file to be parsed.
        :type path: Path
        :return: A list of raw table data extracted from the PDF.
        :rtype: list

        .. note::
            - Specific program codes need to have their own implementation.

        .. warning::
            - Only :attr:`routinepy.lib.api.enums.ProgramCode.CSE_DAY` using :class:`Program006ExamPdfParser` is currently supported

        .. seealso::
            For an example implementation, see the source code of :class:`Program006ExamPdfParser`.
        """
        parser = None
        match program_code:
            case ProgramCode.CSE_Day:
                parser = Program006ExamPdfParser()

            case _:
                logger.warning(
                    f"Exam PDF parser for program {program_code.name} is not available"
                )
                return

        return parser.extract_raw_tables(path)
