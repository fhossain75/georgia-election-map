# pip install plotly plotly-geo geopandas pyshp shapely

import plotly.figure_factory as ff

import numpy as np
import pandas as pd

df_sample = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/minoritymajority.csv')
df_sample_r = df_sample[df_sample['STNAME'] == 'Georgia']

values = df_sample_r['TOT_POP'].tolist()
fips = df_sample_r['FIPS'].tolist()

#endpts = list(np.mgrid[min(values):max(values):4j])
colorscale = ["#eafcfd","#b7e0e4","#85c5d3","#60a7c7","#4989bc",
			  "#3e6ab0","#3d4b94","#323268","#1d1d3b","#030512"]
binning_endpoints = list(np.linspace(1, 12, len(colorscale) - 1))
colorscale = ["#f7fbff", "#ebf3fb", "#deebf7", "#d2e3f3", "#c6dbef",
            "#b3d2e9", "#9ecae1", "#85bcdb", "#6baed6", "#57a0ce",
            "#4292c6", "#3082be", "#2171b5", "#1361a9", "#08519c",
            "#0b4083","#08306b"]
fig = ff.create_choropleth(
    fips=fips, values=values, scope=['Georgia'], show_state_data=True,
    colorscale=colorscale, binning_endpoints=endpts, asp=2.0 
	show_hover = True,
	round_legend_values=True,
    plot_bgcolor='rgb(229,229,229)',
    paper_bgcolor='rgb(229,229,229)',
    legend_title='Population by County',
    county_outline={'color': 'rgb(255,255,255)', 'width': 0.5},
    exponent_format=True,
)
fig.layout.template = None
fig.show()