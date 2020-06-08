from bokeh.layouts import column, row
from bokeh.models import Panel, Div
from vis_scripts.commons_util import generate_header_div, generate_spinner_div, show_spinner, hide_spinner


def home_page():
    div_spinner = generate_spinner_div()
    show_spinner(div_spinner)

    text = ("""<div class="header">
    <h1 style="font-size:30px;">Walmart Sales Data Visualization</h1>
    
    <p style="font-size:20px;">The purpose of the visualization is to understand the sales trend at different Walmart 
    stores and departments. Following are the details of visualizations in each of the tabs. </p>
    
    </div> 
    
        <div class="row"> <div class="column"> <h2 style="font-size:20px;">Tab 1: Sales Timeline</h2> <ul> <li><p 
        style="font-size:18px;">Shows the weekly, monthly, and quarterly sales trend of average sales for each store 
        and department.</p></li> </ul> </div> 
          
          <div class="column"> <h2 style="font-size:20px;">Tab 2: Scatter Plots</h2> <ul> <li><p 
          style="font-size:18px;">Shows the scatter plot to analyze the impact of time-dependent variables like 
          temperature, fuel price, CPI, unemployment on average sales of each store.</p></li> </ul> </div> 
          
          <div class="column">
            <h2 style="font-size:20px;">Tab 3: Trend with store size</h2>
            <ul>
            <li><p style="font-size:18px;">Shows the bar chart of every store's size and average sales.</p></li>
            </ul>
          </div>
        </div>
        
        <hr>
        
        <div class="row">
        <div class="column">
        
        <h2 style="font-size:18px;">Resources</h2>
        
        <ul> 
        <li><p style="font-size:15px;"><b>Dataset</b> used for this 
        project is available at <a href="https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting/data" 
        target="_blank">Kaggle</a>.</p></li>
        
        <li><p style="font-size:15px;"><b>GitHub Repository</b> for this 
        project can be found <a href="https://github.com/chikorita5/walmart-sales-data-visualization" 
        target="_blank">here</a>.</p></li>
        
        </ul> 
        </div>
        </div> 
    
    """)

    home_pag_div = Div(text=text, width=1400, height=300)

    hide_spinner(div_spinner)
    layout = column(home_pag_div)
    tab = Panel(child=layout, title='Home Page')
    return tab
