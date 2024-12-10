import pandas as pd
import sqlite3

# Load the datasets
proteins_df = pd.read_csv('/Users/mahayie/temp/compare/train_proteins.csv')
peptides_df = pd.read_csv('/Users/mahayie/temp/compare/train_peptides.csv')
clinical_data_df = pd.read_csv('/Users/mahayie/temp/compare/train_clinical_data.csv')
new_clinical_data_df = pd.read_csv('/Users/mahayie/temp/compare/integrated_patients_data.csv')

# Create a SQLite database and save the datasets into it
conn = sqlite3.connect('patient_data_v2.db')

# Save the datasets to the SQLite database
proteins_df.to_sql('proteins', conn, if_exists='replace', index=False)
peptides_df.to_sql('peptides', conn, if_exists='replace', index=False)
clinical_data_df.to_sql('clinical_data', conn, if_exists='replace', index=False)
new_clinical_data_df.to_sql('new_clinical_data', conn, if_exists='replace', index=False)

# Close the connection
conn.close()
