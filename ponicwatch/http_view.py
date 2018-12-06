import sys
from os import path, system
from glob import glob
import datetime
import json
from markdown import markdown
from bottle import Bottle, template, static_file, request, BaseTemplate, redirect, response, abort, error
from bottlesession import CookieSession, authenticator
from user import User

__version__ = "1.20180623 HK"
__author__ = 'Eric Gibert'
__license__ = 'MIT'

session_manager = CookieSession(cookie_expires=3600)    #  NOTE: you should specify a secret
valid_user = authenticator(session_manager)

http_view = Bottle()
BaseTemplate.defaults['login_logout'] = "Login"

@error(404)
def error404(error):
    return '404 error:<h2>%s</h2>' % error

def get_pwo():
    """Helper function: returns a PonicWatch Object based on the object type and id found in the form.
    Expected fields in the form (can be hidden if necessary):
    - pw_object_type: the class name
    - id: the PWO id, which is the key in the controller's pwo dictionaries
    These two <input> are hidden above to the 'submit' button in the one_pw_object.tpl form
    """
    cls_name = request.forms["pw_object_type"]
    pwo = http_view.controller.get_pwo(cls_name, request.forms["id"])
    return pwo


@http_view.route('/')
def default():
    try:
        session = session_manager.get_session()
    except RuntimeError:
        session = {}
        session["valid"] = False
    http_view.controller.last_start = http_view.controller.log.fetch("select max(created_on) from tb_log where log_type='INFO' and float_value=1.0", only_one=True)
    http_view.controller.last_stop = http_view.controller.log.fetch("select max(created_on) from tb_log where log_type='INFO' and float_value=0.0", only_one=True)
    rows = http_view.controller.log.get_all_records(order_by="created_on desc",
                                                    where_clause="(log_type='ERROR' or log_type='INFO') and julianday(date('now')) - julianday(created_on)  < 8")
    return template("default", session_valid=session["valid"],
                    controller=http_view.controller,
                    rows=rows)

@http_view.route('/log')
@http_view.route('/log/<page:int>')
def log(page=0):
    where, pwo, req_query = "", "", ""
    if "system" in request.query:
        log_type, object_id = request.query["system"].split('_')
        if log_type in ("INFO", "SENSOR", "SWITCH", "HARDWARE", "INTERRUPT", "SCHEDULER"):
            where = "log_type='{}' and object_id={}".format(log_type, object_id)
            pwo = """<a href="/{}/{}">Go to PWO page</a>""".format(log_type.lower() + 's', object_id)
            req_query = "?system=" + request.query["system"]
    rows = http_view.controller.log.get_all_records(from_page=page, order_by="created_on desc", where_clause=where)
    return template("log", rows=rows, current_page=page, pwo=pwo, req_query=req_query)

@http_view.route('/links')
def list_links():
    """List all the links, even the inactive ones"""
    return template("links", controller=http_view.controller)


@http_view.route('/switchs')
@http_view.route('/switchs/<id:int>')
@http_view.route('/sensors')
@http_view.route('/sensors/<id:int>')
@http_view.route('/hardwares')
@http_view.route('/hardwares/<id:int>')
@http_view.route('/interrupts')
@http_view.route('/interrupts/<id:int>')
@http_view.route('/systems')
@http_view.route('/systems/<id:int>')
def pw_object(id=0):
    pwo_dict_name = request.path.split('/')[1]
    pwo_dict = getattr(http_view.controller, pwo_dict_name)  # get the controller's dictionary based on its name
    if id: # one PonicWatch Object page
        pwo = pwo_dict[id]
        return one_pw_object_html(pwo)
    else:
        try:
            pwo = list(pwo_dict.values())[0]
            rows = pwo.get_all_records()
        except IndexError:
            pwo, rows = None, []
            pwo_dict_name = "No %s found" % pwo_dict_name
        return template("pw_objects", pw_object=pwo, rows=rows, pw_object_type=pwo_dict_name, ctrl_pwo_dict=pwo_dict)

def one_pw_object_html(pwo, only_html=False):
    """
    Use the template engine to return the HTML page giving all information from one object
    :param pwo:
    :return:
    """
    if "updated_on" in pwo and isinstance(pwo["updated_on"], datetime.datetime):
        pw_upd_local_datetime = pwo["updated_on"].replace(tzinfo=datetime.timezone.utc).astimezone()
    else:
        pw_upd_local_datetime = "no datetime given"
    return template("one_pwo_html" if only_html else "one_pwo_form",
                    pw_object=pwo,
                    image=make_image(pwo),
                    pw_upd_local_datetime=pw_upd_local_datetime)

