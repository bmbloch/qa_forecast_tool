import dash
import dash_bootstrap_components as dbc

forecast = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title='Forecast Review')

forecast.config.suppress_callback_exceptions = True

server = forecast.server
server.config['SECRET_KEY'] = 'hwyt1cubt!eswip7892'