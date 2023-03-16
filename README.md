![deploy](https://github.com/WGBH-MLA/FastCLAM/actions/workflows/CI.yml/badge.svg)
![deploy](https://github.com/WGBH-MLA/FastCLAM/actions/workflows/CD.yml/badge.svg)
[![codecov](https://codecov.io/gh/WGBH-MLA/FastCLAM/branch/main/graph/badge.svg?token=AJM7UHKH2V)](https://codecov.io/gh/WGBH-MLA/FastCLAM)

# FastCLAM

[FastAPI](https://fastapi.tiangolo.com/) for [CLAMS](https://clams.ai/)

## Install

### pip

```bash
pip install . uvicorn
```

### poetry

```bash
poetry install
```

Enter into the venv shell

```
poetry shell
```

## Usage

```bash
uvicorn fastclam.app:app --reload
```

Use `--reload` for development only

Visit [localhost:8000/docs](http://localhost:8000/docs)

### Args

Additional args that might be helpful to pass to uvicorn:

- `--host 0.0.0.0`
- `--port PORT`
- `--log-level debug`
