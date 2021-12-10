#Imports
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ClientsideFunction
import plotly.figure_factory as ff

import numpy as np
import pandas as pd
import datetime
from datetime import datetime as dt
import pathlib
import plotly.express as px
import requests 
import json
import plotly.graph_objects as go

#Declare Dash App
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Election Statistics"

server = app.server
app.config.suppress_callback_exceptions = True

# ------ API functions ------
def get_results_by_county(sheet_number=2, year = 2016, month = 11, result_column="total_votes"): 
    """
    Uses api endpoint to get the total votes aggregated to the county level. 
    Parameters (all optional): 
    ------------------------------------------------
    year (default 2016) - the year of the election
    month (default 11) - the month of th election
    sheet_number (default 2) - the contest number of the election
    result_column (default total_votes) Options [election_day, provisional, absentee_by_mail, advance_in_person, total_votes]   
    """
    invoke_url = "https://qp4b96543m.execute-api.us-east-2.amazonaws.com/active"
    params = {"sheet_number": sheet_number, "year": year, "month": month, "result_column": result_column}
    response = requests.get(invoke_url + "/get_results", params=params)
    df = pd.read_json(response.text)
    
    return df

def get_turnout_by_county(year=2016, month=11, race=None, gender=None, age_grp=None): 
    """
    Uses api endpoint to the turnout by demographic with optional filtering by a single gender, 
    single race, and/or single age group. 
    """
    invoke_url = "https://qp4b96543m.execute-api.us-east-2.amazonaws.com/active"
    params = {"year": year, "month": month}
    if race: 
        params["race"] = race 
    if gender: 
        params["gender"] = gender
    if age_grp: 
        params["age_grp"] = age_grp

    response = requests.get(invoke_url + "/get_turnout", params=params)
    return pd.read_json(response.text)

def get_distribution(county_name="Fulton", year=2016, month=11, axis="age_grp", metric="voted"):
    """
    Uses api endpoint to get the distribution of the metric by the axis. 
    """
    invoke_url = "https://qp4b96543m.execute-api.us-east-2.amazonaws.com/active"
    params = {"county_name": county_name, "year": year, "month": month, "axis": axis, "metric": metric}
    response = requests.get(invoke_url + "/get_distribution", params=params)
    return pd.read_json(response.text)


# ------ Get data from API ------
results = get_results_by_county()
counties = results['county_name']

values = results['county_name']
contests = results['county_name']
years = ['2016']

# ------ Statewide Election Results ------
def state_results():
	column_list = list(results)
	column_list.remove("county_name")
	state_wide = pd.DataFrame({'votes':results[column_list].sum(axis=0)})
	state_wide.reset_index(inplace=True)
	state_wide = state_wide.rename(columns = {'index':'Candidate'})
	fig = px.histogram(state_wide, x="Candidate", y="votes", title="Statewide Results",)
	fig.update_layout(autosize=True,width=300,height=250,margin=dict(
        l=50,
        r=50,
        b=0,
        t=30
    ),paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)')	
	return fig

# ------ Countywide Election Results ------
def county_results(county):
	column_list = list(results)
	county_results = results[(results['county_name'] == county)]
	county_results = county_results.T
	county_results.reset_index(inplace=True)
	county_results = county_results.rename(columns = {'index':'Candidate'})
	county_results = county_results.rename(columns = {0:'votes'})
	county_results = county_results.drop([0])
	fig = px.histogram(county_results, x="Candidate", y="votes",title="Countywide Results")
	fig.update_layout(autosize=True,width=300,height=250,margin=dict(
			l=65,
			r=50,
			b=0,
			t=30
		),paper_bgcolor='rgba(0,0,0,0)',
		plot_bgcolor='rgba(0,0,0,0)')
	return fig

# ------ Age histogram ------
def age_histogram(county):
	df = get_distribution(county)
	fig = px.histogram(df, x="age_grp", y="voted")
	fig.update_layout(autosize=True,width=350,height=230,margin=dict(
        l=50,
        r=50,
        b=0,
        t=10
    ),)
	return fig

# ------ Gender Histogram ------
def gender_histogram(county):
	df = get_distribution(county, 2016, 11, "gender", metric="voted")
	fig = px.histogram(df, x="gender", y="voted")
	fig.update_layout(autosize=True,width=350,height=190,margin=dict(
        l=50,
        r=50,
        b=0,
        t=10
    ),)
	return fig

# ------ Race Histogram ------
def race_histogram(county):
	df = get_distribution(county, 2016, 11, "race", metric="voted")
	fig = px.histogram(df, x="race", y="voted")
	fig.update_layout(autosize=True,width=350,height=230,margin=dict(
        l=50,
        r=50,
        b=10,
        t=10
    ),)
	return fig

