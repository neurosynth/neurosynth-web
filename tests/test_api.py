''' Test the v2 swagger API. '''
from nsweb.initializers import settings
import json
import requests
import re

root_url = settings.TEST_URL
api_url = root_url + '/api/'


def get_json(url):
    r = requests.get(url)
    return r.json()['data']


def _test_image_file_retrieval(url):
    r = requests.get(url)
    assert 'octet-stream' in r.headers['content-type']
    cd = r.headers['content-disposition']
    assert re.search('attachment.*nii.gz', cd)


def test_images_api():

    url = api_url + '/images'

    # Test basic object retrieval
    first7 = get_json(url + '?limit=7')
    assert len(first7) == 7
    img = first7[0]
    for key in ['analysis', 'description', 'file', 'id', 'label', 'stat', 'type']:
            assert hasattr(img, key)
    assert float(img['id'])
    assert float(img['analysis'])


    # Test pagination
    next7 = get_json(url + '?limit=7&page=2')
    first14 = get_json(url + '?limit=14')
    assert next7[0] == first14[7]

    # Test search
    lang_imgs = get_json(url + '?limit=100&search=language&type=term')
    labels = [l['label'] for l in lang_imgs]
    assert len(lang_imgs) >= 2
    assert "language: association test" in labels
    assert "language: uniformity test" in labels

    # Test file retrieval
    url = root_url + lang_imgs[-1]['file']
    _test_image_file_retrieval(url)


def test_locations_api():

    url = api_url + '/locations'
    region = get_json(url + '?x=0&y=14&z=42&r=4')
    assert len(region['images']) == 2
    assert len(region['studies']) > 50  # Some reasonable number
    assert float(region['images'][0])
    assert float(region['studies'][10])
    assert region['x'] == 0 and region['z'] == 42

    # Make sure the radius parameter is working
    region2 = get_json(url + '?x=0&y=14&z=42&r=10')
    assert len(region2['studies']) > len(region['studies'])

    # Test that image retrieves correctly
    img = region['images'][0]
    _test_image_file_retrieval(root_url + '/images/%s' % img)


def test_decode_api():

    url = api_url + '/decode'

    # Test NeuroVault decoding
    dec = get_json(url + '?neurovault=4933')
    assert dec['url'].startswith('http://neurovault.org')
    assert len(dec['values']) > 100
    assert 'reward' in dec['values']
    assert float(dec['values']['reward'])
    assert float(dec['id'])
    assert float(dec['neurovault_id'])

