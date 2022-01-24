import abc
import json
from typing import Tuple, Any, Union, Optional

from requests import Response


class BodySerializer(abc.ABC):
    @abc.abstractmethod
    def serialize(self, body: Any) -> Tuple[str, Union[str, bytes]]:
        """
        Serialize a given body object, and include the content-type header
        :param body:
        :return: [content-type, body]
        """


class TypedBodySerializer(BodySerializer, abc.ABC):
    """
    Implementation that returns the pre-configured content-type, but requires subclass to handle the actual body
    serialization
    """

    def __init__(self, content_type: str) -> None:
        self.content_type: str = content_type

    def serialize(self, body: Any) -> Tuple[str, Union[str, bytes]]:
        return self.content_type, self.typed_serialize(body)

    @abc.abstractmethod
    def typed_serialize(self, body: Any) -> Union[str, bytes]:
        """
        Serialize the given body
        """


class JsonBodySerializer(TypedBodySerializer):
    """
    Serialize body using json.dumps function
    """

    def __init__(self, content_type: Optional[str] = None) -> None:
        super().__init__(content_type=content_type or 'application/json')

    def typed_serialize(self, body: Any) -> Union[str, bytes]:
        return json.dumps(body)


class BodyDeserializer(abc.ABC):
    def deserialize(self, response: Response) -> Any:
        """
        Deserialize a response
        """
