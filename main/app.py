import dash
import dash_bootstrap_components as dbc
import pandas as pd
import utils 
import os
from dash_bootstrap_templates import load_figure_template
import warnings
warnings.filterwarnings("ignore")

load_figure_template("cyborg")
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY, dbc.themes.GRID])
server = app.server
app.layout 

