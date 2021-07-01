========
Smashbox Viewer
========

Lawrence Gunnell, Michael Bottini, Bennet Wright, Jordan Malubay

This button visualizer for the Smashbox controller will allow users to live view the buttons
that are being pressed while the controller is in use.

The Smashbox controller is an arcade button style controller that is meant to emulate 
a Nintendo Gamecube controller. The Smashbox replaces the analog 2-axis joysticks with 4 buttons
that represent the cardinal angles of the joysticks and 7 modifier buttons to output the
intermediate angles. The Smashbox still outputs the same information as the normal Gamecube
controller. This program will interpret the output from the controller and display the button
combinations pressed so users can accurately show controller inputs.  

=======
Roadmap
=======

Week 1 - Frame poller and event generator - DONE
    Polls the controller for its current state as a frame, can also
    record a set of frames. Event generator checks for differences
    between frames based on a set tolerance.

Week 2 - Visual assets, README, License
    Visualizer image resources and project information. 

Week 4 - Mapping
    Input mapping for frame data.

Week 5 - Calibration
    Initial controller setup handling.

Week 7 - Visualizer (MVP)
    Display of controller data from event generator.

============================
Development Notes
============================

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

    python -m pip install smashbox-0.1.0-py3-none-any.whl

This will install ``smashbox``, along with its dependencies (``pygame``).

You can now import the ``smashbox`` library in your code and run the 
``smashbox.recorder`` with

.. code-block:: bash

    python -m smashbox.recorder

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
