import rrdtool
import datetime
import time
import os
import struct
import socket
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, Response

app = Flask(__name__)
app.config.from_object('config')

def get_date(sec):
    t = time.localtime(sec)
    return time.strftime("%d %b %Y (%H:%M)",t) 

def get_values(host, port):
    s = socket.socket()
    s.connect((host,port))
    values = s.recv(1024)
    s.close
    return values.decode('utf-8')

def generate_plot(rrdfile, start, end, ds):
    imagedata = rrdtool.graphv("-",
                               '--end', "%d" % (end),
                               '--start', "%d" % (start), 
                               "DEF:myspeed=%s:%s:AVERAGE" % (rrdfile,ds),
                               'LINE1:myspeed#FF0000')
    return imagedata['image']

@app.route('/temperature.png')
def plot_temperature():
    end = session['end_time']
    start = session['start_time']
    imagedata = generate_plot(app.config['RRDDB'],start,end,"temperature")
    return Response(imagedata, mimetype='image/png')

@app.route('/humidity.png')
def plot_humidity():
    end = session['end_time']
    start = session['start_time']
    imagedata = generate_plot(app.config['RRDDB'],start,end,"humidity")
    return Response(imagedata, mimetype='image/png')

@app.route('/')
def show_plots():
    return render_template('show_plots.html')

@app.route('/updatetime', methods=['POST'])
def update_time():
    if not session.get('logged_in'):
        abort(401)
    try:
        start_t = time.strptime(request.form['starttime'],"%m/%d/%Y %H:%M")
        end_t = time.strptime(request.form['endtime'],"%m/%d/%Y %H:%M")
        start_t = int(time.strftime("%s",start_t))
        end_t = int(time.strftime("%s",end_t))
    except:
         flash('Invalid time format')
         return redirect(url_for('show_plots'))
    if start_t >= end_t:
        flash('Invalid time format')
        return redirect(url_for('show_plots'))
    session['end_time'] = end_t
    session['start_time'] = start_t 
    return redirect(url_for('show_plots'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            now = int(datetime.datetime.now().strftime('%s'))
            session['logged_in'] = True
            session['end_time'] =  now
            session['start_time'] = now - 24*3600*7
            flash('You were logged in')
            return redirect(url_for('show_plots'))
    return render_template('login.html', error=error)
    
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_plots'))

app.jinja_env.globals['get_date']=get_date
app.jinja_env.globals.update(get_values=get_values)

if __name__ == "__main__":
    app.run(host = '0.0.0.0')
