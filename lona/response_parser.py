import logging

from lona.html.abstract_node import AbstractNode
from lona._json import dumps

logger = logging.getLogger('lona.response_parser')


class ResponseParser:
    def __init__(self, server):
        self.server = server

    def render_response_dict(self, raw_response_dict, view_name):
        response_dict = {
            'status': 200,
            'content_type': 'text/html',
            'text': '',
            'file': '',
            'redirect': '',
            'http_redirect': '',
        }

        key_words = {
            'text',
            'redirect',
            'http_redirect',
            'template',
            'template_string',
            'file',
            'json',
        }

        # Node response
        if isinstance(raw_response_dict, AbstractNode):
            response_dict['text'] = str(raw_response_dict)

            return response_dict

        # string response
        if isinstance(raw_response_dict, str):
            logger.debug("'%s' is a string based view", view_name)

            response_dict['text'] = raw_response_dict

            return response_dict

        # response dict
        elif isinstance(raw_response_dict, dict):

            # check keys
            if len(set(raw_response_dict) & key_words) != 1:
                raise RuntimeError(
                    'response dicts have to contain exactly one keyword of:{}'.format(  # NOQA
                        ', '.join(key_words),
                    )
                )

            # find keys
            for key in response_dict.keys():
                if key in raw_response_dict:
                    value = raw_response_dict[key]
                    response_dict[key] = value

                    logger.debug(
                        "'%s' sets '%s' to %s", view_name, key, repr(value))

        # redirects
        if 'redirect' in raw_response_dict:
            response_dict['redirect'] = raw_response_dict['redirect']

        # http redirect
        elif 'http_redirect' in raw_response_dict:
            response_dict['http_redirect'] = raw_response_dict['http_redirect']

        # template response
        elif('template' in raw_response_dict or
             'template_string' in raw_response_dict):

            logger.debug("'%s' is a template view", view_name)

            template_context = raw_response_dict

            if 'context' in template_context:
                template_context = template_context['context']

            # template file
            if 'template' in raw_response_dict:
                response_dict['text'] = \
                    self.server.templating_engine.render_template(
                        raw_response_dict['template'],
                        template_context,
                    )

            # template string
            else:
                response_dict['text'] = \
                    self.server.templating_engine.render_string(
                        raw_response_dict['template_string'],
                        template_context,
                    )

        # json response
        elif 'json' in raw_response_dict:
            logger.debug("'%s' is a json view", view_name)

            response_dict['text'] = dumps(raw_response_dict['json'])
            response_dict['content_type'] = 'application/json'

        return response_dict
