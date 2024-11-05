import dash_mantine_components as dmc
from dash import Output, Input, html, callback
import dash

def create_dash_application(flask_app):
    dash_app = dash.Dash(server=flask_app,name="Dashboard",url_base_pathname="/dash/")

    dash_app.layout = html.Div(
        [
            dmc.MultiSelect(
                label="Select frameworks",
                placeholder="Select all you like!",
                id="framework-multi-select",
                value=["ng", "vue"],
                data=[
                    {"value": "react", "label": "React"},
                    {"value": "ng", "label": "Angular"},
                    {"value": "svelte", "label": "Svelte"},
                    {"value": "vue", "label": "Vue"},
                ],
                w=400,
                mb=10,
            ),
            dmc.Text(id="multi-selected-value"),
        ]
    )

    return dash_app


@callback(
    Output("multi-selected-value", "children"), Input("framework-multi-select", "value")
)
def select_value(value):
    return ", ".join(value)