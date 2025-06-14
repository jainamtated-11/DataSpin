import os
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output

app = Dash(__name__)
CSV_PATH = r"C:\Users\MADLAB\Desktop\Humayun\tdms_dashboard\merged_csv\output_clean.csv"
LAST_KNOWN_GOOD = pd.DataFrame()

app.layout = html.Div([
    html.H1("Acceleration Data Dashboard"),
    dcc.Interval(id="interval", interval=5000),  # 5 seconds
    html.Div(id="plots")
])

@app.callback(
    Output("plots", "children"),
    Input("interval", "n_intervals")
)
def update_graph(n):
    global LAST_KNOWN_GOOD

    try:
        if not os.path.exists(CSV_PATH):
            return html.Div("Waiting for CSV file to be created...")
    except Exception as e:
        return html.Div(f"Error checking CSV file existence: {e}")

    try:
        df = pd.read_csv(CSV_PATH)
        # return html.Pre(df.head(10).to_string())

    except Exception as e:
        print(f"[ERROR] Reading CSV failed: {e}")
        if LAST_KNOWN_GOOD.empty:
            return html.Div("Error reading CSV and no previous data available.")
        else:
            df = LAST_KNOWN_GOOD.copy()

    try:
        if df.empty or "Time (s)" not in df.columns:
            if LAST_KNOWN_GOOD.empty:
                return html.Div("CSV exists but has no usable data.")
            df = LAST_KNOWN_GOOD.copy()
        else:
            LAST_KNOWN_GOOD = df.copy()
    except Exception as e:
        return html.Div(f"Error checking CSV content: {e}")

    plots = []

    for column in df.columns:
        try:
            if column.lower() in ["time (s)"]:
                continue

            real_time_df = df.tail(25600)

            plots.append(html.H2(f"{column}.tdms - Historical"))
            plots.append(dcc.Graph(
                figure=go.Figure(
                    data=go.Scatter(
                        x=df["Time (s)"],
                        y=df[column],
                        mode='lines',
                        name=f"{column} Full"
                    ),
                    layout=go.Layout(
                        title=f"{column}.tdms - Full Acceleration vs Time",
                        xaxis_title="Time (s)",
                        yaxis_title="Acceleration"
                    )
                )
            ))

            plots.append(html.H2(f"{column}.tdms - Real-Time"))
            plots.append(dcc.Graph(
                figure=go.Figure(
                    data=go.Scatter(
                        x=real_time_df["Time (s)"],
                        y=real_time_df[column],
                        mode='lines+markers',
                        name=f"{column} Live"
                    ),
                    layout=go.Layout(
                        title=f"{column}.tdms - Real-Time Acceleration",
                        xaxis_title="Time (s)",
                        yaxis_title="Acceleration"
                    )
                )
            ))
        except Exception as e:
            plots.append(html.Div(f"Error processing column {column}: {e}"))

    return plots

if __name__ == "__main__":
    try:
        app.run(debug=True, port=8050)
    except Exception as e:
        print(f"[ERROR] Failed to launch Dash app: {e}")