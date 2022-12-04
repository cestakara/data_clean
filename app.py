#import library regex, pandas, sqlite
import re
import sqlite3 as sql
import pandas as pd

#import from flask
from flask import Flask, jsonify, request
from flasgger import Swagger, LazyJSONEncoder, LazyString, swag_from

#define app w/ flask
app = flask(__name__)
app.json_encoder = LazyJSONEncoder

swagger_template = dict(
    info = {
        'title': LazyString(lambda:'API Data Cleansing Hate Speech Twitter Gold Challenge'),
        'version': LazyString(lambda:'1.0.0'),
        'description': LazyString(lambda:'Dokumentasi Cleansing data hate speech')
        }, host = LazyString(lambda: request.host)
    }
)

swagger_config = {
        "headers":[],
        "specs":[
            {
            "endpoint":'docs',
            "route":'/docs.json'
            }
        ],
        "static_url_path":"/flasgger_static",
        "swagger_ui":True,
        "specs_route":"/docs/"
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)

#Import 'kamus alay' and 'abusive words'
