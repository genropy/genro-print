Computed Objects
================

Computed objects are the result of compiling a Bag structure. They contain
all calculated values (dimensions, positions) ready for rendering.

.. note::

   The computed module is planned but not yet implemented. The current
   implementation compiles directly within the builder's ``render()`` method.

   Future versions will separate compilation into dedicated computed objects
   for better testability and caching.
