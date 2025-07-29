# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from __future__ import annotations

from typing import TYPE_CHECKING
from sphinx.domains.python import PythonDomain

if TYPE_CHECKING:
    from docutils.nodes import Element
    from sphinx.application import Sphinx
    from sphinx.builders import Builder
    from sphinx.environment import BuildEnvironment
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "MaMMoS"
copyright = "2025, Thomas Schrefl, Swapneel Amit Pathak, Andrea Petrocchi, Samuel Holt, Martin Lang, Hans Fangohr"
author = "Thomas Schrefl, Swapneel Amit Pathak, Andrea Petrocchi, Samuel Holt, Martin Lang, Hans Fangohr"
# release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "nbsphinx",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
autosummary_generate = True
autosummary_generate_overwrite = True
autodoc_mock_imports = ["esys-escript", "mammos_mumag.simulation"]
autoclass_content = "both"
autodoc_typehints = "description"
autodoc_default_options = {
    # Autodoc members
    "members": True,
    # Autodoc undocumented memebers
    "undoc-members": True,
    # Autodoc private memebers
    "private-members": False,
    # Autodoc special members (for the moment only __init__)
    "special-members": "__init__",
}
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "astropy": ("https://docs.astropy.org/en/stable", None),
}
exclude_patterns = ["**.ipynb_checkpoints"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]

html_theme_options = {
    "external_links": [
        {"name": "MaMMoS project", "url": "https://mammos-project.github.io"},
    ],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/MaMMoS-project",
            "icon": "fab fa-github-square",
        },
    ],
    "header_links_before_dropdown": 6,

}
html_sidebars = {
    "changelog": [],
    "design": [],
}


# code snippet for fixing mappings taken from
# https://github.com/tox-dev/pyproject-api/blob/136e5ded8f65fb157c2e5fee5e8e05de9eefcdd4/docs/conf.py
def setup(app: Sphinx) -> None:  # noqa: D103
    class PatchedPythonDomain(PythonDomain):
        def resolve_xref(  # noqa: PLR0913,PLR0917
            self,
            env: BuildEnvironment,
            fromdocname: str,
            builder: Builder,
            type: str,  # noqa: A002
            target: str,
            node: resolve_xref,
            contnode: Element,
        ) -> Element:
            # fixup some wrongly resolved mappings
            mapping = {
                "pathlib._local.Path": "pathlib.Path",
            }
            if target in mapping:
                target = node["reftarget"] = mapping[target]
            return super().resolve_xref(
                env, fromdocname, builder, type, target, node, contnode
            )

    app.add_domain(PatchedPythonDomain, override=True)
