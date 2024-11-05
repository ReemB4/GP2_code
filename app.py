from flask import Flask, render_template, request, redirect, url_for
import dash_mantine_components as dmc
#from dash import Dash, Output, Input, html, dcc
#import mpld3.plugins
from dash_application import create_dash_application
#from dash import html
import pandas as pd
import sqlite3
import plotly.express as px
import plotly as py
#import plotly.graph_objs as go
import matplotlib.pyplot as plt, mpld3
from mpld3 import fig_to_html, plugins
import jinja2
from jinja2 import Template
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import requests
import re

app = Flask(__name__)
DB = "patient_data_v2.db"


def get_months(patient_id):
    visit_months = []
    try:
        
        con = sqlite3.connect(DB)
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        query = f"SELECT DISTINCT visit_month FROM new_clinical_data WHERE patient_id = {patient_id};"
        cur.execute(query)

        rows = cur.fetchall()

        visit_months = [row[0] for row in rows]

        #print("Unique Visit Months:")
        #print(visit_months)

    except:
        patient_id = None
    finally:
        con.close()

    return visit_months


def get_patients(patient_id):
    patients = []
    try:
        
        con = sqlite3.connect(DB)
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        query = f"SELECT DISTINCT patient_id FROM new_clinical_data WHERE NOT patient_id = {patient_id};"
        cur.execute(query)

        rows = cur.fetchall()

        patients = [row[0] for row in rows]

        #print("Unique Visit patients:")
        #print(patients)

    except:
        patients = 0
    finally:
        con.close()

    return patients

def get_all_patients():
    data = []
    #try:
        
    con = sqlite3.connect(DB)

    query = f"""SELECT patient_id, visit_month, updrs_1, updrs_2, updrs_3, updrs_4
            FROM new_clinical_data
            ORDER BY visit_month DESC
            """
    
    #SELECT DISTINCT patient_id FROM new_clinical_data WHERE visit_months = {patient_id}; 
    #cur.execute(query)
    #rows = cur.fetchall()
    #patients = [row[0] for row in rows]

    data = pd.read_sql_query(query, con)
    #print(data)

    # Rename all columns
    data.columns = ['Patient ID', 'Visit Months', 'updrs_1 Score', 'updrs_2 Score', 'updrs_3 Score', 'updrs_4 Score']
    #print(data)

    data['Visit Months'] = data['Visit Months'].astype(int)
    #print(data)

    # Keep only the row with the highest 'Visit Months' for each 'Patient ID'
    #df_highest_visit = data.loc[data.groupby('Patient ID')['Visit Months'].idxmax()]
    df_sorted = data.sort_values(by=['Patient ID', 'Visit Months'], ascending=[True, True])
    #print(df_sorted)

    # Reset index if needed
    #df_highest_visit = df_highest_visit.reset_index(drop=True)
    df_highest_visit = df_sorted.drop_duplicates(subset='Patient ID', keep='last').reset_index(drop=True)
    #print(df_highest_visit)

    #print("Unique Visit patients:")
    #print(patients)


    con.close()

    return df_highest_visit

@app.route('/')
def home():

    patients = get_all_patients().to_dict(orient='records')
    #print(patients)

    return render_template('doctor_base.html', patients=patients)


def patient_info(patient_id):

    con = sqlite3.connect(DB)

    pr_query = f"""SELECT visit_month, UniProt, NPX
            FROM proteins
            WHERE patient_id = ?
            ORDER BY visit_month DESC
            """
    
    pe_query = f"""SELECT visit_month, UniProt, Peptide, PeptideAbundance
            FROM peptides
            WHERE patient_id = ?
            ORDER BY visit_month DESC
            """
    
    s_query = f"""SELECT visit_month, updrs_1, updrs_2, updrs_3, updrs_4
            FROM new_clinical_data
            WHERE patient_id = ?
            ORDER BY visit_month DESC
            """

    pr_data = pd.read_sql_query(pr_query, con, params=(patient_id,))
    pe_data = pd.read_sql_query(pe_query, con, params=(patient_id,))
    s_data = pd.read_sql_query(s_query, con, params=(patient_id,))
    #print(data)


    pr_data['visit_month'] = pr_data['visit_month'].astype(int)
    pe_data['visit_month'] = pe_data['visit_month'].astype(int)
    s_data['visit_month'] = s_data['visit_month'].astype(int)

    print(pr_data)

    con.close()

    return pr_data.to_dict(orient='records'), pe_data.to_dict(orient='records'), s_data.to_dict(orient='records')


@app.route('/view_patient', methods = ['GET','POST'])
def view_patient():
    if request.method == 'POST':
        patient_id = request.form['view_patient']
        #print(1)
    else:
        msg = 'Error: try again'
        patients = get_all_patients().to_dict(orient='records')
        #print(2)
        return render_template('doctor_base.html', patients=patients, msg=msg )
    

    patient_pro_info, patient_pep_info, patient_sco_info = patient_info(patient_id)

    return render_template('patient_page.html', patient_id=patient_id, patient_pro_info=patient_pro_info,patient_pep_info=patient_pep_info,patient_sco_info=patient_sco_info)