# ------ Create the HTML Div containing age, gender, and race graphs 
def graphs(county):
	"""
	:return: A div containing age, gender, and race graphs. Also builds the County Selector Dropdown menu
	"""
	return html.Div(
		id="graph-section",
		children=[
			html.Div(id="county-select",children=[html.B("Select County"),
            dcc.Dropdown(
                options=[{"label": i, "value": i} for i in counties],
                value=counties[0],
            ),]),
			dcc.Graph(figure=age_histogram(county)),
			dcc.Graph(figure=gender_histogram(county)),
			dcc.Graph(figure=race_histogram(county)),
	
		],
	)

# ------ NOT CURRENTLY IN USE ------
def description_card():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H4("Welcome to the Georgia Election Analytics Dashboard"),
            html.Div(
                id="intro",
                children="Explore Georgia election results by contest, year, and value. Click on the heatmap to visualize turnout in different counties.",
            ),
        ],
    )

# ------ State Map Data control card: Contest, Year, Value dropdowns 
def generate_control_card():
    """
    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.P("Select Contest"),
            dcc.Dropdown(
                id="contest-select",
                options=[{"label": i, "value": i} for i in contests],
                value=contests[0],
            ),
            html.Br(),
            html.P("Select Year"),
            dcc.Dropdown(
                id="year-select",
                options=[{"label": i, "value": i} for i in years],
                value=years[0],
            ),
            html.Br(),
            html.P("Select Value"),
            dcc.Dropdown(
                id="value-select",
                options=[{"label": i, "value": i} for i in values],
                value=values[0],
            ),
            html.Br(),
            html.Br(),
            html.Div(
                id="reset-btn-outer",
                children=html.Button(id="reset-btn", children="Reset", n_clicks=0),
            ),
        ],
    )

# ------ Georgia Choropleth Map ------
def generate_map(contest, year, value):
    """
    :param: start: start date from selection.
    :param: end: end date from selection.
    :param: clinic: clinic from selection.

    :return: Patient volume annotated heatmap.
    """
##
    df_sample = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/minoritymajority.csv')
    df_sample_r = df_sample[df_sample['STNAME'] == 'Georgia']

    values = df_sample_r['TOT_POP'].tolist()
    fips = df_sample_r['FIPS'].tolist()

    endpts = list(np.mgrid[min(values):max(values):4j])
    colorscale = ["#030512","#1d1d3b","#323268","#3d4b94","#3e6ab0",
                "#4989bc","#60a7c7","#85c5d3","#b7e0e4","#eafcfd"]
    fig = ff.create_choropleth(
        fips=fips, values=values, scope=['Georgia'], show_state_data=True,
        colorscale=colorscale, binning_endpoints=endpts, round_legend_values=True,
        plot_bgcolor='rgb(229,229,229)',
        paper_bgcolor='rgb(229,229,229)',
        legend_title='Population by County',
        county_outline={'color': 'rgb(255,255,255)', 'width': 0.5},
        exponent_format=True,
    )
    fig.layout.template = None
    fig.update_layout(autosize=True,width=1000,height=500,)
    
    ##

    return fig

# ------ APPLICATION LAYOUT ------
app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        #html.Div(
            #id="banner",
            #className="banner",
            #children=#[html.Img(src=app.get_asset_url("plotly_logo.png"))],
        #),
        # Banner (election select)
        html.Div(
            id="banner2",
            className="four columns",
            children=[generate_control_card()]
            + [
                html.Div(
                    ["initial child"], id="election-control", style={"display": "none"}
                )
            ],
        ),
        # Left column (GA Map, state and county results graphs)
        html.Div(
            id="left-column",
            className="eight columns",
            children=[
                html.Div(
                    id="state-graph",
                    children=[
						html.Div(id="state-wide",children=dcc.Graph(figure=state_results()),),
						html.Div(id="county-wide",children=dcc.Graph(figure=county_results('Appling')),),
                        dcc.Graph(figure=generate_map(0,0,0)),
                    ], 
                ),
            ],            
        ),
		# Right column (County select, age, gender, race graphs)
        html.Div(
            id="right-column",
            className="eight columns",
            children=[graphs("Appling")]
            + [
                html.Div(
                    ["initial child"], id="graphs", style={"display": "none"}
                )
            ],   
        ),
    ],
)

# ------ I don't know what this is ------
@app.callback(
    Output("patient_volume_hm", "figure"),
    [
        Input("date-picker-select", "start_date"),
        Input("date-picker-select", "end_date"),
        Input("clinic-select", "value"),
        Input("patient_volume_hm", "clickData"),
        Input("admit-select", "value"),
        Input("reset-btn", "n_clicks"),
    ],
)


# ------ I don't know what this is ------
def update_heatmap(start, end, clinic, hm_click, admit_type, reset_click):
    start = start + " 00:00:00"
    end = end + " 00:00:00"

    reset = False
    # Find which one has been triggered
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "reset-btn":
            reset = True

    # Return to original hm(no colored annotation) by resetting
    return generate_patient_volume_heatmap(
        start, end, clinic, hm_click, admit_type, reset
    )


# ------ Run the server ------
if __name__ == "__main__":
    app.run_server(debug=True)

