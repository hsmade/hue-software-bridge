#!/usr/bin/env python
from flask import Flask, Response, request, url_for, render_template, make_response
import json
import logging
import argparse
from uuid import uuid4
import imp
import yaml

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('Flask')

config = yaml.load(open('config.yaml').read())  # FIXME: define path
app = Flask(__name__)

lamp_status = {}
index = 1
for lamp in config['lights']:
    lamp_status[str(index)] = {
        'data': lamp,
        'status': False
    }
    index += 1


def get_action(action_name, action_type):
    result = None
    for action in config['actions']:
        if action['name'] == action_name:
            result = action[action_type]
            module_name = action['file'].replace('.py', '')
            action_module = imp.load_source(module_name, 'actions/' + action['file'])
            action_method = getattr(action_module, action['method'])
            result['method'] = action_method
            break
    return result


def generate_light_status():
    status = {}
    for lamp_index, lamp_item in lamp_status.iteritems():
        status[lamp_index] = create_light_status(lamp_item['data'], lamp_index)
    return status


def get_status(lamp_index):
    return lamp_status[lamp_index]['status']


def create_light_status(lamp_object, lamp_index):
    """
    Creates the dictionary for a lamp's status info

    :param lamp_object:
    :return: dict
    """
    result = {
        "state": {
            "on": get_status(lamp_index),
            "bri": 0,
            "hue": 0,
            "sat": 0,
            "xy": [0.0,0.0],
            "ct": 0,
            "alert": "none",
            "effect": "none",
            "colormode": "xy",
            "reachable": True
        },
        "type": lamp_object['type'],
        "name": lamp_object['name'],
        "modelid": lamp_object['type'],
        "swversion": "0",
        "pointsymbol": {
            "1": "none",
            "2": "none",
            "3": "none",
            "4": "none",
            "5": "none",
            "6": "none",
            "7": "none",
            "8": "none"
        }
    }
    return result


@app.route('/api', methods=['POST'])
def connect_user():
    deviceType = request.form.get('devicetype')
    username = request.form.get('username', str(uuid4()))
    logger.info('connect_user: {data}'.format(data=request.form))
    result = [{'success': {'username': username}}]
    return json.dumps(result), 200


@app.route('/api/<username>/config/whitelist/<username_to_delete>', methods=['DELETE'])
def delete_user(username, username_to_delete):
    logger.info('delete_user: username={user}, username_to_delete={delete}'.format(
        user=username, delete=username_to_delete))
    return '', 200


@app.route('/api/<username>/lights', methods=['GET'])
def list_lights(username):
    """
    Get all lights for this user, with their status

    :param username:
    :return:
    """
    logger.info('list_lights: username={user}'.format(user=username))
    response = generate_light_status()
    logger.debug('list_lights: response: {response}'.format(response=response))
    return Response(json.dumps(response), mimetype='application/json'), 200


@app.route('/api/<username>/lights/<index>/state', methods=['PUT'])
def switch_light(username, index):
    """
    Switch light <index>

    :param username:
    :param index:
    :return:
    """
    logger.info('switch_light: username={user}, index={idx}, data={data}, state={state}'.format(
        user=username, idx=index, data=request.get_data(), state=request.form.get("on")))
    state = json.loads(request.get_data())
    action = get_action(lamp_status[index]['data']['action'], 'set')
    kwargs = action['parameters']
    result = action['method'](state=state['on'], **kwargs)
    logger.debug('switch_light: result: {result}'.format(result=result))
    if result:
        status_code = 200
    else:
        status_code = 500
    return '', status_code


@app.route('/description.xml', methods=['GET'])
def description():
    result = render_template('description.xml', ip=args.ip, port=args.port, mac=args.mac)
    response = make_response(result)
    response.headers["Content-Type"] = "application/xml"
    return response


@app.route('/api/<username>', methods=['GET'])
def full_state(username):
    logger.info('full_state: username={user}'.format(user=username))
    return '', 200

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='uPnP sender')
    parser.add_argument('--ip', dest='ip', action='store', required=True)
    parser.add_argument('--port', dest='port', action='store', required=True)
    parser.add_argument('--mac', dest='mac', action='store', required=True)
    args = parser.parse_args()

    app.run(host=args.ip, debug=True, port=int(args.port))
