from os import path
from glob import glob
from bottle import Bottle, template
from markdown import markdown
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

@http_view.route('/docs')
@http_view.route('/docs/<doc_name>')
def docs(doc_name=""):
    if doc_name:
        with open(path.join('views', doc_name), "rt") as doc:
            http_rendered = markdown("".join(doc.readlines()))
        return template("docs", text=http_rendered)
    else:
        text = "<h1>List of Documents</h1>"
        for _file in glob("views/*.md"):
            text += "<a href='/docs/{f}'>{f}</a><br />".format(f=path.basename(_file))
        return template("docs", text=text)