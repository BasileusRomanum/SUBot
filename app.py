# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

modelsShowup = pd.read_csv(r"C:\VirtualPython\SUBot\dane.csv", sep=";", index_col=0)
modelsList = list(modelsShowup.index)[2:]
modelsShowup = modelsShowup.transpose()
#Po odczycie dataframe z pliku tworzymy nowy index. Klasyczny. 0,1,2...
#Ale najpierw klonujemy aktualny index, tworzymy potem nową kolumnę 0,1,2 itp i
# to ją robimy indexem. :)
modelsShowup.insert(0, 'Date', modelsShowup.index)
modelsShowup.insert(0, 'index', range(len(modelsShowup)))
modelsShowup.set_index('index', inplace=True)


def ModelsPlot(modelName='Oglądających'):
    return px.line(modelsShowup[modelName],
                    title=" ".join(modelName),
                    x=modelsShowup['Date'],
                    y=modelsShowup[modelName]
                    )

app.layout = html.Div(children=[
    html.H1(children='Hella hehe'),

    dcc.Dropdown(
        id="Nick modelki",
        options=[{'label':x, 'value':x} for x in list(modelsShowup.transpose().index)[1:]],
        value=['Oglądających'],
        multi=True
    ),
    html.Div(id="dd-output-container"),
    dcc.Graph(
        id='basic-graph',
        figure=ModelsPlot()
    )

])

@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('Nick modelki', 'value')])
def update_output(value):
    def average(modelka):
        tmpSeriesModel = modelsShowup[modelka].copy()
        suma, enum = 0, 0
        for x in range(len(tmpSeriesModel)):
            suma = int(tmpSeriesModel[x]) + suma
            enum = enum + (1 if int(tmpSeriesModel[x]) != 0 else 0)
        return round(suma/enum)
    result = ", ".join([f'{x} średnia: {average(x)}' for x in value])
    return f'Wybrano {result}'

@app.callback(
    dash.dependencies.Output('Nick modelki', 'options'),
    [dash.dependencies.Input('Nick modelki', 'value')])
def update_dropdown(value='Liczba_widzow_ogolem'):
    modelsShowup = pd.read_csv(r"C:\VirtualPython\SUBot\dane.csv", sep=";", index_col=0).transpose()
    return [{'label':x, 'value':x} for x in list(modelsShowup.transpose().index)[1:]]

@app.callback(
    dash.dependencies.Output('basic-graph', 'figure'),
    [dash.dependencies.Input('Nick modelki', 'value')])
def update_graph(value):
    modelsShowup = pd.read_csv(r"C:\VirtualPython\SUBot\dane.csv", sep=";", index_col=0).transpose()
    modelsShowup.insert(0, 'Date', modelsShowup.index)
    modelsShowup.insert(0, 'index', range(len(modelsShowup)))
    modelsShowup.set_index('index', inplace=True)
    return px.line({x : {modelsShowup['Date'][y] : modelsShowup[x][y] for y in range(len(modelsShowup))} for x in value},
                    title=" ".join(value)
                    )




if __name__ == '__main__':
    app.run_server(debug=True)
