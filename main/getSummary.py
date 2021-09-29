import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import utils 
from assets import pattern_list 
import boto3
import os 
import json
from talib import abstract
main_dir = os.path.dirname(os.getcwd())

# AWS S3 Credentials
s3 = boto3.resource(
        's3',
        aws_access_key_id= os.environ['aws_access_key_id'],
        aws_secret_access_key = os.environ['aws_secret_access_key'] 
        )

# Load list of SPY500 symbols
df_spy500 = pd.read_csv(main_dir+'/main/assets/spy500_list.csv', index_col = 0)

# Yesterday's Date
d =  datetime.today() #+ timedelta(days=1) 
dend = d - timedelta(days=2) if d.weekday() == 6 else d - timedelta(days=1) if  d.weekday() == 5 else d
dstart = d - timedelta(days=10) 

# Get list of all possible patterns from pattern_list
pattern_options = pattern_list.pattern_list

# Loop through symbols to identify patterns
summary = {}
for i, symbol in enumerate(df_spy500.Symbol[:100]):
	data = utils.get_data(symbol, start=dstart, end=dend)
	if len(data)==0: continue;
	patterns_found = []
	for pattern, name in pattern_options.items():
		pattern_func = abstract.Function(pattern)
		pattern_df = pattern_func(data.open, data.high, data.low, data.close) 
		if False in (0 == np.array(pattern_df)): #this means there was a pattern on the last 5 days.
			data[name] = pattern_df
			pattern_idx = list(data[ data[name] != 0 ].index.values)
			pattern_direction = list( data[ data[name] != 0 ][name].values )
			patterns_found.append( (pattern, pattern_idx[-1], pattern_direction[-1] ) )

	print(data)
	#print(patterns_found)
	#print()
	if len(patterns_found)!=0:
		last_pattern_date = max(patterns_found, key=lambda item: item[1])[1] 
		patterns_found = [ item for item in patterns_found if item[1]==last_pattern_date]
		#print(patterns_found)
		summary[symbol] = patterns_found
	print('======================')


# Dump summary in S3 Bucket
s3.Bucket('patternsummarybucket').put_object(
     Body= json.dumps(summary, sort_keys=True, indent = 4, default=str),
     Key='summary'
)




