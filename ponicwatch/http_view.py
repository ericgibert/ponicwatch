from os import path
from glob import glob
import datetime
from markdown import markdown
from bottle import Bottle, template, static_file, request, BaseTemplate
from bottlesession import CookieSession, authenticator
session_manager = CookieSession()    #  NOTE: you should specify a secret
valid_user = authenticator(session_manager)

http_view = Bottle()
BaseTemplate.defaults['login_logout'] = "Login"

@http_view.route('/')
def default():
    return template("default")

@http_view.route('/log')
@http_view.route('/log/<page:int>')
def log(page=0):
    try:
        system = int(request.query["system"])
        log_type, object_id = system // 1000, system % 1000
        where = "log_type={} and object_id={}".format(log_type, object_id)
    except (KeyError, ValueError):
        where = ""
    rows = http_view.controller.log.get_all_records(from_page=page, order_by="created_on desc", where_clause=where)
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

@http_view.post('/sensors')
def post_sensor():
    """Update a sensor record from FORM"""
    id = request.forms.get('_id')
    sensor = http_view.controller.sensors[id]
    upd_fields = []
    for k, v in request.forms:
        if k!="id" and k in sensor.columns:
            upd_fields[k] = v
    if upd_fields:
        sensor.update(**upd_fields)
    redirect('/sensors/{}'.format(id))    
    
    
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
    where = "log_type={} and object_id={} and created_on>=?".format(log_type, data_object["id"])  #, yesterday.strftime('%Y-%m-%d %H:%M:%S'))
    # print(obj_class_name, log_type, image_file)
    print("where ==>", where, yesterday)
    rows = http_view.controller.log.get_all_records(page_len=0, where_clause=where, order_by="created_on asc", args=(yesterday,))
    # for row in rows: print(row)
    x = [row[-1] for row in rows]
    y = [row[5] for row in rows]
    print(len(x), "log entries:")
    print("x ==>",min(x), max(x))
    print("y ==>", min(y), max(y))
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    # ax.scatter(x, y)
    ax.set_title(data_object["name"])
    ax.grid(True)
    ax.set_xlabel('time')
    xax = ax.get_xaxis()  # get the x-axis
    adf = xax.get_major_formatter()  # the the auto-formatter
    adf.scaled[1. / 24] = '%H:%M'  # set the < 1d scale to H:M
    # ax.format_xdata = mdates.DateFormatter('%H:%M:%S')  # .strftime("%y-%m-%d %H:%M:%S")
    ax.set_ylabel('measure')
    canvas.print_figure(image_file)
    return '/' + image_file

@http_view.route('/Login')
def login():
    return template('login.tpl', error="")
@http_view.post('/Login')
# @http_view.view('login.tpl')
def do_login():
    passwds = { 'guest' : 'guest' }

    username = request.forms.get('username')
    password = request.forms.get('password')

    if not username or not password:
      return template('login.tpl', error='Please specify username and password')

    session = session_manager.get_session()
    session['valid'] = False

    if password and passwds.get(username) == password:
      session['valid'] = True
      session['name'] = username

    session_manager.save(session)
    if not session['valid']:
       return template('login.tpl', error='Username or password is invalid')

    BaseTemplate.defaults['login_logout'] = "Logout"
    redirect(request.get_cookie('validuserloginredirect', '/'))

@http_view.route('/Logout')
def logout():
    session = session_manager.get_session()
    session['valid'] = False
    session_manager.save(session)
    BaseTemplate.defaults['login_logout'] = "Login"
    redirect('/')


if __name__ == "__main__":
    http_view.run()
