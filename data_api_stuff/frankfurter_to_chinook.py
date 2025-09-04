import requests
import pandas as pd
import sqlalchemy as sql

# Get historical USD to ILS exchange rates from Frankfurter API (no login required)
response = requests.get(
    'https://api.frankfurter.app/2018-01-01..2022-12-25?amount=1&from=USD&to=ILS'
)
rates_table = pd.read_json(response.text)

# Extract the ILS rate from each 'rates' dictionary
rates_list = [
    rate_dict.get('ILS') for rate_dict in rates_table['rates'].values
]
rates_table['rates'] = rates_list

# Connect to local PostgreSQL ('chinook' database)
engine = sql.create_engine("postgresql://postgres:postgres@localhost:5432/chinook")

# Write the rates to the 'Dim_currency' table in the 'chinook_dwh' schema
rates_table['rates'].to_sql(
    name='Dim_currency',
    con=engine,
    schema='chinook_dwh'
)

# Optional: Print success message
print("Exchange rates loaded to table Dim_currency in schema chinook_dwh.")
