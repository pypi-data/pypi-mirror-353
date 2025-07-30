=================
Hackathon 18 Demo
=================

A demo library for the hackathon




Development Setup with Poetry
-----------------------------

Building the Project
''''''''''''''''''''
.. code-block:: console

    $ cd hackathon-18-demo
    $ poetry install

Run Tests
'''''''''

.. code-block:: console

    $ poetry run pytest

Run Quality Tools
'''''''''''''''''

.. code-block:: console

    $ poetry run pylint hackathon_18_demo
    $ poetry run mypy hackathon_18_demo

Generate Documentation
''''''''''''''''''''''

.. code-block:: console

    $ poetry run sphinx-build doc doc/_build

Then open the index.html file generated in *hackathon-18-demo/doc/_build/*.

Build wheels
''''''''''''

.. code-block:: console

    $ poetry build

Using the Library
-----------------

To install hackathon-18-demo in your project, run this command in your terminal:

.. code-block:: console

    $ poetry add hackathon-18-demo

You can then use the library in your project through

    import hackathon_18_demo
