===================
OSS Python Template
===================

Python library integrating with MeteoSwiss systems.

Development Setup with Poetry
-----------------------------

Building the Project
''''''''''''''''''''
.. code-block:: console

    $ cd oss-python-template
    $ poetry install

Run Tests
'''''''''

.. code-block:: console

    $ poetry run pytest

Run Quality Tools
'''''''''''''''''

.. code-block:: console

    $ poetry run pylint oss_python_template
    $ poetry run mypy oss_python_template

Generate Documentation
''''''''''''''''''''''

.. code-block:: console

    $ poetry run sphinx-build doc doc/_build

Then open the index.html file generated in *oss-python-template/doc/_build/*.

Build wheels
''''''''''''

.. code-block:: console

    $ poetry build

Using the Library
-----------------

To install oss-python-template in your project, run this command in your terminal:

.. code-block:: console

    $ poetry add oss-python-template

You can then use the library in your project through

    import oss_python_template