def get_results(patient_id, compare_by, selected_visit_months):
    conn = sqlite3.connect(DB)
    results = 1
    formatted_months = ', '.join(f'"{month}"' for month in selected_visit_months)
    limit = len(selected_visit_months) * 10
    if compare_by == 'Peptide':
        print('hi')
        query = f"""
            SELECT Peptide, visit_month, PeptideAbundance, UniProt
            FROM peptides
            WHERE patient_id = ?
            AND visit_month IN ({formatted_months})
            ORDER BY PeptideAbundance DESC
        """

        
        data = pd.read_sql_query(query, conn, params=(patient_id,))
        print(type(data))
        print(data)

        peptides_sorted_df = data.sort_values(by='PeptideAbundance', ascending=False)
        print(f'peptides_sorted_df\n{peptides_sorted_df}')

        peptides_highest_df = peptides_sorted_df.drop_duplicates(subset='Peptide', keep='first')
        print(f'peptides_highest_df\n{peptides_highest_df.head(20)}')

        #top20_peptides_df = peptides_highest_df.head(20)

        filtered_df = peptides_sorted_df[peptides_sorted_df['Peptide'].isin(peptides_highest_df['Peptide'])]#top20_peptides_df['Peptide'])]

        print(f'filtered_df\n{filtered_df}')
        
        valid_peptides = (
            filtered_df.groupby('Peptide')
            .filter(lambda x: len(x) == len(selected_visit_months))
        )

        print(f'valid_peptides{type(valid_peptides)}')
        print(f'valid_peptides{valid_peptides.info()}')

        valid_peptides['visit_month'] = valid_peptides['visit_month'].astype(str)

        print(f'valid_peptides{type(valid_peptides)}')
        print(f'valid_peptides{valid_peptides}')


        """         
        fig1 = px.bar(valid_peptides, 
             x='Peptide', 
             y='PeptideAbundance', 
             color='visit_month', 
             barmode='group',
             text='visit_month'
             
        ) """

        # Create a new column in the DataFrame with the desired hover text
        #valid_peptides['UniProt_ID'] = (
            #'Peptide: ' + valid_peptides['Peptide'] +
            #'<br>Visit Month: ' + valid_peptides['visit_month'].astype(str) +
            #'<br>Abundance: ' + valid_peptides['PeptideAbundance'].astype(str) +
            #'<br>UniProt ID: ' + 
            #valid_peptides['UniProt'])

        # Pass this new column to the `text` parameter in the `px.bar` function
        fig1 = px.bar(
            valid_peptides,
            x='Peptide',
            y='PeptideAbundance',
            color='visit_month',
            barmode='group',
            hover_data='UniProt',
            text='visit_month'  # Set the hover text to our custom column
        )

        """
        # Customize the hover template to display `text` only
        fig1.update_traces(
            hovertemplate='%{hover_data}<extra></extra>'
        )
        """
        
        fig1.update_layout(
            title=f'Patient {patient_id} Peptides Abundance Grouped by Visit Months',
            dragmode='pan'  # Set the default interaction mode to pan
            #xaxis_title='Peptide',
            #yaxis_title='Peptide Abundance',
            #barmode='group'
        )

        # For Peptide or Protein bar chart
        fig1.update_xaxes(
            rangeslider=dict(visible=True),  # This adds the scrollbar below the plot
            range=[-1, 10]  # Adjust the range as needed to show only a part of the x-axis initially
            
        )

        fig1.update_layout(
            xaxis=dict(
                title='Peptide' if compare_by == 'Peptide' else 'UniProt',
                tickangle=45  # Rotates labels to avoid overlap if there are many
            ),
            yaxis_title="Peptide Abundance" if compare_by == 'Peptide' else "NPX",
            title_text=f"Patient {patient_id} {'Peptides' if compare_by == 'Peptide' else 'Proteins'} Abundance Grouped by Visit Months"
        )

        """
        fig1.update_traces(
            hovertemplate=(
                '<b>Peptide:</b> %{x}<br>'
                '<b>Visit Month:</b> %{customdata[0]}<br>'
                '<b>Abundance:</b> %{y}<br>'
                '<b>UniProt ID:</b> %{customdata[1]}<extra></extra>'
            ),
            customdata=valid_peptides[['visit_month', 'UniProt']].values
        )
        """

        fig1.show()

        """fig1 = px.bar(valid_peptides, x="Peptide", 
                      y="PeptideAbundance", 
                      color="visit_month", 
                      text="visit_month", 
                      barmode='group', title=f"Patient {patient_id} Peptides Abundance Bar Plot")"""
        




    elif compare_by == 'Protein':
        query = f"""
            SELECT UniProt, visit_month, NPX
            FROM proteins
            WHERE patient_id = ?
            AND visit_month IN ({formatted_months})
            ORDER BY NPX DESC
        """

        
        data = pd.read_sql_query(query, conn, params=(patient_id,))
        print(type(data))
        print(data)

        proteins_sorted_df = data.sort_values(by='NPX', ascending=False)
        print(f'proteins_sorted_df\n{proteins_sorted_df}')

        proteins_highest_df = proteins_sorted_df.drop_duplicates(subset='UniProt', keep='first')
        print(f'proteins_highest_df\n{proteins_highest_df.head(20)}')

        #top20_proteins_df = proteins_highest_df.head(20)

        filtered_df = proteins_sorted_df[proteins_sorted_df['UniProt'].isin(proteins_highest_df['UniProt'])]#top20_proteins_df['UniProt'])]

        print(f'filtered_df\n{filtered_df}')
        
        valid_proteins = (
            filtered_df.groupby('UniProt')
            .filter(lambda x: len(x) == len(selected_visit_months))
        )

        print(f'valid_proteins{type(valid_proteins)}')
        print(f'valid_proteins{valid_proteins.info()}')

        valid_proteins['visit_month'] = valid_proteins['visit_month'].astype(str)

        print(f'valid_proteins{type(valid_proteins)}')
        print(f'valid_proteins{valid_proteins.info()}')


        fig1 = px.bar(valid_proteins, 
             x='UniProt', 
             y='NPX', 
             color='visit_month', 
             barmode='group',
             text='visit_month'
             
        )


        
        fig1.update_layout(
            title=f'Patient {patient_id} UniProt Proteins Abundance Grouped by Visit Months',
            #xaxis_title='Peptide',
            #yaxis_title='Peptide Abundance',
            #barmode='group'
        )

        # For Peptide or Protein bar chart
        fig1.update_xaxes(
            rangeslider=dict(visible=True),  # This adds the scrollbar below the plot
            range=[-1, 10]  # Adjust the range as needed to show only a part of the x-axis initially
        )

        fig1.update_layout(
            xaxis=dict(
                title='Peptide' if compare_by == 'Peptide' else 'UniProt',
                tickangle=45  # Rotates labels to avoid overlap if there are many
            ),
            yaxis_title="Peptide Abundance" if compare_by == 'Peptide' else "NPX",
            title_text=f"Patient {patient_id} {'Peptides' if compare_by == 'Peptide' else 'Proteins'} Abundance Grouped by Visit Months"
        )

        fig1.update_layout(
            dragmode='pan'  # Set the default interaction mode to pan
        )

        fig1.show()

    elif compare_by == 'Score':
        query = f"""
        SELECT visit_month, updrs_1, updrs_2, updrs_3, updrs_4
        FROM new_clinical_data
        WHERE patient_id = ? AND visit_month IN ({formatted_months});
        
        """

        print('data')
        score_data = pd.read_sql_query(query, conn, params=(patient_id,))
        print(type(score_data))
        print(score_data)
        df_melted = score_data.melt(id_vars=["visit_month"], var_name="score", value_name="value")
        print(df_melted)
        #top_10 = data
        #dic_top_10 = top_10.set_index('visit_month').T.to_dict('list')
        #print(dic_top_10)
        #df = px.data.gapminder().query("continent == 'Oceania'")
        #print(df)
        #fig = px.line(df, x='year', y='lifeExp', color='iso_num')
        #fig.show()
        fig3 = px.line(
            df_melted, 
            x='visit_month', 
            y='value', 
            color='score', 
            markers=True, 
            title=f"Patient {patient_id} UPDRS Score Trends Over Time",
        )

        fig3.show()

        fig3.write_html("/Users/mahayie/temp/compare/templates/file.html")

        py.iplot(df_melted, filename='UPDRS Score Trends Over Time')

        first_plot_url = py.plot(df_melted, filename='UPDRS Score Trends Over Time', auto_open=False,)
        #print(f'fffffff{first_plot_url}')

    else:
        results = 0



    """ 
    print('data')
    data = pd.read_sql_query(query, conn, params=(patient_id,))
    print(type(data))
    print(data.head(20))
    top_10 = data.head(10)

    dic_top_10 = top_10.set_index('Peptide').T.to_dict('list')

 
    print(dic_top_10)
    
    pivot_data = data.pivot_table(index=['UniProt', 'Peptide'], 
                                  columns='visit_month', 
                                  values='PeptideAbundance', 
                                  aggfunc='first')
    print(pivot_data)
    
    pivot_data = pivot_data.fillna('-')
    print('pivot_data')
    print(pivot_data)
    sorted_data = pivot_data.sort_values(by=[('PeptideAbundance')], ascending=False)
    print('sorted_data')
    print(sorted_data) """
    """ 
    top_10 = sorted_data.head(10)
    print(top_10)

    html_table =''

    for index, row in top_10.iterrows():
        html_table += f"<tr><td>{index[1]}</td>"  # Peptide Name
        for month in selected_visit_months:
            html_table += f"<td>{row.get(month, '-')}</td>"
        html_table += "</tr>"

    html_table += "</tbody></table>"
    print(html_table) """
    
    conn.close()

    return results

