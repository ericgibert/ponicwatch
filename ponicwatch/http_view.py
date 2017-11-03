import sys
from os import path
from glob import glob
import datetime
from markdown import markdown
from bottle import Bottle, template, static_file, request, BaseTemplate, redirect
from bottlesession import CookieSession, authenticator
from user import User
session_manager = CookieSession()    #  NOTE: you should specify a secret
valid_user = authenticator(session_manager)

http_view = Bottle()
BaseTemplate.defaults['login_logout'] = "Login"

@http_view.route('/')
def default():
    session = session_manager.get_session()
    rows = http_view.controller.log.get_all_records(order_by="created_on desc", where_clause="log_type='ERROR'")
    return template("default", session_valid=session["valid"],
                    controller=http_view.controller,
                    rows=rows)

@http_view.route('/log')
@http_view.route('/log/<page:int>')
def log(page=0):
    if "system" in request.query:
        log_type, object_id =  request.query["system"].split('_')
        where = "log_type='{}' and object_id={}".format(log_type, object_id)
        pwo = """<a href="/{}s/{}">Go to PWO page</a>""".format(log_type.lower() + ('e' if log_type.lower()=='switch' else ''),
                                                                object_id) if log_type in ("SENSOR", "SWITCH", "HARDWARE") else ""
    else:
        where, pwo = "", ""
    rows = http_view.controller.log.get_all_records(from_page=page, order_by="created_on desc", where_clause=where)
    return template("log", rows=rows, current_page=page, pwo=pwo)

@http_view.route('/switches')
@http_view.route('/switches/<object_id:int>')
@http_view.route('/sensors')
@http_view.route('/sensors/<object_id:int>')
@http_view.route('/hardwares')
@http_view.route('/hardwares/<object_id:int>')
@http_view.route('/interrupts')
@http_view.route('/interrupts/<object_id:int>')
@http_view.route('/systems')
@http_view.route('/systems/<object_id:int>')
def pw_object(object_id=0):
    pw_object_type = (request['bottle.route'].rule[1:].split('/'))[0]
    pw_list = getattr(http_view.controller, pw_object_type) # get the controller's dictionary based on its name
    if object_id:
        pwo = pw_list[object_id]
        return one_pw_object_html(pwo)
    elif pw_list.values():
        try:
            pwo = list(pw_list.values())[0]
            rows = pwo.get_all_records()
        except IndexError:
            pwo, rows = None, []
        return template("pw_objects", pw_object=pwo, rows=rows, pw_object_type=pw_object_type)
    else:
        return template("pw_objects", pw_object=None, rows=[], pw_object_type="No %s found" % pw_object_type)

def one_pw_object_html(pwo):
    """
    Use the template engine to return the HTML mesage givien all  information from one object
    :param pwo:
    :return:
    """
    if "updated_on" in pwo and isinstance(pwo["updated_on"], datetime.datetime):
        pw_upd_local_datetime = pwo["updated_on"].replace(tzinfo=datetime.timezone.utc).astimezone()
    else:
        pw_upd_local_datetime = "no datetime given"
    return template("one_pw_object", pw_object=pwo,
                    image=make_image(pwo),
                    pw_upd_local_datetime=pw_upd_local_datetime)


@http_view.post('/switches')
@http_view.post('/sensors')
@http_view.post('/hardwares')
@http_view.post('/interrupts')
@http_view.post('/systems')
def post_pw_object():
    """Update a switch record from FORM"""
    id = int(request.forms.get('id'))
    pw_object_type = request.forms.get('pw_object_type')
    pw_list = getattr(http_view.controller, pw_object_type)
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

@http_view.post('/switch/<pin>/<set_to>')
def set_pin_to(pin, set_to):
    """Set the pin of an IC to a value
    - MCP23017: outAx | outBx where the last 2 char are the pin number to set
    - RPI3: RPIxx where xx is the pin to set
    set_to: ON | OFF"""
    if pin.startswith("out"):
        http_view.controller.MCP23017.write(pin[-2:], int(set_to == "ON"))

