# Main app file
#
# UGA Fall 2021 - CSCI 4370
# Final Project: Election Statistics Database
# Authors: Abbie Thomas, Ayush Kumar, Faisal Hossain, Khemisha Brown, Sagar Asthana 
# Professor: Mario Guimaraes

#Import Modules
import dash
import pandas as pd
import api_calls as api
import plotly.express as px
import plotly.graph_objects as go
import dash_core_components as dcc
import plotly.figure_factory as ff
import dash_html_components as html
from dash.dependencies import Input, Output

# Declare Dash App
app = dash.Dash( __name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],)
app.title = "Georgia Election"
server = app.server
app.config.suppress_callback_exceptions = True

# Get data from API
results = api.get_results_by_county()
counties = results['county_name']
values = results['county_name']
contests = results['county_name']
years = ['2016']

# -- Georgia Choropleth Map Data
FIPS_df = pd.read_csv("https://raw.githubusercontent.com/fhossain75/georgia-election-map/main/data/georgiaFIPS.csv")
countyResults = results
countyResults['winner'] = countyResults[['DONALD J. TRUMP', 'GARY JOHNSON', 'HILLARY CLINTON']].idxmax(axis=1)
countyResults.insert(0, "FIPS", FIPS_df["FIPS"])
fips = countyResults['FIPS'].tolist()
values = countyResults['winner'].tolist()
colorscale = ["#DE0100", "#1405BD"]

# Statewide Results Chart Data
column_list = list(results)
column_list.remove("county_name")
state_wide = pd.DataFrame({'votes' : results[column_list].sum(axis=0)})
state_wide.reset_index(inplace=True)
state_wide = state_wide.rename(columns = {'index':'Candidate'})

# Statewide results chart
def state_results():
    # Figure
	fig = px.histogram(state_wide, x = "Candidate", y = "votes", title = "Statewide Results")
	fig.update_layout(autosize = True, width = 300, height = 250,
        margin = dict(l=50, r=50, b=0, t=30), paper_bgcolor = 'rgba(0,0,0,0)', plot_bgcolor = 'rgba(0,0,0,0)')	

	return fig

# HTML Div containing charts for age, gender, and race; and county selector dropdown menu
def graphs():
	return html.Div(id = "graph-section", children = [
			html.Div(id = "county-select", children = [ 
                html.B("Select County"),
                    dcc.Dropdown(id = "county-drop-select",
                        options=[{"label": i, "value": i} for i in counties], value=counties[0])]),
            dcc.Graph(id = "age_histogram"),
            dcc.Graph(id = "gender_histogram"),
            dcc.Graph(id = "race_histogram")])

# ------ NOT CURRENTLY IN USE ------
def description_card():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id = "description-card",
        children = [
            html.H4("Welcome to the Georgia Election Analytics Dashboard"),
            html.Div(
                id = "intro",
                children = "Explore Georgia election results by contest, year, and value. Click on the heatmap to visualize turnout in different counties.",
            ),
        ],
    )

# State Map data control card: Contest, Year, Value dropdown menus
def generate_control_card():
    return html.Div(
        id="control-card",
        children=[
            html.P("Select Contest"),
            dcc.Dropdown(
                id="contest-select",
                options=[{"label": i, "value": i} for i in contests],
                value = contests[0],
            ),
            html.Br(),
            html.P("Select Year"),
            dcc.Dropdown(
                id = "year-select",
                options = [{"label": i, "value": i} for i in years],
                value = years[0],
            ),
            html.Br(),
            html.P("Select Value"),
            dcc.Dropdown(
                id = "value-select",
                options = [{"label": i, "value": i} for i in values],
                value = values[0],
            ),
            html.Br(),
            html.Br(),
            html.Div(
                id = "reset-btn-outer",
                children = html.Button(id="reset-btn", children="Reset", n_clicks=0),
            ),
        ],
    )

# Georgia Choropleth Map 
def generate_map(contest, year, value):
    fig = ff.create_choropleth(
        fips = fips, values = values, scope = ['Georgia'], colorscale = colorscale,
        round_legend_values = True,
        plot_bgcolor = 'rgb(229,229,229)',
        paper_bgcolor = 'rgb(229,229,229)',
        legend_title = 'Majority Vote by County',
        county_outline = {'color': 'rgb(255,255,255)', 'width': 0.5},
        exponent_format = True
    )
    fig.layout.template = None
    fig.update_layout(autosize = True, width = 1000, height = 500)
    
    return fig

# Application Layout
app.layout = html.Div(
    id="app-container",
    children=[
        # State Map data control card
        html.Div(
            id = "banner2",
            className = "four columns",
            children = [generate_control_card()] + [html.Div(["initial child"], id="election-control", style={"display": "none"})]
        ),

        # Left column: GA Map, State and County Results charts
        html.Div(
            id="left-column",
            className="eight columns",
            children=[
                html.Div(
                    id="state-graph",
                    children=[
						html.Div(id="state-wide",children=dcc.Graph(figure=state_results()),),
                        html.Div(id="county-wide",children=dcc.Graph(id = 'county-bar'),),
                        dcc.Graph(figure=generate_map(0,0,0)),
                    ], 
                ),
            ],            
        ),
		# Right column: County Select dropdown menu & Age, Gender, Race Charts
        html.Div(
            id = "right-column",
            className = "eight columns",
            children = [graphs()]+ [html.Div(["initial child"], id="graphs", style={"display": "none"})],   
        ),
    ],
)

# County Select call back
@app.callback(
    [Output("county-bar", "figure"), Output("age_histogram", "figure"), Output("gender_histogram", "figure"), Output("race_histogram", "figure")],
    [Input('county-drop-select','value')],
)

# County Select call back - update
def update_charts(dropdown_value):
    # Data
    county_results = results[(results['county_name'] == dropdown_value)].iloc[: , 1:].T
    county_results.reset_index(inplace=True)
    county_results.columns = ["Candidate", "Votes"]

    ageData = api.get_distribution(dropdown_value, 2016, 11, "age_grp", "voted")
    genderData = api.get_distribution(dropdown_value, 2016, 11, "gender", "voted")
    raceData = api.get_distribution(dropdown_value, 2016, 11, "race", "voted")
    
    # -- Countywide Results Chart
    countyBar = go.Figure(data = [go.Bar(x = county_results["Candidate"], y = county_results["Votes"])],
        layout=go.Layout(title = go.layout.Title(text = "Countywide Results")))
    
    countyBar.update_layout(autosize = True, width = 300, height = 250, margin = dict(l=65, r=50, b=0, t=30),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    # -- Age Histogram
    ageHist = px.histogram(ageData, x = "age_grp", y = "voted")
    ageHist.update_layout(autosize = True, width = 300, height = 250, margin = dict(l=50, r=50, b=0, t=10))

    # ------ Gender Histogram ------
    genderBar = px.histogram(genderData, x = "gender", y = "voted")
    genderBar.update_layout(autosize = True, width = 350, height = 190, margin = dict(l=50, r=50, b=0, t=10))
    
    # ------ Race Histogram ------
    raceHist = px.histogram(raceData, x = "race", y = "voted")
    raceHist.update_layout(autosize = True, width = 350, height = 230, margin = dict(l=50, r=50, b=10, t=10))
    
    return countyBar, ageHist, genderBar, raceHist

# ------ Run the server ------
if __name__ == "__main__":
    app.run_server(debug=True)