@app.route("/compare_visits", methods = ['POST'])
def compare_visits():
    if request.method == 'POST':
        patient_id = request.form['patient_id'] 
        visit_months = get_months(patient_id)

        patients = get_all_patients().to_dict(orient='records')
    else:
        return redirect('doctor_base.html', patients=patients)

    return render_template('compare_visits.html',patient_id=patient_id, visit_months=visit_months)
    

@app.route("/comperison_results", methods = ['POST'])
def comperison_results():
    
    if request.method == 'POST':
        
        patients = get_all_patients().to_dict(orient='records')

        try:
            patient_id = request.form['patient_id'] 
            visit_months = get_months(patient_id)

            compare_by = request.form['compare_by'] #str
            selected_visit_months = request.form.getlist('visit_month') #list of str

            results = get_results(patient_id, compare_by, selected_visit_months)

        except:
            results = f'Error'
            return redirect('doctor_base.html', patients=patients, results=results)

        finally:
            #con.close()
            return render_template('compare_visits.html',patient_id=patient_id, visit_months=visit_months, patients=patients)
                    

#---------------------

def get_common_visit_months(patient_id, selected_patient_id):
    try:
        con = sqlite3.connect(DB)
        con.row_factory = sqlite3.Row

        cur = con.cursor()

        query_1 = f"""
            SELECT DISTINCT visit_month 
            FROM new_clinical_data 
            WHERE patient_id = {patient_id};
        """
        cur.execute(query_1)
        patient1_months = {row[0] for row in cur.fetchall()}  

       
        query_2 = f"""
            SELECT DISTINCT visit_month 
            FROM new_clinical_data 
            WHERE patient_id = {selected_patient_id};
        """
        cur.execute(query_2)
        patient2_months = {row[0] for row in cur.fetchall()} 

        print(f"Patient {patient_id} Visit Months: {patient1_months}")
        print(f"Patient {selected_patient_id} Visit Months: {patient2_months}")

        common_months = patient1_months.intersection(patient2_months)

        print(f"Common Visit Months: {common_months}")

        return list(common_months)

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    finally:
        con.close()

