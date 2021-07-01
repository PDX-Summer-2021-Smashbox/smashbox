===============
smashbox_viewer
===============

Smashbox button visualizer

At the moment, this is a couple of libraries for parsing joystick events from
PyGame in a format that can be tested. Later, this is going to be used to
visualize button presses for a Smashbox controller.

============================
Getting Started With Poetry
============================

You'll need to install ``poetry`` from Pypi with

.. code-block:: bash

    python -m pip install poetry

============================
Testing a package
============================

Build a ``.whl`` with

.. code-block:: bash

    poetry build

And in some other Python environment, (possibly a venv or something similar) run

.. code-block:: bash

    python -m pip install smashbox_viewer-0.1.0-py3-none-any.whl

This will install ``smashbox_viewer``, along with its dependencies (``pygame``).

You can now import the ``smashbox_viewer`` library in your code and run the 
``smashbox_viewer.recorder`` with

.. code-block:: bash

    python -m smashbox_viewer.recorder

===========================================
Playing Nicely with IDEs During Development
===========================================

By default, ``poetry`` places the project's ``venv`` inside
``~/.cache/pypoetry/virtualenvs``. This means that your IDE won't be able to
find it, and thus your linter will complain about missing imports and whatnot.
To solve this, run

.. code-block:: bash

    poetry config virtualenvs.in-project true

This will set the ``venv`` location to ``.venv`` inside the project's root directory,
meaning that it will be detected by VSCode.

You can then delete the ``venv`` and run ``poetry install`` to create the new one.
