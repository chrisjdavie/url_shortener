

from sqlalchemy import Column, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import FlushError

Base = declarative_base()

class Url(Base):
    __tablename__ = "url"
    
    shortened_url = Column(String(20), primary_key=True)
    full_url = Column(String(2000), unique=True)

    def __repr__(self):
        return "<Url(shortened_url={}, full_url={})".format(
                    self.shortened_url, self.full_url)


class DuplicateUrlError(ValueError):
    pass

class MissingUrlError(ValueError):
    pass

class DatabaseDatastore:

    def __init__(self, engine):

        self.engine = engine


    def __enter__(self):

        Session = sessionmaker(autocommit=False, autoflush=False, bind = self.engine)
        self.session = scoped_session(Session)
        return self


    def __exit__(self, *args):

        self.session.close()


    def shortened_url_from_full_url(self, full_url):
        a_url = self.session.query(Url).filter_by(full_url=full_url).first()
        if a_url:
            return a_url.shortened_url
        return



    def full_url_from_shortened_url(self, shortened_url):
        a_url = self.session.query(Url).filter_by(shortened_url=shortened_url
                                                        ).first()
        if a_url:
            return a_url.full_url
        return
        
        
    def set_url(self, shortened_url, full_url):
        """ Set a new shortened_url, full_url pair in the db

        Raises:
            - DuplicateFullUrlError if full_url is not unique or shortened_url
                is not unique
        """
        
        new_url = Url(shortened_url = shortened_url, 
                      full_url = full_url)

        self.session.add(new_url)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise DuplicateUrlError("Either full_url {} or shortened_url {} is " 
                "already in the datastore".format(full_url, shortened_url))

