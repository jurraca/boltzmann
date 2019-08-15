import dash 
import dash_bootstrap_components as dbc 
import dash_core_components as dcc 
import dash_html_components as html 
from plotly.graph_objs import Layout
from dash.dependencies import Input, Output
import dash_daq as daq 
import dash_cytoscape as cyto 
from ludwig import *

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY]) 

theme = {
	'dark': True, 
	'detail': '#007439',
    'primary': '#00EA64', 
    'secondary': '#6E6E6E'}

stylesheet = [
	{
		'selector': '.green',
		'style': {
			'background-color': 'green',
			'line-color': 'green'
		}
	},
	{
		'selector': '.red',
		'style': {
			'background-color': 'red',
			'line-color': 'red'
		}
	}
]

app.layout = html.Div(
	
	children=[

	html.H1(children='Tx Entropy'),

	html.Div(children='''
		Boltzmann entropy for Bitcoin transactions.
		'''),

	html.Div([ 
		html.Div([
			daq.DarkThemeProvider(theme= theme, children= [
				dcc.Checklist(
				options=[
					{'label': 'PreCheck', 'value': 'PRECHECK'}, 
					{'label': 'Compute Entropy?', 'value': 'LINKABILITY'}, 
					{'label': 'Merge inputs?', 'value': 'MERGE_INPUTS'},
					{'label': 'Merge outputs?', 'value': 'MERGE_OUTPUTS'},
					{'label': 'Merge fees?', 'value': 'MERGE_FEES'}
				], value=['PRECHECK', 'LINKABILITY', 'MERGE_INPUTS'] 
			)]),
			daq.DarkThemeProvider(theme= theme, children= [
			daq.Knob(
				id='duration-input',
				label='Max processing seconds.',
				labelPosition='bottom',
				min=0,
				max=1000,
				value=600
			)]),
			daq.DarkThemeProvider(theme= theme, children= [
			daq.Knob(
				id='maxtxnb-input',
				label='Max Number of Txs to process.',
				labelPosition='bottom',
				min=0,
				max=250,
				value=12
			)]),
			daq.DarkThemeProvider(theme= theme, children= [
			daq.Knob(
				id='cjmaxfeeratio-input',
				label='Max intrafees paid by taker (%).',
				labelPosition='bottom',
				min=0,
				max=99,
				value=40
			)])
		], style={'margin': 'auto', 'margin-right': 0, 'display': 'flex', 'width': '45%', 'margin-bottom': 'inherit'}),
#		html.Div([
#			dcc.Checklist(
#				options=[
#					{'label': 'PreCheck', 'value': 'PRECHECK'}, 
#					{'label': 'Compute Entropy?', 'value': 'LINKABILITY'}, 
#					{'label': 'Merge inputs?', 'value': 'MERGE_INPUTS'},
#					{'label': 'Merge outputs?', 'value': 'MERGE_OUTPUTS'},
#					{'label': 'Merge fees?', 'value': 'MERGE_FEES'}
#				], value=['PRECHECK', 'LINKABILITY', 'MERGE_INPUTS'] )
#			], style={'display': 'block', 'width': '10%', 'margin': 'auto'}),
		html.Div([
			dcc.Input(
				id='tx-input',
		    	placeholder='Enter a tx id',
		    	type='text',
		    	size='75',
		    	debounce=True,
		    	value='00cd588eb04f6bdef3644ec17dfc3622b85212d52021ffaf020ef7bcada1ae63'
			)], style={'margin': 'auto', 'margin-bottom': 'inherit', 'display': 'block', 'width': '40%'} ),
		html.Div([
			cyto.Cytoscape(
				id='tx-map',
				stylesheet=stylesheet,
				elements=[],
				), 
			dcc.Textarea(
				id='output-box',
				draggable=True,
				rows=15,
				cols=65
				)
			], style={'padding': 0, 'width': '600px', 'background-color': 'grey', 'margin-bottom': 'inherit', 'display': 'block', 'margin': 'auto'}), 

		], style={'margin-top': 50, 'margin-bottom': 25}),

	], style={'padding': 20,'display': 'block', 'width': '100vw'})

def build_elements(tx_links): 
	elements = [] 
	for i, tx in enumerate(tx_links): 
		input_addr = tx[0][0]
		input_value = tx[0][1]
		output_addr = tx[1][0]
		output_value = tx[1][1]
#		position 
#		class
		y_value = 10 * i * 3

		#Nodes
		elements.append({'data': {'id': input_addr, 'label': input_value}, 'position': {'x': 50, 'y': y_value}, 'selectable': True, 'grabbable': True, 'classes': 'green'})
		elements.append({'data': {'id': output_addr, 'label': output_value}, 'position': {'x': 200, 'y': y_value}, 'selectable': True, 'grabbable': True, })
		# Links
		elements.append({'data': {'source': input_addr, 'target': output_addr}, 'classes': 'red'})

#	print(elements)
	return elements

