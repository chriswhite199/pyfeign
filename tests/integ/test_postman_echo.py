from typing import Dict, Any

import pytest

import pyfeign
from pyfeign import Config, Query

"""
https://www.postman.com/postman/workspace/published-postman-templates/documentation/631643-f695cab7-6878-eb55-7943-ad88e1ccfd65
"""


@pyfeign.Pyfeign(config=Config(base_url='https://postman-echo.com'))
class PostmanEcho:
    @pyfeign.get('/get')
    def get(self, foo1: str = Query(), foo2: str = Query(default='bar2')) -> Dict[str, Any]:
        pass


@pytest.fixture
def client() -> PostmanEcho:
    return PostmanEcho()


@pytest.mark.integration
def test_get(client):
    resp_json = client.get(foo1='bar1')
    assert resp_json['args'] == dict(foo1='bar1', foo2='bar2')
    assert resp_json['url'] == 'https://postman-echo.com/get?foo1=bar1&foo2=bar2'
