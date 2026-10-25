from pathlib import Path

import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px


# Load the dataset and keep a local copy for submission
DATA_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "d51iMGfp_t0QpO30Lym-dw/automobile-sales.csv"
)

DATA_FILE = (
    Path(__file__).resolve().parent / "automobile-sales.csv"
)

if DATA_FILE.exists():
    data = pd.read_csv(DATA_FILE)
else:
    data = pd.read_csv(DATA_URL)
    data.to_csv(DATA_FILE, index=False)

data["Year"] = pd.to_numeric(data["Year"]).astype(int)
month_map = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}

data["Month"] = data["Month"].map(month_map).astype(int)


# Initialize the Dash application
app = dash.Dash(__name__)
app.title = "Automobile Sales Statistics Dashboard"

year_list = list(range(1980, 2024))

dropdown_options = [
    {
        "label": "Yearly Statistics",
        "value": "Yearly Statistics",
    },
    {
        "label": "Recession Period Statistics",
        "value": "Recession Period Statistics",
    },
]


# TASK 2.1: Title
app.layout = html.Div(
    [
        html.H1(
            "Automobile Sales Statistics Dashboard",
            style={
                "textAlign": "center",
                "color": "#503D36",
                "fontSize": 24,
            },
        ),

        # TASK 2.2: Report-type dropdown
        html.Div(
            [
                html.Label("Select Statistics:"),
                dcc.Dropdown(
                    id="dropdown-statistics",
                    options=dropdown_options,
                    value="Select Statistics",
                    placeholder="Select a report type",
                    clearable=False,
                    style={
                        "width": "80%",
                        "padding": "3px",
                        "fontSize": "20px",
                    },
                ),
            ],
            style={"marginBottom": "15px"},
        ),

        # TASK 2.2: Year dropdown
        html.Div(
            [
                html.Label("Select Year:"),
                dcc.Dropdown(
                    id="select-year",
                    options=[
                        {"label": str(year), "value": year}
                        for year in year_list
                    ],
                    value="Select-year",
                    placeholder="Select-year",
                    disabled=True,
                    clearable=False,
                    style={"width": "80%"},
                ),
            ],
            style={"marginBottom": "15px"},
        ),

        # TASK 2.3: Output container
        html.Div(
            [
                html.Div(
                    id="output-container",
                    className="chart-grid",
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "12px",
                    },
                ),
            ]
        ),
    ],
    style={
        "fontFamily": "Arial",
        "padding": "20px",
    },
)


# Arrange four charts in two rows and two columns
def make_chart_grid(figures):
    charts = []

    for figure in figures:
        figure.update_layout(
            height=350,
            margin={"l": 55, "r": 20, "t": 80, "b": 70},
            title={"font": {"size": 15}},
        )
        charts.append(
            html.Div(
                dcc.Graph(figure=figure),
                style={
                    "width": "50%",
                    "minWidth": "0",
                },
            )
        )

    return [
        html.Div(
            charts[:2],
            className="chart-item",
            style={"display": "flex"},
        ),
        html.Div(
            charts[2:],
            className="chart-item",
            style={"display": "flex"},
        ),
    ]


# TASK 2.4: Enable or disable year selection
@app.callback(
    Output("select-year", "disabled"),
    Input("dropdown-statistics", "value"),
)
def update_input_container(selected_statistics):
    if selected_statistics == "Yearly Statistics":
        return False
    return True


