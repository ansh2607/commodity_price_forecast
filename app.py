from os import name, stat
import re
from typing import ValuesView
import flask
from flask import Flask, render_template, request, redirect, url_for
from numpy import mod
from pandas.core.algorithms import mode
import requests
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
import csv
from flask import Flask, render_template, jsonify, request, flash
from flask_mysqldb import MySQL,MySQLdb 
import psycopg2 
import psycopg2.extras
import pandas as pd
import json
from jinjasql import JinjaSql
from scipy import stats
# import tensorflow as tf
# from tensorflow import keras
# from tensorflow.keras import Sequential, layers, callbacks
# from tensorflow.keras.layers import Dense, Dropout, GRU
from sklearn import metrics
import pickle
import datetime
from datetime import date
from prophet import Prophet


# Create Flask's `app` object
app = Flask(
    __name__,
    template_folder="templates"
)

@app.route("/" )
def index():
    return render_template('index.html')

state = ''
commodity = ''
sdistrict = ''
variety = ""



app.secret_key = "caircocoders-ednalan"
      
app.config['MYSQL_HOST'] = 'postgresql://postgres:AggarwalAnSh26@localhost/postgres'

app.config['MYSQL_DB'] = 'postgres'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

con = psycopg2.connect(
        host = "localhost",
        database = "postgres",
        user = "postgres",
        password = 'AggarwalAnSh26'
    )
   
@app.route('/graphs.html')
def main():
    
    cur = con.cursor()
    result = cur.execute("SELECT DISTINCT state from prices order by state")
    state = cur.fetchall()
    state_list = []
    for value in state:
        state_list.append(value[0])
   
    return render_template('graphs.html', state=state_list)


@app.route('/forecast.html')
def submain():
    
    cur = con.cursor()
    result = cur.execute("SELECT DISTINCT state from prices order by state")
    state = cur.fetchall()
    state_list = []
    for value in state:
        state_list.append(value[0])
   
    return render_template('forecast.html', state=state_list)


@app.route("/district/<state>")
def district(state):  
    
   
    cur = con.cursor()
    
    result = cur.execute("SELECT DISTINCT district FROM prices WHERE state = %s ORDER BY district ASC", [state] )
    district_value = cur.fetchall()  
    
    OutputArray = []
    for row in district_value:
        OutputArray.append(row)
    return jsonify({'districtArray': OutputArray})


@app.route("/market/<district>")
def market(district):  
    
  
    cur = con.cursor()
    
    result = cur.execute("SELECT DISTINCT market FROM prices WHERE district = %s ORDER BY market ASC", [district] )
    commodity_value = cur.fetchall()  
    
    OutputArray = []
    for row in commodity_value:
        OutputArray.append(row)

    return jsonify({'marketArray': OutputArray})



@app.route("/commodity/<market>")
def commodity(market):  
    
  
    cur = con.cursor()
    
    result = cur.execute("SELECT DISTINCT commodity FROM prices WHERE market = %s ORDER BY commodity ASC", [market] )
    commodity_value = cur.fetchall()  
    
    OutputArray = []
    for row in commodity_value:
        OutputArray.append(row)

    return jsonify({'commodityArray': OutputArray})


@app.route("/variety/<commodity>")
def variety(commodity):  
    
    
    cur = con.cursor()
    
    result = cur.execute("SELECT DISTINCT variety FROM prices WHERE commodity = %s ORDER BY variety ASC", [commodity] )
    commodity_value = cur.fetchall()  
    
    OutputArray = []
    for row in commodity_value:
        OutputArray.append(row)

    return jsonify({'varietyArray': OutputArray})































def plotprice(start_date, end_date,state, district, market, commodity, variety) :
    params= {
        'state': state,
        'district': district,
        'market': market,
        'commodity': commodity,
        'variety' : variety,
        'start_date': start_date,
        'end_date': end_date,

    }
    query = """SELECT * FROM prices WHERE state= {{ state }} and district = {{ district }}  and commodity = {{ commodity }} and variety = {{ variety }}"""
    query1 = """SELECT * FROM prices WHERE state= {{ state }} and district = {{ district }}  and commodity = {{ commodity }} and variety = {{ variety }} and arrival_date BETWEEN {{ start_date}} and {{end_date}}"""
    j = JinjaSql(param_style='pyformat')
    query, bind_params = j.prepare_query(query, params)
    query1, bind_params1 = j.prepare_query(query1, params)
    df = pd.read_sql_query(query,con=con, params= bind_params)
    df1= pd.read_sql_query(query1,con=con, params= bind_params1)
    print(df)
    print(df1)
    
    bar = px.bar(df, x="market", y='modal_price')
    line = px.line(df1, x="arrival_date", y='modal_price')

    priceJSON = json.dumps(bar, cls=plotly.utils.PlotlyJSONEncoder)
    lineJSON = json.dumps(line, cls=plotly.utils.PlotlyJSONEncoder)
    return priceJSON, lineJSON