@http_view.get('/sensor/read/<sensor_id:int>')
def sensor_read(sensor_id):
    """Force read the sensor value now"""
    for sensor in http_view.controller.sensors.values():
        if sensor["id"] == sensor_id:
            sensor.execute()
            redirect("/sensors/%d" % sensor_id)

@http_view.get('/interrupt/exec/<inter_id:int>')
def sensor_read(inter_id):
    """Force the interruption's callback execution now"""
    for inter in http_view.controller.interrupts.values():
        if inter["id"] == inter_id:
            inter.on_interrupt()
            redirect("/interrupts/%d" % inter_id)

@http_view.get('/switch/exec/<switch_id:int>')
def sensor_read(switch_id):
    """Force the setting of the switch now"""
    for switch in http_view.controller.switches.values():
        if switch["id"] == switch_id:
            switch.execute(switch.init_dict["set_value_to"])
            redirect("/switches/%d" % switch_id)

#
### Login/Logout form & process
#
@http_view.route('/Login')
def login():
    return template('login.tpl', error="")

@http_view.post('/Login')
def do_login():
    """
    Fetch the login/password from the form and check this couple against the tb_user table
    """
    username = request.forms.get('username')
    password = request.forms.get('password')

    if not username or not password:
      return template('login.tpl', error='Please specify username and password')

    session = session_manager.get_session()
    session['valid'] = False

    new_user = User(http_view.controller)
    new_user.get_user(username, password)
    if new_user["id"]:
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

@http_view.route('/stop')
def stop():
    """Stops the application"""
    http_view.controller.stop(from_bottle=True)
    sys.stderr.close()

#
### Generation of the PNG to display the data as a plot
#
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

@http_view.route("/images/<filepath>")
def img(filepath):
    return static_file(filepath, root="images")

def get_image_file(pwo):
    return "images/{}_id_{}.png".format(pwo.__class__.__name__, pwo["id"])  # images/sensor_id_1.png

def make_image(data_object):
    """Creates an image for the status of the given object (sensor, switch)"""
    obj_class_name = data_object.__class__.__name__ # Sensor / Switch
    if obj_class_name not in ("Sensor", "Switch"):
        return ""
    image_file = get_image_file(data_object)  # images/sensor_id_1.png
    log_type = obj_class_name.upper()  # http_view.controller.log.LOG_TYPE[obj_class_name.upper()]
    yesterday = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(1)
    where_clause = "log_type='{}' and object_id={} and created_on>=?".format(log_type, data_object["id"])  #, yesterday.strftime('%Y-%m-%d %H:%M:%S'))
    if http_view.controller.debug >= 3:
        print(obj_class_name, data_object, image_file)
        # print("where ==>", where_clause, yesterday)
    rows = http_view.controller.log.get_all_records(page_len=0, where_clause=where_clause, order_by="created_on asc", args=(yesterday,))
    # for row in rows: print(row)
    x = [row[-1].replace(tzinfo=datetime.timezone.utc).astimezone() for row in rows]
    y = [row[5] for row in rows]
    # print(len(x), "log entries:")
    # print("x ==>",min(x), max(x))
    # print("y ==>", min(y), max(y))
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    if obj_class_name == "Switch":
        ax.scatter(x, y)
    else:
        ax.plot(x, y)
    ax.set_title(data_object["name"])
    ax.grid(True)
    ax.set_xlabel('time')
    xax = ax.get_xaxis()  # get the x-axis
    adf = xax.get_major_formatter()  # the the auto-formatter
    try:
        adf.scaled[1. / 24] = '%H:%M'  # set the < 1d scale to H:M
    except AttributeError:
        pass
    ax.format_xdata = mdates.DateFormatter('%H:%M:%S')  # .strftime("%y-%m-%d %H:%M:%S")
    ax.set_ylabel('measure')
    canvas.print_figure(image_file)
    return '/' + image_file


if __name__ == "__main__":
    http_view.run()
