
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine

from shortening.datastore import DatabaseDatastore, Url, \
    DuplicateUrlError, Base


class TestCaseWithDb(unittest.TestCase):

    def setUp(self):
        
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(self.engine)
        self.mock_db = DatabaseDatastore(self.engine)
        self.mock_db.__enter__()
        
    
    def tearDown(self):
        
        self.mock_db.__exit__(None, None, None)
        self.engine.dispose()
    
    
class TestDatabaseDatastore(TestCaseWithDb):

    def test_init_enter(self):
    
        self.assertEqual(self.mock_db.session.bind, self.engine)
        
        
    def test_cant_set_duplicate_shortened_url(self):
    
        shortened_url = "bird"
        shortened_url1 = "cat"
        full_url = "feather"

        self.mock_db.set_url(shortened_url, full_url)
        self.assertRaises(DuplicateUrlError,
                          self.mock_db.set_url,
                          shortened_url1, 
                          full_url)


    def test_cant_set_duplicate_full_url(self):

        shortened_url = "bird"
        full_url = "feather"
        full_url1 = "arm"

        self.mock_db.set_url(shortened_url, full_url)
        self.assertRaises(DuplicateUrlError,
                          self.mock_db.set_url,
                          shortened_url,
                          full_url1)


    def test_cant_set_complete_duplicate(self):

        shortened_url = "bird"
        full_url = "feather"

        self.mock_db.set_url(shortened_url, full_url)
        self.assertRaises(DuplicateUrlError,
                          self.mock_db.set_url,
                          shortened_url,
                          full_url)


    def test_set_after_exception(self):
    
        shortened_url = "bird"
        full_url = "feather"
        shortened_url0 = "coke"
        full_url0 = "cola" 
        
        self.mock_db.set_url(shortened_url, full_url)
        try:
            self.mock_db.set_url(shortened_url, full_url)
        except DuplicateUrlError:
            pass
        # this should run without exception
        self.mock_db.set_url(shortened_url0, full_url0)


    def test_full_url_from_shortened_url(self):

        shortened_url = "bird"
        full_url = "feather"
        expected = Url(shortened_url = shortened_url,
                       full_url = full_url)

        self.mock_db.set_url(shortened_url, full_url)
        actual = self.mock_db.full_url_from_shortened_url(shortened_url)

        self.assertEqual(full_url, actual)


    def test_full_url_from_shortened_url_no_url(self):

        false_url = "bird"
        self.assertIsNone(self.mock_db.full_url_from_shortened_url(false_url))


    def test_shortened_url_from_full_url(self):

        shortened_url = "bird"
        full_url = "feather"

        self.mock_db.set_url(shortened_url, full_url)
        actual = self.mock_db.shortened_url_from_full_url(full_url)

        self.assertEqual(shortened_url, actual)


    def test_shortened_url_from_full_url_no_url(self):

        false_url = "bird"
        self.assertIsNone(self.mock_db.shortened_url_from_full_url(false_url))

