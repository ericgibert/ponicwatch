from bottle import Bottle, template
http_view = Bottle()

@http_view.route('/')
def default():
    return template("default")

@http_view.route('/log')
@http_view.route('/log/<page:int>')
def log(page=0):
    rows = http_view.controller.log.get_all_records(from_page=page, order_by="created_on desc")
    return template("log", rows=rows, current_page=page)

@http_view.route('/sensors')
@http_view.route('/sensors/<sensor_id:int>')
def sensors(sensor_id=0):
    if sensor_id:
        sensor = http_view.controller.sensors[sensor_id]
        return template("one_sensor", sensor=sensor)
    else:
        first_sensor = list(http_view.controller.sensors.values())[0]
        rows = first_sensor.get_all_records()
        return template("sensors", rows=rows)
