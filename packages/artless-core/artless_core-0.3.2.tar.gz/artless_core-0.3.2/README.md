# artless-core

![PyPI Version](https://img.shields.io/pypi/v/artless-core)
![Development Status](https://img.shields.io/badge/status-3%20--%20Alpha-orange)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/artless-core)
[![Downloads](https://static.pepy.tech/badge/artless-core)](https://pepy.tech/project/artless-core)
![PyPI - License](https://img.shields.io/pypi/l/artless-core)

The artless and ultralight web framework for building minimal APIs and apps.

## Motivation

An extremely minimalistic framework was needed to create the same minimalistic applications. Those "micro" frameworks like `Flask`, `Pyramid`, `CherryPie`, etc - turned out to be not micro at all). Even a single-module `Bottle` turned out to be a "monster" of 4 thousand LOC and supporting compatibility with version 2.7.

Therefore, it was decided to sketch out our own simple, minimally necessary implementation of the WSGI and ASGI library for building simple APIs and apps.

## Why artless-core?

* 🪶 Tiny: Single module, no dependencies, less then 500 LOC
* ⚡ Fast: Optimized pure Python with async support
* 🧩 Simple: Intuitive API with type hints
* ✅ Tested: 100% coverage
* 🐍 Modern: Python 3.11+ only

## Quickstart

### Installation

``` shellsession
$ pip install artless-core
```

### WSGI Example

``` python
from artless import WSGIApp, Request, Response, plain


def say_hello(request: Request, name: str) -> Response:
    return plain(f"Hello, {name}!")


def create_application() -> WSGIApp:
    app = WSGIApp()
    app.set_routes([("GET", r"^/hello/(?P<name>\w+)$", say_hello)])
    return app


application = create_application()
```

Run with Gunicorn:

``` shellsession
$ gunicorn app
[2025-01-11 16:34:19 +0300] [62111] [INFO] Starting gunicorn 23.0.0
[2025-01-11 16:34:19 +0300] [62111] [INFO] Listening at: http://127.0.0.1:8000 (62111)
[2025-01-11 16:34:19 +0300] [62111] [INFO] Using worker: sync
[2025-01-11 16:34:19 +0300] [62155] [INFO] Booting worker with pid: 62155
```

Check it:

``` shellsession
$ curl http://127.0.0.1:8000/hello/Bro
Hello, Bro!
```

Need more? See [documentation](https://pages.peterbro.su/py3-artless-core/) and [wsgi examples](https://git.peterbro.su/peter/py3-artless-core/src/branch/master/examples/wsgi).

### ASGI Example

``` python
from artless import ASGIApp, Request, Response, plain


async def say_hello(request: Request, name: str) -> Response:
    return plain(f"Hello, {name}!")


def create_application() -> ASGIApp:
    app = ASGIApp()
    app.set_routes([("GET", r"^/hello/(?P<name>\w+)$", say_hello)])
    return app


application = create_application()
```

Run with Uvicorn:

``` shellsession
$ uvicorn app:application
INFO:     Started server process [62683]
INFO:     Waiting for application startup.
INFO:     ASGI 'lifespan' protocol appears unsupported.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Check it:

``` shellsession
$ curl http://127.0.0.1:8000/hello/Bro
Hello, Bro!
```

Need more? See [documentation](https://pages.peterbro.su/py3-artless-core/) and [asgi examples](https://git.peterbro.su/peter/py3-artless-core/src/branch/master/examples/asgi).

## Limitations

* ❌ No `WebSockets`
* ❌ No `multipart/form-data` support.
* ❌ No `Cookies` support.
* ❌ No builtin models, ORM, template engine, form serialisation and other.
* ❌ No built-in protections, such as: `CSRF`, `XSS`, `clickjacking` and other.

## Benchmarks results

See more details in benchmarks/README.md.

## WSGI (single worker)

| Framework | RPS (mean) |
|-----------|------------|
| Falcon    | 1794.59    |
| Artless   | 1782.67    |
| Bottle    | 1646.37    |
| Flask     | 1468.70    |
| Django    | 1359.61    |

## WSGI (multiple workers)

| Framework | RPS (mean) |
|-----------|------------|
| Falcon    | 3437.07    |
| Artless   | 3414.04    |
| Bottle    | 3331.41    |
| Flask     | 2974.08    |
| Django    | 1701.12    |

## ASGI (single worker)

| Framework  | RPS (mean) |
|------------|------------|
| Blacksheep | 3456.86    |
| Falcon     | 3338.41    |
| Artless    | 3320.35    |
| FastAPI    | 2191.76    |
| Django     | 1160.94    |
| Flask      | 777.81     |

## ASGI multiple workers plaintext response

| Framework  | RPS (mean) |
|------------|------------|
| Falcon     | 5393.27    |
| Blacksheep | 5382.32    |
| Artless    | 5332.50    |
| FastAPI    | 3594.12    |
| Django     | 2050.55    |
| Flask      | 1627.59    |

## Roadmap

- [x] Add Sphinx doc.
- [x] Add benchmarks.
- [x] Add Async/ASGI support.
- [ ] Add test clients (for WSGI and ASGI).
- [ ] Add plugins support.
- [ ] Add middlewares support.
- [ ] Add more complex examples.

## Related projects

* [artless-template](https://pypi.org/project/artless-template/) - the artless and small template library for server-side rendering.
