from bokeh.models import Div, Select

_spinner_text = """
<div class="loader">
<style scoped>
.loader {
    border: 16px solid #f3f3f3; /* Light grey */
    border-top: 16px solid #3498db; /* Blue */
    border-radius: 50%;
    width: 120px;
    height: 120px;
    animation: spin 2s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
} 
</style>
</div>
"""


def generate_header_div(header):
    return Div(
        text="""<br><h5 style="box-sizing: border-box; margin-top: 0px; margin-bottom: 0.5rem; font-family: 
            &quot;Nunito Sans&quot;, -apple-system, system-ui, &quot;Segoe UI&quot;, Roboto, &quot;Helvetica Neue&quot;, 
            Arial, sans-serif, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, &quot;Segoe UI Symbol&quot;; 
            font-weight: 300; color: rgb(26, 26, 26); font-size: 2rem; text-transform: uppercase; letter-spacing: 
            3px;">""" + header + """</h5><hr>""",
        width=1000, height=80, style={'text-align': 'center'})


def generate_spinner_div():
    return Div(text="", width=80, height=80)


def show_spinner(div_spinner):
    div_spinner.text = _spinner_text


def hide_spinner(div_spinner, display_text=""):
    if display_text != "":
        display_text = _replace_spinner_text_with_display_text(display_text)
    div_spinner.text = display_text


def generate_store_id_selector(dataset):
    store_id_options_int = sorted(dataset.Store.unique().tolist())
    store_id_options = list(map(str, store_id_options_int))
    return Select(title="Store Id:", value=store_id_options[0], options=store_id_options)


def _replace_spinner_text_with_display_text(text_to_display):
    return """<h6 style="box-sizing: border-box; margin-top: 0px; margin-bottom: 0.5rem; font-family: 
        &quot;Nunito Sans&quot;, -apple-system, system-ui, &quot;Segoe UI&quot;, Roboto, &quot;Helvetica Neue&quot;, 
        Arial, sans-serif, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, &quot;Segoe UI Symbol&quot;; 
        font-weight: 300; color: rgb(26, 26, 26); font-size: 2rem; text-transform: uppercase; letter-spacing: 
        3px;">""" + text_to_display + """</h6>"""
