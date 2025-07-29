Command Line Interface
======================

A CLI tool to fetch academic routine with various filtering options.

Basic Usage
-----------

.. code-block:: bash

   routinepy --routine-type <TYPE> [OPTIONS]


Required Arguments
------------------

.. program:: routine_fetcher
.. option:: --routine-type <TYPE>

   *Required*. Specifies the type of routine to fetch.

   Choices: see :class:`~routinepy.lib.api.enums.RoutineType` for valid values

Optional Filters
---------------

.. option:: --semester-type <TYPE>

   Semester filter (default: ``present``).

   Choices: see :class:`~routinepy.lib.api.enums.SemesterType` for valid values

.. option:: --faculty-code <CODE>

   Short code of the faculty member.

.. option:: --room <NUMBER>

   4-digit room number filter.

.. option:: --program-code <CODE>

   Program code filter.

   Choices: see :class:`~routinepy.lib.api.enums.ProgramCode` for valid values

.. option:: --intake <NUMBER>

   Intake number

.. option:: --section <NUMBER>

   Section number (requires intake).

.. option:: --course-code <CODE>

   Course code to filter by.

Output Options
--------------

.. option:: --format <FORMAT>

   Output format (default: ``text``).

   Choices: ``json``, ``html``, ``text``

.. option:: --output-dir <PATH>

   Path to save output file.

.. option:: --verbose

   Enable detailed logging.


Examples
--------

- Fetch current class routine of CSE (day) department in JSON format:

.. code-block:: bash

   routinepy --routine-type class --program-code 006 --format json

- Fetch current class routine of CSE (day) department intake 50:

.. code-block:: bash

   routinepy --routine-type class --program-code 006 --intake 50

- Fetch exam routine for specific program:

.. code-block:: bash

   routinepy --routine-type mid --program-code 006