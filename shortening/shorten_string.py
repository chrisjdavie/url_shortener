import base64
import hashlib

from shortening.datastore import DuplicateUrlError


class HashError(Exception):
    pass


def shorten_url_safe(full_url, shorten_len):
    
    url_hash = hashlib.md5(full_url.encode('utf-8')).digest()
    shorten_url = base64.urlsafe_b64encode(url_hash).decode('utf-8')
    shorten_url = str(shorten_url)[:shorten_len].replace('=','_')
    
    return shorten_url


def shorten_url(full_url, shorten_len, max_len, datastore):
    # look up full url in db. If present, return shortened url
    short_url = datastore.shortened_url_from_full_url(full_url)
    if short_url:
        return short_url
    
    for url_len in range(shorten_len, max_len + 1):
        short_url = shorten_url_safe(full_url, url_len)
        
        try:
            datastore.set_url(short_url, full_url)
            break
        except DuplicateUrlError:
            # testing race condition
            short_url = datastore.shortened_url_from_full_url(full_url)
            if short_url:
                break
            # otherwise, it was a hash collision, 
            # continue generating a new hash
    else:
        raise HashError("No unshortened URL can be produced that isnt already "
           "used. It may be that the length of the maximum cache {} is too "
           "short.".format(max_len))

    return short_url

