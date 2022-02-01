from typing import Optional, Any, Dict

import pytest
from requests import Session, HTTPError
from requests_mock import Mocker

import pyfeign

config = pyfeign.Config(base_url='http://localhost', session=Session())


@pyfeign.get('/{id}', config=config)
def get_by_id(id_val: str = pyfeign.Path('id'),
              query1: Optional[str] = pyfeign.Query(),
              query2: Optional[int] = pyfeign.Query(default=99),
              cookie: Optional[str] = pyfeign.Cookie(),
              header: Optional[str] = pyfeign.Header(name='HEADER_NAME', default='HEADER_VALUE')) -> Dict:
    """
    get by ID
    """


@pyfeign.post('http://localhost:8080/', expected_status=201)
def add_new(body: Dict[str, Any] = pyfeign.Body()):
    pass


@pyfeign.put('/{id}', config=config, default_headers=dict(header1='value1'), expected_status=[200, 202])
def update(id: str, body: Dict[str, Any] = pyfeign.Body()):
    pass


@pyfeign.head('/{id}', config=config, default_params=dict(full=False, history=True))
def meta(id: str, full: bool = pyfeign.Query()):
    pass


@pyfeign.options('/{id}', config=config)
def opts(id: str):
    pass


@pyfeign.patch('/{id}', config=config)
def patch(id: str):
    pass


@pyfeign.delete('/{id}', config=config)
def delete(id: str):
    pass


@pyfeign.trace('/{id}', config=config)
def trace(id: str):
    pass


def test_get(requests_mock: Mocker):
    resp_json = dict(field1='abc')
    requests_mock.get('http://localhost/abc?query2=99', complete_qs=True,
                      request_headers=dict(HEADER_NAME='HEADER_VALUE'),
                      json=resp_json)
    assert get_by_id('abc') == resp_json

    requests_mock.get('http://localhost/def?query1=q1&query2=99', status_code=201,
                      complete_qs=True,
                      request_headers=dict(HEADER_NAME='HEADER_VALUE'),
                      json=resp_json)
    assert get_by_id('def', query1='q1') == resp_json

    def matcher(request) -> bool:
        return dict(Cookie='cookie=test-me').items() <= request.headers.items()

    requests_mock.get('http://localhost/ghi?query2=99', complete_qs=True,
                      additional_matcher=matcher,
                      request_headers=dict(HEADER_NAME='HEADER_VALUE'),
                      json=resp_json)
    assert get_by_id('ghi', cookie='test-me') == resp_json


def test_raise_for_status_status(requests_mock: Mocker):
    requests_mock.get('http://localhost/err', status_code=404)
    with pytest.raises(HTTPError):
        get_by_id('err')


def test_post(requests_mock: Mocker):
    requests_mock.post('http://localhost:8080/', additional_matcher=lambda req: req.json() == dict(field1='abc'),
                       status_code=201)
    assert add_new(dict(field1='abc')).status_code == 201


def test_put(requests_mock: Mocker):
    requests_mock.put('http://localhost/id1', additional_matcher=lambda req: req.json() == dict(field1='abc'),
                      request_headers=dict(header1='value1'))
    assert update('id1', dict(field1='abc')).status_code == 200


def test_delete(requests_mock: Mocker):
    requests_mock.delete('http://localhost/id1')
    assert delete('id1').status_code == 200


def test_head(requests_mock: Mocker):
    requests_mock.head('http://localhost/id1?full=False&history=True', complete_qs=True)
    assert meta('id1').status_code == 200

    requests_mock.head('http://localhost/id1?full=True&history=True', complete_qs=True)
    assert meta('id1', full=True).status_code == 200


def test_options(requests_mock: Mocker):
    requests_mock.options('http://localhost/id1')
    assert opts('id1').status_code == 200


def test_patch(requests_mock: Mocker):
    requests_mock.patch('http://localhost/id1')
    assert patch('id1').status_code == 200


def test_trace(requests_mock: Mocker):
    requests_mock.request('TRACE', 'http://localhost/id1')
    assert trace('id1').status_code == 200


@pyfeign.Pyfeign
class TestClass1:
    @pyfeign.get('/{id}', config=config)
    def get_by_id(self, id_val: str = pyfeign.Path('id'),
                  query1: Optional[str] = pyfeign.Query(),
                  query2: Optional[int] = pyfeign.Query(default=99),
                  cookie: Optional[str] = pyfeign.Cookie(),
                  header: Optional[str] = pyfeign.Header(name='HEADER_NAME', default='HEADER_VALUE')) -> Dict:
        """
        get by ID
        """


@pyfeign.Pyfeign(config=config)
class TestClass2:
    @pyfeign.get('/{id}')
    def get_by_id(self, id_val: str = pyfeign.Path('id'),
                  query1: Optional[str] = pyfeign.Query(),
                  query2: Optional[int] = pyfeign.Query(default=99),
                  cookie: Optional[str] = pyfeign.Cookie(),
                  header: Optional[str] = pyfeign.Header(name='HEADER_NAME', default='HEADER_VALUE')) -> Dict:
        """
        get by ID
        """


def test_class(requests_mock: Mocker):
    resp_json = dict(field1='abc')
    requests_mock.get('http://localhost/abc?query2=99', complete_qs=True,
                      request_headers=dict(HEADER_NAME='HEADER_VALUE'),
                      json=resp_json)

    test1: TestClass1 = TestClass1()
    test1.get_by_id('abc')

    test2: TestClass2 = TestClass2()
    test2.get_by_id('abc')
