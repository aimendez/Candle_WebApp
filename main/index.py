from dash import dcc
from dash import html 
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from app import app
from pages import SummaryPage, SymbolPage
import utils 
import warnings
warnings.filterwarnings("ignore")

server = app.server
app.title = "CandleDash"


#=====================================================================================#
#=====================================================================================#
# NAV BAR

search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="search for symbol"), width=8),
        dbc.Col(
            dbc.Button(
                "Search", color="primary", className="ml-2", n_clicks=0, style={'font-weight': 'bold', 'background-color': '#FF6B4A'}
            ),
            width="auto",
        ),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0 ",
    align="center",
)

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [ dbc.Col( html.Img(src=app.get_asset_url('logo.png'), style={'marginTop':'23px','marginBottom':'20px', 'height':'85%', 'width':'85%'})) ],
                align="center",
                no_gutters=True,
            ),
            href="/",
        ),

        dbc.NavItem(dbc.NavLink(html.H5('EXPLORE', style={'font-weight': 'bold',  'marginTop':'13px', 'marginLeft':'10px','color':'white'}),  href="/" )),
        dbc.NavItem(dbc.NavLink(html.H5('ABOUT', style={'font-weight': 'bold',  'marginTop':'13px', 'marginLeft':'10px','color':'white'}),  href="#" )),

        dbc.Collapse(
            search_bar, id="navbar-collapse", navbar=True, is_open=False
        ),
    ],
style={'height':'84px'}, color='dark', dark=True, sticky="top", className = "nav")

#=====================================================================================#
#=====================================================================================#
# APP LAYOUT

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/' or pathname == '/SummaryPage':
        return SummaryPage.layout
    elif pathname == '/SymbolPage':
        return SymbolPage.layout
   
if __name__ == '__main__':
    app.run_server(debug=True)
