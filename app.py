import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import pandas as pd
from graphs import *
import dill

# Read multiconutries data
heatdays = pd.read_csv('europe_heatdays.csv')
heatdays = subset_helper(heatdays).subset()
visuals = overall_plots(heatdays)

# Read model
with open('gradientboosting.pkl', 'rb') as model_file:
    model = dill.load(model_file)


app = dash.Dash(__name__,title = "Visualisations", 
                external_stylesheets = [dbc.themes.JOURNAL])
server = app.server
# Adding dropdown box for selecting countries
dropdown = dcc.Dropdown(id = "id_country",
                        options = [
                            {"label": 'Belgium', 'value': 'Belgium'},
                            {"label": 'France', 'value': 'France'},
                            {"label": 'Greece', 'value': 'Greece'},
                            {"label": 'Romania', 'value': 'Romania'},
                            {"label": 'Russia', 'value': 'Russia'},
                            {"label": 'United Kingdom', 'value': 'UK'},
                        ],
                        value = 'Belgium')

# Slider for meteorological variables, avoid extrapolation
data_pred = {'TEMP_MEAN': 21, 'TEMP_RNG': 15, 'WS50M_MEAN': 5.76, 'PRECTOT_MEAN': 2.18, 
             'RH2M_MEAN': 76.51, 'HEAT_DAYS': 2, 'YEAR': 2018, 'MONTH': 8, 'REGION': 4000,
             'COD': 'Diseases of the circulatory system'}

slider1 = dcc.Slider(id = 'id_temp_mean',
    min = 14,
    max = 24,
    value = 21,
    step = 0.01,
    marks = {i: {'label': '{}°C'.format(i)} for i in range(14, 25)},
    updatemode = 'drag')

slider2 = dcc.Slider(id = 'id_temp_rng',
    min = 11,
    max = 16,
    value = 15,
    step = 0.01,
    marks = {i: {'label': '{}°C'.format(i)} for i in range(11, 17)})

slider3 = dcc.Slider(id = 'id_ws50m_mean',
    min = 5.00,
    max = 6.50 + 1 / 100**5, # Bug in dash applications for floating dict
    value = 5.76,
    step = 0.01,
    marks = {i / 100 + 1 / 100**5: {'label': '{}m/s'.format(i / 100)} for i in range(500, 660, 25)})

slider4 = dcc.Slider(id = 'id_prectot_mean',
    min = 0.5,
    max = 5.0 + 1 / 10**5,
    value = 2.18,
    step = 0.01,
    marks = {i / 10 + 1 / 10**5: {'label': '{}mm'.format(i / 10)} for i in range(5, 51, 5)})

slider5 = dcc.Slider(id = 'id_rh2m_mean',
    min = 70,
    max = 85,
    value = 76.51,
    step = 0.01,
    marks = {i: {'label': '{}%'.format(i)} for i in range(70, 86, 3)})

slider6 = dcc.Slider(id = 'id_heat_days',
    min = 0,
    max = 9,
    value = 2,
    step = 1,
    marks = {i: {'label': '{}'.format(i)} for i in range(0, 10, 1)})

# Dropdown for demographic variables
dropdown3 = dcc.Dropdown(id = "id_region",
                        options = [
                            {"label": 'Antwerp', 'value': 2000},
                            {"label": 'Dinant', 'value': 3000},
                            {"label": 'Brussels', 'value': 4000}
                        ],
                        value = 4000)

dropdown4 = dcc.Dropdown(id = "id_cod",
                        options = [
                            {"label": 'Diseases of the circulatory system', 'value': 'Diseases of the circulatory system'},
                            {"label": 'Diseases of the respiratory system', 'value': 'Diseases of the respiratory system'},
                            {"label": 'Diseases of the skin and subcutaneous tissue', 'value': 'Diseases of the skin and subcutaneous tissue'}
                        ],
                        value = 'Diseases of the circulatory system')

# Cross-countries visualization objects
country_visuals = country_plots(heatdays)

# Model prediction objects
prediction_visuals = prediction_table(model)


