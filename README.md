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
*
* Header
* Cookie
* Body