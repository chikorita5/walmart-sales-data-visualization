from bokeh.layouts import column, row
from bokeh.models import Panel, ColumnDataSource, Range1d, HoverTool
from bokeh.plotting import figure

from vis_scripts.commons_util import generate_header_div, generate_spinner_div, show_spinner, hide_spinner, \
    generate_store_id_selector

selected_store_id = None


def scatter_plots(dataset):
    global selected_store_id

    div_heading = generate_header_div("Scatter Plots for Various Features")

    div_spinner = generate_spinner_div()

    show_spinner(div_spinner)

    store_id_selector = generate_store_id_selector(dataset)

    store_wise_dataset = {}
    for store_id in range(dataset['Store'].min(), dataset['Store'].max() + 1):
        store_wise_dataset[store_id] = dataset[dataset['Store'] == store_id]

    selected_store_id = store_id_selector.value

    # -----------------------------------------------------------------------------------------------------------------
    # -------------------------------------------- Scatter Plot Starts here -------------------------------------------

    def generate_scatter_plot_data(store_id, group_by_feature):
        store_weekly_dataset = store_wise_dataset[int(store_id)]
        store_weekly_dataset = store_weekly_dataset.sort_values(group_by_feature)
        store_avg_sales_by_grouped_feature = store_weekly_dataset.groupby(group_by_feature).agg(
            Store=('Store', 'first'),
            Avg_Sales=('Weekly_Sales', 'mean')
        )
        store_avg_sales_by_grouped_feature.reset_index(level=0, inplace=True)
        return store_avg_sales_by_grouped_feature

    def generate_scatter_plot_data_dict(store_avg_sales_by_feature, group_by_feature):
        data_dict = dict(
            avg_sales=store_avg_sales_by_feature.Avg_Sales.tolist()
        )
        data_dict[group_by_feature] = store_avg_sales_by_feature[group_by_feature].tolist()
        return data_dict

    def generate_title(group_by_feature):
        title_suffix = {
            "Fuel_Price": "Fuel Price",
            "CPI": "CPI	"
        }
        return "Avg Sales v/s " + title_suffix.get(group_by_feature, group_by_feature)

    def generate_x_axis_label(group_by_feature):
        x_axis_labels = dict(
            Temperature="Temperature in F",
            Fuel_Price="Fuel Price in $"
        )
        return x_axis_labels.get(group_by_feature, group_by_feature)

    def generate_x_range(store_avg_sales_by_grouped_feature, group_by_feature):
        if group_by_feature == "Temperature":
            start = 10 * (round(dataset[group_by_feature].min() // 10) - 1)
            end = 10 * (round(dataset[group_by_feature].max() / 10) + 1)
        else:
            start = (round(store_avg_sales_by_grouped_feature[group_by_feature].min()) - 1)
            end = (round(store_avg_sales_by_grouped_feature[group_by_feature].max()) + 1)
        return start, end

    def generate_tool_tip_key(group_by_feature):
        tool_tip_key = dict(
            Temperature="Temperature (F)",
            Fuel_Price="Fuel Price ($)"
        )
        return tool_tip_key.get(group_by_feature, group_by_feature)

    def generate_scatter_plot_figure_and_data_source(group_by_feature):
        store_avg_sales_by_grouped_feature = generate_scatter_plot_data(selected_store_id, group_by_feature)

        scatter_data_dict = generate_scatter_plot_data_dict(store_avg_sales_by_grouped_feature, group_by_feature)
        circle_data = ColumnDataSource(
            data=scatter_data_dict
        )

        (x_start_range, x_end_range) = generate_x_range(store_avg_sales_by_grouped_feature, group_by_feature)
        scatter_plot_figure = figure(
            title=generate_title(group_by_feature),
            x_range=Range1d(start=x_start_range, end=x_end_range),
            plot_width=700,
            plot_height=350,
            tools="box_zoom,reset"
        )
        scatter_plot_figure.xaxis.axis_label = generate_x_axis_label(group_by_feature)
        scatter_plot_figure.yaxis.axis_label = 'Avg Sales in USD'

        scatter_plot_circles = scatter_plot_figure.circle(
            source=circle_data,
            x=group_by_feature,
            y='avg_sales',
            size=15, color="green", alpha=0.5)

        # Adding hover tool
        scatter_hover = HoverTool(
            tooltips=[
                ('Avg Sales', '$' + '@avg_sales{0.00}'),
                (generate_tool_tip_key(group_by_feature), '@' + group_by_feature + '{0.00}')],
            mode='vline')
        scatter_plot_figure.add_tools(scatter_hover)

        scatter_plot_data_source = scatter_plot_circles.data_source
        return scatter_plot_figure, scatter_plot_data_source

    figures_and_data_sources_dict = dict(
        Temperature=generate_scatter_plot_figure_and_data_source("Temperature"),
        Fuel_Price=generate_scatter_plot_figure_and_data_source("Fuel_Price"),
        CPI=generate_scatter_plot_figure_and_data_source("CPI"),
        Unemployment=generate_scatter_plot_figure_and_data_source("Unemployment")
    )

    # --------------------------------------------- Scatter Plot Ends here --------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------

    hide_spinner(div_spinner)

    def clear_specific_plot_data_source(group_by_feature):
        data_source = figures_and_data_sources_dict.get(group_by_feature)[1]
        data_source.data = {k: [] for k in data_source.data}

    def update_specific_plot(updated_store_id, group_by_feature):

        updated_store_avg_sales_by_grouped_feature = generate_scatter_plot_data(updated_store_id, group_by_feature)

        if updated_store_avg_sales_by_grouped_feature is None:
            hide_spinner(div_spinner, "Sorry! Some of the data is not available")
            clear_specific_plot_data_source(group_by_feature)
            return

        scatter_plot_figure = figures_and_data_sources_dict.get(group_by_feature)[0]
        scatter_plot_data_source = figures_and_data_sources_dict.get(group_by_feature)[1]

        (updated_x_range_start, updated_x_range_end) = \
            generate_x_range(updated_store_avg_sales_by_grouped_feature, group_by_feature)

        scatter_plot_figure.x_range.start = updated_x_range_start
        scatter_plot_figure.x_range.end = updated_x_range_end

        updated_scatter_data_dict = generate_scatter_plot_data_dict(updated_store_avg_sales_by_grouped_feature, group_by_feature)
        scatter_plot_data_source.data = updated_scatter_data_dict

    def update_callback(attr, old, new):
        show_spinner(div_spinner)

        global selected_store_id

        updated_store_id = store_id_selector.value

        update_specific_plot(updated_store_id, "Temperature")
        update_specific_plot(updated_store_id, "Fuel_Price")
        update_specific_plot(updated_store_id, "CPI")
        update_specific_plot(updated_store_id, "Unemployment")

        selected_store_id = updated_store_id

        hide_spinner(div_spinner)

    store_id_selector.on_change("value", update_callback)

    layout = column(row(div_heading, div_spinner),
                    row(store_id_selector),
                    row(
                        figures_and_data_sources_dict.get("Temperature")[0],
                        figures_and_data_sources_dict.get("Fuel_Price")[0]
                    ),
                    row(
                        figures_and_data_sources_dict.get("CPI")[0],
                        figures_and_data_sources_dict.get("Unemployment")[0]
                    )
                    )
    tab = Panel(child=layout, title='Scatter Plots for Various Features')
    return tab
