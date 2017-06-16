import validators

from flask import Flask, redirect
from flask_api import status
from flask_restful import reqparse, Resource, Api
from functools import partial, wraps
from sqlalchemy import create_engine

from shortening.datastore import Base, Url, DatabaseDatastore
from shortening.shorten_string import shorten_url

shorten_len = 12
max_len = 20

# creating a mock database for example purposes

class DatabaseConnect(DatabaseDatastore):
    def __init__(self, connect_string = None, debug = False):

        self.connect_string = connect_string
        self.debug = debug   
        self.engine = None
             
        
    def __enter__(self):
        
        int_con_str = self.connect_string
        if not self.connect_string:
            int_con_str = 'sqlite:////tmp/test.db'
            
        self.engine = create_engine(int_con_str, echo = self.debug)
                
        if not self.connect_string:
            Base.metadata.create_all(self.engine)
            
        super().__enter__()
        
        return self


    def __exit__(self, *args):
    
        super().__exit__(*args)
        self.engine.dispose()


class ShortenUrl(Resource):

    def __init__(self, db, service_base, shorten_len, max_len):
        self.datastore = db
        self.service_base = service_base
        self.shorten_len = shorten_len
        self.max_len = max_len
        
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('url')
        

    def post(self):
        full_url = self.parser.parse_args()['url']
        if not full_url:
            message = ("Please provide a url to be shortened, in the field "
                       "'url'")
            return message, status.HTTP_400_BAD_REQUEST
        if validators.url(full_url):
            shortened_url = shorten_url(full_url, 
                                    self.shorten_len, self.max_len, self.datastore)
            return { 'shortened_url': self.service_base + shortened_url }
        else:
            message = ("Invalid url provided. Requires scheme ('http://', "
                       "'https://', etc) at the start and a '.<something>' "
                       "too")
            return message, status.HTTP_400_BAD_REQUEST
