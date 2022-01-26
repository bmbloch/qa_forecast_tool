from functools import wraps
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask import session
import pandas as pd

users = {
            'bbloch': {'password': "test1", 'sectors': ["apt", "ind", "off", "ret"], 'write': 'yes'},
            'emingione': {'password': "test2", 'sectors': ["apt"], 'write': 'yes'},
            'rrosas': {'password': "test3", 'sectors': ["off"], 'write': 'yes'},
            'dcaputo': {'password': "test4", 'sectors': ["ret"], 'write': 'yes'},
            'dquan': {'password': "test5", 'sectors': ["apt", "ind", "off", "ret"], 'write': 'no'},
            'nmorton': {'password': "test6", 'sectors': ["apt", "ind", "off", "ret"], 'write': 'no'},
        }

# Function that returns True if the user and password input is a correct match, otherwise False
def authenticate_user(credentials):

    authed = (credentials['user'] in list(users.keys())) and (credentials['password'] == users[credentials['user']]['password']) and (credentials['sector'] in users[credentials['user']]['sectors'])
    
    if authed:
        write = users[credentials['user']]['write']
    else:
        write = False

    return authed, write

# Function that returns layout objects and checks if the user is logged in or not throughout the session. If not, returns an error with link to the login page.
def validate_login_session(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        if session.get('authed',None)==True:
            return f(*args,**kwargs)
        return html.Div(
            dbc.Row(
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H2('401 - Unauthorized',className='card-title'),
                                html.A(dcc.Link('Login',href='/login'))
                            ],
                            body=True
                        )
                    ],
                    width=5
                ),
                justify='center'
            )
        )
    return wrapper
