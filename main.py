import pandas as pd
import networkx
import matplotlib.pyplot as plt
import numpy as np
from bokeh.io import output_notebook, show, save, curdoc
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, EdgesAndLinkedNodes, NodesAndLinkedEdges, LabelSet, TapTool, Div, CustomJS
from bokeh.plotting import figure
from bokeh.plotting import from_networkx
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.transform import linear_cmap
from networkx.algorithms import community
from bokeh.events import Tap

# def display_event(div, attributes=[]):
#     """
#     Function to build a suitable CustomJS to display the current event
#     in the div model.
#     """
#     style = 'float: left; clear: left; font-size: 13px'
#     return CustomJS(args=dict(div=div), code="""
#         const {to_string} = Bokeh.require("core/util/pretty")
#         const attrs = %s;
#         const args = [];
#         for (let i = 0; i<attrs.length; i++ ) {
#             const val = to_string(cb_obj[attrs[i]], {precision: 2})
#             args.push(attrs[i] + '=' + val)
#         }
#         const line = "<span style=%r><b>" + cb_obj.event_name + "</b>(" + args.join(", ") + ")</span>\\n";
#         const text = div.text.concat(line);
#         const lines = text.split("\\n")
#         if (lines.length > 35)
#             lines.shift();
#         div.text = lines.join("\\n");
#     """ % (attributes, style))

# def print_event(attributes=[]):
#     """
#     Function that returns a Python callback to pretty print the events.
#     """
#     def python_callback(event):
#         cls_name = event.__class__.__name__
#         attrs = ', '.join(['{attr}={val}'.format(attr=attr, val=event.__dict__[attr])
#                        for attr in attributes])
#         print(f"{cls_name}({attrs})")

#     return python_callback

def choose_node_outline_colors(nodes_clicked):
    outline_colors = []
    for node in G.nodes():
        if str(node) in nodes_clicked:
            outline_colors.append('pink')
        else:
            outline_colors.append('black')
    return outline_colors


def update_node_highlight(event):
    nodes_clicked_ints = source.selected.indices
    nodes_clicked = list(map(str, nodes_clicked_ints))
    source.data['line_color'] = choose_node_outline_colors(nodes_clicked)

# got_df = pd.read_csv('./sample-social-network-datasets\sample-datasets\game-of-thrones\got-edges.csv')
got_df = pd.read_csv('connections.csv')
nodes = pd.read_csv('nodes.csv')

service = nodes.Service
div = Div(width=1000)

for i in range(0,len(service)):
      service.loc[i] = service.loc[i].split(";")

service.index = nodes.Name

port = nodes.port
port.index = nodes.Name

repository = nodes.repository
repository.index = nodes.Name

service = pd.Series(service, index = nodes.Name).to_dict()
port = pd.Series(port, index = nodes.Name).to_dict()
repository = pd.Series(repository, index=nodes.Name).to_dict()

# print(service)

# print("Voy a imprimir")
# print(nodes)
# print(service)
# print(port)

G = networkx.from_pandas_edgelist(got_df, 'Source', 'Target', 'Weight')

degrees = dict(networkx.degree(G))
networkx.set_node_attributes(G, name='degree', values=degrees)
networkx.set_node_attributes(G, name='service', values = service)
networkx.set_node_attributes(G, name='port', values = port)
networkx.set_node_attributes(G, name="repository", values = repository)

#Pick a color palette — Blues8, Reds8, Purples8, Oranges8, Viridis8
node_highlight_color = 'blue'
edge_highlight_color = 'red'

#Choose attributes from G network to size and color by — setting manual size (e.g. 10) or color (e.g. 'skyblue') also allowed
size_by_this_attribute = 'adjusted_node_size'
color_by_this_attribute = 'modularity_color'

#Pick a color palette — Blues8, Reds8, Purples8, Oranges8, Viridis8
color_palette = Blues8

number_to_adjust_by = 10
adjusted_node_size = dict([(node, (degree*3)+number_to_adjust_by) for node, degree in networkx.degree(G)])
networkx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)

#Choose a title!
title = 'Mapa'

#Establish which categories will appear when hovering over each node
HOVER_TOOLTIPS = [
       ("Character", "@index"),
        ("Degree", "@degree"),
        ("Service", "@service"),
        ("Port", "@port"),
        ("Repositorio", "@repository")
]

#Create a plot — set dimensions, toolbar, and title
plot = figure(tooltips = HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
            x_range=Range1d(-10.1, 10.1), y_range=Range1d(-10.1, 10.1), title=title)

plot.add_tools(TapTool())

#Create a network graph object
# https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html
network_graph = from_networkx(G, networkx.spring_layout, scale=10, center=(0, 0))

source = network_graph.node_renderer.data_source

#Set node sizes and colors according to node degree (color as category from attribute)
network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=color_by_this_attribute)
#Set node highlight colors
network_graph.node_renderer.hover_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)
network_graph.node_renderer.selection_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)

#Set edge opacity and width
network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.3, line_width=1)
#Set edge highlight colors
network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)

#Highlight nodes and edges
network_graph.selection_policy = NodesAndLinkedEdges()
network_graph.inspection_policy = NodesAndLinkedEdges()

plot.renderers.append(network_graph)

#Add Labels
x, y = zip(*network_graph.layout_provider.graph_layout.values())
node_labels = list(G.nodes())
source = ColumnDataSource({'x': x, 'y': y, 'name': [node_labels[i] for i in range(len(x))]})
labels = LabelSet(x='x', y='y', text='name', source=source, background_fill_color='white', text_font_size='10px', background_fill_alpha=.7)
plot.renderers.append(labels)


callback = CustomJS(args=dict(source=source), code="""
    # const data = source.data
    # console.log(data)
    window.location.href = "https://www.youtube.com/";
""")

taptool = plot.select(type=TapTool)

# plot.on_event(Tap, update_node_highlight)

plot.js_on_event(Tap, callback)
# # plot.js_on_event(events.DoubleTap, display_event(div, attributes=point_attributes))
# # plot.js_on_event(events.Press,     display_event(div, attributes=point_attributes))

curdoc().add_root(plot)

show(plot)
#save(plot, filename=f"{title}.html")