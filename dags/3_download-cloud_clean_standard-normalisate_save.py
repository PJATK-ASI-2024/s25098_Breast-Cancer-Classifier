from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os
import numpy as np

SHEET_NAME = "Breast_Cancer_Project"
CREDENTIALS_FILE_PATH = "/opt/airflow/credentials/credentials.json"


# Task 1: Fetch data from Google Sheets
def load_data_from_google_sheets(**kwargs):
    # Get credentials and authorize Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE_PATH, scope)
    client = gspread.authorize(credentials)

    sheet = client.open(SHEET_NAME)
    train_set_worksheet = sheet.worksheet("Train Set")

    # Read data
    print("Reading data")
    rows = train_set_worksheet.get_all_values()
    headers = rows[0]
    data = pd.DataFrame(rows[1:], columns=headers)

    kwargs['ti'].xcom_push(key='original_data', value=data.to_dict())
    print("Data loaded successfully!")


# Task 2: Clean the data
def clean_data(**kwargs):
    # Pull original data from the previous task
    original_data = kwargs['ti'].xcom_pull(key='original_data', task_ids='fetch_data')
    data = pd.DataFrame(original_data)
    print("Original data loaded successfully.")

    # Drop rows with missing values
    print(f"Number of rows with missing data:\n {data.isnull().sum().sum()}")
    if data.isnull().sum().sum() > 0:
        data = data.dropna()
        print("Rows with missing data deleted.")
    else:
        print("No missing data found.")

    # Drop duplicates
    number_of_duplicates = data.duplicated().sum()
    if number_of_duplicates > 0:
        print(f"Found {number_of_duplicates} duplicates. Removing them.")
        data = data.drop_duplicates()
    else:
        print("No duplicates found.")

    # Delete outliers based on IQR
    columns_to_check = ['Tumor Size', 'Regional Node Examined', 'Reginol Node Positive']

    lower_bounds = {}
    upper_bounds = {}

    print("Ensuring columns are numeric...")
    for col in columns_to_check:
        data[col] = pd.to_numeric(data[col], errors='coerce')
        print(f"Column '{col}' converted to numeric values.")

    # Calculate IQR and bounds for outlier detection
    print("Calculating IQR for outlier detection...")
    for col in columns_to_check:
        Q1 = data[col].quantile(0.25)
        Q3 = data[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bounds[col] = Q1 - 1.5 * IQR
        upper_bounds[col] = Q3 + 1.5 * IQR
        print(
            f"For column '{col}', IQR is {IQR:.2f}, lower bound is {lower_bounds[col]:.2f}, upper bound is {upper_bounds[col]:.2f}")

    # Remove rows that are outliers
    cleaned_data = data
    for col in columns_to_check:
        initial_rows = cleaned_data.shape[0]
        cleaned_data = cleaned_data[(cleaned_data[col] >= lower_bounds[col]) & (cleaned_data[col] <= upper_bounds[col])]
        removed_rows = initial_rows - cleaned_data.shape[0]
        if removed_rows > 0:
            print(f"Removed {removed_rows} outlier rows from column '{col}'")
        else:
            print(f"No outliers removed from column '{col}'")

    # Modify the 'Grade' column
    cleaned_data['Grade'] = cleaned_data['Grade'].replace(" anaplastic; Grade IV", '4')
    cleaned_data['Grade'] = pd.to_numeric(cleaned_data['Grade'], errors='coerce')
    print("Replaced ' anaplastic; Grade IV' with '4' in the 'Grade' column.")

    # Drop unwanted columns
    cleaned_data = cleaned_data.drop(columns=['A Stage', 'Estrogen Status'])
    print("Dropped 'A Stage' and 'Estrogen Status' columns.")

    # Push cleaned data to XCom
    kwargs['ti'].xcom_push(key='cleaned_data', value=cleaned_data.to_dict())

    print("Cleaned data pushed to XCom.")


# Task 3: Standardize, normalize and encode data
def process_data(**kwargs):
    # Pull cleaned data from XCom
    cleaned_data = kwargs['ti'].xcom_pull(key='cleaned_data', task_ids='clean_data')
    data = pd.DataFrame(cleaned_data)
    print("Cleaned data loaded successfully.")

    X = data.drop(columns=['Status'])
    y = data['Status']

    # Identify numerical and categorical columns
    numerical_cols = X.select_dtypes(include=['number']).columns
    categorical_cols = X.select_dtypes(exclude=['number']).columns

    # Standardize the numeric columns
    print("Standardizing the numerical data...")
    scaler = StandardScaler()
    X_numeric_scaled = pd.DataFrame(scaler.fit_transform(X[numerical_cols]), columns=numerical_cols)
    print("Numerical data standardized successfully.")

    # Normalize the standardized numeric data
    print("Normalizing the standardized data...")
    normalizer = MinMaxScaler()
    X_numeric_normalized = pd.DataFrame(normalizer.fit_transform(X_numeric_scaled), columns=numerical_cols)
    print("Numerical data normalized successfully.")

    # One-hot encoding for categorical data
    print("Encoding categorical variables using one-hot encoding...")
    X_categorical_encoded = pd.get_dummies(X[categorical_cols], drop_first=True)
    print("Categorical data encoded successfully")

    # Index reset
    X_categorical_encoded = X_categorical_encoded.reset_index(drop=True)
    X_numeric_normalized.reset_index(drop=True, inplace=True)

    # Map 'True'/'False' to 1/0 for any boolean columns after one-hot encoding
    for col in X_categorical_encoded.columns:
        if X_categorical_encoded[col].dtype == bool:  # Check if column is of boolean type
            print(f"Mapping 'True'/'False' to 1/0 in column '{col}'...")
            X_categorical_encoded[col] = X_categorical_encoded[col].astype(int)

    # Concatenate the numeric and categorical data
    print("Combining normalized numerical data with encoded categorical data...")
    processed_data = pd.concat([X_numeric_normalized, X_categorical_encoded], axis=1)
    processed_data['Status'] = y.values
    print(f"Processed data shape: {processed_data.shape}")

    # Push the processed data to XCom
    kwargs['ti'].xcom_push(key='processed_data', value=processed_data.to_dict())
    print("Processed data pushed to XCom.")


# Task 4: Save processed data to Google Sheets
def save_data_to_sheets(**kwargs):
    # Get credentials and authorize Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE_PATH, scope)
    client = gspread.authorize(credentials)

    sheet = client.open(SHEET_NAME)

    # Pull processed data from XCom
    processed_data = kwargs['ti'].xcom_pull(key='processed_data', task_ids='process_data')
    data = pd.DataFrame(processed_data)
    print(f"Processed data pulled from XCom successfully. Data shape: {data.shape}")

    # Save processed data
    try:
        print("Saving processed data to 'Processed Train Set' worksheet...")
        processed_data_worksheet = sheet.worksheet("Processed Train Set")
        processed_data_worksheet.clear()
        processed_data_worksheet.update([data.columns.values.tolist()] + data.values.tolist())
        print("Processed data saved successfully.")
    except Exception as e:
        print(f"Error saving processed data: {e}")


with DAG(
        dag_id="3_download-cloud_clean_standard-normalisate_save_dag",
        start_date=datetime(2025, 1, 1),
        schedule_interval=None,
        catchup=False,
) as dag:
    # Task 1: Load data from Google Sheets
    fetch_data_task = PythonOperator(
        task_id="fetch_data",
        python_callable=load_data_from_google_sheets,
    )

    # Task 2: Clean data
    clean_data_task = PythonOperator(
        task_id="clean_data",
        python_callable=clean_data,
    )

    # Task 3: Standardize, normalize and encode data
    process_data_task = PythonOperator(
        task_id="process_data",
        python_callable=process_data,
    )

    # Task 4: Save processed data into Google Sheets
    save_data_task = PythonOperator(
        task_id="save_data",
        python_callable=save_data_to_sheets,
    )

    # Define task dependencies
    fetch_data_task >> clean_data_task >> process_data_task >> save_data_task
