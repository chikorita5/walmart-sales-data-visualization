import math

from bokeh.layouts import column, row
from bokeh.models import Panel, FactorRange, ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.transform import dodge
from vis_scripts.commons_util import generate_header_div, generate_spinner_div, show_spinner, hide_spinner


def store_size_bar_plot(dataset):

    div_heading = generate_header_div("Sales Trend with Store Size")
    div_spinner = generate_spinner_div()
    show_spinner(div_spinner)

    store_avg_sales = dataset.groupby("Store").agg(
        Avg_Sales=('Weekly_Sales', 'mean'),
        Size=('Size', 'first')
    )
    store_avg_sales.reset_index(level=0, inplace=True)
    store_avg_sales['Size'] = store_avg_sales['Size'].astype(str)

    store_avg_sales_trimmed = store_avg_sales[
        (store_avg_sales.Store != 36) &
        (store_avg_sales.Store != 37) &
        (store_avg_sales.Store != 44) &
        (store_avg_sales.Store != 33) &
        (store_avg_sales.Store != 38) &
        (store_avg_sales.Store != 42) &
        (store_avg_sales.Store != 19) &
        (store_avg_sales.Store != 24)]

    store_avg_sales_size_trimmed_data_dict = dict(
        store=store_avg_sales_trimmed.Store.tolist(),
        avg_sales=store_avg_sales_trimmed.Avg_Sales.tolist(),
        size=store_avg_sales_trimmed.Size.tolist()
    )

    pair_left_dict = dict(
        store=['24'],
        avg_sales=['18969.106500'],
        size=['203819']
    )

    pair_right_dict = dict(
        store=['19'],
        avg_sales=['20362.126734'],
        size=['203819']
    )

    tuple_center_dict = dict(
        store=['37', '42'],
        avg_sales=['10297.355026', '11443.370118'],
        size=['39910', '39690']
    )

    tuple_left_dict = dict(
        store=['36', '38'],
        avg_sales=['8584.412563', '7492.478460'],
        size=['39910', '39690']
    )

    tuple_right_dict = dict(
        store=['44', '33'],
        avg_sales=['6038.929814', '5728.414053'],
        size=['39910', '39690']
    )

    store_size_trend_figure = figure(
        title="Avg Sales v/s Store Size",
        x_range=FactorRange(*sorted(set(store_avg_sales['Size']), reverse=True)),
        plot_width=1400,
        plot_height=400,
        tools="box_zoom,reset"
    )
    store_size_trend_figure.xaxis.axis_label = 'Store Size'
    store_size_trend_figure.yaxis.axis_label = 'Avg Sales in USD'

    store_size_trend_figure.vbar(
        source=ColumnDataSource(data=store_avg_sales_size_trimmed_data_dict),
        x=dodge('size', 0.0, range=store_size_trend_figure.x_range), width=0.4, bottom=0,
        top='avg_sales', color="green")

    store_size_trend_figure.vbar(
        source=ColumnDataSource(data=tuple_center_dict),
        x=dodge('size', 0.0, range=store_size_trend_figure.x_range), width=0.2, bottom=0,
        top='avg_sales', color="green")

    store_size_trend_figure.vbar(
        source=ColumnDataSource(data=tuple_left_dict),
        x=dodge('size', -0.3, range=store_size_trend_figure.x_range), width=0.2, bottom=0,
        top='avg_sales', color="green")

    store_size_trend_figure.vbar(
        source=ColumnDataSource(data=tuple_right_dict),
        x=dodge('size', 0.3, range=store_size_trend_figure.x_range), width=0.2, bottom=0,
        top='avg_sales', color="green")

    store_size_trend_figure.vbar(
        source=ColumnDataSource(data=pair_left_dict),
        x=dodge('size', -0.2, range=store_size_trend_figure.x_range), width=0.3, bottom=0,
        top='avg_sales', color="green")

    store_size_trend_figure.vbar(
        source=ColumnDataSource(data=pair_right_dict),
        x=dodge('size', 0.2, range=store_size_trend_figure.x_range), width=0.3, bottom=0,
        top='avg_sales', color="green")

    # Adding hover tool
    store_size_trend_hover = HoverTool(
        tooltips=[
            ('Store', '@store'),
            ('Avg Sales', '$' + '@avg_sales{int}')],
        mode='vline')
    store_size_trend_figure.add_tools(store_size_trend_hover)

    store_size_trend_figure.x_range.range_padding = 0.05
    store_size_trend_figure.xgrid.grid_line_color = None
    store_size_trend_figure.xaxis.major_label_orientation = math.pi / 4

    hide_spinner(div_spinner)

    layout = column(row(div_heading, div_spinner),
                    store_size_trend_figure)
    tab = Panel(child=layout, title='Sales Trend with Store Size')
    return tab
