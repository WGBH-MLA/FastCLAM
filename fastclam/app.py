from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from clams.source import generate_source_mmif
from pydantic import BaseModel
from typing import List
import requests
from .log import log
from .version import __VERSION__
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError
from json import loads
from json.decoder import JSONDecodeError


class Inputs(BaseModel):
    files: List[str]


class Pipeline(Inputs):
    apps: List[str]


class MMIFException(HTTPException):
    pass


app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.get('/')
def home() -> dict:
    """version info"""
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
def run_pipeline(pipeline: Pipeline) -> list | dict | str:
    """Run a list of media through a list of apps"""
    results = []
    log.info(f'Starting pipeline {pipeline}')
    for media in pipeline.files:
        input_mmif = generate_source(Inputs(files=[media]))
        output_mmif = None
        for app in pipeline.apps:
            log.debug(f'Running {media} through {app}')
            response = requests.post(app, json=output_mmif or input_mmif)
            log.debug(f'received response {response.status_code}, {response.headers}')
            if response.status_code != 200:
                log.error(f'Bad response from {app} with {media}')
                log.debug(response.content)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f'Unsuccessful response from {app}: {response.status_code} - {response.content}',
                )
            content_type = response.headers.get('Content-Type')
            if 'application/json' in content_type:
                try:
                    output_mmif = response.json()
                    results.append(output_mmif)
                except JSONDecodeError as e:
                    log.error(f'Error parsing JSON: {e}')
                    log.debug(response.content)
            elif 'application/xml' in content_type:
                try:
                    log.debug('parsing as xml')
                    output_mmif = ElementTree.fromstring(response.content)
                    results.append(ElementTree.tostring(output_mmif))
                except ParseError as e:
                    log.error(f'Error parsing XML: {e}')
                    log.debug(response.content)
                    raise MMIFException(
                        status_code=499,
                        detail=f'Failed to parse XML from {app}: {response.status_code} - {response.content}',
                    )

    log.info(f'Ran {len(pipeline.files)} files through {len(pipeline.apps)} apps')

    if len(results) == 1:
        return results[0]
    return results
