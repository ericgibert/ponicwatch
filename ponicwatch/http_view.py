from os import path
from glob import glob
import datetime
from markdown import markdown
from bottle import Bottle, template, static_file

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
        return template("one_sensor", sensor=sensor, image=make_image(sensor))
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


from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

@http_view.route("/images/<filepath>")
def img(filepath):
    return static_file(filepath, root="images")

def make_image(data_object):
    """Creates an image for the reading of the given obkect (sensor, switch)"""
    obj_class_name = data_object.__class__.__name__ # Senor / Switch
    image_file = "images/{}_{}.png".format(obj_class_name, data_object["id"])  # images/sensor_id_1.png
    log_type = http_view.controller.log.LOG_TYPE[obj_class_name.upper()]
    yesterday = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(1)
    where = "log_type={} and object_id={} and created_on>='{}'".format(log_type, data_object["id"], yesterday.strftime('%Y-%m-%d %H:%M:%S'))
    # print(obj_class_name, log_type, image_file)
    print("where ==>", where)
    rows = http_view.controller.log.get_all_records(page_len=0, where_clause=where, order_by="created_on asc")
    x = [row[-1].utcnow() for row in rows]
    y = [row[5] for row in rows]
    print("x ==>",x)
    print("y ==>", y)
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    ax.set_title('hi mom')
    ax.grid(True)
    ax.set_xlabel('time')
    ax.format_xdata = mdates.DateFormatter('%H:%M:%S')  # .strftime("%y-%m-%d %H:%M:%S")
    ax.set_ylabel('volts')
    canvas.print_figure(image_file)

    return '/' + image_file


