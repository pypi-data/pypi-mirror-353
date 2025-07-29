""" Contains some shared types for properties """

from collections.abc import MutableMapping
from http import HTTPStatus
from typing import BinaryIO, Generic, Literal, Optional, TypeVar

from attrs import define
from httpx import HTTPError, codes


class Unset:
    def __bool__(self) -> Literal[False]:
        return False


UNSET: Unset = Unset()

FileJsonType = tuple[Optional[str], BinaryIO, Optional[str]]


@define
class File:
    """Contains information for file uploads"""

    payload: BinaryIO
    file_name: Optional[str] = None
    mime_type: Optional[str] = None

    def to_tuple(self) -> FileJsonType:
        """Return a tuple representation that httpx will accept for multipart/form-data"""
        return self.file_name, self.payload, self.mime_type


T = TypeVar("T")


@define
class Response(Generic[T]):
    """A response from an endpoint"""

    status_code: HTTPStatus
    content: bytes
    headers: MutableMapping[str, str]
    parsed: Optional[T]

    @property
    def is_informational(self) -> bool:
        """
        A property which is `True` for 1xx status codes, `False` otherwise.
        """
        return codes.is_informational(int(self.status_code))

    @property
    def is_success(self) -> bool:
        """
        A property which is `True` for 2xx status codes, `False` otherwise.
        """
        return codes.is_success(int(self.status_code))

    @property
    def is_redirect(self) -> bool:
        """
        A property which is `True` for 3xx status codes, `False` otherwise.

        Note that not all responses with a 3xx status code indicate a URL redirect.

        Use `response.has_redirect_location` to determine responses with a properly
        formed URL redirection.
        """
        return codes.is_redirect(int(self.status_code))

    @property
    def is_client_error(self) -> bool:
        """
        A property which is `True` for 4xx status codes, `False` otherwise.
        """
        return codes.is_client_error(int(self.status_code))

    @property
    def is_server_error(self) -> bool:
        """
        A property which is `True` for 5xx status codes, `False` otherwise.
        """
        return codes.is_server_error(int(self.status_code))

    @property
    def is_error(self) -> bool:
        """
        A property which is `True` for 4xx and 5xx status codes, `False` otherwise.
        """
        return codes.is_error(int(self.status_code))

    @property
    def has_redirect_location(self) -> bool:
        """
        Returns True for 3xx responses with a properly formed URL redirection,
        `False` otherwise.
        """
        return (
            self.status_code
            in (
                # 301 (Cacheable redirect. Method may change to GET.)
                codes.MOVED_PERMANENTLY,
                # 302 (Uncacheable redirect. Method may change to GET.)
                codes.FOUND,
                # 303 (Client should make a GET or HEAD request.)
                codes.SEE_OTHER,
                # 307 (Equiv. 302, but retain method)
                codes.TEMPORARY_REDIRECT,
                # 308 (Equiv. 301, but retain method)
                codes.PERMANENT_REDIRECT,
            )
            and "Location" in self.headers
        )

    def raise_for_status(self):
        """Raises :class:`HTTPError`, if one occurred."""

        http_error_msg = ""
        if isinstance(self.content, bytes):
            # We attempt to decode utf-8 first because some servers
            # choose to localize their reason strings. If the string
            # isn't utf-8, we fall back to iso-8859-1 for all other
            # encodings. (See PR #3538)
            try:
                reason = self.content.decode("utf-8")
            except UnicodeDecodeError:
                reason = self.content.decode("iso-8859-1")
        else:
            reason = self.content

        if 400 <= int(self.status_code) < 500:
            http_error_msg = "%s Client Error: %s" % (self.status_code, reason)

        elif 500 <= int(self.status_code) < 600:
            http_error_msg = "%s Server Error: %s" % (self.status_code, reason)

        if http_error_msg:
            raise HTTPError(http_error_msg)


__all__ = ["UNSET", "File", "FileJsonType", "Response", "Unset"]