# app layout
app.layout = dbc.Container([
        html.Div(children = [html.H1(children = 'Visualisations for European Countries',
                                   style = {'textAlign': 'center'}),
                           html.H2(children = 'Overall Visualisations',
                                   style = {'textAlign': 'center'})],
                 style = {'color': 'black'}),
        html.Hr(),
        html.Div([html.P('Worldwide, it is highly acknowledged that the climate is warming.'
                         'According to the international disasters database (EM-DAT), there have been 25 '
                         'events of heatwaves from 2018 to 2020 in Europe which were considered as natural '
                         'disasters and 5 of them were from Belgium. Based on the data from EM-DAT, we selected 7 countries '
                         'in Europe which were affected the most by heat waves namely Belgium, France, Greece, '
                         'Romania, Russia, Spain and United Kingdom (U.K.).')]),
        dbc.Row([
            dbc.Col(dcc.Graph(id = "id_graph", figure = visuals.boxplot()), md = 20),
            dbc.Col(dcc.Graph(id = "id_graph3", figure = visuals.lineplot()), md = 20)
            ], justify = "center"),
        dbc.Row([
            dbc.Col(dcc.Graph(id = "id_graph2", figure = visuals.scatterplot()), width = 8)
        ], justify = 'center'),
        dbc.Row([
            dbc.Col(html.H1(children = "Country Level Visualisations",
                            style = {'textAlign': 'center'}))
            ],
            align = "center"),
        dbc.Row([
            dbc.Col(html.Hr())
            ]),
        dbc.Row([
            dbc.Col(dropdown, md = 4)],
            justify = "center"),
        dbc.Row([
            dbc.Col(dcc.Graph(id = "id_graph4", figure = country_visuals.heatmap('Belgium'))),
            dbc.Col(dcc.Graph(id = "id_graph5", figure = country_visuals.lineplot('Belgium')))
        ]),
        dbc.Row([
            dbc.Col(html.H1(children = "Mortality model",
                            style = {'textAlign': 'center'}))
            ],
            align = "center"),
        html.Hr(),
        dbc.Row([
            dbc.Col(html.P('The monthly average of maximum temperature'), md = 4),
            dbc.Col(slider1, md = 4)],
            justify = "center"),
        dbc.Row([
            dbc.Col(html.P('The monthly average of temperature range'), md = 4),
            dbc.Col(slider2, md = 4)],
            justify = "center"),     
        dbc.Row([
            dbc.Col(html.P('The monthly average of wind speed'), md = 4),
            dbc.Col(slider3, md = 4)],
            justify = "center"),
        dbc.Row([
            dbc.Col(html.P('The monthly average of precipitation'), md = 4),
            dbc.Col(slider4, md = 4)],
            justify = "center"),
        dbc.Row([
            dbc.Col(html.P('The monthly average of relative humidity'), md = 4),
            dbc.Col(slider5, md = 4)],
            justify = "center"),
        dbc.Row([
            dbc.Col(html.P('The number of heat days in the month'), md = 4),
            dbc.Col(slider6, md = 4)],
            justify = "center"),
        dbc.Row([
            dbc.Col(html.P('Region'), md = 4),
            dbc.Col(dropdown3, md = 4)],
            justify = "center"),
        dbc.Row([
            dbc.Col(html.P('Cause of death'), md = 4),
            dbc.Col(dropdown4, md = 4)],
            justify = "center"),
        dbc.Row([
            dbc.Col(dcc.Graph(id = "id_graph6", figure = prediction_visuals.draw_table(data_pred)))
            ])
        ],
        fluid = True,)

@app.callback(
    Output('id_graph4', 'figure'),
    Output('id_graph5', 'figure'),
    [Input('id_country', 'value')]
)
def update_chart(id_country):
    fig1 = country_visuals.heatmap(id_country)
    fig2 = country_visuals.lineplot(id_country)
    
    return fig1, fig2

@app.callback(
    Output('id_graph6', 'figure'),
    [Input('id_temp_mean', 'value'),
     Input('id_temp_rng', 'value'),
     Input('id_ws50m_mean', 'value'),
     Input('id_prectot_mean', 'value'),
     Input('id_rh2m_mean', 'value'),
     Input('id_heat_days', 'value'),
     Input('id_region', 'value'),
     Input('id_cod', 'value')]
)
def update_predict( id_temp_mean, id_temp_rng, id_ws50m_mean, id_prectot_mean, 
                 id_rh2m_mean, id_heat_days, id_region, id_cod):
    data_pred = {'TEMP_MEAN': id_temp_mean, 'TEMP_RNG': id_temp_rng, 'WS50M_MEAN': id_ws50m_mean, 
                 'PRECTOT_MEAN': id_prectot_mean, 'RH2M_MEAN': id_rh2m_mean, 'HEAT_DAYS': id_heat_days, 
                 'YEAR': 2018, 'MONTH': 8, 'REGION': id_region, 'COD': id_cod}
    
    fig3 = prediction_visuals.draw_table(data_pred)
    return fig3

if __name__ == '__main__':
    app.run_server(debug = True)