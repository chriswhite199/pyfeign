from typing import Optional

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
