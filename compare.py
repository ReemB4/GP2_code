import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import sqlite3

def load_data_from_db():
    conn = sqlite3.connect('patient_data_v2.db')
    
    proteins_df = pd.read_sql('SELECT * FROM proteins', conn)
    peptides_df = pd.read_sql('SELECT * FROM peptides', conn)
    clinical_data_df = pd.read_sql('SELECT * FROM clinical_data', conn)
    
    merged_df = proteins_df.merge(peptides_df, on=['patient_id', 'visit_month'], suffixes=('_protein', '_peptide'))
    merged_df = merged_df.merge(clinical_data_df, on=['patient_id', 'visit_month'])
    
    conn.close()
    return merged_df

data_df = load_data_from_db()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Common Protein Comparison for Patients at Each Visit"),
    dcc.Dropdown(
        id='patient-selector',
        options=[{'label': patient, 'value': patient} for patient in data_df['patient_id'].unique()],
        multi=True,
        placeholder='Select patients...'
    ),
    dcc.Dropdown(
        id='protein-selector',
        options=[{'label': protein, 'value': protein} for protein in data_df['protein'].unique()],
        multi=True,
        placeholder='Select proteins...'
    ),
    dcc.Dropdown(
        id='peptide-selector',
        options=[{'label': peptide, 'value': peptide} for peptide in data_df['peptide'].unique()],
        multi=True,
        placeholder='Select peptides...'
    ),
    dcc.Dropdown(
        id='visit-month-selector',
        options=[{'label': str(month), 'value': month} for month in data_df['visit_month'].unique()],
        multi=True,
        placeholder='Select visit months...'
    ),
    dash_table.DataTable(
        id='comparison-table',
        columns=[{"name": col, "id": col} for col in data_df.columns],
        data=data_df.to_dict('records'),
        page_size=10,
        filter_action='native',
        sort_action='native',
        sort_mode='multi',
        column_selectable='single',
        row_selectable='multi',
        selected_columns=[],
        selected_rows=[],
        style_table={'overflowX': 'auto'}
    )
])

@app.callback(
    Output('comparison-table', 'data'),
    [
        Input('patient-selector', 'value'),
        Input('protein-selector', 'value'),
        Input('peptide-selector', 'value'),
        Input('visit-month-selector', 'value')
    ]
)
def update_table(selected_patients, selected_proteins, selected_peptides, selected_months):
    filtered_df = data_df.copy()

    if selected_patients:
        filtered_df = filtered_df[filtered_df['patient_id'].isin(selected_patients)]
    if selected_proteins:
        filtered_df = filtered_df[filtered_df['protein'].isin(selected_proteins)]
    if selected_peptides:
        filtered_df = filtered_df[filtered_df['peptide'].isin(selected_peptides)]
    if selected_months:
        filtered_df = filtered_df[filtered_df['visit_month'].isin(selected_months)]

    return filtered_df.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)
