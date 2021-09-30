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
import random
from datetime import datetime, timedelta, date
from assets import pattern_list 
import pandas as pd
import numpy as np
import utils 
import os
import io
import boto3
main_dir = os.path.dirname(os.getcwd())
#=====================================================================================#
#=====================================================================================#
d =  datetime.today() # - timedelta(days=1) 
d = d- timedelta(days=2) if d.weekday() == 6 else d - timedelta(days=1) if  d.weekday() == 5 else d
dstart = d - timedelta(days=10) 
d = str(d).split( ' ' )[0]

#=====================================================================================#
#=====================================================================================#
df_spy500 = pd.read_csv(main_dir+'/main/assets/spy500_list.csv', index_col = 0)

#=====================================================================================#
#=====================================================================================#
# Load summary from S3 AWS Bucket
s3 = boto3.resource(
        's3',
        aws_access_key_id= os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY'] 
        )

obj = s3.Object('patternsummarybucket', 'summary' )
summary = json.load(obj.get()['Body'])

#=====================================================================================#
#=====================================================================================#
# COMPONENTS
checklist_direction = dcc.Checklist( id = 'filter-direction',
    options=[
			{'label': 'Bullish' , 'value':0},
			{'label': 'Bearish', 'value':1},
			{'label': 'Neutral', 'value':2},

			
			], 
		value = [],
		labelStyle={'display': 'block'},
		inputStyle={'marginLeft':'15px', 'marginRight':'15px'}
	)

checklist_confidence = dcc.Checklist( id= 'filter-strength',
    options=[
			{'label': 'Strong' , 'value':0},
			{'label': 'Reliable', 'value':1},
			{'label': 'Weak', 'value':2},
			], 
		value = [],
		labelStyle={'display': 'block'},
		inputStyle={'marginLeft':'15px', 'marginRight':'15px'}
	)

checklist_signal = dcc.Checklist( id = 'filter-type',
    options=[
			{'label': 'Reversal' , 'value':0},
			{'label': 'Continuation', 'value':1},
			{'label': 'Consolidation', 'value':2},
			], 
		value = [],
		labelStyle={'display': 'block'},
		inputStyle={'marginLeft':'15px', 'marginRight':'15px'}
	)

checklist_time =  dcc.Checklist( id = 'filter-date',
    options=[
			{'label': 'Today' , 'value':0},
			{'label': 'Last 5 Days', 'value':1},
			], 
		value = [],
		labelStyle={'display': 'block'},
		inputStyle={'marginLeft':'15px', 'marginRight':'15px'}
	)

checklist_sector = dcc.Checklist(
    options=[
			{'label': 'Communications', 'value':1},
			{'label': 'Consumer Discretionary', 'value':2},
			{'label': 'Energy', 'value':3},
			{'label': 'Financials', 'value':4},
			{'label': 'Health Care', 'value':5},
			{'label': 'Industrial', 'value':6},
			{'label': 'Materials', 'value':7},
			{'label': 'Real Estate', 'value':8},
			{'label': 'Tech' , 'value':9},
			{'label': 'Utilities', 'value':10},
			], 
		value = [],
		labelStyle={'display': 'block'},
		inputStyle={'marginLeft':'15px', 'marginRight':'15px'}
	)


checklist_marketCap = dcc.Checklist(
    options=[
			{'label': '≥ $200B' , 'value':0},
			{'label': '[ $10B , $200B ]', 'value':1},
			{'label': '[ $2B , $10B ]' , 'value':2},
			{'label': '[ $300M , $2B ]', 'value':3},
			{'label': '< $300M', 'value':4},
			], 
		value = [],
		labelStyle={'display': 'block'},
		inputStyle={'marginLeft':'15px', 'marginRight':'15px'}
	)

sidebar_header = dbc.Navbar(
    [
        html.H4( "FILTERS", style={'marginLeft':'-18px', 'font-weight':'bold'}),
    ],
color='none', dark=True, style={'height':'30px', 'marginTop':"20px", 'marginBottom':'-10px'} )

sidebar = html.Div(
    [
        sidebar_header,
        html.Hr(style={ 'borderColor':'white'}),

        html.H5('DIRECTION', className='mt-5'),
        checklist_direction,

        html.H5('STRENGTH', className='mt-5'),
        checklist_confidence,
        
        html.H5('SIGNAL TYPE', className='mt-5'),
        checklist_signal,

        html.H5('DATE', className='mt-5'),
        checklist_time,

        html.H5('GICS SECTOR', className='mt-5'),
        checklist_sector,

        html.Div(style={'marginBottom':'200px'})
    ],
style={'height':'900px' ,"overflowY": "scroll"} )

#=====================================================================================#
#=====================================================================================#
# CALLBACKS 