# TASK 2.4: Update the report output
@app.callback(
    Output("output-container", "children"),
    [
        Input("dropdown-statistics", "value"),
        Input("select-year", "value"),
    ],
)
def update_output_container(selected_statistics, input_year):

    # TASK 2.5: Recession Period Statistics
    if selected_statistics == "Recession Period Statistics":
        recession_data = data[data["Recession"] == 1]

        # R1: Average annual sales during recessions
        yearly_rec = (
            recession_data.groupby("Year")["Automobile_Sales"]
            .mean()
            .reset_index()
        )

        fig_r1 = px.line(
            yearly_rec,
            x="Year",
            y="Automobile_Sales",
            markers=True,
            title="Average Automobile Sales During Recessions",
            labels={
                "Automobile_Sales": "Average Automobile Sales"
            },
        )

        # R2: Average sales by vehicle type
        average_sales = (
            recession_data.groupby("Vehicle_Type")[
                "Automobile_Sales"
            ]
            .mean()
            .reset_index()
        )

        fig_r2 = px.bar(
            average_sales,
            x="Vehicle_Type",
            y="Automobile_Sales",
            title="Average Sales by Vehicle Type During Recessions",
            labels={
                "Vehicle_Type": "Vehicle Type",
                "Automobile_Sales": "Average Automobile Sales",
            },
        )

        # R3: Total advertising expenditure by vehicle type
        exp_rec = (
            recession_data.groupby("Vehicle_Type")[
                "Advertising_Expenditure"
            ]
            .sum()
            .reset_index()
        )

        fig_r3 = px.pie(
            exp_rec,
            names="Vehicle_Type",
            values="Advertising_Expenditure",
            title="Advertising Expenditure Share During Recessions",
        )

        # R4: Unemployment rate and sales by vehicle type
        unemp_data = (
            recession_data.groupby(
                ["unemployment_rate", "Vehicle_Type"]
            )["Automobile_Sales"]
            .mean()
            .reset_index()
        )

        fig_r4 = px.bar(
            unemp_data,
            x="unemployment_rate",
            y="Automobile_Sales",
            color="Vehicle_Type",
            barmode="group",
            title="Unemployment Rate and Sales During Recessions",
            labels={
                "unemployment_rate": "Unemployment Rate",
                "Automobile_Sales": "Average Automobile Sales",
                "Vehicle_Type": "Vehicle Type",
            },
        )

        return make_chart_grid(
            [fig_r1, fig_r2, fig_r3, fig_r4]
        )

    # TASK 2.6: Yearly Statistics
    elif selected_statistics == "Yearly Statistics":

        if input_year not in year_list:
            return html.P("Please select a year.")

        yearly_data = data[data["Year"] == input_year]

        if yearly_data.empty:
            return html.P(
                f"No data is available for {input_year}."
            )

        # Y1: Average annual sales across the whole period
        yas = (
            data.groupby("Year")["Automobile_Sales"]
            .mean()
            .reset_index()
        )

        fig_y1 = px.line(
            yas,
            x="Year",
            y="Automobile_Sales",
            markers=True,
            title="Average Yearly Automobile Sales — Whole Period",
            labels={
                "Automobile_Sales": "Average Automobile Sales"
            },
        )

        # Y2: Total monthly sales for the selected year
        mas = (
            yearly_data.groupby("Month")["Automobile_Sales"]
            .sum()
            .reset_index()
            .sort_values("Month")
        )

        fig_y2 = px.line(
            mas,
            x="Month",
            y="Automobile_Sales",
            markers=True,
            title=f"Total Monthly Automobile Sales in {input_year}",
            labels={
                "Automobile_Sales": "Total Automobile Sales"
            },
        )

        fig_y2.update_xaxes(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=[
                "Jan", "Feb", "Mar", "Apr",
                "May", "Jun", "Jul", "Aug",
                "Sep", "Oct", "Nov", "Dec",
            ],
        )

        # Y3: Average sales by vehicle type in selected year
        avr_vdata = (
            yearly_data.groupby("Vehicle_Type")[
                "Automobile_Sales"
            ]
            .mean()
            .reset_index()
        )

        fig_y3 = px.bar(
            avr_vdata,
            x="Vehicle_Type",
            y="Automobile_Sales",
            title=f"Average Sales by Vehicle Type in {input_year}",
            labels={
                "Vehicle_Type": "Vehicle Type",
                "Automobile_Sales": "Average Automobile Sales",
            },
        )

        # Y4: Total advertising expenditure in selected year
        exp_data = (
            yearly_data.groupby("Vehicle_Type")[
                "Advertising_Expenditure"
            ]
            .sum()
            .reset_index()
        )

        fig_y4 = px.pie(
            exp_data,
            names="Vehicle_Type",
            values="Advertising_Expenditure",
            title=f"Advertising Expenditure by Vehicle Type in {input_year}",
        )

        return make_chart_grid(
            [fig_y1, fig_y2, fig_y3, fig_y4]
        )

    return html.P("Please select a report type.")


if __name__ == "__main__":
    app.run()