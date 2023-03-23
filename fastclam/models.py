"""Models

Pipeline validation models
"""

from pydantic import BaseModel, AnyHttpUrl
from typing import List


class Inputs(BaseModel):
    """Inputs

    Accepts list of files as input

    Attributes:
        files: A List of file paths as strings
    """

    files: List[str]


class Pipeline(Inputs):
    """Pipeline

    A simple pieline validator, based on Inputs

    Attributes:
        apps: A List of apps to run, where each appp is a url string for the service
    """

    apps: List[AnyHttpUrl]
