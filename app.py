# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
modelsShowup = pd.read_csv(r"C:\VirtualPython\SUBot\dane.csv", sep=";", index_col=0)
modelsList = list(modelsShowup.index)[2:]
modelsShowup = modelsShowup.transpose()
hellahella = modelsShowup['hellahella']

def ModelsPlot(modelName="hellahella"):
    return px.line(modelsShowup[modelName],
                    x=modelsShowup.index,
                    y=modelsShowup[modelName],
                    title=modelName,
                    )

app.layout = html.Div(children=[
    html.H1(children='Hella hehe'),

    dcc.Dropdown(
        id="Nick modelki",
        options=[{'label':x, 'value':x} for x in list(modelsShowup.transpose().index)[1:]],
        value='Liczba_widzow_ogolem'
    ),
    html.Div(id="dd-output-container"),
    dcc.Graph(
        id='example-graph',
        figure=ModelsPlot()
    )

])

@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('Nick modelki', 'value')])
def update_output(value):
    return 'Wybrano "{}"'.format(value)

@app.callback(
    dash.dependencies.Output('Nick modelki', 'options'),
    [dash.dependencies.Input('Nick modelki', 'value')])
def update_dropdown(value='Liczba_widzow_ogolem'):
    modelsShowup = pd.read_csv(r"C:\VirtualPython\SUBot\dane.csv", sep=";", index_col=0).transpose()
    return [{'label':x, 'value':x} for x in list(modelsShowup.transpose().index)[1:]]

@app.callback(
    dash.dependencies.Output('example-graph', 'figure'),
    [dash.dependencies.Input('Nick modelki', 'value')])
def update_graph(value):
    modelsShowup = pd.read_csv(r"C:\VirtualPython\SUBot\dane.csv", sep=";", index_col=0).transpose()
    return px.line(modelsShowup[value],
                    x=modelsShowup.index,
                    y=modelsShowup[value],
                    title=value if value != "Liczba_widzow_ogolem" else "Liczba widzów ogółem",
                    )




if __name__ == '__main__':
    app.run_server(debug=True)