@app.route('/compare_two', methods = ['POST']) 
def compare_two():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        patients = get_patients(patient_id)
        #print(1)
    else:
        msg = 'Error: try again'
        all_patients = get_all_patients().to_dict(orient='records')
        #print(2)
        return render_template('doctor_base.html', all_patients=all_patients, msg=msg )
    
    return render_template('compare_two.html', patient_id=patient_id, patients=patients)



@app.route('/compare_patients', methods = ['GET'])
def compare_patients():
    if request.method == 'GET':
        patient_id = request.args.get('patient_id') #942 #request.form['patient_id']
        selected_patient_id = request.args.get('compare_patients')
        
        visit_months = get_common_visit_months(patient_id,selected_patient_id)
        
        return render_template('compare_patients.html',visit_months=visit_months, selected_patient_id=selected_patient_id, patient_id=patient_id)
        

def get_two_results(patient_id, selected_patient_id, compare_by, selected_visit_months):
    conn = sqlite3.connect(DB)
    formatted_months = ', '.join(f'"{month}"' for month in selected_visit_months)

    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f"Patient {patient_id}", f"Patient {selected_patient_id}"),
        
    ) #shared_yaxes=True  # Optional: Share y-axis if comparing values directly

    if compare_by == 'Peptide':
        query = f"""
            SELECT Peptide, visit_month, PeptideAbundance, UniProt
            FROM peptides
            WHERE patient_id = ? 
            AND visit_month IN ({formatted_months})
            ORDER BY PeptideAbundance DESC
        """

        data1 = pd.read_sql_query(query, conn, params=(patient_id,))
        data2 = pd.read_sql_query(query, conn, params=(selected_patient_id,))

        print(data1)
        print(data2)

        # Add a new column to each DataFrame with the patient ID
        data1['Patient_ID'] = f'Patient {patient_id}'
        data2['Patient_ID'] = f'Patient {selected_patient_id}'

        print(f'data1\n{data1}')
        print(f'data2\n{data2}')

        # common peptides
        common_peptides = set(data1['Peptide']).intersection(data2['Peptide'])

        #print(f'common_peptides\n{common_peptides}')

        # Filter data to keep only common peptides
        data1_filtered = data1[data1['Peptide'].isin(common_peptides)]
        data2_filtered = data2[data2['Peptide'].isin(common_peptides)]

        print(f'data1_filtered\n{data1_filtered}')
        print(f'data2_filtered\n{data2_filtered}')

        # top 20 
        # Removed since we want to display all data

        #data1_sorted = data1.sort_values(by='PeptideAbundance',ascending=False)
        #data2_sorted = data2.sort_values(by='PeptideAbundance',ascending=False)

        #print(data1_sorted)
        #print(data2_sorted)

        #data1_highest_df = data1_sorted.drop_duplicates(subset='Peptide', keep='first')
        #data2_highest_df = data2_sorted.drop_duplicates(subset='Peptide', keep='first')


        #data1_filtered_df = data1_sorted[data1_sorted['Peptide'].isin(data1_highest_df['Peptide'])]#top20_peptides_df['Peptide'])]
        #data2_filtered_df = data2_sorted[data2_sorted['Peptide'].isin(data2_highest_df['Peptide'])]#top20_peptides_df['Peptide'])]

 
        """         
        data1_valid_peptides = data1_filtered.groupby('Peptide').filter(
            lambda x: set(x['visit_month']) == set(selected_visit_months)
        )
        data2_valid_peptides = data2_filtered.groupby('Peptide').filter(
            lambda x: set(x['visit_month']) == set(selected_visit_months)
        ) """


        data1_filtered['visit_month'] = data1_filtered['visit_month'].astype(str)
        data2_filtered['visit_month'] = data2_filtered['visit_month'].astype(str)

        print(f'data1_valid_peptides\n{data1_filtered}')
        print(f'data2_valid_peptides\n{data2_filtered}')


        combined_data = pd.concat([data1_filtered, data2_filtered], ignore_index=True)

        print(f'combined_data\n{combined_data}')
        print(f'combined_data\n{combined_data.info()}')
        
        combined_data2 = combined_data.sort_values(by='PeptideAbundance',ascending=False)

        """         
        fig1 = px.bar(valid_peptides, 
             x='Peptide', 
             y='PeptideAbundance', 
             color='visit_month', 
             barmode='group',
             text='visit_month'
             
        ) """

        # Create a new column in the DataFrame with the desired hover text
        #valid_peptides['UniProt_ID'] = (
            #'Peptide: ' + valid_peptides['Peptide'] +
            #'<br>Visit Month: ' + valid_peptides['visit_month'].astype(str) +
            #'<br>Abundance: ' + valid_peptides['PeptideAbundance'].astype(str) +
            #'<br>UniProt ID: ' + 
            #valid_peptides['UniProt'])

        # Pass this new column to the `text` parameter in the `px.bar` function
        fig1 = px.bar(
            combined_data2,
            x='Peptide',
            y='PeptideAbundance',
            color='visit_month',
            barmode='group',
            #facet_col='Patient_ID',
            hover_data='UniProt',
            hover_name='Patient_ID',
            text='visit_month',  # Set the hover text to our custom column
            pattern_shape="Patient_ID", 
            #pattern_shape_sequence=[".", "x"]
        )

        """
        # Customize the hover template to display `text` only
        fig1.update_traces(
            hovertemplate='%{hover_data}<extra></extra>'
        )
        """
        
        fig1.update_layout(
            title=f"Comparison of {compare_by} Results for Patients {patient_id} and Patients {selected_patient_id}",
            dragmode='pan'  # Set the default interaction mode to pan
            #xaxis_title='Peptide',
            #yaxis_title='Peptide Abundance',
            #barmode='group'
        )


        # For Peptide or Protein bar chart
        fig1.update_xaxes(
            rangeslider=dict(visible=True),  # This adds the scrollbar below the plot
            range=[-0.5, 10]  # Adjust the range as needed to show only a part of the x-axis initially
            
        )

        fig1.add_annotation(
            text="This chart shows common peptides to both patients but may not be across all selected visit months.",
            xref="paper", yref="paper",
            x=0.5, y=1.05,  # Position the subtitle below the main title
            showarrow=False,
            font=dict(size=12, color="gray"),
            #xanchor='center'
        )

        fig1.update_layout(
            xaxis=dict(
                title='Peptide' if compare_by == 'Peptide' else 'UniProt',
                #tickangle=45  # Rotates labels to avoid overlap if there are many
            ),
            yaxis_title="Peptide Abundance" if compare_by == 'Peptide' else "NPX",
            #title_text=f"Patient {patient_id} {'Peptides' if compare_by == 'Peptide' else 'Proteins'} Abundance Grouped by Visit Months"
        )

        fig1.show()




        

        """ # Plot for Patient 1
        fig.add_trace(
            go.Bar(
                x=data1['Peptide'], 
                y=data1['PeptideAbundance'], 
                text=data1['visit_month'].astype(str),
                name=f"Patient {patient_id}"
            ),
            row=1, col=1
        )

        # Plot for Patient 2
        fig.add_trace(
            go.Bar(
                x=data2['Peptide'], 
                y=data2['PeptideAbundance'], 
                text=data2['visit_month'].astype(str),
                name=f"Patient {selected_patient_id}"
            ),
            row=1, col=2
        ) """

    elif compare_by == 'Protein':
        query = f"""
            SELECT UniProt, visit_month, NPX
            FROM proteins
            WHERE patient_id = ? AND visit_month IN ({formatted_months})
            ORDER BY NPX DESC
        """

        data1 = pd.read_sql_query(query, conn, params=(patient_id,))
        data2 = pd.read_sql_query(query, conn, params=(selected_patient_id,))

        print(data1)
        print(data2)

        # Add a new column to each DataFrame with the patient ID
        data1['Patient_ID'] = f'Patient {patient_id}'
        data2['Patient_ID'] = f'Patient {selected_patient_id}'

        print(f'data1\n{data1}')
        print(f'data2\n{data2}')

        # common proteins
        common_proteins = set(data1['UniProt']).intersection(data2['UniProt'])

        #print(f'common_proteins\n{common_proteins}')

        # Filter data to keep only common proteins
        data1_filtered = data1[data1['UniProt'].isin(common_proteins)]
        data2_filtered = data2[data2['UniProt'].isin(common_proteins)]

        print(f'data1_filtered\n{data1_filtered}')
        print(f'data2_filtered\n{data2_filtered}')


        data1_filtered['visit_month'] = data1_filtered['visit_month'].astype(str)
        data2_filtered['visit_month'] = data2_filtered['visit_month'].astype(str)

        print(f'data1_valid_proteins\n{data1_filtered}')
        print(f'data2_valid_proteins\n{data2_filtered}')


        combined_data = pd.concat([data1_filtered, data2_filtered], ignore_index=True)

        print(f'combined_data\n{combined_data}')
        print(f'combined_data\n{combined_data.info()}')
        
        combined_data2 = combined_data.sort_values(by='NPX',ascending=False)

        fig1 = px.bar(
            combined_data2,
            x='UniProt',
            y='NPX',
            color='visit_month',
            barmode='group',
            #facet_col='Patient_ID',
            #hover_data='UniProt',
            hover_name='Patient_ID',
            text='visit_month',  # Set the hover text to our custom column
            pattern_shape="Patient_ID", 
            #pattern_shape_sequence=[".", "x"]
        )

        
        fig1.update_layout(
            title=f"Comparison of {compare_by} Results for Patients {patient_id} and Patients {selected_patient_id}",
            dragmode='pan'  # Set the default interaction mode to pan
            #xaxis_title='UniProt',
            #yaxis_title='NPX',
            #barmode='group'
        )


        fig1.update_xaxes(
            rangeslider=dict(visible=True),  # This adds the scrollbar below the plot
            range=[-0.5, 10]  # Adjust the range as needed to show only a part of the x-axis initially
            
        )

        fig1.add_annotation(
            text="This chart shows common proteins to both patients but may not be across all selected visit months.",
            xref="paper", yref="paper",
            x=0.5, y=1.05,  # Position the subtitle below the main title
            showarrow=False,
            font=dict(size=12, color="gray"),
            #xanchor='center'
        )

        fig1.update_layout(
            xaxis=dict(
                title='Peptide' if compare_by == 'Peptide' else 'UniProt',
                #tickangle=45  # Rotates labels to avoid overlap if there are many
            ),
            yaxis_title="Peptide Abundance" if compare_by == 'Peptide' else "NPX",
            #title_text=f"Patient {patient_id} {'Peptides' if compare_by == 'Peptide' else 'Proteins'} Abundance Grouped by Visit Months"
        )

        fig1.show()

        """ fig.add_trace(
            go.Bar(
                x=data1.head(30)['UniProt'], 
                y=data1.head(30)['NPX'], 
                text=data1.head(30)['visit_month'].astype(str),
                name=f"Patient {patient_id}"
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Bar(
                x=data2.head(30)['UniProt'], 
                y=data2.head(30)['NPX'], 
                text=data2.head(30)['visit_month'].astype(str),
                name=f"Patient {selected_patient_id}"
            ),
            row=1, col=2
        ) """

    elif compare_by == 'Score':
        query = f"""
            SELECT visit_month, updrs_1, updrs_2, updrs_3, updrs_4
            FROM new_clinical_data
            WHERE patient_id = ? AND visit_month IN ({formatted_months})
        """

        data1 = pd.read_sql_query(query, conn, params=(patient_id,))
        data2 = pd.read_sql_query(query, conn, params=(selected_patient_id,))

        # Add a new column to each DataFrame with the patient ID
        data1['Patient_ID'] = f'Patient {patient_id}'
        data2['Patient_ID'] = f'Patient {selected_patient_id}'

        print(f'data1\n{data1}')
        print(f'data2\n{data2}')

        combined_data = pd.concat([data1, data2], ignore_index=True)

        print(f'combined_data\n{combined_data}')
        print(f'combined_data\n{combined_data.info()}')
        
        combined_data_melted = combined_data.melt(
            id_vars=['visit_month', 'Patient_ID'],  # Keep these columns
            var_name='score',                       # New column for scores
            value_name='value'                      # New column for values
        )

        """ 
         df_melted = score_data.melt(id_vars=["visit_month"], var_name="score", value_name="value")
        print(df_melted)

        fig3 = px.line(
            df_melted, 
            x='visit_month', 
            y='value', 
            color='score', 
            markers=True, 
            title=f"Patient {patient_id} UPDRS Score Trends Over Time",
        )
          
            """

        

        fig1 = px.line(
            combined_data_melted,
            x='visit_month',
            y='value',
            color='score',
            markers=True,
            facet_col='Patient_ID',
            #hover_data='UniProt',
            #hover_name='Patient_ID',
            #text='visit_month',  # Set the hover text to our custom column
            #pattern_shape="Patient_ID", 
            #pattern_shape_sequence=[".", "x"]
        )

        
        fig1.update_layout(
            title=f"Comparison of UPDRS {compare_by} Trends Over Time for Patients {patient_id} and Patients {selected_patient_id}",
            dragmode='pan'  # Set the default interaction mode to pan
            #xaxis_title='UniProt',
            #yaxis_title='NPX',
            #barmode='group'  Patient {patient_id} UPDRS Score Trends Over Time
        )

        fig1.show()

        """ df1_melted = data1.melt(id_vars=["visit_month"], var_name="score", value_name="value")
        df2_melted = data2.melt(id_vars=["visit_month"], var_name="score", value_name="value")

        fig.add_trace(
            go.Scatter(
                x=df1_melted['visit_month'], 
                y=df1_melted['value'], 
                mode='lines+markers',
                name=f"Patient {patient_id}",
                line=dict(color='blue')
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=df2_melted['visit_month'], 
                y=df2_melted['value'], 
                mode='lines+markers',
                name=f"Patient {selected_patient_id}",
                line=dict(color='red')
            ),
            row=1, col=2
        ) """

    else:
        print("Invalid comparison type")
        return 0
    
    """ fig.update_layout(
        title=f"Comparison of {compare_by} Results for Patients {patient_id} and Patients {selected_patient_id}",
        showlegend=False 
    )

    fig.show() """
    return 1