@app.callback(
 [ 
 	Output('summary-div', 'children'),
	],              

	[
	Input('filter-date', 'value'),
	Input('filter-strength', 'value'),
	Input('filter-type', 'value'),
	Input('filter-direction', 'value'),

	], 
)
def CreateSummary(filter_date, filter_strength, filter_type, filter_direction):

	total_cards = []
	for k,v in summary.items():

		# NAME AND SYMBOL
		symbol = k
		company_name = df_spy500[df_spy500.Symbol == symbol]['Security']
		header1 = company_name + f' ({symbol})'
		
		# SECTOR 
		sector = df_spy500[df_spy500.Symbol == symbol]['GICS Sector'].values[0]
		
		# DIRECTION
		direction = [ 'BULLISH' if int(item[2])>=0 else 'BEARISH' for item in v]
		direction_final = 'BULLISH' if False not in ( 'BULLISH'==np.array(direction) ) else 'BEARISH' if False not in ('BEARISH'==np.array(direction)) else 'NEUTRAL'
		logo = 'bear-logo.png' if direction_final == 'BEARISH' else 'bull-logo.png' if direction_final == 'BULLISH' else 'neutral-logo.png'
		header2 = html.Img( src=app.get_asset_url(logo), style={ 'height': '35px', 'width':'35px', 'marginTop': '-10px', 'marginRight':'10px'})
		if direction_final=='NEUTRAL':
			header2 = html.Img( src=app.get_asset_url(logo), style={ 'height': '30px', 'width':'30px', 'marginTop': '-8px', 'marginRight':'10px'})

		# DATE(S)
		dates = np.unique([ item[1] for item in v])
		date_line = html.P( [html.Strong('LAST PATTERN: '), dates[0] ] )

		# TYPE OF PATTERN(S)
		patterns = [ item[0] for item in v ]
		type_patterns = np.unique([pattern_list.pattern_img[pattern][3] if len(pattern_list.pattern_img[pattern])==4 else 'Unknown' for pattern in patterns  ])
		type_line = 'TYPE: '+ ', '.join(type_patterns)
		type_line = html.P([ html.Strong('TYPE: ') , ', '.join(type_patterns) ])

		# STRENGTH OF PATTERN(S)
		strength_patterns = np.unique([pattern_list.pattern_img[pattern][2] if len(pattern_list.pattern_img[pattern])==4 else 'Unknown' for pattern in patterns  ])
		strength_line = html.P([ html.Strong('STRENGTH: ') , ', '.join(strength_patterns) ])

		summary_description = html.P( [date_line, type_line,  strength_line,] )
		card_tmp=  html.Div( 
		    	[
		        dbc.Card(
		        		[
	                        dbc.CardHeader( 
	                        				html.A(
	                        						href='/', children = [ 
	                        												html.Div( [ html.H5(header1, style={'font-weight': 'bold', 'color':'#FFAB4A', 'marginLeft':'15px'}), header2 ], className = 'row justify-content-between mb-0')
	                        											]
	                        						),
                								style = {'height': '40px'}),
	                        html.Div(className='row', children = [
	                        	html.Div( children = summary_description, className='col', style={'marginTop':'30px', 'marginBottom':'30px', 'marginLeft':'40px'} ),
	                        	html.Div( className='col', style={'background-color':'white', 'marginRight':'20px'} ),

	                        	])
		               ], className="card")
		    	], style = {'marginBottom':'50px'})

		total_cards.append([dates, type_patterns, strength_patterns, direction_final, sector, card_tmp])


	#----- Filters -----#
	filter_idx = []

	#DIRECTION
	filter_idx_direction = []
	if filter_direction is not None and len(filter_direction)!=0:
		bull = bear = neutral = []
		if 0 in filter_direction:
			bull = [ idx for idx, item in enumerate(total_cards) if 'BULLISH' == item[3]]
		if 1 in filter_direction: 
			bear = [ idx for idx, item in enumerate(total_cards) if 'BEARISH' == item[3]]
		if 2 in filter_direction: 
			neutral = [ idx for idx, item in enumerate(total_cards) if 'NEUTRAL' == item[3]]
		filter_idx_direction = np.unique( sorted(bull+bear+neutral) )

	#STRENGTH 
	filter_idx_strength = []
	if filter_strength is not None and len(filter_strength)!=0:
		strong = rel = weak = []
		if 0 in filter_strength:
			strong = [ idx for idx, item in enumerate(total_cards) if 'strong' in item[2]]
		if 1 in filter_strength: 
			rel = [ idx for idx, item in enumerate(total_cards) if 'reliable' in item[2]]
		if 2 in filter_strength: 
			weak = [ idx for idx, item in enumerate(total_cards) if 'weak' in item[2]]
		filter_idx_strength = np.unique( sorted(strong+rel+weak) )

	#TYPE 
	filter_idx_type = []
	if filter_type is not None and len(filter_type)!=0:
		rev = cont = cons = []
		if 0 in filter_type:
			rev = [ idx for idx, item in enumerate(total_cards) if 'reversal' in item[1]]
		if 1 in filter_type: 
			cont = [ idx for idx, item in enumerate(total_cards) if 'continuation' in item[1]]
		if 2 in filter_type: 
			cons = [ idx for idx, item in enumerate(total_cards) if 'consolidation' in item[1]]
		filter_idx_type = np.unique( sorted(rev+cont+cons) )

	# DATE
	filter_idx_date = []
	if filter_date is not None and len(filter_date)!=0:
		total_cards_filter1 = total_cards_filter2 = []
		if 0 in filter_date:
			total_cards_filter1 = [ idx for idx, item in enumerate(total_cards) if str(d).split(' ')[0] in item[0]]
		if 1 in filter_date: 
			total_cards_filter2 = [ idx for idx, item in enumerate(total_cards) if str(d).split(' ')[0] not in item[0]]
		filter_idx_date = np.unique( sorted(total_cards_filter1+total_cards_filter2) )


	# no filter
	if len(filter_date)==0 and len(filter_strength)==0 and len(filter_type)==0 and len(filter_direction)==0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards)  ]

	# 1 filter on 
	if len(filter_date)!=0 and len(filter_strength)==0 and len(filter_type)==0 and len(filter_direction)==0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_date)  ]

	if len(filter_date)==0 and len(filter_strength)!=0 and len(filter_type)==0 and len(filter_direction)==0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_strength) ]

	if len(filter_date)==0 and len(filter_strength)==0 and len(filter_type)!=0 and len(filter_direction)==0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_type) ]

	if len(filter_date)==0 and len(filter_strength)==0 and len(filter_type)==0 and len(filter_direction)!=0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_direction) ]

	# 2 filters on
	if len(filter_date)!=0 and len(filter_strength) !=0 and len(filter_type)==0 and len(filter_direction)==0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_date) and (idx in filter_idx_strength)   ]

	if len(filter_date)!=0 and len(filter_strength) ==0 and len(filter_type)!=0 and len(filter_direction)==0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_date) and (idx in filter_idx_type)   ]

	if len(filter_date)!=0 and len(filter_strength) ==0 and len(filter_type)==0 and len(filter_direction)!=0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_date) and (idx in filter_idx_direction)   ]

	if len(filter_date)==0 and len(filter_strength) !=0 and len(filter_type)!=0 and len(filter_direction)==0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_strength) and (idx in filter_idx_type)   ]

	if len(filter_date)==0 and len(filter_strength) !=0 and len(filter_type)==0 and len(filter_direction)!=0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_strength) and (idx in filter_idx_direction)   ]

	if len(filter_date)==0 and len(filter_strength) ==0 and len(filter_type)!=0 and len(filter_direction)!=0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_type) and (idx in filter_idx_direction)   ]

	# 3 filters on 
	if len(filter_date)!=0 and len(filter_strength) !=0 and len(filter_type)!=0 and len(filter_direction)==0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_date) and (idx in filter_idx_strength) and (idx in filter_idx_type)   ]
	
	if len(filter_date)!=0 and len(filter_strength) !=0 and len(filter_type)==0 and len(filter_direction)!=0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_date) and (idx in filter_idx_strength) and (idx in filter_idx_direction)   ]

	if len(filter_date)!=0 and len(filter_strength) ==0 and len(filter_type)!=0 and len(filter_direction)!=0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_date) and (idx in filter_idx_type) and (idx in filter_idx_direction)   ]

	if len(filter_date)==0 and len(filter_strength) !=0 and len(filter_type)!=0 and len(filter_direction)!=0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_strength) and (idx in filter_idx_type) and (idx in filter_idx_direction)   ]

	# 4 filters on
	if len(filter_date)!=0 and len(filter_strength) !=0 and len(filter_type)!=0 and len(filter_direction)!=0:
		filter_symbols = [ item[-1] for idx, item in enumerate(total_cards) if (idx in filter_idx_date) and (idx in filter_idx_strength) and (idx in filter_idx_type) and (idx in filter_idx_direction)   ]

	return [filter_symbols]

#=====================================================================================#
#=====================================================================================#
# LAYOUT

layout = html.Div([ 
	dbc.Row([
		dbc.Col(sidebar, width=2, style={'marginLeft':'250px'}),
		dbc.Col( html.Div( id = 'summary-div', style={'paddingTop':'100px', 'marginLeft':'180px', 'paddingRight':'250px', 'height':'900px' ,"overflowY": "scroll"} )), #, style={'marginTop':'100px', 'marginLeft':'100px','marginRight':'100px'}) ),
		]),
	dcc.Store(id='filter-data')
	])

#=====================================================================================#
#=====================================================================================#
