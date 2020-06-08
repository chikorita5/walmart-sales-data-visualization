# Run Command
# bokeh serve --show main.py

import pandas as pd

# Bokeh basics
from bokeh.io import curdoc
from bokeh.layouts import row
from bokeh.models.widgets import Tabs

from vis_scripts.home_page import home_page
from vis_scripts.sales_timeline import sales_timeline
from vis_scripts.scatter_plots import scatter_plots
from vis_scripts.store_size_bar_plot import store_size_bar_plot

stores = pd.read_csv("myapp/dataset/stores.csv")
features = pd.read_csv("myapp/dataset/features.csv")
train = pd.read_csv("myapp/dataset/train.csv")
merged = pd.read_csv("myapp/dataset/train_merged_cleaned.csv")

# Create each of the tabs
home_page_tab = home_page()
sales_timeline_tab = sales_timeline(merged)
scatter_plots_tab = scatter_plots(merged)
store_size_bar_plot_tab = store_size_bar_plot(merged)

# Put all the tabs into one application
tabs = Tabs(tabs=[home_page_tab, sales_timeline_tab, scatter_plots_tab, store_size_bar_plot_tab])

home_layout = row(tabs)

# Put the tabs in the current document for display
curdoc().add_root(home_layout)
