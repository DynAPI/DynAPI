#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
from collections import defaultdict
import flask
from flask import request
from __main__ import app
from database import DatabaseConnection, dbutil


@app.route("/list-tables-meta")
def list_tables_meta():
    meta_data = defaultdict(lambda: dict())
    with DatabaseConnection() as conn:
        for table in dbutil.list_tables(connection=conn):
            meta_data[table.schema][table.table] = dbutil.list_columns(
                connection=conn, schema=table.schema, table=table.table
            )

    response_format = request.args.get('format', 'short')
    if response_format == "short":
        return flask.jsonify(meta_data)
    elif response_format == "long":
        return flask.jsonify(
            transform_format_short2long(meta_data)
        )
    else:
        raise KeyError(response_format)


def transform_format_short2long(short):
    return [
        {
            'schema_name': schema_name,
            'tables': [
                {
                    'table_name': table_name,
                    'columns': [
                        {
                            'column_name': column_name,
                            'specs': cols
                        } for column_name, cols in column_meta.items()
                    ]
                } for table_name, column_meta in table_meta.items()
            ]
        } for schema_name, table_meta in short.items()
    ]


def get_openapi_spec():
    def get_basic_meta(schema: dict, fmt: str):
        return {
            'get': {
                'tags': ["Meta"],
                'summary': f"Gets Schema with their Tables and columns ({fmt})",
                'parameters': [
                    {
                        'name': "__format__",
                        'in': "query",
                        'description': "Response Format",
                        'schema': dict(
                            type="string",
                            enum=["short", "long"],
                            default="short",
                            example=fmt,
                        )
                    },
                ],
                'responses': {
                    '200': {
                        'description': "Successful operation",
                        'content': {
                            "application/json": {
                                'schema': schema
                            }
                        }
                    }
                }
            }
        }

    return {
        # format: short
        # {
        #     schema: {
        #         table: {
        #             id: {},
        #             name: {}
        #         },
        #     },
        # }
        '/list-tables-meta': get_basic_meta({
            'type': "object",
            'properties': {
                'schema': {
                    'type': "object",
                    'properties': {
                        'table': {
                            'type': "object",
                            'properties': {
                                'column': {
                                    'type': "object",
                                    'properties': {
                                        'is_nullable': {
                                            'type': "string"
                                        },
                                        'data_type': {
                                            'type': "string"
                                        },
                                        'is_identity': {
                                            'type': "string"
                                        },
                                        'is_generated': {
                                            'type': "string"
                                        },
                                        'is_updatable': {
                                            'type': "string"
                                        },
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }, "short"),
        # format: long
        # [
        #     {
        #         schema_name: string,
        #         tabels: [
        #             {
        #                 table_name: string
        #                 columns: [
        #                     {
        #                         column_name: string
        #                     }
        #                 ]
        #             }
        #         ]
        #     }
        # ]
        '/list-tables-meta?__format__=long': get_basic_meta({
            'type': "array",
            'items': {
                'type': "object",
                'properties': {
                    'schema_name': {
                        'type': "string",
                    },
                    'tables': {
                        'type': "array",
                        'items': {
                            'type': "object",
                            'properties': {
                                'table_name': {
                                    'type': "string",
                                },
                                'columns': {
                                    'type': "array",
                                    'items': {
                                        'type': "object",
                                        'properties': {
                                            'is_nullable': {
                                                'type': "string"
                                            },
                                            'data_type': {
                                                'type': "string"
                                            },
                                            'is_identity': {
                                                'type': "string"
                                            },
                                            'is_generated': {
                                                'type': "string"
                                            },
                                            'is_updatable': {
                                                'type': "string"
                                            },
                                        }
                                    }
                                }
                            },
                        }
                    }
                },
            }
        }, "long")
    }
