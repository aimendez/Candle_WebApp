from dash import dcc
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
import talib
import boto3

from app import app
import json
from datetime import datetime, timedelta, date
from assets import pattern_list 
import pandas as pd
import numpy as np
import utils 
import os 
import warnings
warnings.filterwarnings("ignore")

cwd = os.path.dirname(os.getcwd())

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


pattern_options = pattern_list.pattern_list
#=====================================================================================#
#=====================================================================================#
# COMPONENTS

dropdown_patterns =   dcc.Dropdown( id='dropdown-pattern', value = 0, style= {'color':'black'})

radio_horizon = dcc.RadioItems( id = 'radio-horizon', 
								options = [
										{'label':'1W', 'value':0},
										{'label':'1M', 'value':1},
										{'label':'3M', 'value':2},
										{'label':'6M', 'value':3},
									],
								value = 0,
								inputStyle={"margin-right": "10px", "margin-left": "10px"}
								)





#=====================================================================================#
#=====================================================================================#
# CALLBACKS 
@app.callback(
    [
    Output('dropdown-pattern', 'options'),
    Output('dropdown-pattern', 'value'),
    ],
    [
    Input('url', 'pathname'),
    ])
def dropdown_pattern(pathname):
	query_str =  flask.request.referrer.split('?')[-1] #value1=symbol&
	symbol =  query_str.split('&')[0]
	patterns = [ item[0] for item in summary[symbol] ]
	options = [ {'label': pattern_options[pattern], 'value': i} for i, pattern in enumerate(patterns)]
	value = 0
	return [options, value] 

@app.callback(
[
    Output('candlestick-plot', 'figure'),
],
[
    Input('url', 'pathname'),
    Input('dropdown-pattern', 'value'),
    Input('radio-horizon', 'value')
],
    )
