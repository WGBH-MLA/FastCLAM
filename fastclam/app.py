from json import loads
from json.decoder import JSONDecodeError
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

import requests
from clams.source import generate_source_mmif_from_file
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ._version import __version__
from .log import log
from .models import Inputs, Pipeline


class MMIFException(HTTPException):
    pass


app = FastAPI(title='FastCLAM', version=__version__)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.get('/')
def home() -> dict:
    """Return version info"""
    return {'FastCLAM': __version__}


@app.post('/source')
def generate_source(files: Inputs) -> dict:
    """Generate a new source MMIF from multiple input files"""
    log.info(f'sourcing media {files.files}')
    mmif = generate_source_mmif_from_file(files.files)
    json_value = loads(str(mmif))
    log.debug(f'sourced: {json_value}')
    return json_value


@app.post('/run')
def run_app(url: str, mmif: dict) -> dict:
    """Run a single app with a single MMIF"""
    log.info(f'Running {url}')
    response = requests.post('http://' + url, json=mmif)
    log.debug(f'received response {response.status_code}, {response.headers}')
    if response.status_code != 200:
        log.debug(response.content)
        raise HTTPException(
            status_code=response.status_code,
            detail=response.content,
        )
    results = response.json()
    log.success(f'{url} Success!')
    return results


@app.post('/pipeline')
def run_pipeline(pipeline: Pipeline) -> list | dict | str:
    """Run a list of media through a list of apps

    Sources all input files into the same input MMIF"""
    log.info(f'Starting pipeline {pipeline}')
    input_mmif = generate_source(Inputs(files=pipeline.files))
    output_mmif = None
    for app in pipeline.apps:
        log.debug(f'Running {pipeline.files} through {app}')
        response = requests.post(app, json=output_mmif or input_mmif)
        log.debug(f'received response {response.status_code}, {response.headers}')
        if response.status_code != 200:
            log.error(f'Bad response from {app} with {pipeline.files}')
            log.debug(response.content)
            raise HTTPException(
                status_code=response.status_code,
                detail=f'Unsuccessful response from {app}: {response.status_code} - {response.content}',  # noqa E501
            )
        content_type = response.headers.get('Content-Type')
        if 'application/json' in content_type:
            try:
                output_mmif = response.json()
            except JSONDecodeError as e:
                log.error(f'Error parsing JSON: {e}')
                log.debug(response.content)
        elif 'application/xml' in content_type:
            try:
                log.debug('parsing as xml')
                output_mmif = ElementTree.fromstring(response.content)
                output_mmif = ElementTree.tostring(output_mmif)
            except ParseError as e:
                log.error(f'Error parsing XML: {e}')
                log.debug(response.content)
                raise MMIFException(
                    status_code=499,
                    detail=f'Failed to parse XML from {app}: {response.status_code} - {response.content}',  # noqa E501
                )

    log.info(f'Ran {len(pipeline.files)} files through {len(pipeline.apps)} apps')

    return output_mmif