def display_results(mat_lnk, nb_cmbn, inputs, outputs, fees, intrafees, efficiency):
    '''
    Displays the results for a given transaction
    Parameters:
        mat_lnk   = linkability matrix
        nb_cmbn   = number of combinations detected
        inputs    = list of input txos (tuples (address, amount))
        outputs   = list of output txos (tuples (address, amount))
        fees      = fees associated to this transaction
        intrafees = max intrafees paid/received by participants (tuple (max intrafees received, max intrafees paid))
        efficiency= wallet efficiency for this transaction (expressed as a percentage)
    '''

    stats = {}
    print('\nInputs = ' + str(inputs))
    print('\nOutputs = ' + str(outputs))
    print('\nFees = %i satoshis' % fees)
    stats['fees'] = fees

    if (intrafees[0] > 0) and (intrafees[1] > 0):
        print('\nHypothesis: Max intrafees received by a participant = %i satoshis' % intrafees[0])
        print('Hypothesis: Max intrafees paid by a participant = %i satoshis' % intrafees[1])

    print('\nNb combinations = %i' % nb_cmbn)
    if nb_cmbn > 0:
        print('Tx entropy = %f bits' % math.log2(nb_cmbn))
        stats['nb_cmbn'] = math.log2(nb_cmbn)

    if efficiency is not None and efficiency > 0:
        print('Wallet efficiency = %f%% (%f bits)' % (efficiency*100, math.log2(efficiency)))
        stats['efficiency'] = math.log2(efficiency)

    if mat_lnk is None:
        if nb_cmbn == 0:
            print('\nSkipped processing of this transaction (too many inputs and/or outputs)')
    else:
        if nb_cmbn != 0:
            print('\nLinkability Matrix (probabilities) :')
            print(mat_lnk / nb_cmbn)
        else:
            print('\nLinkability Matrix (#combinations with link) :')
            print(mat_lnk)

        print('\nDeterministic links :')
        tx_links = []
        for i in range(0, len(outputs)):
            for j in range(0, len(inputs)):
                if (mat_lnk[i,j] == nb_cmbn) and mat_lnk[i,j] != 0 :
                    links = (inputs[j], outputs[i])
                    tx_links.append(links)
                    #print('%s & %s are deterministically linked' % (inputs[j], outputs[i]))
        return tx_links


def main(txids, rpc, testnet, smartbit, options=['PRECHECK', 'LINKABILITY', 'MERGE_INPUTS'], max_duration=600, max_txos=12, max_cj_intrafees_ratio=0):
    '''
    Main function
    Parameters:
        txids                   = list of transactions txids to be processed
        rpc                     = use bitcoind's RPC interface (or blockchain.info web API)
        testnet                 = use testnet (blockchain.info by default)
        smartbit                = use smartbit data provider
        options                 = options to be applied during processing
        max_duration            = max duration allocated to processing of a single tx (in seconds)
        max_txos                = max number of txos. Txs with more than max_txos inputs or outputs are not processed.
        max_cj_intrafees_ratio  = max intrafees paid by the taker of a coinjoined transaction.
                                  Expressed as a percentage of the coinjoined amount.
    '''
    blockchain_provider = None
    provider_descriptor = ''
    if rpc:
        blockchain_provider = BitcoindRPCWrapper()
        provider_descriptor = 'local RPC interface'
    else:
        if smartbit == True:
            blockchain_provider = SmartbitWrapper()
            provider_descriptor = 'remote Smartbit API'
        else:
            blockchain_provider = BlockchainInfoWrapper()
            provider_descriptor = 'remote blockchain.info API'

    print("DEBUG: Using %s" % provider_descriptor)

    for txid in txids:
        print('\n\n--- %s -------------------------------------' % txid)
        # retrieves the tx from local RPC or external data provider
        try:
            tx = blockchain_provider.get_tx(txid, not testnet)
            #print("DEBUG: Tx fetched: {0}".format(str(tx)))
        except Exception as err:
            #print('Unable to retrieve information for %s from %s: %s %s' % (txid, provider_descriptor, err, traceback.format_exc()))
            continue

        # Computes the entropy of the tx and the linkability of txos
        (mat_lnk, nb_cmbn, inputs, outputs, fees, intrafees, efficiency) = process_tx(tx, options, max_duration, max_txos, max_cj_intrafees_ratio)
        links = display_results(mat_lnk, nb_cmbn, inputs, outputs, fees, intrafees, efficiency)
        # Displays the results
        output = build_elements(links)
        return output


@app.callback(
	Output('tx-map', 'elements'),
	[Input('tx-input', 'value'),
	Input('duration-input', 'value'),
	Input('maxtxnb-input', 'value'),
	Input('cjmaxfeeratio-input', 'value')
	])

#@app.callback(Output('output-box', 'value'), [Input('tx-input', 'value')])

def update_fig(txid, duration, maxtxnb, cjmaxfee):

	elements = main(txids=[txid], rpc=False, testnet=False, smartbit=False, options=['LINKABILITY', 'MERGE_INPUTS'], max_duration=duration, max_txos=maxtxnb, max_cj_intrafees_ratio=cjmaxfee)
	return elements

if __name__ == '__main__': 
	app.run_server(debug=True) 