import os
import validators

from flask import Flask, redirect
from flask_api import status
from flask_restful import reqparse, Resource, Api
from functools import partial, wraps
from sqlalchemy import create_engine

from shortening.datastore import Base, Url, DatabaseDatastore
from shortening.shorten_string import shorten_url, HashError


class DatabaseConnect(DatabaseDatastore):
    """ Handles setting up the SQLAlchemy engine.
    """
    tmp_path = '/tmp/test.db'
    
    def __init__(self, connect_string = None, tmp_db_path = None, debug = False):

        self.connect_string = connect_string
        self.debug = debug
        self.engine = None
             
        
    def __enter__(self):
        """ initialise the engine, set up the schema if using a local
        database. """
        
        int_con_str = self.connect_string
        if not self.connect_string:
            # test database
            int_con_str = 'sqlite:///' + self.tmp_path
            
        self.engine = create_engine(int_con_str, echo = self.debug)
                
        if not self.connect_string:
            # building the schema for the test database
            Base.metadata.create_all(self.engine)
            
        super().__enter__()
        
        return self


    def __exit__(self, *args):
        """" close down the engine, remove the tempory database if one
        was used """
    
        super().__exit__(*args)
        self.engine.dispose()
        
        if not self.connect_string:
            # cleaning up the test db
            os.remove(self.tmp_path)


class ShortenUrl(Resource):
    """ A POST request that returns the shortened url from a full url."""

    def __init__(self, db, service_base, shorten_len, max_len):
        # parameters for shortening
        self.datastore = db
        self.shorten_len = shorten_len
        self.max_len = max_len
        
        # the url of the redirection service
        self.service_base = service_base
        
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('url')
        

    def post(self):
        """Returns the shortened url from a full url.
        
        If a url is not present or the url is invalid, it returns an error
        message and a bad request status.
        
        If the hashing fails, it returns an appropriate error."""
        full_url = self.parser.parse_args()['url']
        if not full_url:
            message = ("Please provide a url to be shortened, in the field "
                       "'url'")
            return message, status.HTTP_400_BAD_REQUEST

        if not validators.url(full_url):
            message = ("Invalid url provided. Requires scheme ('http://', "
                       "'https://', etc) at the start and a '.<something>' "
                       "too")
            return message, status.HTTP_400_BAD_REQUEST

        try:
            shortened_url = shorten_url(full_url, 
                                        self.shorten_len, self.max_len, self.datastore)
            return { 'shortened_url': self.service_base + shortened_url }
        except HashError:
            message = "Unable to shorten url."
            return message, status.HTTP_500_INTERNAL_SERVER_ERROR

