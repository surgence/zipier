import logging
from collections import OrderedDict
logger = logging.getLogger(__name__)


def build_dict(items):
    # Gotta have that OrderedDict so non-targeted tests work!
    if isinstance(items, list):
        built_dict = OrderedDict()

        for item in items:
            if 'key' in item and 'value' in item:
                key = item.get('key')
                value = item.get('value')
            else:
                key = getattr(item, 'key', item)
                value = getattr(item, 'value', item)

            built_dict[key] = value
        return built_dict


def search_dict(input_key, input_dict):
    if hasattr(input_dict, 'items'):
        for key, value in input_dict.items():
            if isinstance(input_key, str) and key == input_key:
                yield key, value
            elif isinstance(input_key, list) and key in input_key:
                yield key, value
            if isinstance(value, dict):
                for result in search_dict(input_key, value):
                    yield result
            elif isinstance(value, list):
                for item in value:
                    for result in search_dict(input_key, item):
                        yield result


def handle_response(response):
    try:
        result = response.json()
    except ValueError as e:  # error decoding json
        logger.error(e, extra=response)
        result = response.content

    if 200 <= response.status_code <= 299:
        return result
    else:
        raise Exception(response.content)
