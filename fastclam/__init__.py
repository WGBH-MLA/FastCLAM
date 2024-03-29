"""# FastCLAM

FastAPI for CLAMS

Example:
    Run the server:
        `$ uvicorn fastclam.app`

    Use the API docs to make requests:
        [localhost:8000/docs](http://localhost:8000/docs)

"""

from ._version import __version__
from .app import app

__all__ = ['__version__', 'app']
