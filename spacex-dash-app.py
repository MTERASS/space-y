# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Br(),
                                dcc.Dropdown(
                                    id='site-dropdown',  # unique identifier for the dropdown
                                    # options is a list of dictionaries, each with 'label' and 'value'
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},  # default option to show all sites
                                        # dynamically create options from spacex_df launch sites
                                        # assuming spacex_df['Launch Site'] contains the site names
                                        *[{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]
                                    ],
                                    value='ALL',  # default selected value
                                    placeholder="Select a Launch Site",  # hint text shown when nothing is selected
                                    searchable=True) , # allows typing to search through options

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                # RangeSlider component for selecting payload mass range
                                dcc.RangeSlider(
                                    id='payload-slider',        # unique identifier for the slider
                                    min=0,                      # slider starting point (Kg)
                                    max=10000,                  # slider ending point (Kg)
                                    step=1000,                  # interval step size (Kg)
                                    value=[min_payload, max_payload],  # default selected range from variables
                                    marks={                     # optional: show labeled ticks for clarity
                                        0: '0',
                                        2000: '2000',
                                        5000: '5000',
                                        7000: '7000',
                                        10000: '10000'
                                    },
                                    tooltip={"placement": "bottom", "always_visible": True}  # show current values
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def update_pie_chart(selected_site):
    # If ALL sites are selected
    if selected_site == 'ALL':
        # Count total successes (class=1) across all sites
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',  # class column holds 0/1, so sum gives success count
            title='Total Success Launches by Site'
        )
        return fig
    else:
        # Filter dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        # Count success vs failure for that site
        fig = px.pie(
            filtered_df,
            names='class',
            title=f'Success vs Failure for site {selected_site}'
        )
        return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    # payload_range is a list [min, max]
    low, high = payload_range

    # Filter dataframe by payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]

    # If ALL sites are selected
    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites'
        )
        return fig
    else:
        # Filter dataframe for the selected site
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for site {selected_site}'
        )
        return fig

# Run the app
if __name__ == '__main__':
    app.run()
