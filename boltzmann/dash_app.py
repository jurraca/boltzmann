import dash 
import dash_bootstrap_components as dbc 
import dash_core_components as dcc 
import dash_html_components as html 
from plotly.graph_objs import Layout
from dash.dependencies import Input, Output
import dash_daq as daq 
import ludwig

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY]) 

app.layout = html.Div(
	
	children=[ 

	html.H1(children='Tx Entropy'),

	html.Div(children='''
		Boltzmann entropy for Bitcoin transactions.
		'''),

	html.Div([
			dcc.Input(
				id='tx-input',
		    	placeholder='Enter a tx id',
		    	type='text',
		    	value='00cd588eb04f6bdef3644ec17dfc3622b85212d52021ffaf020ef7bcada1ae63'
			), 
			daq.NumericInput(
				id='duration-input',
				label='Max processing seconds.',
				labelPosition='bottom',
				min=0,
				value=600
			),
			daq.NumericInput(
				id='maxtxnb-input',
				label='Max Number of Txs to process.',
				labelPosition='bottom',
				min=0,
				max=250,
				value=12
			),
			daq.NumericInput(
				id='cjmaxfeeratio-input',
				label='Max intrafees paid by taker (%).',
				labelPosition='bottom',
				min=0,
				max=99,
				value=40
			), 
			dcc.Textarea(
				id='output-box'

				)
		], style={'margin-top': 50, 'align-items': 'left'}),

	], style={'padding': 20})

## handle inputs 
## call ludwig and handle outputs
## pass to graph 

@app.callback(
	Output('output-box', 'value'),
	[Input('tx-input', 'value'),
	Input('duration-input', 'value'),
	Input('maxtxnb-input', 'value'),
	Input('cjmaxfeeratio-input', 'value')
	])

def update_fig(txid, duration, maxtxnb, cjmaxfee):
	output = ludwig.main(txids=[txid], rpc=False, testnet=False, smartbit=False, options=['LINKABILITY'], max_duration=duration, max_txos=maxtxnb, max_cj_intrafees_ratio=cjmaxfee)
	return output

if __name__ == '__main__': 
	app.run_server(debug=True) 