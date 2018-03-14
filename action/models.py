import json
import logging
import requests

from django.db import models
from django.contrib.postgres.fields import JSONField

from dicttoxml import dicttoxml
from model_utils.models import TimeStampedModel

import action.utils as utils
from zip.models import Zip

logger = logging.getLogger(__name__)


class Action(TimeStampedModel):
    data = JSONField(blank=True, null=True, default=None)
    title = models.CharField(max_length=200, default='Webhook Action')
    zip = models.ForeignKey(Zip, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class ActionWebhook(Action):
    HOOK_GET = 'get'
    HOOK_POST = 'post'
    HOOK_PUT = 'put'
    HOOK_CHOICES = (
        (HOOK_GET, 'Get'),
        (HOOK_POST, 'Post'),
        (HOOK_PUT, 'Put'),
    )
    hook_type = models.CharField(max_length=256, choices=HOOK_CHOICES)
    BASE_SCHEMA = {
        "title": "Webhook",
        "description": "Set up Webhooks by Zipier",
        "type": "object",
        "required": [
            "url"
        ],
        "definitions": {
            "data": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string"
                    },
                    "value": {
                        "type": "string"
                    }
                }
            }
        },
        "properties": {
            "url": {
                "type": "string",
                "title": "URL"
            },
            "payloadType": {
                "type": "string",
                "title": "Payload Type",
                "description": ("""Pay special attention to the proper """
                                """mapping of the data below."""),
                "enum": [
                    "form",
                    "json",
                    "xml"
                ],
                "enumNames": [
                    "Form",
                    "Json",
                    "Xml"
                ]
            },
            "data": {
                "type": "array",
                "title": "Data",
                "description": ("""If you leave this empty, it will """
                                """default to including the raw data from """
                                """the previous step. Key, value pairs """
                                """sent as data."""),
                "items": {
                    "$ref": "#/definitions/data"
                }
            },
            "headers": {
                "type": "array",
                "title": "Headers",
                "description": ("""Key, value pairs to be added as headers """
                                """in all requests."""),
                "items": {
                    "$ref": "#/definitions/data"
                }
            }
        }
    }

    def __str__(self):
        return self.title

    def get_schema(self, schema_type):
        schema = self.BASE_SCHEMA
        if schema_type == self.HOOK_GET:
            schema['title'] = "Webhook GET"
            schema['description'] = "Set up Webhooks by Zipier GET"
            if 'payloadType' in schema['properties'].keys():
                del schema['properties']['payloadType']
            if 'data' in schema['properties'].keys():
                schema['properties']['data']['title'] = "Query String Params"
                schema['properties']['data']['description'] = (
                    """These params will be URL-encoded and appended to the """
                    """URL when making the request. Note: If you specify """
                    """nothing for this field, we will automatically encode """
                    """and include every field from the previous step in """
                    """the query string. If you don't want this, use the """
                    """\"Custom Request\" action.""")
        elif schema_type == self.HOOK_POST:
            schema = self.BASE_SCHEMA
            schema['title'] = "Webhook POST"
            schema['description'] = "Set up Webhooks by Zipier POST"
        elif schema_type == self.HOOK_PUT:
            schema = self.BASE_SCHEMA
            schema['title'] = "Webhook PUT"
            schema['description'] = "Set up Webhooks by Zipier PUT"
        return schema

    def make_it_so(self):
        to_run = {
            self.HOOK_POST: self.run_post,
            self.HOOK_GET: self.run_get,
            self.HOOK_PUT: self.run_put,
        }

        runner = to_run.get(self.hook_type)

        if runner:
            return runner()
        else:
            return 'Nope'

    def run_post(self):
        payload_type = self.data.get('payloadType', 'form')
        headers = {}
        if payload_type == 'json':
            headers['Content-Type'] = 'application/json'
        elif payload_type == 'xml':
            headers['Content-Type'] = 'application/xml'
        else:
            headers['Content-Type'] = 'multipart/form-data'

        # Yes I'm letting the user overwrite the content-type
        # If they want to mess things up ¯\_(ツ)_/¯

        headers = self.get_headers(headers)
        payload = self.get_data()

        response = requests.post(self.data.get('url'), data=payload,
                                 headers=headers, timeout=30)

        return utils.handle_response(response)

    def run_get(self):
        headers = self.get_headers()
        payload = self.get_data() or ''

        response = requests.get('{0}{1}'.format(self.data.get('url'), payload),
                                headers=headers, timeout=30)

        return utils.handle_response(response)

    def run_put(self):
        payload_type = self.data.get('payloadType', 'form')
        headers = {}
        if payload_type == 'json':
            headers['Content-Type'] = 'application/json'
        elif payload_type == 'xml':
            headers['Content-Type'] = 'application/xml'
        else:
            headers['Content-Type'] = 'multipart/form-data'

        headers = self.get_headers(headers)
        payload = self.get_data()

        response = requests.put(self.data.get('url'), data=payload,
                                headers=headers, timeout=30)

        return utils.handle_response(response)

    def get_data(self):
        data = utils.build_dict(self.data.get('data'))

        if not data or len(data) <= 0:
            # I can follow any coding style needed. Even having returns
            # in the middle of a function! I know some people hate it...
            return None

        if self.hook_type == self.HOOK_GET:
            get_data = '?'
            for key, value in data.items():
                get_data += '{0}={1}&'.format(key, value)
            # Oh hi return, almost didnt see you there.
            return get_data[:-1]

        payload_type = self.data.get('payloadType', 'form')
        if payload_type == 'json':
            # ┬─┬﻿ ノ( ゜-゜ノ)
            return json.dumps(data)
        elif payload_type == 'xml':
            # (╯°□°)╯︵ ┻━┻
            return dicttoxml(data)

        # (ノ^_^)ノ┻━┻ ┬─┬ ノ( ^_^ノ)
        return data

    def get_headers(self, headers={}):
        results = list(utils.search_dict('headers', self.data))
        # import ipdb; ipdb.set_trace()
        if results and len(results) > 0:
            _, list_headers = results[0]
            if len(list_headers) > 0:
                headers.update(utils.build_dict(list_headers))
        return headers
