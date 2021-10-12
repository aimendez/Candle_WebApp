import dash_core_components as dcc
from dash import html 
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output, State
from dash import no_update
import dash
import flask 

import plotly.graph_objs as go 
from plotly.subplots import make_subplots
import plotly.express as px

from talib import abstract

from app import app
import json
from datetime import datetime , date
from assets import pattern_list 
import pandas as pd
import numpy as np
import utils 
import os 


cwd = os.path.dirname(os.getcwd())
#=====================================================================================#
#=====================================================================================#
# NAV BAR


#=====================================================================================#
#=====================================================================================#
# COMPONENTS


#=====================================================================================#
#=====================================================================================#
# CALLBACKS 


@app.callback(
    [
    Output('symbol-page', 'children'),
    ],
    [
    Input('url', 'pathname'),
    ])
def callback_func(pathname):
	query_str =  flask.request.referrer.split('?')[-1] #value1=symbol&
	symbol =  query_str.split('&')[0]
	return [no_update]


#=====================================================================================#
#=====================================================================================#
# LAYOUT

layout = html.Div( 'this is a test', id = 'symbol-page')

#=====================================================================================#
#=====================================================================================#
