print('[INFO] importing app.py files...')
from flask import Flask, render_template
from dataAnalyser import *
import mysql.connector
import pandas as pd
import json
import time

#Connecting to database
db=mysql.connector.connect(host="localhost",user="root",passwd="root",database="accessController0")

#Create a pandas dataframe to read data from database
df=pd.read_sql("SELECT * FROM Trackers",db)

#Calculate some statistics from preview data in database
weekly_labels,weekly_values = weekdayAverage(df)  #Average of people into the establishment per day of the week
daily_labels,daily_values = dailyAverage(df)      #Average of people into the establishment per day of the month
hour_labels,hour_values = hourFlow(df)            ##Average of people into the establishment per hour of the day

#Create the application instance
app = Flask(__name__)

@app.route('/')
def index():
     return render_template('index.html', title='Fluxo atual')

@app.route('/ref_data', methods=['POST','GET'])
def ref_data():
     db=mysql.connector.connect(host="localhost",user="root",passwd="root",database="accessController0")
     last_row = pd.read_sql('SELECT * FROM Trackers ORDER BY datetime DESC LIMIT 1',db)
     datetime = last_row.values[0][3].strftime('%d/%m/%Y - %H:%M:%S')
     total = str(last_row.values[0][1])
     entradas = str(getTodayFlowIn(db))
     time.sleep(0.5)
     return json.dumps({'status':'OK','total':total,'datetime':datetime, 'entradas':entradas})

@app.route('/diario')
def diario():
     dsc = "Este gráfico representa o número médio de pessoas dentro do estabelecimento em determinado dia"
     
     db=mysql.connector.connect(host="localhost",user="root",passwd="root",database="accessController0")
     df = pd.read_sql('SELECT Total FROM Trackers',db)
     m = max(50,df.max().Total)
     return render_template('line_chart.html', description = dsc, title='Média diária',max = m, labels=daily_labels, values=daily_values)

@app.route('/horario')
def horario():
     dsc = "Este gráfico representa o número médio de pessoas em cada hora do dia"
     return render_template('line_chart.html', description = dsc, title='Média por horário',max = 350, labels=hour_labels, values=hour_values)

@app.route('/semanal')
def semanal():
     colors = [
         "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
         "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
         "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
     return render_template('pie_chart.html', title='Média semanal',max = 350, set=zip(weekly_values,weekly_labels,colors))


if __name__==("__main__"):
     app.run(host='0.0.0.0',port=5000,debug=True,threaded=True)
