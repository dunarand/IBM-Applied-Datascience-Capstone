import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the data (from module-1)
spacex_df = pd.read_csv('./spacex_launch_dash.csv')

min_payload = 0
max_payload = int(spacex_df['Payload Mass (kg)'].max())

# Create the app
app = dash.Dash(__name__)

# Create the layout
app.layout = html.Div(children = [
    html.H1(
        'SpaceX Launches',
        style = {
            'font-family': 'Helvetica (sans-serif)',
            'textAlign': 'center',
            'color': '#302f2f',
            'font-size': 32
        }
    ),
    html.Div(
        dcc.Dropdown(
            id ='site-dropdown',
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                {
                    'label': 'Cape Canaveral Space Force Station LC-40',
                    'value': 'CCAFS LC-40'
                },
                {
                    'label': 'Cape Canaveral Space Force Station SLC-40',
                    'value': 'CCAFS SLC-40'
                },
                {
                    'label': 'Kennedy Space Center LC-39A',
                    'value': 'KSC LC-39A'
                },
                {
                    'label': 'Vandenberg AFB SLC-4E',
                    'value': 'VAFB SLC-4E'
                }
            ],
            value='ALL',
            placeholder='Select a Launch Site',
            searchable=True,
            style = {
                'width': '75%', 'padding': '0px', 'font-size': '18px',
                'textAlign': 'center', 'margin': '0 auto'
            }
        ),
        style = {
            'display': 'flex', 'justify-content': 'center',
            'align-items': 'center', 'textAlign': 'center'
        }
    ),
    html.Div(
        dcc.Graph(
            id='success-pie-chart'
        ),
        style = {
            'display': 'flex', 'justify-content': 'center',
            'align-items': 'center', 'textAlign': 'center'
        }
    ),
    html.Div([
        html.H2(
            id = 'payload-range',
            children = f'Payload Range (kg): {min_payload} - {max_payload}',
            style = {
                'font-family': 'Helvetica (sans-serif)',
                'textAlign': 'center',
                'color': '#302f2f',
                'font-size': 16
            }
        ),
        dcc.RangeSlider(
            id = 'payload-slider',
            min = min_payload, max = max_payload,
            step = (max_payload - min_payload) / 100,
            marks = {
                i: str(i) for i in \
                range(min_payload, max_payload + 1, (max_payload - min_payload) // 10)
            },
            value = [min_payload, max_payload]
            )
    ], style = {
        'width': '59%', 'margin': '0 auto', 'textAlign': 'center'
        }
    ),
    html.Div(
        dcc.Graph(
            id = 'success-payload-scatter-chart'
        ),
        style = {
            'display': 'flex', 'justify-content': 'center',
            'align-items': 'center', 'textAlign': 'center'
        }
    )
    ],
    style = {
        'max-width': '85%', 'margin': '0 auto', 'padding': '20px'
    }
)

# Callback 1: Update the Payload Range text (HTML)
@app.callback(
    Output(component_id='payload-range', component_property='children'),
    [Input(component_id='payload-slider', component_property='value')]
)
def update_payload_range(selected_range):
    min_range, max_range = selected_range
    payload_range_text = f'Payload Range (kg): {min_range} - {max_range}'
    return payload_range_text

# Callback 2: Update the Pie Chart based on selected site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_pie_chart(entered_site, selected_range):
    _min_payload, _max_payload = selected_range
    filtered_df = spacex_df[
        (_min_payload <= spacex_df['Payload Mass (kg)']) &
        (spacex_df['Payload Mass (kg)'] <= _max_payload)
    ]
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class',
                     names='Launch Site',
                     title='Launch Success by Site')
        fig.update_traces(hovertemplate='Site: %{label}<br>Count: %{value}<extra></extra>')
    else:
        site_df = filtered_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(
            site_df, names='class', title=f'Success for Site {entered_site}'
            )
        fig.update_traces(hovertemplate='Outcome: %{label}<br>Count: %{value}<extra></extra>')

    return fig

# Callback 3: Update the Scatter Plot based on selected site
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_plot(entered_site, selected_range):
    _min_payload, _max_payload = selected_range
    filtered_df = spacex_df[
        (_min_payload <= spacex_df['Payload Mass (kg)']) &
        (spacex_df['Payload Mass (kg)'] <= _max_payload)
    ]
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Payload Mass vs Success',
                         width=1000, height=500)
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(site_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Payload Mass vs Success for {entered_site}',
                         width=1000, height=500)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