@app.route("/comperison_two", methods = ['POST'])
def comperison_two():
    
    if request.method == 'POST':
        try:
            patient_id = request.form['patient_id'] #942 #request.form['patient_id']
            #print(patient_id)
            selected_patient_id = request.form['selected_patient_id']
            #print(selected_patient_id)

            visit_months = get_common_visit_months(patient_id,selected_patient_id)
            #print(visit_months)

            compare_by = request.form['compare_by'] #str
            #print(compare_by)
            selected_visit_months = request.form.getlist('visit_month') #list of str
            print(selected_visit_months)

            result_two = get_two_results(patient_id,selected_patient_id,compare_by,selected_visit_months)


            """ with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute() """

        except:
            data_html = f'{result_two}'

        finally:
            #con.close()
            return render_template('compare_patients.html',visit_months=visit_months, selected_patient_id=selected_patient_id, patient_id=patient_id)
        
    else:
        return redirect('home.html')



'''def peptide_information(json_data):

     txt
    lines = response.strip().split('\n')
    peptide_info = {
        'Entry': '',
        'Entry_name': '',
        'ProteinName': '',
        'Gene': '',
        'Organism': '',
        'Length': '',
        'Function': '',
        'DiseaseInvolvement': ''
    }
    reading_function = False
    reading_disease = False

    for line in lines:
            
        if line.startswith("ID   "):
            peptide_info['Entry_name'] = line.split()[1]
            peptide_info['Length'] = line.split('Reviewed;        ')[1].split(';')[0].strip()
        elif line.startswith("AC   "):
            peptide_info['Entry'] = line.split()[1].rstrip(';')
        elif 'RecName: Full=' in line:
            peptide_info['ProteinName'] = line.split('Full=')[1].split(';')[0].strip()

        elif line.startswith("OS   "):
            peptide_info['Organism'] = line.split('OS   ')[1].rstrip('.')
        elif line.startswith("GN   Name="):
            peptide_info['Gene'] = line.split('Name=')[1].split(';')[0].strip()
        elif line.startswith("CC   -!- FUNCTION:"):
            reading_function = True
            peptide_info['Function'] = line[19:].strip()
        elif reading_function and line.startswith("CC       "):
            peptide_info['Function'] += ' ' + line.strip()
        elif not line.startswith("CC       ") and reading_function:
            reading_function = False
        elif line.startswith("CC   -!- DISEASE:"):
            reading_disease = True
            peptide_info['DiseaseInvolvement'] = line[19:].strip()
        elif reading_disease and line.startswith("CC       "):
            peptide_info['DiseaseInvolvement'] += ' ' + line.strip()
        elif not line.startswith("CC       ") and reading_disease:
            reading_disease = False
            
    
    peptide_info = {
        'Entry': json_data.get('primaryAccession', ''),
        'Entry_name': json_data.get('uniProtkbId', ''),
        'ProteinName': '',
        'Gene': '',
        'Organism': json_data.get('organism', {}).get('scientificName', ''),
        'Length': json_data.get('sequence', {}).get('length', ''),
        'Function': '',
        'DiseaseInvolvement': ''
    }

    # Extract the recommended protein name if available
    if 'proteinDescription' in json_data:
        recommended_name = json_data['proteinDescription'].get('recommendedName', {})
        peptide_info['ProteinName'] = recommended_name.get('fullName', {}).get('value', '')

    # Extract the gene name if available
    if 'genes' in json_data and len(json_data['genes']) > 0:
        peptide_info['Gene'] = json_data['genes'][0].get('geneName', {}).get('value', '')

    # Extract function information if available
    if 'comments' in json_data:
        for comment in json_data['comments']:
            # Check if 'type' key exists in comment
            if comment.get('type') == 'FUNCTION':
                peptide_info['Function'] = comment.get('text', [{}])[0].get('value', '')
                break  # Assume only one main function description

    # Extract disease involvement information if available
    if 'comments' in json_data:
        for comment in json_data['comments']:
            # Check if 'type' key exists in comment
            if comment.get('type') == 'DISEASE':
                peptide_info['DiseaseInvolvement'] = comment.get('text', [{}])[0].get('value', '')
                break  # Assume only one main disease description

    return peptide_info'''

