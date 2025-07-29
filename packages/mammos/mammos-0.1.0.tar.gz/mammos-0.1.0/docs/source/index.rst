.. MaMMoS documentation master file, created by
   sphinx-quickstart on Wed May 21 08:47:01 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MaMMoS documentation
====================

.. toctree::
   :maxdepth: 1
   :hidden:

   Home <self>
   examples/index
   api
   design
   changelog

About
-----

MaMMoS provides software suite for magnetic multiscale modeling. It consists of several software components. The following table provides a short overview and contains links to example and API reference for the individual packages. The binder badges allow running the examples for the individual packages interactively in the cloud.

.. list-table::
   :header-rows: 1

   * - Package repository
     - Examples
     - API
     - Interactive examples
   * - `mammos <https://github.com/mammos-project/mammos>`__
     - Workflows in :doc:`examples/index`
     - –
     - .. image:: https://mybinder.org/badge_logo.svg
          :target: https://mybinder.org/v2/gh/mammos-project/mammos/main?urlpath=lab%2Ftree%2Fdocs%2Fsource%2Fexamples%2Fworkflows
   * - `mammos-analysis <https://github.com/mammos-project/mammos-analysis>`__
     - :doc:`examples/mammos-analysis/index`
     - :doc:`_autosummary/mammos_analysis`
     - .. image:: https://mybinder.org/badge_logo.svg
          :target: https://mybinder.org/v2/gh/mammos-project/mammos-analysis/main?urlpath=lab%2Ftree%2Fexamples
   * - `mammos-dft <https://github.com/mammos-project/mammos-dft>`__
     - :doc:`examples/mammos-dft/index`
     - :doc:`_autosummary/mammos_dft`
     - .. image:: https://mybinder.org/badge_logo.svg
          :target: https://mybinder.org/v2/gh/mammos-project/mammos-dft/main?urlpath=lab%2Ftree%2Fexamples
   * - `mammos-entity <https://github.com/mammos-project/mammos-entity>`__
     - :doc:`examples/mammos-entity/index`
     - :doc:`_autosummary/mammos_entity`
     - .. image:: https://mybinder.org/badge_logo.svg
          :target: https://mybinder.org/v2/gh/mammos-project/mammos-entity/main?urlpath=lab%2Ftree%2Fexamples
   * - `mammos-mumag <https://github.com/mammos-project/mammos-mumag>`__
     - :doc:`examples/mammos-mumag/index`
     - :doc:`_autosummary/mammos_mumag`
     - .. image:: https://mybinder.org/badge_logo.svg
          :target: https://mybinder.org/v2/gh/mammos-project/mammos-mumag/main?urlpath=lab%2Ftree%2Fexamples
   * - `mammos-spindynamics <https://github.com/mammos-project/mammos-spindynamics>`__
     - :doc:`examples/mammos-spindynamics/index`
     - :doc:`_autosummary/mammos_spindynamics`
     - .. image:: https://mybinder.org/badge_logo.svg
          :target: https://mybinder.org/v2/gh/mammos-project/mammos-spindynamics/main?urlpath=lab%2Ftree%2Fexamples
   * - `mammos-units <https://github.com/mammos-project/mammos-units>`__
     - :doc:`examples/mammos-units/index`
     - :doc:`_autosummary/mammos_units`
     - .. image:: https://mybinder.org/badge_logo.svg
          :target: https://mybinder.org/v2/gh/mammos-project/mammos-units/main?urlpath=lab%2Ftree%2Fexamples

Installation
------------

The MaMMoS software suite consists of a collection of packages for ... workflows. The metapackage ``mammos`` can be used to install a consistent set of sub-packages.


.. tab-set::

   .. tab-item:: pixi

      Requirements: ``pixi`` (https://pixi.sh/)

      Pixi will install Python and mammos.

      To conveniently work with the notebook tutorials we install
      ``jupyterlab``. (``packaging`` needs to be pinned due to a limitation of
      pixi/PyPI.):

      Some examples also require `esys-escript
      <https://github.com/LutzGross/esys-escript.github.io>`__. On linux we can
      install it from conda-forge. On Mac or Windows refer to the esys-escript
      installation instructions:

      - Linux:

        .. code:: shell

           pixi init
           pixi add python jupyterlab "packaging<25" esys-escript
           pixi add mammos --pypi

      - Mac/Windows:

        .. code:: shell

           pixi init
           pixi add python jupyterlab "packaging<25"
           pixi add mammos --pypi

      Finally start a shell where the installed packages are available:

      .. code:: shell

         pixi shell

   .. tab-item:: conda

      Requirements: ``conda`` (https://conda-forge.org/download/)

      Use ``conda`` in combination with ``pip`` to get packages from
      conda-forge and PyPI.

      To conveniently work with the notebook tutorials we install
      ``jupyterlab``. (``packaging`` needs to be pinned due to a dependency
      issue in ``mammos-entity``.)

      Some examples also require `esys-escript
      <https://github.com/LutzGross/esys-escript.github.io>`__. On linux we can
      install it from conda-forge. On Mac or Windows refer to the esys-escript
      installation instructions.

      .. code:: shell

         conda create -n mammos-environment python pip jupyterlab "packaging<25" esys-escript
         conda activate mammos-environment
         pip install mammos

   .. tab-item:: pip

      Requirements: ``python>=3.11`` and ``pip``

      When using ``pip`` we recommend creating a virtual environment to isolate the MaMMoS installation.

      First, create a new virtual environment. Here, we choose the name
      ``mammos-venv``.

      .. code:: shell

         python3 -m venv mammos-venv

      To activate it run

      - on MacOS/Linux

        .. code:: shell

          . mammos-venv/bin/activate
          pip install mammos

      - on Windows

        .. code:: shell

           mammos-venv/bin/activate.sh

      Finally install ``mammos`` from PyPI:

      .. code:: shell

        pip install mammos

      Some examples also require `esys-escript
      <https://github.com/LutzGross/esys-escript.github.io>`__, which must be
      installed separately. Please refer to the documentation of esys-escript
      for installation instructions.

Acknowledgement
---------------

This software has been supported by the European Union’s Horizon Europe research and innovation programme under grant agreement No 101135546 `MaMMoS <https://mammos-project.github.io/>`__.
