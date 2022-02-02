# PyFeign - Declarative REST Client

Python implementation of Feign.

## Installation

```bash
pip install pyfeign
# or
poetry install pyfeign
```

## Usage

Decorate function with appropriate `pyfeign.$method` decorator:

```python
@pyfeign.get(url='http://localhost/{id}')
def get_by_id(id: str = Path()) -> Dict[str, Any]:
    """
    Get by ID
    """


obj_dict = get_by_id('id123')
```

### Parameters

* Path - Argument should be used as a path template variable. Reserved variable names can be used using the `name`
  parameter:

    ```python
    @pyfeign.get(url='http://localhost/{id}')
    def get_by_id(id_val: str = Path(name='id')) -> Dict[str, Any]:
        """
        Get by ID
        """
    ```

* Query - Argument should be used as a query parameter, and can be optionally set with a default value if not provided

    ```python
    @pyfeign.get(url='http://localhost/{id}')
    def get_by_id(id_val: str = Path, 
                  summary: bool = Query(default=False, name='summary_details')) -> Dict[str, Any]:
        """
        Get by ID
  
        get_byt_id('id1', False) == http://localhost/id1?summary_details=False
        """
    ```

* Header - Argument will be used as an HTTP Header

* Cookie - Argument will be used as an HTTP Cookie

* Body - Argument will be sent as the request body (JSON serialized)

### Classes

```python
@pyfeign.Pyfeign(config=Config(base_url='https://postman-echo.com'))
class PostmanEcho:
    @pyfeign.get('/get')
    def get(self, foo1: str = Query(), foo2: str = Query(default='bar2')) -> Dict[str, Any]:
        pass
```

### Responses

If the response function / method is typed with `Dict` or `List`, then the response json will be parsed and returned.

If return type is `str` then the response text will be returned

For either of these responses, the return code is asserted via `Response.raise_for_status()`, and so an HTTPError will
be raised accordingly

Otherwise the full `requests.Response` object is returned.