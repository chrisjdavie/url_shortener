
from flask import Flask
from flask_restful import reqparse, Resource, Api
from sqlalchemy import create_engine

from shortening.datastore import Base, Url, DatabaseDatastore
from shortening.shorten_string import shorten_url

# TODO
# - shorten_url endpoint
# - shortened to full endpoint
# - main

shorten_len = 12
max_len = 20

# creating a mock database for example purposes

class DatabaseConnect(DatabaseDatastore):
    def __init__(connect_string = None, debug = False):

        self.connect_string = connect_string
        self.debug = debug   
        self.engine = None
             
        
    def __enter__(self):
        
        int_con_str = self.connect_string
        if not connect_string:
            int_con_str = 'sqlite:////tmp/test.db'
            
        self.engine = create_engine(int_con_str, echo = self.debug)
                
        if not connect_string:
            Base.metadata.create_all(engine)
            Base.query = datastore.session.query_property()
            
        self.super().__enter__()
        
        return self


    def __exit__(self):
    
        self.super().__exit__()
        self.engine.dispose()


app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('url')

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class ShortenUrl(Resource):

    def __init__(self, db):
        self.datastore = db

    def post(self):
        args = parser.parse_args()
        #shortened_url = shorten_url(
        #                    args['url'], shorten_len, max_len, self.datastore)
        return dir(self.datastore.engine.url)

if __name__ == '__main__':

    with DatabaseConnect() as db:
        api.add_resource(HelloWorld, '/', )
        api.add_resource(ShortenUrl, '/shorten_url', 
                         resource_class_args = [db])
        app.run(debug=True, host='0.0.0.0')