@http_view.post('/switch/upd/<id:int>')
@http_view.post('/sensor/upd/<id:int>')
@http_view.post('/hardware/upd/<id:int>')
@http_view.post('/interrupt/upd/<id:int>')
def pwo_update(id):
    """update the PWO's record with the form's values"""
    # cls_name =  request.forms["pw_object_type"]   # request.path.split('/')[1]
    # pwo = http_view.controller.get_pwo(cls_name, id)
    pwo = get_pwo()
    upd_dict = {}
    for k in ("name", "timer", "init", "mode"):     # <-- ensure the tuple is the same in one_pw_object.tpl
        try:
            v = request.forms[k]
            if v != pwo[k]:
                upd_dict[k] = v
                if http_view.controller.debug >= 3:
                    print("Update id:", id, pwo, "changes:", k, v)
        except (KeyError, IndexError):
            pass
    if upd_dict:
        # check that the init dictionary is JSON ok
        try:
            new_init_dict = json.loads(upd_dict.get('init', "{}"))
        except:
            return "<h1>Syntax error in the propose init JSON dictionary</h1>"
        else:
            pwo.update(**upd_dict)
    url = request.forms["pw_object_type"] + 's'
    redirect("/{}/{}".format(url, id))

@http_view.get('/switch/value/<id:int>')
@http_view.get('/sensor/value/<id:int>')
@http_view.get('/hardware/value/<id:int>')
@http_view.get('/interrupt/value/<id:int>')
def pwo_value(id):
    pwo = http_view.controller.get_pwo(request.path.split('/')[1], id)
    try:
        if_expression = pwo.init_dict['if']
    except KeyError:
        result = { "if": "No 'if' in init_dict", "make": "", "eval": ""}
    else:
        if_make = http_view.controller.make_expression(pwo, if_expression)
        if_eval = http_view.controller.eval_expression(pwo, if_expression, if_make)
        result = {"if": if_expression, "make": if_make, "eval": if_eval}
    try:
        result["value"] = pwo.value
    except AttributeError:
        result["value"] = "Not implemented"
    if http_view.controller.debug >= 3:
        print(result, json.dumps(result))
    response.content_type = 'application/json'
    return json.dumps(result)

#
###  Special operations on specific PWO
#
@http_view.post('/hardware/<id:int>/<pin>/<set_to>')
def set_pin_to(id, pin, set_to):
    """Set the pin of an IC to a value
    - to set a pin on MCP23017: outAx | outBx where the last 2 char are the pin number to set
    - to set a pin on RPI3: RPIxx where xx is the pin to set
    set_to: ON | OFF"""
    if pin.startswith("out") or pin.startswith("RPI"):
        MCP23017 = http_view.controller.get_pwo("Hardware", id)
        MCP23017.write(pin[-2:], int(set_to == "ON"))

@http_view.get('/sensor/exec/<sensor_id:int>')
def sensor_exec(sensor_id):
    """Force read the sensor value now"""
    try:
        sensor = http_view.controller.sensors[sensor_id]
        sensor.execute()
    except KeyError:
        abort(404, "Unknown Sensor %d" % sensor_id)
    redirect("/sensors/%d" % sensor_id)

@http_view.get('/interrupt/exec/<inter_id:int>')
def interrupt_exec(inter_id):
    """Force the interruption's callback execution now"""
    try:
        inter = http_view.controller.interrupts[inter_id]
        inter.on_interrupt()
    except KeyError:
        abort(404, "Unknown Interrupt %d" % inter_id)
    redirect("/interrupts/%d" % inter_id)

@http_view.get('/switch/exec/<switch_id:int>')
def switch_exec(switch_id):
    """Force the setting of the switch now"""
    try:
        switch = http_view.controller.switchs[switch_id]
        switch.execute(given_value=switch.init_dict["set_value_to"])
    except KeyError:
        abort(404, "Unknown Switch %d" % switch_id)
    redirect("/switchs/%d" % switch_id)

#
####  *.md documents posted in the 'views' folder
#
@http_view.route('/docs')
@http_view.route('/docs/<doc_name>')
def docs(doc_name=""):
    if doc_name:
        with open(path.join('views', doc_name), "rt") as doc:
            http_rendered = markdown("".join(doc.readlines()))
        return template("docs", text=http_rendered)
    else:
        text = "<h1>List of Documents</h1>"
        for file_ in glob("views/*.md"):
            text += "<a href='/docs/{f}'>{f}</a><br />".format(f=path.basename(file_))
        return template("docs", text=text)

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

@http_view.route('/restart')
def restart():
    """Restarts the application"""
    system(path.dirname(path.abspath(__file__)) + "/ponicwatch.sh restart")

@http_view.route('/stop')
def stop():
    """Stops the application"""
    # http_view.controller.stop(from_bottle=True)
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
    if obj_class_name not in ("Sensor", ):   #   ("Sensor", "Switch"):
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
    from model.pw_db import Ponicwatch_Db
    from pw_log import Ponicwatch_Log
    class ctrl:
        def __init__(self):
            self.name = 'Mushtent'
            self.db = Ponicwatch_Db("sqlite3", {'database': 'local_ponicwatch.db'})
            self.log = Ponicwatch_Log(controller=self, debug=3)
    http_view.controller = ctrl()
    http_view.run()
