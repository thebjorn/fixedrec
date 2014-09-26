.. fixedrec documentation master file, created by
   sphinx-quickstart on Thu Feb 13 18:59:19 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to fixedrec's documentation!
=================================

Installation::

    pip install -e <path-to-fixedrec-folder-containing-setup.py>

or simply (if your in the project folder):

    pip install -e .


Running tests
------------------------------------------------------------
One of:

    python setup.py test
    py.test fixedrec
    python runtests.py

with coverage (one of):

    py.test --cov=.
    python runtests.py --cov=.
    coverage run runtests.py && coverage report



Building documentation
------------------------------------------------------------

    python setup.py build_sphinx


Contents:

.. toctree::
   :maxdepth: 2




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
