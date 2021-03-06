#!usr/bin/env python3
import creds
import dash
import dash_core_components as dcc
import dash_html_components as html
import colorlover as cl
import datetime as dt
import flask
import os
import pandas as pd
from pandas_datareader.data import DataReader
import time
import plotly.graph_objs as go
import numpy as np
from sklearn.preprocessing import MinMaxScaler

import plotly
plotly.tools.set_credentials_file(username=creds.username, api_key=creds.api_key)


app = dash.Dash('stock-ticker_one')
server = app.server

app.scripts.config.serve_locally = False

colorscale = cl.scales['9']['qual']['Paired']

df_symbol = pd.read_csv('stocklisttwo.csv')

df_symbol_two = pd.read_csv('stocklisttwo.csv')

app.layout = html.Div([
    html.Div([
        html.H2('Anacott Steel',
                style={'display': 'inline',
                       'float': 'left',
                       'font-size': '2.65em',
                       'margin-left': '7px',
                       'font-weight': 'bolder',
                       'font-family': 'Product Sans',
                       'color': "rgba(117, 117, 117, 0.95)",
                       'margin-top': '20px',
                       'margin-bottom': '0'
                       }),
        html.Div([
            dcc.DatePickerRange(
                id='date-range',
                start_date=dt.date(2017, 1, 1),
                end_date=dt.date.today(),
            ),
        ], style={'clear': 'left', 'padding-top': '10px'},
        ),

        html.Img(src="https://img.etsystatic.com/il/816ca7/1430618519/il_570xN.1430618519_mwz6.jpg?version=1",
                 style={
                     'height': '200px',
                     'float': 'right'
                 },
                 ),

        html.H4('Choose dates from the calandar to start off your chart analyzing'),
        html.H4('''Choose your "comparison stock"'''),
        html.H4('Then chose another stock/stocks to compare with your first pick.  The stock prices will be normalized on a 0-1 scale so the graphs will be a lot easier to analyze'),
        html.H4('*You can always hover over lines to show the actual stock prices'),
        html.H4('*Click and drag over graph to zoom in; double click to zoom out'),

    ]),

    html.H2('Pick your comparison'),

    dcc.Dropdown(
        id='stock-ticker-input',
        options=[{'label': s[0], 'value': str(s[1])}
                 for s in zip(df_symbol.Company, df_symbol.Symbol)],
        multi=True
    ),


    html.H2('Pick your other stock/stocks'),



    dcc.Dropdown(
        id='stock-ticker-input-two',
        options=[{'label': s[0], 'value': str(s[1])}
                 for s in zip(df_symbol_two.Company, df_symbol_two.Symbol)],
        multi=True
    ),
    html.Div(id='graphs')
], className="container")


@app.callback(
    dash.dependencies.Output('graphs', 'children'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
     dash.dependencies.Input('stock-ticker-input-two', 'value'),
     dash.dependencies.Input('date-range', 'start_date'), dash.dependencies.Input('date-range', 'end_date')])
def update_graph(ticker_one, ticker_two, start_date, end_date):

    if not ticker_one or not ticker_two:
        return []

    graphs = []
    for i, ticker in enumerate(ticker_one):
        try:
            df = DataReader(str(ticker), 'quandl',
                            dt.datetime.strptime(start_date, '%Y-%m-%d'),
                            dt.datetime.strptime(end_date, '%Y-%m-%d'))
            series = df['Close']
            values = series.values
            values = values.reshape((len(values), 1))
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaler = scaler.fit(values)
            normalized = scaler.transform(values)

            h = []
            for i in range(len(values)):
                h.append(float(normalized[i]))
            df['Norm'] = h

        except:
            graphs.append(html.H3(
                'Data is not available for {}'.format(ticker),
                style={'marginTop': 20, 'marginBottom': 20}
            ))

    for i, ticker_two in enumerate(ticker_two):
        try:

            df_two = DataReader(str(ticker_two), 'quandl',
                                dt.datetime.strptime(start_date, '%Y-%m-%d'),
                                dt.datetime.strptime(end_date, '%Y-%m-%d'))
            series = df_two['Close']
            values = series.values
            values = values.reshape((len(values), 1))
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaler = scaler.fit(values)
            normalized = scaler.transform(values)

            g = []
            for i in range(len(values)):
                g.append(float(normalized[i]))
            df_two['Norm'] = g

        except:
            graphs.append(html.H3(
                'Data is not available for {}'.format(ticker_two),
                style={'marginTop': 20, 'marginBottom': 20}
            ))
            continue
        ticker = ticker[5:]
        line1 = {
            'x': df.index,
            'y': df['Norm'],
            'type': {'line': {'color': colorscale[0]}},
            'name': ticker,
            'legendgroup': ticker,
            'text': df['Close'],
            'hoverinfo': 'text'

        }
        ticker_two = ticker_two[5:]
        line2 = {
            'x': df_two.index,
            'y': df_two['Norm'],
            'type': 'line',
            'name': ticker_two,
            'legendgroup': ticker_two,
            'text': df_two['Close'],
            'hoverinfo': 'text'
        }

        graphs.append(dcc.Graph(
            id='{} vs + {}'.format(ticker_one, ticker_two),
            figure={
                'data': [line1, line2],
                'layout': go.Layout(
                    xaxis={'title': 'Date'},
                    yaxis={'title': 'Price'},
                    margin={'l': 60, 'b': 100, 't': 10, 'r': 40},
                    legend={'x': 0, 'y': 1},
                )
            }
        )
        )

    return graphs


external_css = ["https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/2cc54b8c03f4126569a3440aae611bbef1d7a5dd/stylesheet.css"]

for css in external_css:
    app.css.append_css({"external_url": css})


if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
