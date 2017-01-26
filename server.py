from flask import Flask, request, Response, \
  render_template
import json
import uuid

app = Flask(__name__)
HOST_IP='10.199.1.5'
PORT=5000
UUID=uuid.uuid1()

from functools import wraps

def returns_xml(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    r = f(*args, **kwargs)
    return Response(r, content_type='text/xml; charset=utf-8')
  return decorated_function

def returns_json(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    r = f(*args, **kwargs)
    if app.config['DEBUG']:
      print(json.dumps(r, indent=2))
    return Response(
      json.dumps(r),
      content_type='application/json; charset=utf-8'
    )
  return decorated_function

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.before_request
def before():
  print(request.headers)
  print(json.dumps({
    'method': request.method,
    'args': request.args,
    'path': request.full_path,
    'data': request.get_data().decode('utf8')
  }, indent=2))

@app.route('/description.xml')
@returns_xml
def discovery():
  data = {
    'host_ip': HOST_IP,
    'port': PORT, 
    'uuid': UUID,
  }
  return render_template('description.xml', **data)

@app.route('/api/<garbage>')
@returns_json
def empty_response(garbage):
  return '{}'

@app.route('/api/<user_id>/lights')
@returns_json
def get_lights(user_id):
  return devices

@app.route('/api/<user_id>/lights/<id>')
@returns_json
def get_light(user_id, id):
  return devices[id]

@app.route('/api/<user_id>/lights/<id>/state', methods=['PUT', 'GET'])
@returns_json
def change_state(user_id, id):
    try:
      # fucking alexa and content types!
      request_data = json.loads(request.get_data().decode('utf8'))
      devices[id]['state'].update(request_data)
      base_path = '/lights/{}/state/'.format(id)
      response = {
        "success": {}
      }
      for key, val in request_data.items():
        response['success']['{}{}'.format(base_path, key)] = devices[id]['state'][key]
      return [response]
    except:
      return [{}]

def gen_light(id):
  return {
      "pointsymbol": {
          "1": "none",
          "3": "none",
          "2": "none",
          "5": "none",
          "4": "none",
          "7": "none",
          "6": "none",
          "8": "none",
      },
      "state": {
          "on": False,
          "xy": [0.4589, 0.4103],
          "alert": "none",
          "reachable": True,
          "bri": 255,
          "hue": 14924,
          "colormode": "hs",
          "ct": 365,
          "effect": "none",
          "sat": 143
      },
      "swversion": "6601820",
      "name": app.config['lights'][id]['name'],
      "manufacturername": "Philips",
      "uniqueid": id,
      "type": "Extended color light",
      "modelid": "LCT001"
  }

with open('config.json') as config_fp:
  config_data = json.load(config_fp)
  app.config.update(**config_data)  
  app.config['SERVER_NAME'] = '{}:{}'.format(
    config_data['host'], config_data['port']
  )

devices = dict()

for light_id in config_data['lights'].keys():
  devices[light_id] = gen_light(light_id)

app.run(
  debug=True,
  host=app.config['host'],
  port=app.config['port'],
)
