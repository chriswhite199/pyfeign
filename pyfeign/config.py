from typing import Optional, Any

from requests import Session

from pyfeign.serializer import BodySerializer, JsonBodySerializer


class Config:
    def __init__(self,
                 base_url: Optional[str] = None,
                 session: Optional[Session] = None,
                 body_serializer: Optional[BodySerializer] = None) -> None:
        self.base_url = base_url
        self.session = session
        self.body_serializer = body_serializer or JsonBodySerializer()
        self.default_config: Optional['Config'] = None

    def __getattr__(self, item) -> Any:
        val = object.__getattribute__(self, item)
        if val is None and self.default_config is not None:
            return getattr(self.default_config, item)
        else:
            return None
