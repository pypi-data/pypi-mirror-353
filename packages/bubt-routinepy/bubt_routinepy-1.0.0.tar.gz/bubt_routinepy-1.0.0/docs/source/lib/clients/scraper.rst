Scraper Client
==============

.. automodule:: routinepy.lib.scraper.client
   :members:
   :member-order: bysource
   :undoc-members:

Example
-------

Basic Setup
-----------

First, initialize the Scraper client:

.. code-block:: python

   from routinepy.lib import ScraperClient

   client = ScraperClient()

Some Scenarios
--------------

1. **Department Routine** - Get class routine for an entire department:
   
.. code-block:: python

   data = await client.get_class_routine(program_code=ProgramCode.CSE_Day)

2. **Faculty Routine** - Get class routine for a specific faculty member:

.. code-block:: python

   data = await client.get_class_routine(faculty_code="MDI")

3. **Intake Routine** - Get class routine for a specific department intake:

.. code-block:: python

   data = await client.get_class_routine(program_code=ProgramCode.CSE_Day, intake="50")


4. **Exam Routine** - Get exam routine for a specific department intake:

.. code-block:: python

   data = await client.get_exam_routine(
      program_code=ProgramCode.CSE_Day,
      intake="50"
   )
.. warning::
   - Only `ProgramCode.CSE_DAY` is currently supported