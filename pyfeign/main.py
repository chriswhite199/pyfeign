import copy
import inspect
import json
import logging
import re
from functools import wraps
from typing import Callable, TypeVar, Any, cast, Optional, Dict, Literal, List

import requests
from requests import Response
from requests.utils import CaseInsensitiveDict

from pyfeign.config import Config

F = TypeVar('F', bound=Callable[..., Any])

logger = logging.getLogger(__name__)

ArgType = Literal['query', 'header', 'cookie', 'body', 'path']


class FeignArg:
    def __init__(self,
                 arg_type: ArgType,
                 default: Any = None,
                 name: Optional[str] = None,
                 include_none: Optional[bool] = False) -> None:
        self.arg_type = arg_type
        self.name = name
        self.default = default
        self.include_none = include_none


def Body(default: Any = None,
         name: Optional[str] = None,
         include_none: Optional[bool] = None) -> Any:
    return FeignArg('body', default=default, name=name, include_none=include_none)


def Query(default: Any = None,
          name: Optional[str] = None,
          include_none: Optional[bool] = None) -> Any:
    """
    Parameter that is used in as a query parameter to the request url
    """
    return FeignArg('query', default=default, name=name, include_none=include_none)


def Header(default: Any = None,
           name: Optional[str] = None,
           include_none: Optional[bool] = None) -> Any:
    """
    Parameter that is used in request header
    """
    return FeignArg('header', default=default, name=name, include_none=include_none)


def Cookie(default: Any = None,
           name: Optional[str] = None,
           include_none: Optional[bool] = None) -> Any:
    """
    Parameter that is used as a request Cookie
    """
    return FeignArg('cookie', default=default, name=name, include_none=include_none)


def Path(name: Optional[str] = None) -> Any:
    """
    Parameter that is used in a url path template
    """
    return FeignArg('path', name=name)


def method(http_method: str,
           url: str,
           *,
           config: Optional[Config] = None,
           default_headers: Optional[Dict[str, Any]] = None,
           default_params: Optional[Dict[str, Any]] = None,
           default_cookies: Optional[Dict[str, Any]] = None):
    default_headers: CaseInsensitiveDict = CaseInsensitiveDict(default_headers or {})
    default_params = default_params or {}
    default_cookies = default_cookies or {}

    def decorator(func: F) -> F:
        arg_spec = inspect.getfullargspec(func)
        return_type = arg_spec.annotations and arg_spec.annotations.get('return', Response)
        defaults = arg_spec.defaults if arg_spec.defaults else tuple()
        default_len = len(defaults)

        def validate_defaults():
            for idx, default in enumerate(defaults):
                if default is None:
                    raise SyntaxError(f'{func.__name__} - arg {arg_spec.args[idx]} has no default value')

        def merge_args_into_kwargs(*args, kwargs: Dict[str, Any]):
            if args:
                for idx, arg in enumerate(args):
                    arg_name = arg_spec.args[idx]
                    if idx >= len(args) - default_len:
                        default = defaults[idx - default_len]
                    else:
                        default = None
                    name_override = default.name if default else None
                    arg = default.default if default and arg is None else arg
                    kwargs[name_override or arg_name] = arg

        def build_typed_dict(arg_type: ArgType, kwargs: Dict[str, Any]):
            typed_dict = {}
            for idx, default in enumerate(defaults):
                if default.arg_type == arg_type:
                    name = default.name or arg_spec.args[len(arg_spec.args) - default_len + idx]
                    val = kwargs.get(name, default.default if default else None)
                    if val is not None or default.include_none:
                        typed_dict[name] = val

            return typed_dict

        def get_body(kwargs: Dict[str, Any]):
            for idx, default in enumerate(defaults):
                if default.arg_type == 'body':
                    name = arg_spec.args[len(arg_spec.args) - default_len + idx]
                    return kwargs.get(name, None)

                return None

        @wraps(decorator)
        def wrapper(*args, **kwargs):
            merge_args_into_kwargs(*args, kwargs=kwargs)

            expanded_url = url.format(*args, **kwargs)
            if not re.match(r'https?://', expanded_url):
                if config and config.base_url:
                    expanded_url = config.base_url + expanded_url
                else:
                    raise ValueError(f'Baseless URL: {expanded_url}')

            cookies = copy.deepcopy(default_cookies)
            cookies.update(build_typed_dict('cookie', kwargs))

            headers = copy.deepcopy(default_headers)
            headers.update(build_typed_dict('header', kwargs))

            params = copy.deepcopy(default_params)
            params.update(build_typed_dict('query', kwargs))

            body = get_body(kwargs)
            if body and config and config.body_serializer:
                content_type, body = config.body_serializer.serialize(body)
                headers.update({'Content-Type': content_type})
            elif isinstance(body, Dict) or isinstance(body, List):
                body = json.dumps(body)

            request_args = dict(method=http_method,
                                url=expanded_url,
                                params=params or None,
                                headers=headers or None,
                                cookies=cookies or None,
                                data=body)

            if config and config.session:
                resp = config.session.request(**request_args)
            else:
                resp = requests.request(**request_args)

            resp.raise_for_status()
            if return_type in [Dict, List]:
                return resp.json()
            elif return_type == str:
                return resp.text
            else:
                return resp

        validate_defaults()
        return cast(F, wrapper)

    return decorator


def get(url: str, *,
        config: Optional[Config] = None,
        default_headers: Optional[Dict[str, Any]] = None,
        default_params: Optional[Dict[str, Any]] = None,
        default_cookies: Optional[Dict[str, Any]] = None):
    return method('GET', **locals())


def post(url: str, *,
         config: Optional[Config] = None,
         default_headers: Optional[Dict[str, Any]] = None,
         default_params: Optional[Dict[str, Any]] = None,
         default_cookies: Optional[Dict[str, Any]] = None):
    return method('POST', **locals())


def put(url: str, *,
        config: Optional[Config] = None,
        default_headers: Optional[Dict[str, Any]] = None,
        default_params: Optional[Dict[str, Any]] = None,
        default_cookies: Optional[Dict[str, Any]] = None):
    return method('PUT', **locals())


def head(url: str, *,
         config: Optional[Config] = None,
         default_headers: Optional[Dict[str, Any]] = None,
         default_params: Optional[Dict[str, Any]] = None,
         default_cookies: Optional[Dict[str, Any]] = None):
    return method('HEAD', **locals())


def delete(url: str, *,
           config: Optional[Config] = None,
           default_headers: Optional[Dict[str, Any]] = None,
           default_params: Optional[Dict[str, Any]] = None,
           default_cookies: Optional[Dict[str, Any]] = None):
    return method('DELETE', **locals())


def patch(url: str, *,
          config: Optional[Config] = None,
          default_headers: Optional[Dict[str, Any]] = None,
          default_params: Optional[Dict[str, Any]] = None,
          default_cookies: Optional[Dict[str, Any]] = None):
    return method('PATCH', **locals())


def options(url: str, *,
            config: Optional[Config] = None,
            default_headers: Optional[Dict[str, Any]] = None,
            default_params: Optional[Dict[str, Any]] = None,
            default_cookies: Optional[Dict[str, Any]] = None):
    return method('OPTIONS', **locals())


def trace(url: str, *,
          config: Optional[Config] = None,
          default_headers: Optional[Dict[str, Any]] = None,
          default_params: Optional[Dict[str, Any]] = None,
          default_cookies: Optional[Dict[str, Any]] = None):
    return method('TRACE', **locals())