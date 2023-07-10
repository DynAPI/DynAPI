#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from __main__ import app, __version__, ROUTES
import textwrap
import datetime
import traceback
from collections import defaultdict
from database import DatabaseConnection, dbutil
from util import minicache
from exceptions import DoNotImportException
from apiconfig import config


if not config.getboolean("web", "redoc", fallback=False) and not config.getboolean("web", "swagger", fallback=False):
    raise DoNotImportException()


@app.route("/openapi")
@minicache(max_age=30)
def openapi():
    paths = defaultdict(dict)
    with DatabaseConnection() as connection:
        tables_meta = dbutil.list_tables_meta(connection=connection)
        for route in ROUTES:
            if not hasattr(route, 'get_openapi_spec'):
                continue
            try:
                spec = route.get_openapi_spec(connection, tables_meta)
                if not isinstance(spec, dict):
                    raise TypeError(f"{type(spec).__name__} is not of type dict")
            except Exception as exc:
                print(f"Failed to load openapi_spec from {route.__name__}")
                traceback.print_exception(type(exc), exc, exc.__traceback__)
            else:
                for path, path_spec in spec.items():
                    paths[path].update(path_spec)
    return dict(
        openapi="3.0.0",
        info=dict(
            title="DynAPI",
            version=__version__,
            # summary=summary,
            description=textwrap.dedent(fr"""
            Last-Update: {datetime.datetime.now():%Y-%m-%d %H:%M}.
            See the [documentation](/docs) or [go Home](/)
            """.strip()),
        ),
        paths=paths,
    )
