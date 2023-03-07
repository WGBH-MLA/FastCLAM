from fastapi import FastAPI
from clams.source import generate_source_mmif
from json import loads
from pydantic import BaseModel
from typing import List
import requests
from os import path, environ
from datetime import datetime
from .version import __VERSION__


class Inputs(BaseModel):
    files: List[str]


class Pipeline(Inputs):
    apps: List[str]


app = FastAPI()


@app.get('/')
def home() -> dict:
    """version info"""
    return {'FastCLAM': __VERSION__}


@app.post('/source')
def generate_source(files: Inputs) -> dict:
    """Generate a new source MMIF"""
    mmif = generate_source_mmif(files.files)
    json_value = loads(str(mmif))
    return json_value


@app.post('/pipeline')
def run_pipeline(pipeline: Pipeline) -> list:
    results = []
    for media in pipeline.files:
        mmif = generate_source(Inputs(files=[media]))
        results.append(mmif)
        print('have source', mmif)
        for app in pipeline.apps:
            response = requests.post(app, json=mmif)
            assert response.status_code == 200, f'Error with {pipeline}: {response}'
            mmif = response.json()
            results.append(mmif)
    print('results: ', results)
    return results
