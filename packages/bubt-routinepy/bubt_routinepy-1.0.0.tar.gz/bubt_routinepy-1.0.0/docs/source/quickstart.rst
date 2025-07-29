Quickstart Guide
================

Installation
------------

First, install the package using pip:

.. code-block:: bash

   pip install bubt-routinepy

Basic Usage
-----------

The package provides two main clients:

- :class:`~routinepy.lib.scraper.client.ScraperClient` - Retrieves data by parsing the university's official website and PDF documents. 
- :class:`~routinepy.lib.api.client.ApiClient` - Uses the university's internal API (reverse-engineered) for data access.
  
  
Initializing Clients
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # For scraping functionality
   from routinepy.lib import ScraperClient
   scraper = ScraperClient()

   # For API functionality
   from routinepy.lib import ApiClient
   api = ApiClient()

Common Scenarios
----------------

1. Getting Class Routines
~~~~~~~~~~~~~~~~~~~~~~~~~

Department-wide routine:

.. code-block:: python

   from routinepy.lib.enums import ProgramCode

   # Using Scraper or API
   dept_routine = await client.get_class_routine(program_code=ProgramCode.CSE_Day)

Faculty-specific routine:

.. code-block:: python

   # Using Scraper or API
   faculty_routine = await client.get_class_routine(faculty_code="MDI")

Intake-specific routine:

.. code-block:: python

   # Using Scraper or API
   intake_routine = await client.get_class_routine(
       program_code=ProgramCode.CSE_Day,
       intake="49"
   )


2. Getting Exam Routines
~~~~~~~~~~~~~~~~~~~~~~~~

Mid or Final term exams:

.. code-block:: python

   mid_terms = await api.get_mid_routine(
       program_code=ProgramCode.CSE_Day,
       intake="50"
   )

   final_terms = await api.get_final_routine(
       program_code=ProgramCode.CSE_Day,
       intake="50"
   )   

.. note::
   Getting Mid/Final term exam routines is only available via API client

Current term exams:

.. code-block:: python

   # Using Scraper only
   terms = await scraper.get_exam_routine(
       program_code=ProgramCode.CSE_Day,
       intake="50"
   )

.. note::
   The university routine page provides only the current term's exam routine. There is no dedicated section for Mid/Final term exam.

Important Notes
---------------

.. warning::
   **Current Limitations of ScraperClient:**   
      - :class:`ProgramCode.CSE_DAY` is the only program currently supported for exam routine.
      - Supplementary routines is not supported due to the complex and inconsistent PDF structure.
      - Some programs have PDF as the class routine which is not supported.
