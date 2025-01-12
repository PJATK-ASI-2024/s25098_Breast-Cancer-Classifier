from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

SHEET_NAME = "Breast_Cancer_Project"
CSV_FILE_PATH = "/opt/airflow/datasets/Breast_Cancer.csv"
CREDENTIALS_FILE_PATH = "/opt/airflow/credentials/credentials.json"


# Task 1: Load data from a local CSV file
def load_data(**kwargs):
    data = pd.read_csv(CSV_FILE_PATH)
    kwargs['ti'].xcom_push(key='original_data', value=data.to_dict())
    print("Data loaded successfully!")


# Task 2: Split data into train and test sets
def split_data(**kwargs):
    # Pull original data from the previous task
    original_data = kwargs['ti'].xcom_pull(key='original_data', task_ids='load_data')

    data = pd.DataFrame(original_data)
    print(f"Original data shape: {data.shape}")

    # Split into train and test sets
    print("Splitting data into training and testing sets...")
    train_set, test_set = train_test_split(data, test_size=0.3, random_state=42)
    print(f"Train data shape: {train_set.shape}")
    print(f"Test data shape: {test_set.shape}")

    # Push split sets to XCom
    kwargs['ti'].xcom_push(key='train_set', value=train_set.to_dict())
    kwargs['ti'].xcom_push(key='test_set', value=test_set.to_dict())
    print("Data split completed!")


# Task 3: Save split data to Google Sheets
def save_split_data_to_sheets(**kwargs):
    # Get credentials and authorize Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE_PATH, scope)
    client = gspread.authorize(credentials)

    sheet = client.open(SHEET_NAME)
    print(sheet.worksheets())

    # Pull train and test set from XCom
    train_data = kwargs['ti'].xcom_pull(key='train_set', task_ids='split_data')
    test_data = kwargs['ti'].xcom_pull(key='test_set', task_ids='split_data')
    train_df = pd.DataFrame(train_data)
    test_df = pd.DataFrame(test_data)
    print(f"Train set to be saved: {train_df.shape}")
    print(f"Test set to be saved: {test_df.shape}")

    # Update train set worksheet
    try:
        train_set_worksheet = sheet.worksheet("Train Set")
        train_set_worksheet.clear()
        train_set_worksheet.update([train_df.columns.values.tolist()] + train_df.values.tolist())
        print(f"'{train_set_worksheet}' updated successfully!")
    except Exception as e:
        print(f"Error updating train set worksheet: {e}")

    # Update test set worksheet
    try:
        test_set_worksheet = sheet.worksheet("Test Set")
        test_set_worksheet.clear()
        test_set_worksheet.update([test_df.columns.values.tolist()] + test_df.values.tolist())
        print(f"'{test_set_worksheet}' updated successfully!")
    except Exception as e:
        print(f"Error updating test set worksheet: {e}")


# Define the DAG
with DAG(
        dag_id="data_split_dag",
        start_date=datetime(2025, 1, 1),
        schedule_interval=None,
        catchup=False,
) as dag:
    # Task 1: Load CSV data
    load_task = PythonOperator(
        task_id="load_data",
        python_callable=load_data,
    )

    # Task 2: Split data into train and test sets
    split_data_task = PythonOperator(
        task_id="split_data",
        python_callable=split_data,
    )

    # Task 3: Save the training and testing data into Google Sheets
    save_split_data_task = PythonOperator(
        task_id="save_split_data",
        python_callable=save_split_data_to_sheets,
    )

    # Define task dependencies
    load_task >> split_data_task >> save_split_data_task