def line_chart(df,title):
    # df_plot =pd.melt(df, id_vars=[arrival_date], value_vars=['modal_price'])
    fig = px.line(df, x='arrival_date', y='modal_price', title=title)
    fig.update_xaxes(rangeslider_visible=True)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def bar_chart(df,title):
    # df_plot =pd.melt(df, id_vars=[arrival_date], value_vars=['modal_price'])
    fig = px.bar(df, x='market', y='modal_price',title=title)
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@app.route("/forecast" , methods = ['POST', 'GET'])
def forecast():
    if request.method == 'POST':
        state = request.form.get('state')
        district =  request.form.get('district')
        market = request.form.get('market')
        commodity = request.form.get('commodity')
        variety = request.form.get('variety')
        end_date = request.form.get('date-1')
        end_date=pd.to_datetime(end_date)
        days=datetime.timedelta(365)
        start_date= end_date-days
        start_date=start_date.strftime('%Y-%m-%d')

        # calling Data
        params= {
            'state': state,
            'district': district,
            'market': market,
            'commodity': commodity,
            'variety' : variety,
            'start_date': start_date,
            'end_date': end_date,

        }
        
        query1 = """SELECT * FROM prices WHERE state= {{ state }} and district = {{ district }}  and commodity = {{ commodity }} and variety = {{ variety }} and arrival_date BETWEEN {{ start_date}} and {{end_date}} ORDER BY arrival_date ASC"""
        j = JinjaSql(param_style='pyformat')
        query1, bind_params1 = j.prepare_query(query1, params)
        df3=pd.read_csv('static/csv/kollam2011-21.csv')
        df4=df3.rename(columns={'arrival_date':'ds','modal_price':'y'})
        df= pd.read_sql_query(query1,con=con, params= bind_params1)
        df1=df[['arrival_date','modal_price']]
        #print(df1)
        df2=df1.rename(columns={'arrival_date':'ds','modal_price':'y'})
        df2=df2.interpolate(method='linear',limit_direction='both')
        #print(df2)
        model=Prophet()
        model.fit(df2)
        future=model.make_future_dataframe(periods=365)
        prediction=model.predict(future)
        prediction=prediction[['ds','yhat']]
        prediction=prediction[prediction['ds']>end_date]
        prediction=prediction.rename(columns={'ds':'arrival_date','yhat':'modal_price'})
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df2['ds'],y=df2['y'],mode='lines',name='historical data'))
        fig.add_trace(go.Scatter(x=prediction['arrival_date'],y=prediction['modal_price'],mode='lines',name='prediction'))
        fig.update_layout(title_text='<b>'+commodity+'<b> ',
                  title_x=0.5,
                  autosize=False,
                  width= 900,
                  height= 800)
        fig.update_xaxes(rangeslider_visible=True)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        #return graphJSON
        #graphJSON = line_chart(df2,commodity)
        #graphJSON = line_chart(prediction,commodity)

        try:
            return render_template('forecast.html',price = graphJSON, line = graphJSON)
        except:
                return redirect(url_for('submain'))
        





@app.route("/graphs" , methods = ['POST', 'GET'])
def graphs():
    if request.method == 'POST' :
        state = request.form.get('state')
        district =  request.form.get('district')
        market = request.form.get('market')
        commodity = request.form.get('commodity')
        variety = request.form.get('variety')
        start_date = request.form.get('date')
        end_date= request.form.get('date-1')
        


        # calling Data
        params= {
            'state': state,
            'district': district,
            'market': market,
            'commodity': commodity,
            'variety' : variety,
            'start_date': start_date,
            'end_date': end_date,

        }
        query = """SELECT * FROM prices WHERE state= {{ state }} and district = {{ district }}  and commodity = {{ commodity }} and variety = {{ variety }} and arrival_date = {{end_date}} ORDER BY arrival_date ASC"""
        query1 = """SELECT * FROM prices WHERE state= {{ state }} and district = {{ district }}  and commodity = {{ commodity }} and variety = {{ variety }} and arrival_date BETWEEN {{ start_date}} and {{end_date}} ORDER BY arrival_date ASC"""
        j = JinjaSql(param_style='pyformat')
        query, bind_params = j.prepare_query(query, params)
        query1, bind_params1 = j.prepare_query(query1, params)
        df = pd.read_sql_query(query,con=con, params= bind_params)
        df1= pd.read_sql_query(query1,con=con, params= bind_params1)
        
        print(df1)
    
    # Ploting graphs
        priceJSON= bar_chart(df,commodity)
        lineJSON= line_chart(df1,commodity)
    try:
        return render_template('graphs.html',price = priceJSON,  line=lineJSON)
    except:
        return redirect(url_for('main'))


@app.route('/render', methods = ['POST' , 'GET'])
def render():
    if request.method == 'POST':
        start_date = request.form.get("date")
        end_date = request.form.get("date-1")
        results = []
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
        result = cur.execute("SELECT arrival_date,state, district, market, commodity, variety,modal_price FROM prices Where arrival_date BETWEEN %s and %s", [start_date,end_date])
        commodity_value = cur.fetchall() 
        
        for row in commodity_value:
            results.append(dict(row))
        
        # results = pd.DataFrame(commodity_value, columns=column_names)
                
     
        fieldnames = [key for key in results[0].keys()]

        return render_template('index.html', results=results, fieldnames=fieldnames, len=len)


if __name__ == '__main__':
    app.run(debug=True)
# if _name_ == '_main_':
#     from werkzeug.serving import run_simple
#     run_simple('localhost', 9000, app)