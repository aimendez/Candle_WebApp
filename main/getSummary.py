import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import utils 
from assets import pattern_list 
import plotly.graph_objs as go 
import boto3
import os 
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt  
import json
from base64 import b64encode
from talib import abstract
import mplfinance as mpf
main_dir = os.path.dirname(os.getcwd())

# AWS S3 Credentials
s3 = boto3.resource(
        's3',
        aws_access_key_id= os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY'] 
        )

# Load list of SPY500 symbols
df_spy500 = pd.read_csv(main_dir+'/main/assets/spy500_list.csv', index_col = 0)

# Yesterday's Date
d =  datetime.today() #+ timedelta(days=1) 
dend = d - timedelta(days=2) if d.weekday() == 6 else d - timedelta(days=1) if  d.weekday() == 5 else d
dstart = d - timedelta(days=60) 

# Get list of all possible patterns from pattern_list
pattern_options = pattern_list.pattern_list

# Loop through symbols to identify patterns
summary = {}
list_figures = []
for i, symbol in enumerate(df_spy500.Symbol[:100]):
	data = utils.get_data(symbol, start=dstart, end=dend)
	if len(data)==0: continue;
	data.index = pd.to_datetime(data.index)

	#plotyl 
	fig = go.Figure()
	fig.add_trace( go.Candlestick( x = data.index ,
                                    open = data.open,
                                    high = data.high,
                                    low = data.low,
                                    close = data.close,
                                    showlegend=False,
                                    name = 'OHLC'
                                    )
							)
	fig.update_layout(xaxis_rangeslider_visible=False, paper_bgcolor = '#303030',	plot_bgcolor = '#303030')
	fig.update_xaxes(showline=True, linewidth=1, linecolor='black',  gridwidth=1, gridcolor='LightGray', mirror=True, tickfont=dict(color="#FFAB4A"))
	fig.update_yaxes(showline=True, linewidth=1, linecolor='black',  gridwidth=1, gridcolor='LightGray', mirror=True, tickfont=dict(color="#FFAB4A") )
	#fig.show()
	#break
	img_bytes = fig.to_image(format="png")
	
	
	data = data[-10:]
	patterns_found = []
	for pattern, name in pattern_options.items():
		pattern_func = abstract.Function(pattern)
		pattern_df = pattern_func(data.open, data.high, data.low, data.close) 
		if False in (0 == np.array(pattern_df)): #this means there was a pattern on the last 5 days.
			data[name] = pattern_df
			pattern_idx = list(data[ data[name] != 0 ].index.values)
			pattern_direction = list( data[ data[name] != 0 ][name].values )
			patterns_found.append( (pattern, pattern_idx[-1], pattern_direction[-1] ) )

	if len(patterns_found)!=0:
		last_pattern_date = max(patterns_found, key=lambda item: item[1])[1] 
		patterns_found = [ item for item in patterns_found if item[1]==last_pattern_date]
		summary[symbol] = patterns_found
		list_figures.append( (symbol, img_bytes) )

# Dump summary in S3 Bucket
s3.Bucket('patternsummarybucket').put_object(
     Body= json.dumps(summary, sort_keys=True, indent = 4, default=str),
     Key='summary'
)

# Save imgs to S3 Bucket
for symbol, img in list_figures:
	s3.Bucket('patternsummarybucket').put_object(Body=img, ContentType='image/png', Key=f'Figures/{symbol}')

