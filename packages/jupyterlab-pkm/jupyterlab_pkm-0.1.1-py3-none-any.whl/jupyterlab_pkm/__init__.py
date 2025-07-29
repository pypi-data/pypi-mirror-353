"""
jupyterlab_pkm

Personal Knowledge Management extension for JupyterLab Desktop
"""

from ._version import __version__

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "@jupyterlab/pkm-extension"
    }]