"""Launches the Flask url shortening app

Connects to a memcache server described in the config file
"""
import configparser
import os
import sys

from flask import Flask, redirect, Response
from flask_api import status
from flask_restful import Api
from pymemcache.client.base import Client

from shorten_api import DatabaseConnect, ShortenUrl

# getting configuation variables from file
config_path = sys.argv[1]
config = configparser.ConfigParser()
config.readfp(open(config_path, 'r'))

config_vars = config['Basic']
server_vars = config['Server']
memcache_vars = config['memcache']

app = Flask(__name__)
api = Api(app)

memcache_client = Client(('localhost', 11211))

@app.route('/')
def instructions():
    """Something to appear on the front end"""
    instructions = ('Redirecting service. Endpoints:<br>'
                    '/shorten_url, POST &lt;full_url&gt;,' 
                    'response GET { "shortened_url": &lt;shortened_url&gt; }<br>'
                    '/&lt;shortened_url&gt;, redirect to &lt;full_url&gt;')
    return instructions


with DatabaseConnect(connect_string = config_vars['connect_string'],
                     tmp_db_path = config_vars['tmp_db_path']) as db:

    @app.route('/<short>')
    def redirect_from(short):
        """redirects a short url to the corresponding full url
        
        Tries to get it from memcache. If not there, tries the db.
        If not there, returns an error"""
        full_url = memcache_client.get(short)
        if not full_url:
            full_url = db.full_url_from_shortened_url(short)
            if full_url:
                memcache_client.set(short, full_url)

        if full_url:
            return redirect(full_url)
        return Response("Shortened URL not valid", status.HTTP_400_BAD_REQUEST)

    api.add_resource(ShortenUrl, '/shorten_url', 
         resource_class_args = [db, 
                                config_vars['service_base'],
                                config_vars.getint('shorten_len'), 
                                config_vars.getint('max_len')])
    app.run(debug=False, 
            host=server_vars['host'], 
            port=server_vars.getint('port'))

