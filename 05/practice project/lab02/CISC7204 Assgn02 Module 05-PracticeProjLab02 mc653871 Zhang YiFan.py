import calendar

import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px


# Create the application
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True


# Read the wildfire dataset
DATA_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/"
    "Data%20Files/Historical_Wildfires.csv"
)

df = pd.read_csv(DATA_URL)

# Extract year and month from Date
dates = pd.to_datetime(df["Date"])
df["Month"] = dates.dt.month_name()
df["Year"] = dates.dt.year

month_order = list(calendar.month_name)[1:]


# Task 2.1: Dashboard title
app.layout = html.Div(
    children=[
        html.H1(
            "Australia Wildfire Dashboard",
            style={
                "textAlign": "center",
                "color": "#503D36",
                "fontSize": 26,
            },
        ),

        # Outer division
        html.Div(
            children=[
                # First inner division: input controls
                html.Div(
                    children=[
                        # Task 2.2: Region radio items
                        html.H2(
                            "Select Region:",
                            style={"marginRight": "2em"},
                        ),

                        dcc.RadioItems(
                            options=[
                                {
                                    "label": "New South Wales",
                                    "value": "NSW",
                                },
                                {
                                    "label": "Northern Territory",
                                    "value": "NT",
                                },
                                {
                                    "label": "Queensland",
                                    "value": "QL",
                                },
                                {
                                    "label": "South Australia",
                                    "value": "SA",
                                },
                                {
                                    "label": "Tasmania",
                                    "value": "TA",
                                },
                                {
                                    "label": "Victoria",
                                    "value": "VI",
                                },
                                {
                                    "label": "Western Australia",
                                    "value": "WA",
                                },
                            ],
                            value="NSW",
                            id="region",
                            inline=True,
                            labelStyle={"marginRight": "15px"},
                        ),

                        # Task 2.2: Year dropdown
                        html.H2(
                            "Select Year:",
                            style={"marginRight": "2em"},
                        ),

                        dcc.Dropdown(
                            options=[
                                {"label": str(year), "value": year}
                                for year in range(2005, 2021)
                            ],
                            value=2005,
                            id="year",
                            clearable=False,
                        ),
                    ]
                ),

                # Second inner division: chart outputs
                # Task 2.3: Two empty divisions
                html.Div(
                    children=[
                        html.Div(
                            id="plot1",
                            style={"flex": "1", "minWidth": "0"},
                        ),
                        html.Div(
                            id="plot2",
                            style={"flex": "1", "minWidth": "0"},
                        ),
                    ],
                    style={"display": "flex"},
                ),
            ]
        ),
    ],
    style={"padding": "20px", "fontFamily": "Arial"},
)


# Task 2.4: Callback outputs and inputs
@app.callback(
    [
        Output("plot1", "children"),
        Output("plot2", "children"),
    ],
    [
        Input("region", "value"),
        Input("year", "value"),
    ],
)
# Task 2.5: Filter data and create charts
def reg_year_display(input_region, input_year):
    region_data = df[df["Region"] == input_region]
    y_r_data = region_data[region_data["Year"] == input_year]

    # Monthly average estimated fire area
    est_data = (
        y_r_data.groupby("Month")["Estimated_fire_area"]
        .mean()
        .reindex(month_order)
        .dropna()
        .reset_index()
    )

    fig1 = px.pie(
        est_data,
        values="Estimated_fire_area",
        names="Month",
        title=(
            f"{input_region} : Monthly Average Estimated Fire Area "
            f"in year {input_year}"
        ),
    )

    # Monthly average count of pixels for presumed vegetation fires
    veg_data = (
        y_r_data.groupby("Month")["Count"]
        .mean()
        .reindex(month_order)
        .dropna()
        .reset_index()
    )

    fig2 = px.bar(
        veg_data,
        x="Month",
        y="Count",
        category_orders={"Month": month_order},
        title=(
            f"{input_region} : Average Count of Pixels for Presumed "
            f"Vegetation Fires in year {input_year}"
        ),
    )

    return [
        dcc.Graph(figure=fig1),
        dcc.Graph(figure=fig2),
    ]


if __name__ == "__main__":
    app.run()
    