def callback_func(pathname, dropdown, horizon):

	query_str =  flask.request.referrer.split('?')[-1] #value1=symbol&
	symbol =  query_str.split('&')[0]

	# DATE OF CHART
	dstart = datetime.today() - timedelta(days=600) 
	data_all = utils.get_data(symbol, dstart)

	# INDICATORS
	macd, macdsignal, macdhist = talib.MACD(data_all.close, fastperiod=12, slowperiod=26, signalperiod=9)
	data_all['MACD'] = macd

	real = talib.RSI(data_all.close, timeperiod=14)
	data_all['RSI'] = real

	# FOR CHART
	lookback = 30
	data = data_all[-lookback:]
	if horizon == 0:
		lookup = 5
	elif horizon == 1:
		lookup = 30
	elif horizon == 2:
		lookup = 90 
	elif horizon == 3:
		lookup = 180

	# # PATTERN FORECAST 
	curr_close = data_all.close[-1]
	if dropdown is not None:
		pattern = summary[symbol][dropdown]
		direction = np.sign(int(pattern[-1]))
		pattern_func = abstract.Function(pattern[0])
		idx_list = pattern_func(data_all.open, data_all.high, data_all.low, data_all.close) 
		idx_list = [i for i, signal in enumerate(idx_list) if np.sign(int(signal))==direction]
		forecast_dates = data_all.index[idx_list]

		# quartiles for filtering 
		q_macd  = list( np.percentile( [data_all.loc[date,'MACD'] for date in forecast_dates if not np.isnan(data_all.loc[date,'MACD'])], [0,25,50,75,100]) )
		q_macd = [ (q_macd[i], q_macd[i+1]) for i, q in enumerate(q_macd) if i+1 < len(q_macd) and (q_macd[i] <= data_all.MACD.values[-1] < q_macd[i+1])][0]
		q_rsi  = list( np.percentile( [data_all.loc[date,'RSI'] for date in forecast_dates if not np.isnan(data_all.loc[date,'RSI'])], [0,25,50,75,100]) )
		q_rsi = [ (q_rsi[i], q_rsi[i+1]) for i, q in enumerate(q_rsi) if i+1 < len(q_rsi) and (q_rsi[i] <= data_all.RSI.values[-1] < q_rsi[i+1])][0]

		y_list = []
		for i, date in enumerate(forecast_dates[:-1]):
			df_tmp = data_all.loc[date:, :]
			
			# fitler
			macd_tmp = data_all.loc[date,'MACD' ]
			rsi_tmp = data_all.loc[date,'RSI' ]
			if q_macd[0] <= macd_tmp <=q_macd[1]  and  q_rsi[0]<= rsi_tmp <= q_rsi[1]:
				df_tmp['pct_change'] = df_tmp.apply(lambda x: curr_close + curr_close*(x['close']/ df_tmp['close'].values[0] - 1), axis=1 ).replace(np.nan, 0)	
				y = df_tmp['pct_change'].values[:min(lookup, len(df_tmp))]
				y_list.append(y)

		upper_bound	, lower_bound, std, median = ([] for i in range(4))
		for i in range(lookup):
			tmp = [ y[i] for y in y_list if len(y) > i ]
			upper_bound.append( max(tmp) )
			lower_bound.append( min(tmp) )
			std.append(np.std(tmp))
			median.append(np.median(tmp)) 

	# PRICE PLOT
	fig = make_subplots(rows=3, cols=1,
						row_heights=[0.7, 0.15, 0.15], 
						shared_xaxes=True,
                    	vertical_spacing=0.0)
	fig.update_layout(height=400)
	fig.update_layout(showlegend=False)
	fig.update_layout(xaxis=dict(type='category'), xaxis_rangeslider_visible=False, margin=dict(t=40), paper_bgcolor = '#303030',	plot_bgcolor = '#303030')
	fig.update_xaxes(showline=True, linewidth=1, linecolor='black',  gridwidth=1, gridcolor = '#303030', mirror=True, tickfont=dict(color="#FFAB4A"))
	fig.update_yaxes(showline=True, linewidth=1, linecolor='black',  gridwidth=1, gridcolor = '#303030', mirror=True, tickfont=dict(color="#FFAB4A") )
	
	fig.add_trace( go.Candlestick( x = data.index ,
                                    open = data.open,
                                    high = data.high,
                                    low = data.low,
                                    close = data.close,
                                    ), 
							row=1, col=1)

	fig.add_trace( go.Scatter( x = data.index ,
                               y = data.close,
                                   ), 
							row=1, col=1)

	fig.add_trace( go.Scatter(  x = data.index ,
                                y = data['MACD'].values,
                                marker = dict( color = '#FFAB4A')
                                    ), 
							row=3, col=1)

	fig.add_trace( go.Scatter(  x = data.index ,
                                y = data['RSI'].values,
                                marker = dict( color = '#FF8230')
                                    ), 
							row=2, col=1)


	# ADD TRACES OF FORECAST

	# CURRENT PRICE LINE
	fig.add_shape(
			    type="line",
			    x0=len(data), y0=curr_close, 
			    x1=len(data)+lookup, y1=curr_close,
			    line=dict(color='white', width=1, dash='dash'),
				)

	

	upper_trace = go.Scatter(
							x =  list(range(len(upper_bound))), 
							y = upper_bound,
							fill=None,
				            mode = 'lines',
				            line_color = 'LightGray',
				            fillcolor='rgba(205,205,205, 0.3)',
						    line = {'width':0.5},
					        )

	lower_trace = go.Scatter(
								x =  list(range(len(lower_bound	))), 
								y = lower_bound	,
				 				fill='tonexty',
			                    mode='lines',
			                    line_color='LightGray',
			                    fillcolor='rgba(205,205,205, 0.3)',
					    		line = {'width':0.5},
			                )

	# MEDIAN LINE 
	median_trace = go.Scatter( 
							x = list(range(len(median))), 
							y=median,  
							line = dict(color='red', width=2, dash='dash'))


	# ADD TRACES
	fig.add_traces([upper_trace,lower_trace, median_trace])
	

	return [fig]


#=====================================================================================#
#=====================================================================================#
# LAYOUT


layout = html.Div([ 

	dbc.Row([
		dbc.Col([ html.Div(dropdown_patterns)])
		]),

	dbc.Row([
		dbc.Col([ html.Div(radio_horizon)])
		]),


	

	dbc.Row([
		dbc.Col([
			html.Div(dcc.Graph(id='candlestick-plot'), style={'marginLeft': '60px', 'marginRight':'60px', 'marginTop':'100px'})
				]),

		]),

	], style={'marginTop':'20px'})


#=====================================================================================#
#=====================================================================================#
