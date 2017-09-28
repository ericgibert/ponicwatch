from os import path
from glob import glob
import datetime
from markdown import markdown
from bottle import Bottle, template, static_file, request, BaseTemplate, redirect
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

def get_pw_list(pw_object_type):
    """ to do: Try using getattr within a try/except """
    if pw_object_type == "switches":
        pw_list = http_view.controller.switches
    elif pw_object_type == "sensors":
        pw_list = http_view.controller.sensors
    elif pw_object_type == "hardware":
        pw_list = http_view.controller.hardwares
    elif pw_object_type == "interrupts":
        pw_list = http_view.controller.interrupts
    elif pw_object_type == "systems":
        pw_list = http_view.controller.systems
    else:
        pw_list = None
    return pw_list

@http_view.route('/switches')
@http_view.route('/switches/<object_id:int>')
@http_view.route('/sensors')
@http_view.route('/sensors/<object_id:int>')
@http_view.route('/hardware')
@http_view.route('/hardware/<object_id:int>')
@http_view.route('/interrupts')
@http_view.route('/interrupts/<object_id:int>')
@http_view.route('/systems')
@http_view.route('/systems/<object_id:int>')
def pw_object(object_id=0):
    pw_object_type = (request['bottle.route'].rule[1:].split('/'))[0]
    pw_list = get_pw_list(pw_object_type)
    if object_id:
        pw_object = pw_list[object_id]
        return template("one_pw_object", pw_object=pw_object, image=make_image(pw_object), pw_object_type=pw_object_type)
    else:
        try:
            pw_object = list(pw_list.values())[0]
            rows = pw_object.get_all_records()
        except IndexError:
            pw_object, rows = None, []
        return template("pw_objects", pw_object=pw_object, rows=rows, pw_object_type=pw_object_type)

@http_view.post('/switches')
@http_view.post('/sensors')
@http_view.post('/hardware')
@http_view.post('/interrupts')
@http_view.post('/systems')
def post_pw_object():
    """Update a switch record from FORM"""

    id = int(request.forms.get('id'))
    pw_object_type = request.forms.get('pw_object_type')
    pw_list = get_pw_list(pw_object_type)
    pw_object = pw_list[id]
    upd_fields = {}
    for k, v in request.forms.items():
        if not(k.endswith("_id")) and k in pw_object.columns and v != pw_object[k]:
            upd_fields[k] = v
    if upd_fields:
        pw_object.update(**upd_fields)
    redirect('/{}/{}'.format(pw_object_type, id))
    
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

#
### Login/Logout form & process
#
@http_view.route('/Login')
def login():
    return template('login.tpl', error="")

@http_view.post('/Login')
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

#
### Generation of the PNG to display the data as a plot
#
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

@http_view.route("/images/<filepath>")
def img(filepath):
    return static_file(filepath, root="images")

def make_image(data_object):
    """Creates an image for the reading of the given obkect (sensor, switch)"""
    obj_class_name = data_object.__class__.__name__ # Sensor / Switch
    if obj_class_name not in ("Sensor", "Switch"):
        return ""
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
    # print(len(x), "log entries:")
    # print("x ==>",min(x), max(x))
    # print("y ==>", min(y), max(y))
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
    ax.format_xdata = mdates.DateFormatter('%H:%M:%S')  # .strftime("%y-%m-%d %H:%M:%S")
    ax.set_ylabel('measure')
    canvas.print_figure(image_file)
    return '/' + image_file


if __name__ == "__main__":
    http_view.run()
