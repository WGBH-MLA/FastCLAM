"""# FastCLAM.app

Example:
    `$ uvicorn fastclam.app`

Todo:
    Stuff

"""

from fastapi import FastAPI
from clams.source import generate_source_mmif
from json import loads
import requests
from .log import log
from .models import Inputs, Pipeline
from .version import __VERSION__
from xml.etree import ElementTree


app = FastAPI()


@app.get('/')
def home() -> dict:
    """Return version info"""
    return {'FastCLAM': __VERSION__}


@app.post('/source')
def generate_source(files: Inputs) -> dict:
    """Generate a new source MMIF from multiple input files"""
    log.info(f'sourcing media {files.files}')
    mmif = generate_source_mmif(files.files)
    json_value = loads(str(mmif))
    log.debug(f'sourced: {json_value}')
    return json_value


@app.post('/pipeline')
def run_pipeline(pipeline: Pipeline, all: bool = False) -> list:
    """Run a list of media through a list of apps"""
    results = []
    log.info(f'Starting pipeline {pipeline}')
    for media in pipeline.files:
        mmif = generate_source(Inputs(files=[media]))

        for app in pipeline.apps:
            log.debug(f'Running {media} through {app}')
            response = requests.post(app, json=mmif)
            assert response.status_code == 200, f'Error with {pipeline}: {response}'
            try:
                mmif = response.json()
            except Exception as e:
                log.warn(f'Error parsing json {e}')
                log.debug('Trying to parse as xml')
                mmif = ElementTree.fromstring(response.content)
            results.append(mmif)

    log.info(f'Ran {len(pipeline.files)} files through {len(pipeline.apps)} apps')
    return results
