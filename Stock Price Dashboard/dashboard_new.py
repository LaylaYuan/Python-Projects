# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 23:29:41 2018

@author: mdjia
"""
import sqlite3
import pandas as pd
import pandas.io as sql
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime 
import time
import colorlover as cl
#from app import app, indicator, millify, df_to_table, sf_manager

from dash.dependencies import Input, Output, Event
colorscale = cl.scales['9']['qual']['Paired']
colors = {
    'background': '#5c5f66',
    'text': '#5775b2'
}
def indicator(size, text, id_value):
    return html.Div(
        [
            
            html.P(
                text,
                className="twelve columns indicator_text"
            ),
            html.P(
                id = id_value,
                className="indicator_value"
            ),
        ],style={'fontSize':size},
        className="four columns indicator",
        
    )

conn = sqlite3.connect('stock.db')
#c = conn.cursor()

df = pd.read_sql_query("SELECT * from historicaldata",conn)
df=df[df['year']==18]
df_d= pd.read_sql_query("SELECT * from dailydata",conn)
#print(df_d)
#print(df['month'].unique())

conn.commit()

conn = sqlite3.connect('new_stock3.db')
c = conn.cursor()
#c.execute("select name from sqlite_master where type='table' order by name")
#c.execute("SELECT * FROM tb_microsoft")
#print(*c.fetchall(), sep='\n') 

df_mic = pd.read_sql_query("SELECT * from MSFT",conn)
df_tsl = pd.read_sql_query("SELECT * from TSLA",conn)
df_goo = pd.read_sql_query("SELECT * from GOOG",conn)
#df_rem = df_goo = pd.read_sql_query("SELECT * from recommendation",conn)
#print (df)
#print(df_d)
#print(df['month'].unique())

conn.commit()
conn = sqlite3.connect('recommend.db')
c = conn.cursor()
#c.execute("select name from sqlite_master where type='table' order by name")
#c.execute("SELECT * FROM tb_microsoft")
#print(*c.fetchall(), sep='\n') 

df_rem = pd.read_sql_query("SELECT * from scoretable",conn)

#df_rem = df_goo = pd.read_sql_query("SELECT * from recommendation",conn)
#print (df)
#print(df_d)
#print(df['month'].unique())

conn.commit()
available_indicators = df['stock'].unique()
available_day = df_d['day'].unique()
#print(df_d['day'].unique())
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
            html.H1(children='Project A'),
            html.Div(children='''
        Dash: The stock price of Microsoft, TSLA, and Google''')
            ],style={'color': colors['text']}),
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='GOOG'
            )


        ],
        style={'width': '49%', 'display': 'inline-block'}),
        html.Div([

            dcc.Dropdown(
                id='day-of-stock',
                options=[{'label': i, 'value': i} for i in available_day],
                value=df_d['day'].max()
            )

        ],
        style={'width': '49%', 'float': 'right', 'display': 'inline-block'})    
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),
    html.Div([html.H3(children='The historical price and Daily Price of target stock')],
    style={'textAlign': 'center','color': colors['text']}),
    #indicators row
    html.Div(
        [
            indicator(
                36,
                "Current Price",
                "left_opportunities_indicator",
            ),
            indicator(
                36,
                "Change",
                "middle_opportunities_indicator",
            ),

        ],
        style={'textAlign': 'center','color': '#4b4d51'},
        className="row"
    ),
     
#    html.Div(id='graphs'),
    html.Div([
        dcc.Graph(id='y-time-series'
#            id='crossfilter-indicator-scatter',
#            hoverData={'points': [{'customdata': 'Japan'}]}
        )
    ], style={'display': 'inline-block', 'width': '49%','height':'100%'}),
        
    html.Div([
        dcc.Graph(id='x-time-series'),
#        dcc.Graph(id='y-time-series'),
    ], style={'display': 'inline-block', 'width': '49%', 'height':'100%'}),


    html.Div(dcc.RangeSlider(
        id='crossfilter-month--slider',
        min=df['month'].min(),
        max=df['month'].max(),
        value=[df['month'].min(),df['month'].max()],
        step=None,
        marks={str(month): str(month) for month in df['month'].unique()}
    ), style={'width': '45%', 'padding': '0px 20px 20px 20px'}),
    html.Div([html.H3(children='The NLP analysis of relative news')],
    style={'textAlign': 'center','color': colors['text']}),
    html.Div([
        dcc.Graph(id='NLP_bar'
#            id='crossfilter-indicator-scatter',
#            hoverData={'points': [{'customdata': 'Japan'}]}
        )
    ], style={'display': 'inline-block', 'width': '55%','height':'100%'}),
    html.Div([
        dcc.Graph(id='pie_chart'),
#        dcc.Graph(id='y-time-series'),

    ], style={'display': 'inline-block', 'width': '43%', 'height':'100%'}),
#    html.Div(id='intermediate-value', style={'display': 'none'})
    html.Div([html.H3(children='The score of Risk Potential')],    
              style={'textAlign': 'center','color': colors['text']}),

    html.Div(
    [
     indicator(
             40,
             "Risk Potential",
             "recommend_score",
        ),

    ],    
        style={'textAlign': 'center','color':'#4b4d51'},
        className="row",
    ),
    dcc.Interval(
        id='graph-update',
        interval=120*1000
    ),
    dcc.Interval(
        id='price-update',
        interval=3*1000
    ),

    dcc.Interval(
        id='increase-update',
        interval=3*1000
    ),
    
])
def create_time_series(dff, title):
    return {
        'data': [go.Candlestick(          
            x=dff['date_new'],
            open= dff['open'],
            high= dff['high'],
            low= dff['low'],
            close= dff['close']
        )],
        'layout': {
            'height': 400,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
#            'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
            'xaxis': {'showgrid': False}
        }
    }


def create_time_series_d(dff,color_value):
    data=[go.Scatter(
            x=dff['hour'],
            y=dff['close'],
            mode='lines',
            fill='tonexty',
            line=dict(color= color_value)
                
        )]
    layout=go.Layout(xaxis = dict(range = [dff['hour'].min(), dff['hour'].max()]),
                     yaxis = dict(range = [dff['close'].min(), dff['close'].max()]),
#                     title = soup.title.text,
                     height=400)
    return {
        'data': data,
        'layout': layout

        }
def create_bar_chart(dff):
    trace1 = go.Bar(
    y=dff['date'],
    x=dff['positive_counts'],
    name='Positive',
    orientation = 'h',
    marker = dict(
        color = 'rgba(74,149,109,0.9)',
        line = dict(
            color = 'rgba(74,149,109,0.9)',
            width = 1)
    )
)
    trace2 = go.Bar(
        y=dff['date'],
        x=dff['negative_counts'],
        name='Negative',
        orientation = 'h',
        marker = dict(
            color = 'rgba(252,77,66,0.9)',
            line = dict(
                color = 'rgba(252,77,66,0.9)',
                width = 1)
        )
    )
    trace3 = go.Bar(
        y=dff['date'],
        x=dff['neural_counts'],
        name='Neural',
        orientation = 'h',
        marker = dict(
            color = 'rgb(244, 229, 66,0.9)',
            line = dict(
                color = 'rgb(244, 229, 66,0.9)',
                width = 1)
        )
    )
    
    data = [trace1, trace2,trace3]
    layout = go.Layout(
        barmode='stack',
        height=600,
    )

    return {"data": data, "layout": layout}
def create_pie_chart(dff):
    labels = ['Positive','Negative','Neural']
    values = [sum(dff['positive_counts']),sum(dff['negative_counts']),sum(dff['neural_counts'])]
    colors = ['rgba(74,149,109,0.9)', 'rgba(252,77,66,0.9)', 'rgb(244, 229, 66,0.9)']
    trace = go.Pie(labels=labels, values=values,marker=dict(colors=colors))
    
    data = [trace]


    return {"data": data}


@app.callback(
    dash.dependencies.Output('pie_chart', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value')])
def update_pie_chart(yaxis_column_name):
#    dff_mic=df_mic[df_mic['stock']==yaxis_column_name]
    if yaxis_column_name=='TSLA':
        df_p=df_tsl
    elif yaxis_column_name=='GOOG':
        df_p=df_goo   
    elif yaxis_column_name=='MSFT':
        df_p=df_mic   
#    dff = df[df['month'] == month_value]
#    dff_d = dff_d[dff_d['day'] == day_value]
    return create_pie_chart(df_p)
@app.callback(
    dash.dependencies.Output('NLP_bar', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value')])
def update_bar_chart(yaxis_column_name):
    if yaxis_column_name=='TSLA':
        df_b=df_tsl
    elif yaxis_column_name=='GOOG':
        df_b=df_goo   
    elif yaxis_column_name=='MSFT':
        df_b=df_mic   
#    dff_mic=df_mic[df_mic['stock']==yaxis_column_name]
    
#    dff = df[df['month'] == month_value]
#    dff_d = dff_d[dff_d['day'] == day_value]
    return create_bar_chart(df_b)
@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-month--slider', 'value')])

def update_x_timeseries(yaxis_column_name,month_value):
    a=month_value[0]
    b=month_value[1]
    dff=df[df['stock']==yaxis_column_name]
    dff=dff[(dff['month']>=a)&(dff['month']<=b)]
    dff=dff.sort_values(by='date_new',ascending= True)
#    dff=dff[dff['year']+2000==year_value]    
#    dff = df[df['month'] == month_value]
#    dff = dff[dff['Indicator Name'] == yaxis_column_name]
    return create_time_series(dff, yaxis_column_name)

@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('day-of-stock', 'value')],
     events=[Event('graph-update', 'interval')])
def update_y_timeseries(yaxis_column_name,day_value):
    dff_d=df_d[df_d['stock']==yaxis_column_name]
    
#    dff = df[df['month'] == month_value]
    dff_d = dff_d[dff_d['day'] == day_value]
#    color_value=get_color(dff_d)
    if dff_d.iloc[len(dff_d)-1,3]>dff_d.iloc[0,2]:
        color_value='rgb(74,149,109)'
    else:
        color_value='rgb(252,77,66)'
    return create_time_series_d(dff_d, color_value)

@app.callback(
    Output("left_opportunities_indicator", "children"),
    [Input("crossfilter-xaxis-column", "value")],
     events=[Event('price-update', 'interval')])
def left_opportunities_indicator_callback(xaxis):
#    print(xaxis)
#    url='https://finance.yahoo.com/quote/BTC-USD?p=BTC-USD'
    url='https://finance.yahoo.com/quote/%s?p=%s&.tsrc=fin-srch'%(xaxis,xaxis)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    spans=soup.find_all('span', {'class' :"Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)"})
    current_price = float([span.get_text() for span in spans][0].replace(',', ''))
#    print(current_price)
#    current_time = datetime.datetime.fromtimestamp(int(time.time())).strftime('%H:%M%p')
    return current_price
@app.callback(
    Output("middle_opportunities_indicator", "children"),
    [Input("crossfilter-xaxis-column", "value")],
     events=[Event('increase-update', 'interval')])
def middle_opportunities_indicator_callback(xaxis):
#    print(xaxis)
#    url='https://finance.yahoo.com/quote/BTC-USD?p=BTC-USD'
    url='https://finance.yahoo.com/quote/%s?p=%s&.tsrc=fin-srch'%(xaxis,xaxis)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    spans=soup.find_all('span', {'class' :"Trsdu(0.3s) Fw(500) Fz(14px) C($dataRed)"})
#    increase_precent = [span.get_text() for span in spans][0].replace(',', '')
    if spans==[]:
        spans=soup.find_all('span', {'class' :"Trsdu(0.3s) Fw(500) Fz(14px) C($dataGreen)"})
    increase_precent = [span.get_text() for span in spans][0].replace(',', '')
#    print(current_price)
#    current_time = datetime.datetime.fromtimestamp(int(time.time())).strftime('%H:%M%p')
    return increase_precent

@app.callback(
    Output("recommend_score", "children"),
    [Input("crossfilter-xaxis-column", "value"),
     Input('day-of-stock', 'value')],
     events=[Event('increase-update', 'interval')])
def recommend_indicator_callback(xaxis,time):
#    print(xaxis)
#    url='https://finance.yahoo.com/quote/BTC-USD?p=BTC-USD'
    dff_rem=df_rem[df_rem['stock']==xaxis]
    dff_rem=dff_rem[dff_rem['date']==time]
    
#    print(current_price)
#    current_time = datetime.datetime.fromtimestamp(int(time.time())).strftime('%H:%M%p')
    return dff_rem['score']



if __name__ == '__main__':
    app.run_server(debug=True)