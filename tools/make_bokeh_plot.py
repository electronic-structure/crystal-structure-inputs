from os.path import dirname, join

import numpy as np
import pandas as pd

from bokeh.plotting import figure, show
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, Div, BoxSelectTool
from bokeh.models.widgets import Slider, Select, TextInput, MultiSelect, RadioButtonGroup
from bokeh.io import curdoc

desc = Div(text="Interactive benchmark viewer for QE", width=800)

runs = pd.read_pickle("info.pkl")
#gen colors
color_list = ["#9c602e","#6764cf","#5cbb4a","#a959cc","#abb741","#c94daa", \
"#62bb82","#e44484","#3fbfbc","#ce4b2a","#5ca5d9","#d4a337","#6279c1", \
"#dd8237","#cc92df","#648a37","#b23972","#35794a","#cd3b4a","#827831", \
"#985891","#d1a770","#e285a4","#e17b6a","#a54c5a"]

runs['color'] = '#000000'
runs['label'] = ''

axis_map = {
    "MPI": "NMpi",
    "Cores": "NCores",
    "OMP": "NOmp",
    "K points" : 'Nk', 
    "# electrons": 'Nelectrons', 
    "KS States": 'Nksstates'
}

for v in runs.columns:
    if not(v in axis_map.values()):
        axis_map[str(v)]=str(v)
    
# Select unique values and populate interactive widgets
app_list = runs['AppName'].unique().tolist()
app_select = MultiSelect(title="App:", value=app_list,
                           options=app_list)

ver_list = runs['Version'].unique().tolist()
ver_select = MultiSelect(title="Version:", value=ver_list,
                           options=ver_list)

system_list = runs['System'].unique().tolist()
sys_select = MultiSelect(title="System:", value=system_list,
                           options=system_list)

input_list = runs['InputName'].unique().tolist()
input_select = MultiSelect(title="Input:", value=input_list,
                           options=input_list)

x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="MPI")
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="electrons_WALL")

all_best_group = RadioButtonGroup(labels=["All", "Best"], active=0)

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], color=[], npool=[], nbg=[], ndiag=[], nomp=[], label=[]))

hover = HoverTool(tooltips=[
    ("Pools", "@npool"),
    ("BG", "@nbg"),
    ("Diag", "@ndiag"),
    ("OMP", "@nomp")
])

p = figure(plot_height=600, plot_width=700, title="", toolbar_location="below", \
            toolbar_sticky=False, tools="pan,wheel_zoom,box_zoom,reset") #x_axis_type="log")
p.add_tools(hover)
p.circle(x="x", y="y", source=source, size=7, color="color",  legend='label', line_color=None)


def select_benchmarks(x_name, y_name):
    """
    Selects subspace of benchmarks
    """
    selected = runs[
        (runs[y_name] >= 0) &
        (runs[x_name] >= 0) 
    ]
    # merge these into one line
    selected = selected[selected.AppName.isin(app_select.value) & \
                        selected.Version.isin(ver_select.value) & \
                        selected.InputName.isin(input_select.value) & \
                        selected.System.isin(sys_select.value)]
    
    # generate labels
    selected.label = selected['InputName']
    for v in ['AppName','Version','System']:
        if selected[v].nunique() > 1:
            selected.label = selected[['label', v]].apply(lambda x: ' '.join(x), axis=1)
    
    # generate colors
    i = 0
    for kk,vv in selected.groupby(['InputName','AppName','Version','System']):
        selected.loc[vv.index,'color']=color_list[i%len(color_list)]
        i += 1

    # only leave best if needed                        
    if (all_best_group.active == 1):
        i = selected.groupby([x_name, 'InputName', 'System'])[y_name].idxmin()
        selected = selected.loc[i]

    return selected


def update():
    #print(curdoc().session_context.request.arguments)
    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]
    
    df = select_benchmarks(x_name,y_name)

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d benchmarks selected" % len(df)

    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        color=df['color'],
        npool=df['NPool'],
        nbg=df['NBgrp'],
        nomp=df['NOmp'],
        ndiag=df['NDiag'],
        label=df['label']
    )

controls = [x_axis, y_axis,input_select,sys_select, app_select, ver_select, all_best_group]

for control in controls:
    if control != all_best_group:
        control.on_change('value', lambda attr, old, new: update())
    else:
        control.on_change('active', lambda attr, old, new: update())

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [desc],
    [inputs, p],
], sizing_mode=sizing_mode)

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "QE Benchmark View"

