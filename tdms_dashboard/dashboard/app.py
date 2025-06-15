import dash
from dash import dcc, html, Input, Output, State
import dash_table
import gspread
import pandas as pd
import plotly.graph_objs as go
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime

# --- Google Sheets Setup ---
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

spreadsheet = client.open("TDMS Dashboard Data")  # change if different

# Load all frequency tabs and store data
def get_all_data():
    data_dict = {}
    for sheet in spreadsheet.worksheets():
        df = pd.DataFrame(sheet.get_all_records())
        if not df.empty:
            # Normalize column names
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
            if 'timestamp' not in df.columns:
                df['timestamp'] = pd.date_range(start='now', periods=len(df), freq='S')
            data_dict[sheet.title] = df
    return data_dict

# --- Dash App ---
app = dash.Dash(__name__)
app.title = "TDMS Viewer"

# --- Initial Data ---
all_data = get_all_data()
frequencies = list(all_data.keys())

app.layout = html.Div([
    html.H1("TDMS Interactive Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select Frequency:"),
        dcc.Dropdown(
            id='frequency-dropdown',
            options=[{'label': freq, 'value': freq} for freq in frequencies],
            value=frequencies[0] if frequencies else None,
            clearable=False
        )
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Timestamp:"),
        dcc.Dropdown(id='timestamp-dropdown')
    ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),

    dcc.Graph(id='acceleration-graph'),

    html.Button("Download Graph as PDF", id='download-btn'),
    html.Div(id='download-message', style={'marginTop': '10px', 'color': 'green'})
])

# --- Callbacks ---
@app.callback(
    Output('timestamp-dropdown', 'options'),
    Output('timestamp-dropdown', 'value'),
    Input('frequency-dropdown', 'value')
)
def update_timestamps(selected_freq):
    df = all_data[selected_freq]
    options = [{'label': str(t), 'value': str(t)} for t in df['timestamp'].unique()]
    return options, options[0]['value'] if options else None

@app.callback(
    Output('acceleration-graph', 'figure'),
    Input('frequency-dropdown', 'value'),
    Input('timestamp-dropdown', 'value')
)
def update_graph(freq, timestamp):
    df = all_data[freq]
    filtered_df = df[df['timestamp'] == timestamp] if timestamp else df

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=filtered_df['z_axis'],
        x=filtered_df.index,
        mode='lines+markers',
        name='Z-Axis Acceleration'
    ))
    fig.update_layout(title=f'Z-Axis Acceleration - {freq} @ {timestamp}',
                      xaxis_title="Sample Index", yaxis_title="Acceleration")
    return fig

@app.callback(
    Output('download-message', 'children'),
    Input('download-btn', 'n_clicks'),
    State('frequency-dropdown', 'value'),
    State('timestamp-dropdown', 'value')
)
def download_graph(n, freq, timestamp):
    if n:
        df = all_data[freq]
        filtered_df = df[df['timestamp'] == timestamp]
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 5))
        plt.plot(filtered_df.index, filtered_df['z_axis'], marker='o')
        plt.title(f"{freq} - {timestamp}")
        plt.xlabel("Sample Index")
        plt.ylabel("Z-Axis Acceleration")
        plt.grid(True)

        file_name = f"{freq}_{timestamp.replace(':', '-')}.pdf"
        plt.savefig(file_name)
        plt.close()
        return f"PDF saved as {file_name}"
    return ""

# Run
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
