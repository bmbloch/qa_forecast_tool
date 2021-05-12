import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from datetime import datetime
import math
import numpy as np
import pandas as pd

# Layout for login page
def get_login_layout():
    currmon = datetime.now().month
    curryr = datetime.now().year
    if currmon in [11,12,1]:
        currqtr = 4
    elif currmon in [2,3,4]:
        currqtr = 1
    elif currmon in [5,6,7]:
        currqtr = 2
    elif currmon in [8,9,10]:
        currqtr = 3
    if currmon == 1:
        curryr = curryr - 1

    return html.Div([
            dcc.Location(id='login-url',pathname='/login',refresh=False),
            dbc.Container([
                dbc.Row(
                    dbc.Col(
                        dbc.Card([
                            html.H4('Login',className='card-title'),
                            dbc.Input(id='login-username',placeholder='User'),
                            dbc.Input(id='login-password',placeholder='Password',type='password'),
                            html.Div([
                                dcc.Dropdown(id='sector_input', 
                                            options=[{'value': 'apt', 'label': 'Apartment'}, {'value': 'ind', 'label': 'Industrial'},
                                                    {'value': 'off', 'label': 'Office'}, {'value': 'ret', 'label': 'Retail'}],
                                            multi=False,
                                            value=None,
                                            placeholder="Sector to load:"
                                            ),
                                        ], style={'display': 'block', 'padding-top': '15px'}),
                            html.Br(),
                            html.Div([
                                html.Div([
                                    html.P(id='Forecast Year Header', 
                                        style={'color': 'black', 'fontSize': 12},
                                        children=["Forecast Year"]
                                        )
                                    ], style={'padding-left': '40px', 'display': 'inline-block'}),
                                html.Div([
                                    html.P(id='Forecast Quarter Header', 
                                        style={'color': 'black', 'fontSize': 12},
                                        children=["Forecast Quarter"]
                                        )
                                    ], style={'padding-left': '85px', 'display': 'inline-block'}),
                                ], style={'display': 'block'}),
                            html.Div([
                                html.Div([
                                    dcc.Dropdown(id='login-curryr', 
                                                options=[{'value': datetime.now().year - 1, 'label': datetime.now().year - 1}, 
                                                            {'value': datetime.now().year, 'label': datetime.now().year},
                                                            {'value': datetime.now().year + 1, 'label': datetime.now().year + 1}],
                                                multi=False,
                                                value=curryr,
                                                ),
                                                    ], style={'width': '30%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.Dropdown(id='login-currqtr', 
                                                options=[{'value': 1, 'label': 1}, 
                                                            {'value': 2, 'label': 2},
                                                            {'value': 3, 'label': 3},
                                                            {'value': 4, 'label': 4},
                                                        ],
                                                multi=False,
                                                value=currqtr,
                                                ),
                                                    ], style={'width': '30%', 'display': 'inline-block', 'padding-left': '20px'}),
                                html.Div([
                                    dcc.Checklist(
                                        id='rol_close',
                                        value=["Y"],
                                        options=[
                                            {'label': ' Use ROL Close', 'value': 'Y'},
                                            ],
                                        labelStyle={'display': 'block', 'margin': '0 10px 0 10px'}), 
                                    ],  style={'padding-left': '10px', 'width': '40%', 'display': 'inline-block', 'vertical-align': 'top'}),
                            ], style={'display': 'block'}),
                                
                            html.Br(),
                            dbc.Button('Submit',id='login-button',color='success',block=True),
                            html.Br(),
                            html.Div(id='login-alert'),
                        ],
                        body=True
                    ),
                    width=6
                ),
                justify='center'
                    ),
                ]),
            ])