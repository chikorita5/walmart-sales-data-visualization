import calendar
import math
import pandas as pd

from bokeh.layouts import column, row
from bokeh.models import Panel, Div, Select, ColumnDataSource, HoverTool, FactorRange, Range1d, LinearAxis, \
    RadioButtonGroup
from bokeh.plotting import figure

from vis_scripts.commons_util import generate_header_div, generate_spinner_div, show_spinner, hide_spinner, \
    generate_store_id_selector

selected_store_id = None
selected_dept_id = None


def sales_timeline(dataset):
    global selected_store_id, selected_dept_id

    div_heading = generate_header_div("Weekly, Monthly, & Quarterly Sales Timeline")

    div_spinner = generate_spinner_div()

    show_spinner(div_spinner)

    store_id_selector = generate_store_id_selector(dataset)

    dept_id_options_int = sorted(dataset.Dept.unique().tolist())
    dept_id_options = list(map(str, dept_id_options_int))
    dept_id_selector = Select(title="Department Id:", value=dept_id_options[0], options=dept_id_options)

    div_toggle_button = Div(text="Display CPI", width=80, height=7)
    cpi_toggle_button = RadioButtonGroup(labels=["Off", "On"], active=0)

    store_wise_dataset = {}
    for store_id in range(dataset['Store'].min(), dataset['Store'].max() + 1):
        store_wise_dataset[store_id] = dataset[dataset['Store'] == store_id]

    selected_store_id = store_id_selector.value
    selected_dept_id = dept_id_selector.value

    # -----------------------------------------------------------------------------------------------------------------
    # ---------------------------------------- CPI Line Plot Data Starts Here -----------------------------------------

    def get_cpi_line_plot_data_dict(sales_line_plot_data):
        return dict(sales_line_plot_data.data)

    # ----------------------------------------- CPI Line Plot Data Ends Here ------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # -------------------------------------------- Weekly Plot Starts Here --------------------------------------------

    def get_weekly_sales_data(store_id, dept_id):
        store_weekly_dataset = store_wise_dataset[int(store_id)]
        store_dept_weekly_dataset = \
            store_weekly_dataset[store_weekly_dataset['Dept'] == int(dept_id)]

        if store_dept_weekly_dataset.empty:
            return None, None

        def date_formatter(single_row, date_type):
            year, month, day = single_row['Date'].split('-')

            if date_type == 'y':
                return year
            if date_type == 'm':
                return int(month)
            if date_type == 'd':
                return int(day)

        store_dept_weekly_dataset['year_month_week'] = store_dept_weekly_dataset.apply(
            lambda row: (
                date_formatter(row, 'y'),
                calendar.month_abbr[date_formatter(row, 'm')],
                str(math.ceil(date_formatter(row, 'd') / 7.0))), axis=1)

        store_dept_sales_on_holiday_dataset = store_dept_weekly_dataset.filter(
            ['Date', 'year_month_week', 'Weekly_Sales', 'IsHoliday', 'CPI'], axis=1)
        store_dept_sales_on_holiday_dataset = store_dept_sales_on_holiday_dataset[
            store_dept_sales_on_holiday_dataset['IsHoliday'] == True]

        return store_dept_weekly_dataset, store_dept_sales_on_holiday_dataset

    def get_weekly_sales_line_plot_data_dict(store_dept_weekly_dataset):
        return dict(
            year_month_week=store_dept_weekly_dataset.year_month_week.tolist(),
            weekly_sales=store_dept_weekly_dataset.Weekly_Sales.tolist(),
            is_holiday=store_dept_weekly_dataset.IsHoliday.tolist(),
            cpi=store_dept_weekly_dataset.CPI.tolist()
        )

    def get_weekly_sales_circle_plot_data_dict(store_dept_sales_on_holiday_dataset):
        return dict(
            year_month_week=store_dept_sales_on_holiday_dataset.year_month_week.tolist(),
            weekly_sales=store_dept_sales_on_holiday_dataset.Weekly_Sales.tolist(),
            is_holiday=store_dept_sales_on_holiday_dataset.IsHoliday.tolist(),
            cpi=store_dept_sales_on_holiday_dataset.CPI.tolist()
        )

    selected_store_dept_weekly_dataset, selected_store_dept_sales_on_holiday_dataset = \
        get_weekly_sales_data(selected_store_id, selected_dept_id)

    weekly_sales_line_plot_data = ColumnDataSource(
        data=get_weekly_sales_line_plot_data_dict(selected_store_dept_weekly_dataset)
    )

    weekly_cpi_line_plot_data = ColumnDataSource(data=get_cpi_line_plot_data_dict(weekly_sales_line_plot_data))

    weekly_sales_circle_plot_data = ColumnDataSource(
        data=get_weekly_sales_circle_plot_data_dict(selected_store_dept_sales_on_holiday_dataset)
    )

    weekly_sales_figure = figure(
        title="Weekly Sales",
        x_range=FactorRange(*selected_store_dept_weekly_dataset.year_month_week.tolist()),
        plot_width=1400,
        plot_height=300,
        tools="box_zoom,reset")

    weekly_sales_figure.yaxis.axis_label = 'Sales in USD'

    weekly_sales_figure.extra_y_ranges['CPI'] = Range1d(start=0, end=300)
    weekly_sales_figure.add_layout(LinearAxis(y_range_name='CPI', axis_label='CPI'), 'right')

    weekly_sales_line_plot = weekly_sales_figure.line(
        source=weekly_sales_line_plot_data,
        x='year_month_week',
        y='weekly_sales',
        legend_label='Sales',
        line_width=2, color="red")

    weekly_sales_circle_plot = weekly_sales_figure.circle(
        source=weekly_sales_circle_plot_data,
        x='year_month_week',
        y='weekly_sales',
        legend_label='Holiday',
        size=10,
        fill_color="blue", line_color="red",
        alpha=0.7)

    weekly_cpi_line_plot = weekly_sales_figure.line(
        source=weekly_cpi_line_plot_data,
        x='year_month_week',
        y='cpi',
        legend_label='CPI',
        y_range_name='CPI',
        line_width=2, color="green")

    # Adding hover tool
    weekly_sales_hover = HoverTool(
        tooltips=[
            ('Holiday', '@is_holiday'),
            ('Sales', '$' + '@weekly_sales{0.00}'),
            ('CPI', '@cpi')],
        mode='vline')
    weekly_sales_figure.add_tools(weekly_sales_hover)

    weekly_sales_figure.xgrid.grid_line_color = None

    weekly_sales_line_plot_data_source = weekly_sales_line_plot.data_source
    weekly_sales_circle_plot_data_source = weekly_sales_circle_plot.data_source
    weekly_cpi_line_plot_data_source = weekly_cpi_line_plot.data_source

    # --------------------------------------------- Weekly Plot Ends Here ---------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # ----------------------------------------- Monthly Avg Plot Starts Here ------------------------------------------

    def get_monthly_avg_sales_data(store_dept_weekly_dataset):

        if store_dept_weekly_dataset.empty:
            return store_dept_weekly_dataset

        store_dept_avg_monthly_dataset = store_dept_weekly_dataset
        store_dept_avg_monthly_dataset['Date'] = pd.to_datetime(
            store_dept_avg_monthly_dataset['Date'])
        store_dept_avg_monthly_dataset.index = pd.DatetimeIndex(
            store_dept_avg_monthly_dataset['Date'])

        store_dept_avg_monthly_dataset = store_dept_avg_monthly_dataset.groupby(
            pd.Grouper(freq="M")).agg(
            Store=('Store', 'first'),
            Dept=('Dept', 'first'),
            Avg_Monthly_Sales=('Weekly_Sales', 'mean'),
            Type=('Type', 'first'),
            Size=('Size', 'first'),
            Avg_Temperature=('Temperature', 'mean'),
            Avg_Fuel_Price=('Fuel_Price', 'mean'),
            Avg_CPI=('CPI', 'mean'),
            Unemployment=('Unemployment', 'first')
        )
        store_dept_avg_monthly_dataset.reset_index(level=0, inplace=True)
        store_dept_avg_monthly_dataset['Date'] = store_dept_avg_monthly_dataset['Date'].dt.strftime(
            '%Y-%m')

        def date_formatter(single_row, date_type):
            year, month = single_row['Date'].split('-')

            if date_type == 'y':
                return year
            if date_type == 'm':
                return int(month)

        store_dept_avg_monthly_dataset['year_month'] = store_dept_avg_monthly_dataset.apply(
            lambda row: (date_formatter(row, 'y'), calendar.month_abbr[date_formatter(row, 'm')]), axis=1)

        return store_dept_avg_monthly_dataset

    def get_monthly_sales_line_plot_data_dict(store_dept_avg_monthly_dataset):
        return dict(
            year_month=store_dept_avg_monthly_dataset.year_month.tolist(),
            monthly_avg_sales=store_dept_avg_monthly_dataset.Avg_Monthly_Sales.tolist(),
            avg_cpi=store_dept_avg_monthly_dataset.Avg_CPI.tolist()
        )

    selected_store_dept_avg_monthly_dataset = get_monthly_avg_sales_data(selected_store_dept_weekly_dataset)

    monthly_sales_line_plot_data = ColumnDataSource(
        data=get_monthly_sales_line_plot_data_dict(selected_store_dept_avg_monthly_dataset)
    )

    monthly_cpi_line_plot_data = ColumnDataSource(data=get_cpi_line_plot_data_dict(monthly_sales_line_plot_data))

    monthly_sales_figure = figure(
        title="Monthly Avg Sales",
        x_range=FactorRange(*selected_store_dept_avg_monthly_dataset.year_month.tolist()),
        plot_width=1400,
        plot_height=300,
        tools="box_zoom,reset")

    monthly_sales_figure.yaxis.axis_label = 'Sales in USD'

    monthly_sales_figure.extra_y_ranges['CPI'] = Range1d(start=0, end=300)
    monthly_sales_figure.add_layout(LinearAxis(y_range_name='CPI', axis_label='CPI'), 'right')

    monthly_sales_line_plot = monthly_sales_figure.line(
        source=monthly_sales_line_plot_data,
        x='year_month',
        y='monthly_avg_sales',
        legend_label='Sales',
        line_width=2, color="red")

    monthly_cpi_line_plot = monthly_sales_figure.line(
        source=monthly_cpi_line_plot_data,
        x='year_month',
        y='avg_cpi',
        legend_label='CPI',
        y_range_name='CPI',
        line_width=2, color="green")

    monthly_sales_hover = HoverTool(
        tooltips=[
            ('Avg Sales', '$' + '@monthly_avg_sales{0.00}'),
            ('Avg CPI', '@avg_cpi')],
        mode='vline')
    monthly_sales_figure.add_tools(monthly_sales_hover)

    monthly_sales_figure.xgrid.grid_line_color = None

    monthly_sales_line_plot_data_source = monthly_sales_line_plot.data_source
    monthly_cpi_line_plot_data_source = monthly_cpi_line_plot.data_source

    # ------------------------------------------ Monthly Avg Plot Ends Here -------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # ---------------------------------------- Quarterly Avg Plot Starts Here -----------------------------------------

    def get_quarterly_avg_sales_data(store_dept_weekly_dataset):
        store_dept_avg_quarterly_dataset = store_dept_weekly_dataset
        store_dept_avg_quarterly_dataset['Date'] = pd.to_datetime(
            store_dept_avg_quarterly_dataset['Date'])
        store_dept_avg_quarterly_dataset.index = pd.DatetimeIndex(
            store_dept_avg_quarterly_dataset['Date'])

        store_dept_avg_quarterly_dataset = store_dept_avg_quarterly_dataset.groupby(
            pd.Grouper(freq="Q")).agg(
            Store=('Store', 'first'),
            Dept=('Dept', 'first'),
            Avg_Quarterly_Sales=('Weekly_Sales', 'mean'),
            Type=('Type', 'first'),
            Size=('Size', 'first'),
            Avg_Quarterly_CPI=('CPI', 'mean')
        )
        store_dept_avg_quarterly_dataset.reset_index(level=0, inplace=True)
        store_dept_avg_quarterly_dataset['Date'] = store_dept_avg_quarterly_dataset[
            'Date'].dt.strftime('%Y-%m')

        def date_formatter(single_row, date_type):
            year, month = single_row['Date'].split('-')

            if date_type == 'y':
                return year
            if date_type == 'm':
                return int(month)
            if date_type == 'q':
                return "Q" + str(math.ceil(int(month) / 3.0))

        store_dept_avg_quarterly_dataset['year_quarter'] = store_dept_avg_quarterly_dataset.apply(
            lambda row: (date_formatter(row, 'y'), date_formatter(row, 'q')), axis=1)

        return store_dept_avg_quarterly_dataset

    def get_quarterly_sales_line_plot_data(store_dept_avg_quarterly_dataset):
        return dict(
            year_quarter=store_dept_avg_quarterly_dataset.year_quarter.tolist(),
            quarterly_avg_sales=store_dept_avg_quarterly_dataset.Avg_Quarterly_Sales.tolist(),
            quarterly_avg_cpi=store_dept_avg_quarterly_dataset.Avg_Quarterly_CPI.tolist()
        )

    selected_store_dept_avg_quarterly_dataset = get_quarterly_avg_sales_data(selected_store_dept_weekly_dataset)

    quarterly_sales_line_plot_data = ColumnDataSource(
        data=get_quarterly_sales_line_plot_data(selected_store_dept_avg_quarterly_dataset)
    )

    quarterly_cpi_line_plot_data = ColumnDataSource(data=get_cpi_line_plot_data_dict(quarterly_sales_line_plot_data))

    quarterly_sales_figure = figure(
        title="Quarterly Avg Sales",
        x_range=FactorRange(*selected_store_dept_avg_quarterly_dataset.year_quarter.tolist()),
        plot_width=1400,
        plot_height=300,
        tools="box_zoom,reset")

    quarterly_sales_figure.yaxis.axis_label = 'Sales in USD'

    quarterly_sales_figure.extra_y_ranges['CPI'] = Range1d(start=0, end=300)
    quarterly_sales_figure.add_layout(LinearAxis(y_range_name='CPI', axis_label='CPI'), 'right')

    quarterly_sales_line_plot = quarterly_sales_figure.line(
        source=quarterly_sales_line_plot_data,
        x='year_quarter',
        y='quarterly_avg_sales',
        legend_label='Sales',
        line_width=2, color="red")

    quarterly_cpi_line_plot = quarterly_sales_figure.line(
        source=quarterly_cpi_line_plot_data,
        x='year_quarter',
        y='quarterly_avg_cpi',
        legend_label='CPI',
        y_range_name='CPI',
        line_width=2, color="green")

    quarterly_sales_hover = HoverTool(
        tooltips=[
            ('Avg Sales', '$' + '@quarterly_avg_sales{0.00}'),
            ('Avg CPI', '@quarterly_avg_cpi')],
        mode='vline')
    quarterly_sales_figure.add_tools(quarterly_sales_hover)

    quarterly_sales_figure.xgrid.grid_line_color = None

    quarterly_sales_line_plot_data_source = quarterly_sales_line_plot.data_source
    quarterly_cpi_line_plot_data_source = quarterly_cpi_line_plot.data_source

    # ----------------------------------------- Quarterly Avg Plot Ends Here ------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------

    hide_spinner(div_spinner)

    def clear_cpi_plot_data_sources():
        weekly_cpi_line_plot_data_source.data = {k: [] for k in weekly_cpi_line_plot_data_source.data}
        monthly_cpi_line_plot_data_source.data = {k: [] for k in monthly_cpi_line_plot_data_source.data}
        quarterly_cpi_line_plot_data_source.data = {k: [] for k in quarterly_cpi_line_plot_data_source.data}

    # -----------------------------------------------------------------------------------------------------------------
    # ------------------------------------------ CPI Plots Default Starts here ----------------------------------------

    # Clear CPI plot if cpi toggle button is set to off by default
    if cpi_toggle_button.active == 0:
        clear_cpi_plot_data_sources()

    # -------------------------------------------- CPI Plots Default Ends here ----------------------------------------
    # -----------------------------------------------------------------------------------------------------------------

    def clear_all_plot_data_sources():
        weekly_sales_line_plot_data_source.data = {k: [] for k in weekly_sales_line_plot_data_source.data}
        weekly_sales_circle_plot_data_source.data = {k: [] for k in weekly_sales_circle_plot_data_source.data}
        monthly_sales_line_plot_data_source.data = {k: [] for k in monthly_sales_line_plot_data_source.data}
        quarterly_sales_line_plot_data_source.data = {k: [] for k in quarterly_sales_line_plot_data_source.data}
        clear_cpi_plot_data_sources()

    def update_cpi_plots():
        weekly_cpi_line_plot_data_source.data = dict(weekly_sales_line_plot_data.data)
        monthly_cpi_line_plot_data_source.data = dict(monthly_sales_line_plot_data.data)
        quarterly_cpi_line_plot_data_source.data = dict(quarterly_sales_line_plot_data.data)

    def update_all_plots(attr, old, new):

        show_spinner(div_spinner)

        global selected_store_id, selected_dept_id

        old_store_id = selected_store_id
        old_dept_id = selected_dept_id

        updated_store_id = store_id_selector.value
        updated_dept_id = dept_id_selector.value

        # -------------------------------------------------------------------------------------------------------------
        # ----------------------------------------- Weekly Plot Update Starts Here ------------------------------------

        new_selected_store_dept_weekly_dataset, new_selected_store_dept_weekly_sales_on_holiday_dataset = \
            get_weekly_sales_data(updated_store_id, updated_dept_id)

        if new_selected_store_dept_weekly_dataset is None:
            hide_spinner(div_spinner, "Sorry! Data not available")
            clear_all_plot_data_sources()
            return

        updated_weekly_sales_line_plot_data_dict = \
            get_weekly_sales_line_plot_data_dict(new_selected_store_dept_weekly_dataset)

        updated_weekly_circle_plot_data_dict = \
            get_weekly_sales_circle_plot_data_dict(new_selected_store_dept_weekly_sales_on_holiday_dataset)

        weekly_sales_figure.x_range.factors = new_selected_store_dept_weekly_dataset.year_month_week.tolist()

        weekly_sales_line_plot_data_source.data = updated_weekly_sales_line_plot_data_dict
        weekly_sales_circle_plot_data_source.data = updated_weekly_circle_plot_data_dict

        # ------------------------------------------ Weekly Plot Update Ends Here -------------------------------------
        # -------------------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------------------
        # ---------------------------------------- Monthly Avg Plot Update Starts Here --------------------------------

        new_selected_store_dept_avg_monthly_dataset = \
            get_monthly_avg_sales_data(new_selected_store_dept_weekly_dataset)

        updated_monthly_sales_line_plot_data_dict = \
            get_monthly_sales_line_plot_data_dict(new_selected_store_dept_avg_monthly_dataset)

        monthly_sales_figure.x_range.factors = new_selected_store_dept_avg_monthly_dataset.year_month.tolist()

        monthly_sales_line_plot_data_source.data = updated_monthly_sales_line_plot_data_dict

        # ----------------------------------------- Monthly Avg Plot Update Ends Here ---------------------------------
        # -------------------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------------------
        # --------------------------------------- Quarterly Avg Plot Update Starts Here -------------------------------

        new_selected_store_dept_avg_quarterly_dataset = \
            get_quarterly_avg_sales_data(new_selected_store_dept_weekly_dataset)

        updated_quarterly_sales_line_plot_data_dict = \
            get_quarterly_sales_line_plot_data(new_selected_store_dept_avg_quarterly_dataset)

        quarterly_sales_figure.x_range.factors = new_selected_store_dept_avg_quarterly_dataset.year_quarter.tolist()

        quarterly_sales_line_plot_data_source.data = updated_quarterly_sales_line_plot_data_dict

        # ---------------------------------------- Quarterly Avg Plot Update Ends Here --------------------------------
        # -------------------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------------------
        # ------------------------------------------ CPI Plots Update Starts here -------------------------------------

        update_cpi_plots()

        # Clear CPI plot if cpi toggle button is set to off
        if cpi_toggle_button.active == 0:
            clear_cpi_plot_data_sources()

        # ------------------------------------------- CPI Plots Update Ends here --------------------------------------
        # -------------------------------------------------------------------------------------------------------------

        selected_store_id = updated_store_id
        selected_dept_id = updated_dept_id

        hide_spinner(div_spinner)

    def toggle_cpi_plot(attr, old, new):

        show_spinner(div_spinner)

        if cpi_toggle_button.active == 0:
            clear_cpi_plot_data_sources()

        if cpi_toggle_button.active == 1:
            weekly_cpi_line_plot_data_source.data = get_cpi_line_plot_data_dict(weekly_sales_line_plot_data)
            monthly_cpi_line_plot_data_source.data = get_cpi_line_plot_data_dict(monthly_sales_line_plot_data)
            quarterly_cpi_line_plot_data_source.data = get_cpi_line_plot_data_dict(quarterly_sales_line_plot_data)

        hide_spinner(div_spinner)

    store_id_selector.on_change("value", update_all_plots)
    dept_id_selector.on_change("value", update_all_plots)

    cpi_toggle_button.on_change('active', toggle_cpi_plot)

    layout = column(row(div_heading, div_spinner),
                    row(
                        store_id_selector,
                        dept_id_selector,
                        column(div_toggle_button, cpi_toggle_button)
                    ),
                    weekly_sales_figure,
                    monthly_sales_figure,
                    quarterly_sales_figure)
    tab = Panel(child=layout, title='Weekly, Monthly, & Quarterly Sales Timeline')
    return tab
