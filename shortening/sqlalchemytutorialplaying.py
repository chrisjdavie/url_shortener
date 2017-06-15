from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///:memory:', echo=False)

Base = declarative_base()

from sqlalchemy import Column, String

class ShortenedUrl(Base):
    __tablename__ = "shortened_url"
    
    shortened_url = Column(String(20), primary_key=True)
    full_url = Column(String(2000))

    def __repr__(self):
        return "<ShortenedUrl(shortened_url={}, full_url={})".format(
                    self.shortened_url, self.full_url)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

demo_url = ShortenedUrl(shortened_url = "foo", full_url = "bar")
print("IN", demo_url)

session.add(demo_url)
a_url = session.query(ShortenedUrl).filter_by(shortened_url="foo").first()
print("OUT", a_url)
print(demo_url is a_url)

session.add_all([ShortenedUrl(shortened_url = "eggs", full_url = "bacon"),
                 ShortenedUrl(shortened_url = "red",  full_url = "blue"),
                 ShortenedUrl(shortened_url = "tree", full_url = "trunk")])

demo_url.full_url = "barbar"

print(session.dirty)
print(session.new)

session.commit()

demo_url.shortened_url = "foot"
bad_url = ShortenedUrl(shortened_url = "a", full_url = "b")
session.add(bad_url)
print()
print(session.query(ShortenedUrl).filter(ShortenedUrl.shortened_url.in_(["foot", "a"])).all())
print(demo_url.shortened_url)
print()

session.rollback()

print()
print(session.query(ShortenedUrl).filter(ShortenedUrl.shortened_url.in_(["foot", "a"])).all())
print(demo_url.shortened_url)
print()

dupe_url = ShortenedUrl(shortened_url = "foo", full_url = "tim")
session.add(dupe_url)
session.commit()

