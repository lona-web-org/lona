from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union, Dict, Any

from lona.html.abstract_node import AbstractNode
from lona.events.input_event import InputEvent


@dataclass
class AbstractResponse:
    @property
    def interactive(self) -> bool:
        raise NotImplementedError()


@dataclass
class Response(AbstractResponse):
    body: Any = None
    status: int | None = None
    content_type: str | None = None
    headers: Dict[str, str] | None = None
    text: str | None = None
    charset: str | None = None

    def __post_init__(self):
        if self.body and self.text:
            raise ValueError('body and text are not allowed together')

    @property
    def interactive(self) -> bool:
        if (self.body or self.status or self.content_type or
                self.headers or self.charset):

            return False

        return True


@dataclass
class HtmlResponse(AbstractResponse):
    html: str | AbstractNode
    status: int | None = None
    content_type: str | None = None
    headers: dict | None = None

    @property
    def interactive(self) -> bool:
        if self.status or self.content_type or self.headers:
            return False

        return True


@dataclass
class TemplateResponse(AbstractResponse):
    name: str
    context: dict = field(default_factory=dict)
    status: int | None = None
    content_type: str | None = None
    headers: dict | None = None

    @property
    def interactive(self) -> bool:
        if self.status or self.content_type or self.headers:
            return False

        return True


@dataclass
class TemplateStringResponse(AbstractResponse):
    string: str
    context: dict = field(default_factory=dict)
    status: int | None = None
    content_type: str | None = None
    headers: dict | None = None

    @property
    def interactive(self) -> bool:
        if self.status or self.content_type or self.headers:
            return False

        return True


@dataclass
class JsonResponse(AbstractResponse):
    data: Any
    status: int | None = None
    content_type: str | None = None
    headers: dict | None = None

    @property
    def interactive(self) -> bool:
        return False


@dataclass
class FileResponse(AbstractResponse):
    path: str
    status: int | None = None
    headers: dict | None = None

    @property
    def interactive(self) -> bool:
        return False


@dataclass
class RedirectResponse(AbstractResponse):
    url: str
    headers: dict | None = None

    @property
    def interactive(self) -> bool:
        if self.headers:
            return False

        return True


@dataclass
class HttpRedirectResponse(AbstractResponse):
    url: str
    headers: dict | None = None

    @property
    def interactive(self) -> bool:
        if self.headers:
            return False

        return True


# response parsing ############################################################
# view return values
def _parse_legacy_view_return_value(
        return_value: dict,
) -> AbstractResponse:

    key_words = {
        'text',
        'body',
        'redirect',
        'http_redirect',
        'template',
        'template_string',
        'file',
        'json',
    }

    # check keys
    if len(set(return_value) & key_words) != 1:
        raise RuntimeError(
            'response dicts have to contain exactly one keyword of: {}'.format(  # NOQA: FS002
                ', '.join(key_words),
            ),
        )

    # redirects
    if 'redirect' in return_value:
        return RedirectResponse(
            url=str(return_value['redirect']),
            headers=return_value.get('headers', None),
        )

    # http redirect
    if 'http_redirect' in return_value:
        return HttpRedirectResponse(
            url=str(return_value['http_redirect']),
            headers=return_value.get('headers', None),
        )

    # json
    if 'json' in return_value:
        return JsonResponse(
            data=return_value['json'],
            status=return_value.get('status', None),
            content_type=return_value.get('content_type', None),
            headers=return_value.get('headers', None),
        )

    # file
    if 'file' in return_value:
        return FileResponse(
            path=return_value['file'],
            status=return_value.get('status', None),
            headers=return_value.get('headers', None),
        )

    context: dict = return_value

    if 'context' in context:
        context = context['context']

    # template
    if 'template' in return_value:
        return TemplateResponse(
            name=str(return_value['template']),
            context=context,
            status=return_value.get('status', None),
            content_type=return_value.get('content_type', None),
            headers=return_value.get('headers', None),
        )

    # template string
    if 'template_string' in return_value:
        return TemplateStringResponse(
            string=str(return_value['template_string']),
            context=context,
            status=return_value.get('status', None),
            content_type=return_value.get('content_type', None),
            headers=return_value.get('headers', None),
        )

    return Response(
        body=return_value.get('body', None),
        status=return_value.get('status', None),
        content_type=return_value.get('content_type', None),
        headers=return_value.get('headers', None),
        text=return_value.get('text', None),
        charset=return_value.get('charset', None),
    )


def parse_view_return_value(
        return_value: AbstractResponse | AbstractNode | str | None | dict,
        interactive: bool,
) -> AbstractResponse | None:

    if return_value is None:
        return return_value

    # legacy view return values
    # TODO: remove in 2.0
    if isinstance(return_value, dict):
        return_value = _parse_legacy_view_return_value(
            return_value=return_value,
        )

    if isinstance(return_value, (str, AbstractNode)):
        return_value = HtmlResponse(html=return_value)

    # check for non-interactive features
    if interactive:

        # some response types can not be used in interactive views
        if isinstance(return_value, (JsonResponse, FileResponse)):
            raise RuntimeError(
                'JSON, binary and file responses and headers are only available in non-interactive mode',
            )

        # some response features can not be used in interactive views
        if (not isinstance(return_value, (RedirectResponse,
                                          HttpRedirectResponse)) and
                not return_value.interactive):

            raise RuntimeError(
                'JSON, binary and file responses and headers are only available in non-interactive mode',
            )

    if isinstance(return_value, AbstractResponse):
        return return_value

    raise RuntimeError(
        f'expected string, Lona Node or Lona response object. Got {type(return_value)}',
    )


# input event handler return values
def _parse_legacy_input_event_handler_return_value(
        return_value: Dict[str, str],
) -> RedirectResponse | HttpRedirectResponse:

    # TODO: remove in 2.0
    supported_keys = ('redirect', 'http_redirect')

    if (len(return_value.keys()) > 1 or
            list(return_value.keys())[0] not in supported_keys):

        raise ValueError(f'response dict has unexpected keys ({repr(list(return_value.keys()))})')

    redirect_type, redirect_target = list(return_value.items())[0]

    if not isinstance(redirect_target, str):
        raise ValueError('redirect target has to be string')

    if redirect_type == 'http_redirect':
        return HttpRedirectResponse(url=redirect_target)

    return RedirectResponse(url=redirect_target)


def parse_input_event_handler_return_value(
        return_value: Union[InputEvent, RedirectResponse, HttpRedirectResponse,
                            None, Dict[str, str]],
) -> InputEvent | RedirectResponse | HttpRedirectResponse | None:

    if return_value is None:
        return return_value

    # legacy input event handler return values
    # TODO: remove in 2.0
    if isinstance(return_value, dict):
        return_value = _parse_legacy_input_event_handler_return_value(
            return_value=return_value,
        )

    if isinstance(return_value, (InputEvent, RedirectResponse,
                                 HttpRedirectResponse)):

        return return_value

    raise RuntimeError(
        f'expected RedirectResponse, HttpRedirectResponse, InputEvent, dict or NoneType. Got {type(return_value)}',
    )