def peptide_information(response_text):
    # Initialize the dictionary to store the required peptide information
    peptide_info = {
        'Entry': '',
        'Entry_name': '',
        'ProteinName': '',
        'Gene': '',
        'Organism': '',
        'Length': '',
        'Function': '',
        'DiseaseInvolvement': ''
    }
    
    reading_function = False
    reading_disease = False

    for line in response_text.splitlines():
        # Extract Entry name and Length
        if line.startswith("ID   "):
            parts = line.split()
            peptide_info['Entry_name'] = parts[1]
            peptide_info['Length'] = parts[-2] if 'Reviewed' in line else parts[-1]

        # Extract Entry (UniProt ID)
        elif line.startswith("AC   "):
            peptide_info['Entry'] = line.split()[1].rstrip(';')

        # Extract Protein Name
        elif 'RecName: Full=' in line:
            peptide_info['ProteinName'] = line.split('Full=')[1].split(';')[0].strip()

        # Extract Organism
        elif line.startswith("OS   "):
            peptide_info['Organism'] = line[5:].strip()

        # Extract Gene Name
        elif line.startswith("GN   Name="):
            peptide_info['Gene'] = line.split('Name=')[1].split(';')[0].strip()

        # Start reading the Function description
        elif line.startswith("CC   -!- FUNCTION:"):
            reading_function = True
            peptide_info['Function'] = line[19:].strip()  # Start with the first line of function

        # Continue reading the Function description
        elif reading_function and line.startswith("CC       "):
            peptide_info['Function'] += ' ' + line[8:].strip()  # Append continuation lines

        # Stop reading the Function section if it ends
        elif reading_function and not line.startswith("CC       "):
            reading_function = False

        # Start reading the Disease involvement section
        elif line.startswith("CC   -!- DISEASE:"):
            reading_disease = True
            peptide_info['DiseaseInvolvement'] = line[19:].strip()  # Start with the first line of disease info

        # Continue reading the Disease involvement section
        elif reading_disease and line.startswith("CC       "):
            peptide_info['DiseaseInvolvement'] += ' ' + line[8:].strip()  # Append continuation lines

        # Stop reading the Disease section if it ends
        elif reading_disease and not line.startswith("CC       "):
            reading_disease = False

    return peptide_info

