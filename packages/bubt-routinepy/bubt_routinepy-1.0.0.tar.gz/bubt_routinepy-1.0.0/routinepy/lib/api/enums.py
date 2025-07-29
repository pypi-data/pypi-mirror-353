from enum import Enum, StrEnum


class SemesterType(StrEnum):
    """
    Type of semester.
    """

    PREVIOUS = "past"
    CURRENT = "present"
    UPCOMING = "upcoming"


class ProgramCode(StrEnum):
    """
    Program codes representing different academic programs.
    """

    B_Arch = "026"
    """
    .. note::
        Program details: Bachelor of Architecture
    
    .. warning::    
        The program is discontinued
    """
    BBA = "001"
    """
    .. note::
        Program details: `Bachelor of Business Administration <https://www.bubt.edu.bd/home/course_details/bba>`_
    """
    CSE_Day = "006"
    """
    .. note::
        Program details: `Computer Science and Engineering <https://www.bubt.edu.bd/home/course_details/bsc-in-cse>`_ (Day Shift)
    """
    CSE_Evn = "019"
    """
    .. note::
        Program details: `Computer Science and Engineering <https://www.bubt.edu.bd/home/course_details/bsc-in-cse>`_ (Evening Shift)
    """
    CSIT = "005"
    """
    .. note::
        Program details: Computer Science & Information Technology
    .. warning::    
        The program is discontinued    
    """
    CVL_Day = "027"
    """
    .. note::
        Program details: `Civil Engineering <https://www.bubt.edu.bd/department/information/civil-engineering>`_ (Day Shift)

    .. warning::    
        The program is discontinued    
    """
    CVL_Evn = "028"
    """
    .. note::
        Program details: `Civil Engineering <https://www.bubt.edu.bd/department/information/civil-engineering>`_ (Evening Shift)   
    """
    ECO = "020"
    """
    .. note::
        Program details: `B.Sc. (Hons.) in Economics <https://www.bubt.edu.bd/home/course_details/bsc-hons-in-economics>`_
    """
    ECO_MSc = "013"
    """
    .. note::
        Program details: `M.Sc. in Economics  <https://www.bubt.edu.bd/home/course_details/msc-in-economics-one-year-program>`_
    """
    EDE = "025"
    """
    .. note::
        Program details: `B.Sc. in Environment and Development Economics <https://www.bubt.edu.bd/home/course_details/bsc-hons-in-ede>`_
    .. warning::    
        The program is discontinued        
    """
    EEE_Day = "021"
    """
    .. note::
        Program details: `B.Sc. in Electrical and Electronic Engineering <https://www.bubt.edu.bd/home/course_details/bsc-in-eee>`_ (Day Shift)
    """
    EEE_Evn = "023"
    """
    .. note::
        Program details: `B.Sc. in Electrical and Electronic Engineering <https://www.bubt.edu.bd/home/course_details/bsc-in-eee>`_ (Evening Shift)
    """
    ELT_MA = "016"
    """
    .. note::
        Program details: `M.A. in English Language Teaching <https://www.bubt.edu.bd/home/course_details/ma-in-elt>`_
    """
    EMBA = "004"
    """
    .. note::
        Program details: `Executive MBA <https://www.bubt.edu.bd/home/course_details/executive-mba>`_
    """
    ENG_BA = "007"
    """
    .. note::
        Program details: `B.A (Hons) in English <https://www.bubt.edu.bd/home/course_details/ba-hons-in-english>`_
    """
    ENG_MA = "008"
    """
    .. note::
        Program details: `MA in English Literature <https://www.bubt.edu.bd/home/course_details/ma-in-english-literature-one-year-program>`_
    .. warning::    
        The program is discontinued    
    """
    LLB = "009"
    """
    .. note::
        Program details: `Bachelor of Laws <https://www.bubt.edu.bd/home/course_details/llb-hons>`_
    .. warning::    
        The program is discontinued    
    """
    LLB_1y = "010"
    """
    .. note::
        Program details: Bachelor of Laws (1 year)
    .. warning::    
        The program is discontinued    
    """
    LLB_2y = "012"
    """
    .. note::
        Program details: Bachelor of Laws (2 years)
    .. warning::    
        The program is discontinued    
    """
    LLM_1y = "014"
    """
    .. note::
        Program details: `Master of Laws <https://www.bubt.edu.bd/home/course_details/llm-1-year>`_ (1 year)
    .. warning::    
        The program is discontinued
    """
    LLM_2y = "015"
    """
    .. note::
        Program details: Master of Laws (2 year)
    .. warning::    
        The program is discontinued
    """
    Math_1y = "011"
    """
    .. note::
        Program details: M.Sc. in Mathematics (1 year)
    .. warning::    
        The program is discontinued
    """
    Math_2y = "018"
    """
    .. note::
        Program details: M.Sc. in Mathematics (1 year)
    .. warning::    
        The program is discontinued
    """
    MBA_Day = "002"
    """
    .. note::
        Program details: `MBA <https://www.bubt.edu.bd/home/course_details/mba>`_ (Day Shift)
    """
    MBA_Evn = "003"
    """
    .. note::
        Program details: `MBA <https://www.bubt.edu.bd/home/course_details/mba>`_ (Evening Shift)
    """
    MBM = "017"
    """
    .. note::
        Program details: `Master of Bank Management <https://www.bubt.edu.bd/home/course_details/mbm>`_
    .. warning::    
        The program is discontinued
    """
    TEXT_Day = "022"
    """
    .. note::
        Program details: `B.Sc. in Textile Engineering <https://www.bubt.edu.bd/home/course_details/bsc-in-textile-engineering>`_
    """
    TEXT_Evn = "024"
    """
    .. note::
        Program details: `B.Sc. in Textile Engineering <https://www.bubt.edu.bd/home/course_details/bsc-in-textile-engineering>`_
    """


class RoutineType(Enum):
    """
    Type of routine.
    """

    CLASS = "class"
    MID = "mid"
    FINAL = "final"


class SyncRoutineType(Enum):
    """
    This enum is similar to :class:`RoutineType` but is used exclusively when making
    requests to retrieve the last update time of a routine.
    """

    CLASS = "routine"
    MID = "mid-exam"
    FINAL = "final-exam"


class ShiftTime(StrEnum):
    """
    Shift type of different academic programs.
    """

    DAY = "Day"
    EVENING = "Evening"


class Weekday(StrEnum):
    SUNDAY = "sun"
    MONDAY = "mon"
    TUESDAY = "tues"
    WEDNESDAY = "wednes"
    THURSDAY = "thurs"
    FRIDAY = "fri"
    SATURDAY = "sat"
