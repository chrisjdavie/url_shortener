import configparser
import os
import sys

from flask import Flask, redirect
from flask_restful import Api

from shorten_api import DatabaseConnect, ShortenUrl

config_path = sys.argv[1]
config = configparser.ConfigParser()
config.readfp(open(config_path, 'r'))

config_vars = config['Basic']
server_vars = config['Server']

app = Flask(__name__)
api = Api(app)


@app.route('/')
def instructions():
    instructions = ('Redirecting service. Endpoints:<br>'
                    '/shorten_url, POST &lt;full_url&gt;,' 
                    'response GET { "shortened_url": &lt;shortened_url&gt; }<br>'
                    '/&lt;shortened_url&gt;, redirect to &lt;full_url&gt;')
    return instructions


with DatabaseConnect(connect_string = config_vars['connect_string']) as db:

    @app.route('/<short>')
    def shorten(short):
        full_url = db.full_url_from_shortened_url(short)
        if full_url:
            return redirect(full_url)
        return "Shortened URL not valid"

    api.add_resource(ShortenUrl, '/shorten_url', 
         resource_class_args = [db, 
                                config_vars['service_base'],
                                config_vars.getint('shorten_len'), 
                                config_vars.getint('max_len')])
    app.run(debug=True, 
            host=server_vars['host'], 
            port=server_vars.getint('port'))

