# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

FONT_FAMILY = "Calibri"

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40, 'font-family': FONT_FAMILY}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                 {'label': 'All Sites', 'value': 'ALL'},
                                                 {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                 {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                 {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                 {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                             ],
                                             value='ALL',
                                             placeholder="Select site here",
                                             searchable=True,
                                             style={"font-family": FONT_FAMILY},
                                             ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000,
                                                marks={
                                                    0: '0 kg',
                                                    2500: '2500',
                                                    5000: '5000',
                                                    7500: '7500',
                                                    10000: '10000'
                                                },
                                                value=[min_payload, max_payload]
                                                ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class',
                     names='Launch Site',
                     title='Success rate of Launch Sites')
    else:
        filtered = spacex_df.loc[spacex_df["Launch Site"] == entered_site, ["Launch Site", "class"]]
        filtered["Label"] = filtered["class"].apply(lambda x: "Success" if x == 1 else "Failure")
        fig = px.pie(filtered.sort_values("class", ascending=False), names='Label',
                     title=f'Success rate of {entered_site}',
                     color="Label",
                     color_discrete_map={"Failure": "red", "Success": "green"},
                     category_orders={"Label": ["Success", "Failure"]})
    return fig.update_layout(font_family=FONT_FAMILY)


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')]
              )
def get_payload_scatter(entered_site, payload):
    low, high = payload
    if entered_site == 'ALL':
        filtered = spacex_df.loc[(spacex_df["Payload Mass (kg)"] >= low) &
                                 (spacex_df["Payload Mass (kg)"] <= high),
                                 ["Payload Mass (kg)", "class", "Booster Version Category"]]
    else:
        filtered = spacex_df.loc[(spacex_df["Payload Mass (kg)"] >= low) &
                                 (spacex_df["Payload Mass (kg)"] <= high) &
                                 (spacex_df["Launch Site"] == entered_site),
                                 ["Payload Mass (kg)", "class", "Booster Version Category"]]
    return px.scatter(filtered, x="Payload Mass (kg)", y="class", color="Booster Version Category")


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
