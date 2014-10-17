__author__ = 'user'

from bottle import *
from modules.lxc import mod_lxc

app = application = Bottle()

module_lxc = mod_lxc()

@app.route('/')
def index():
  return 'Hello'

@app.route('/lxc', method=["GET", "POST"])
@app.route('/lxc/', method=["GET", "POST"])
def lxc_dashboard():
  return module_lxc.dashboard()

@app.route('/lxc/create', method="POST")
@app.route('/lxc/create/', method="POST")
def lxc_create():
  return module_lxc.create()

@app.route('/lxc/destroy', method="POST")
@app.route('/lxc/destroy/', method="POST")
def lxc_destroy():
  return module_lxc.destroy()

@app.route('/lxc/start', method="POST")
@app.route('/lxc/start/', method="POST")
def lxc_start():
  return module_lxc.start()

app.run(
    host='localhost',
    port='8000'
)