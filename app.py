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

modelsShowup = pd.read_json(r".\dane.json")
modelsShowup.fillna(0, inplace=True)
modelsShowup.sort_index(inplace=True,)
modelsList = list(modelsShowup.index)[2:]
#Po odczycie dataframe z pliku tworzymy nowy index. Klasyczny. 0,1,2...
#Ale najpierw klonujemy aktualny index, tworzymy potem nową kolumnę 0,1,2 itp i
# to ją robimy indexem. :)
def ModelsPlot(modelName='Ogladajacych'):
    return px.line(modelsShowup[modelName],
                    title=" ".join(modelName),
                    x=modelsShowup.index,
                    y=modelsShowup[modelName]
                    )

app.layout = html.Div(children=[
    html.H1(children='***** ***'),

    dcc.Dropdown(
        id="Nick modelki",
        options=[{'label':x, 'value':x} for x in list(modelsShowup.index)[1:]],
        value=['hellahella'],
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
            suma = suma + int(tmpSeriesModel[x])
            enum = enum + (1 if int(tmpSeriesModel[x]) != int(0) else 0)
        return round(suma/enum)
    result = ", ".join([f'{x} średnia: {average(x)}' for x in value])
    return f'Wybrano {result}'

@app.callback(
    dash.dependencies.Output('Nick modelki', 'options'),
    [dash.dependencies.Input('Nick modelki', 'value')])
def update_dropdown(value='Liczba_widzow_ogolem'):
    modelsShowup = pd.read_json(r".\dane.json")
    modelsShowup.fillna(0, inplace=True)
    modelsShowup.sort_index(inplace=True,)
    return [{'label':x, 'value':x} for x in list(modelsShowup.transpose().index)[1:]]

@app.callback(
    dash.dependencies.Output('basic-graph', 'figure'),
    [dash.dependencies.Input('Nick modelki', 'value')])
def update_graph(value):
    modelsShowup = pd.read_json(r".\dane.json")
    modelsShowup.fillna(0, inplace=True)
    modelsShowup.sort_index(inplace=True,)
    if len(value) > 0:
        return px.line({x : modelsShowup[x].fillna(0) for x in value},
                        title=" ".join(value)
                        )
    else:
        return px.line(modelsShowup['Ogladajacych'])



if __name__ == '__main__':
    app.run_server(debug=True)
