
import unittest
from unittest.mock import patch

import shortening
from shortening.datastore import DuplicateUrlError
from shortening.shorten_string import shorten_url_safe, shorten_url, \
    HashError
from shortening.tests.test_datastore import TestCaseWithDb

class TestShortenURLSafe(unittest.TestCase):

    def test_length(self):
        """testing the length is correct"""
    
        test_url = "www.google.com"
        shorten_len = 5
        
        string_out = shorten_url_safe(test_url, shorten_len)
        
        self.assertEqual(len(string_out), shorten_len)
        
    
    def test_url_safe(self):
        """testing it's URL safe."""
        
        test_url = "www.google.com"
        safe_characters = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")
        
        string_out = shorten_url_safe(test_url, 22)
        for a_chr in string_out:
            self.assertIn(a_chr, safe_characters)


def return_len_str(full_url, shorten_len):
    return 'a'*shorten_len


def set_simulate_race_condition(*args):
    # in the case of a race condition, set will complain that
    # it has been populated
    raise DuplicateUrlError("")

SHORTENED = "clash"
not_run = True

def get_simulate_race_condition(*args):
    global not_run
    if not_run:
        # The db is empty at first, so will yield nothing.
        not_run = False
        return
    # db has been populated, so returns the hash value
    not_run = True
    return SHORTENED
    


class TestShortenUrl(TestCaseWithDb):

    def test_runs(self):

        full_url = "foo"
        
        shortened_url = shorten_url(full_url, 12, 20, self.mock_db)

        self.assertIsInstance(shortened_url, str)


    def test_returns_existing_value_twice(self):
    
        full_url = "foo"
        
        shortened_url0 = shorten_url(full_url, 12, 20, self.mock_db)
        shortened_url1 = shorten_url(full_url, 12, 20, self.mock_db)
        
        self.assertEqual(shortened_url0, shortened_url1)


    # overriding the hashing function to ensure a clash
    @patch('shortening.shorten_string.shorten_url_safe', side_effect=return_len_str)
    def test_hash_clash_returns_longer_string(self, _):

        full_url0 = "foo"
        full_url1 = "bar"
        
        short_len = 12
        shortened_url0 = shorten_url(full_url0, short_len, 20, self.mock_db)
        shortened_url1 = shorten_url(full_url1, short_len, 20, self.mock_db)
        
        self.assertEqual(shortened_url0, shortened_url1[:short_len])
        self.assertEqual(len(shortened_url1), short_len + 1)
   
    
    # overriding the hashing function to ensure a clash
    @patch('shortening.shorten_string.shorten_url_safe', side_effect=return_len_str)    
    def test_raises_if_cant_find_shortened_url(self, _):
        
        full_url0 = "foo"
        full_url1 = "bar"
        
        short_len = 12
        max_len = 12
        shorten_url(full_url0, short_len, max_len, self.mock_db)
        
        self.assertRaises(HashError, 
                          shorten_url, 
                          full_url1, short_len, max_len, self.mock_db)

    
    def test_race_condition(self):
        
        self.mock_db.shortened_url_from_full_url = get_simulate_race_condition
        self.mock_db.set_url = set_simulate_race_condition
        
        full_url = "foo"
        
        shortened_url = shorten_url(full_url, 12, 20, self.mock_db)
        
        self.assertEqual(shortened_url, SHORTENED)

