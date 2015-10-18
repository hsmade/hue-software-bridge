import requests
import logging

__author__ = 'wfournier'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def send_request(url, data_on, data_off, state, method):
    """
    Do a 'method' request

    :param url: The URL to post to
    :param data: a dict of post parameters
    :param method: The HTTP method
    :return: bool
    """
    if state:
        data = data_on
    else:
        data = data_off
    result = getattr(requests, method.lower())(url, data=data)
    logger.debug('Did a {method} to {url} with data {data}. Result: {status}: {text}'.format(
        method=method,
        url=url,
        data=data,
        status=result.status_code,
        text=result.text
    ))
    print url, result.status_code, result.text
    return state and result.ok


def send_post(**kwargs):
    """
    Do a post request

    :param url: The URL to post to
    :param data: a dict of post parameters
    :return: bool
    """
    print 'Doing post: {data}'.format(data=kwargs)
    return send_request(method='post', **kwargs)


def send_put(**kwargs):
    """
    Do a put request

    :param url: The URL to post to
    :param data: a dict of post parameters
    :return: bool
    """
    return send_request(method='post', **kwargs)