@app.route('/peptide_info', methods = ['POST','GET'])
def peptide_info():

    if request.method == "POST":

        patient_id = request.form['patient_id']
        uniprot = request.form['uniprot']
        selec_pep = request.form['pep_name']

        #if uniprot

        try:
            url = f"https://www.uniprot.org/uniprot/{uniprot}.txt"
            response = requests.get(url)
            response.raise_for_status()
            peptide_info = peptide_information(response.text)
            
            # Check if the disease involvement directly indicates Parkinson's disease
            peptide_info['IsParkinsonRelated'] = 'Parkinson' in peptide_info['DiseaseInvolvement']
            
            if selec_pep != '':
                peptide_info['pep_name'] = selec_pep

            return render_template('peptide_info.html', peptide_info=peptide_info, patient_id=patient_id)
        except requests.HTTPError as e:
            patient_pro_info, patient_pep_info, patient_sco_info = patient_info(patient_id)
            return render_template('patient_page.html', error=f"HTTP Error {e.response.status_code}: {e.response.reason}", patient_id=patient_id, patient_pro_info=patient_pro_info,patient_pep_info=patient_pep_info,patient_sco_info=patient_sco_info)
    elif request.method == "GET":
        patient_id = request.args.get('patient_id')
        uniprot = request.args.get('uniprot')

        try:
            url = f"https://www.uniprot.org/uniprot/{uniprot}.txt"
            response = requests.get(url)
            response.raise_for_status()
            peptide_info = peptide_information(response.text)
            
            # Check if the disease involvement directly indicates Parkinson's disease
            peptide_info['IsParkinsonRelated'] = 'Parkinson' in peptide_info['DiseaseInvolvement']
            

            return render_template('peptide_info.html', peptide_info=peptide_info, patient_id=patient_id)
        except requests.HTTPError as e:
            patient_pro_info, patient_pep_info, patient_sco_info = patient_info(patient_id)
            return render_template('patient_page.html', error=f"HTTP Error {e.response.status_code}: {e.response.reason}", patient_id=patient_id, patient_pro_info=patient_pro_info,patient_pep_info=patient_pep_info,patient_sco_info=patient_sco_info)


    patients = get_all_patients().to_dict(orient='records')
    #print(2)
    return render_template('doctor_base.html', patients=patients)

