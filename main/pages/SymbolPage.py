import dash_core_components as dcc
from dash import html 
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output, State
from dash import no_update
import dash

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
print(cwd+'/logos/logo_transparent.png')
#=====================================================================================#
#=====================================================================================#
# NAV BAR

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src=cwd+'/logos/logo_transparent.png', height="30px")),
                    dbc.Col(dbc.NavbarBrand("Navbar", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
        ),
    ],
)

#=====================================================================================#
#=====================================================================================#
# COMPONENTS


#=====================================================================================#
#=====================================================================================#
# CALLBACKS 



#=====================================================================================#
#=====================================================================================#
# LAYOUT

layout = html.Div([ 
	navbar
])

#=====================================================================================#
#=====================================================================================#