'''if request.method == 'POST':
        patient_id = request.form['view_patient']
        #print(1)
    else:
        msg = 'Error: try again'
        patients = get_all_patients().to_dict(orient='records')
        #print(2)
        return render_template('doctor_base.html', patients=patients, msg=msg )
    

    patient_pro_info, patient_pep_info, patient_sco_info = patient_info(patient_id)

    return render_template('patient_page.html', patient_id=patient_id, patient_pro_info=patient_pro_info,patient_pep_info=patient_pep_info,patient_sco_info=patient_sco_info)
'''

def protein_information(protein):
    lines = protein.strip().split('\n')
    protein_info = {
        'ID': '',
        'Accession': '',
        'ProteinName': '',
        'Organism': '',
        'Function': '',
        'DiseaseInvolvement': ''
    }
    reading_function = False
    reading_disease = False

    for line in lines:
        if line.startswith("ID   "):
            protein_info['ID'] = line.split()[1]
        elif line.startswith("AC   "):
            protein_info['Accession'] = line.split()[1].rstrip(';')
        elif 'RecName: Full=' in line:
            protein_info['ProteinName'] = line.split('Full=')[1].split(';')[0].strip()
        elif line.startswith("OS   "):
            protein_info['Organism'] = line.split('OS   ')[1].rstrip('.')
        elif line.startswith("CC   -!- FUNCTION:"):
            reading_function = True
            protein_info['Function'] = line[19:].strip()
        elif reading_function and line.startswith("CC       "):
            protein_info['Function'] += ' ' + line.strip()
        elif not line.startswith("CC       ") and reading_function:
            reading_function = False
        elif line.startswith("CC   -!- DISEASE:"):
            reading_disease = True
            protein_info['DiseaseInvolvement'] = line[19:].strip()
        elif reading_disease and line.startswith("CC       "):
            protein_info['DiseaseInvolvement'] += ' ' + line.strip()
        elif not line.startswith("CC       ") and reading_disease:
            reading_disease = False

    return protein_info


@app.route('/protein_info')
def protein_info():
    if request.method == "POST":

        patient_id = request.form['patient_id']
        uniprot = request.form['uniprot']

        try:
            url = f"https://www.uniprot.org/uniprot/{uniprot}.txt"
            response = requests.get(url)
            response.raise_for_status()
            protein_info = protein_information(response.text)
            
            # Check if the disease involvement directly indicates Parkinson's disease
            protein_info['IsParkinsonRelated'] = 'Parkinson' in protein_info['DiseaseInvolvement']

            return render_template('protein_info.html', protein_info=protein_info, peptide_info=peptide_info, patient_id=patient_id)
        except requests.HTTPError as e:
            patient_pro_info, patient_pep_info, patient_sco_info = patient_info(patient_id)
            return render_template('patient_page.html', error=f"HTTP Error {e.response.status_code}: {e.response.reason}", patient_id=patient_id, patient_pro_info=patient_pro_info,patient_pep_info=patient_pep_info,patient_sco_info=patient_sco_info)
    
    elif request.method == "GET":
        patient_id = request.args.get('patient_id')
        uniprot = request.args.get('uniprot')

        try:
            url = f"https://www.uniprot.org/uniprot/{uniprot}.txt"
            response = requests.get(url)
            response.raise_for_status()
            protein_info = protein_information(response.text)
            
            # Check if the disease involvement directly indicates Parkinson's disease
            protein_info['IsParkinsonRelated'] = 'Parkinson' in protein_info['DiseaseInvolvement']
            

            return render_template('protein_info.html', protein_info=protein_info, peptide_info=peptide_info, patient_id=patient_id)
        except requests.HTTPError as e:
            patient_pro_info, patient_pep_info, patient_sco_info = patient_info(patient_id)
            return render_template('patient_page.html', error=f"HTTP Error {e.response.status_code}: {e.response.reason}", patient_id=patient_id, patient_pro_info=patient_pro_info,patient_pep_info=patient_pep_info,patient_sco_info=patient_sco_info)

    patients = get_all_patients().to_dict(orient='records')
    #print(2)
    return render_template('doctor_base.html', patients=patients)



if __name__ == '__main__':
    app.run(debug=True) 



