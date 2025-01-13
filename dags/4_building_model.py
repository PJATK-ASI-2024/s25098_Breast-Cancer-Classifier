from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, mean_absolute_error, precision_score, recall_score, f1_score, \
    classification_report
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import joblib
import os

SHEET_NAME = "Breast_Cancer_Project"
CREDENTIALS_FILE_PATH = "/opt/airflow/credentials/credentials.json"


# Task 1: Fetch data from Google Sheets
def load_data_from_google_sheets(**kwargs):
    # Get credentials and authorize Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE_PATH, scope)
    client = gspread.authorize(credentials)

    sheet = client.open(SHEET_NAME)
    train_set_worksheet = sheet.worksheet("Processed Train Set")

    # Read data
    print("Reading data")
    rows = train_set_worksheet.get_all_values()
    headers = rows[0]
    data = pd.DataFrame(rows[1:], columns=headers)

    kwargs['ti'].xcom_push(key='processed_data', value=data.to_dict())
    print("Data loaded successfully!")


# Task 2: Split data
def split_data(**kwargs):
    processed_data = kwargs['ti'].xcom_pull(key='processed_data', task_ids='fetch_processed_data')
    data = pd.DataFrame(processed_data)

    # Converting to floats
    for column in data.columns:
        if data[column].dtype == 'object':
            data[column] = data[column].str.replace(',', '.').astype(float, errors='ignore')

    X = data.drop(columns=["Status"])
    y = data["Status"]

    # Split into train and test sets
    print("Splitting data into training and testing sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    kwargs['ti'].xcom_push(key='train_set', value=(X_train.to_dict(), y_train.to_dict()))
    kwargs['ti'].xcom_push(key='test_set', value=(X_test.to_dict(), y_test.to_dict()))
    print("Train and Test set saved successfully!")


# Task 3: Model training
def train_model(**kwargs):
    train_data = kwargs['ti'].xcom_pull(key='train_set', task_ids='split_data')
    X_train = pd.DataFrame(train_data[0])
    y_train = pd.Series(train_data[1])

    # Model used from tpot analysis
    model = RandomForestClassifier(bootstrap=False, criterion='entropy', max_features=0.9,
                                   min_samples_leaf=16, min_samples_split=3, n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    output_model_path = "/opt/airflow/model/model.pkl"
    joblib.dump(model, output_model_path)
    print(f"Model saved to {output_model_path}")


# Task 4: Model evaluation
def evaluate_model(**kwargs):
    test_data = kwargs['ti'].xcom_pull(key='test_set', task_ids='split_data')
    X_test = pd.DataFrame(test_data[0])
    y_test = pd.Series(test_data[1])

    model_path = "/opt/airflow/model/model.pkl"

    model = joblib.load(model_path)
    y_pred = model.predict(X_test)

    report = classification_report(y_test, y_pred, target_names=['Alive', 'Dead'])
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, pos_label='Alive')
    recall = recall_score(y_test, y_pred, pos_label='Alive')
    f1 = f1_score(y_test, y_pred, pos_label='Alive')

    report_path = "/opt/airflow/reports/evaluation_report.txt"
    with open(report_path, "w") as file:
        file.write(f"Accuracy: {accuracy:.2f}\n")
        file.write(f"Precision: {precision:.2f}\n")
        file.write(f"Recall: {recall:.2f}\n")
        file.write(f"F1-Score: {f1:.2f}\n")
        file.write(f"Classification Report:\n{report}\n")
    print(f"Evaluation report saved to {report_path}")


with DAG(
        dag_id="4_building_model_dag",
        start_date=datetime(2024, 1, 1),
        schedule_interval=None,
        catchup=False,
) as dag:
    fetch_processed_data_task = PythonOperator(
        task_id="fetch_processed_data",
        python_callable=load_data_from_google_sheets,
    )

    split_data_task = PythonOperator(
        task_id="split_data",
        python_callable=split_data,
    )

    train_model_task = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
    )

    evaluate_model_task = PythonOperator(
        task_id="evaluate_model",
        python_callable=evaluate_model,
    )

    fetch_processed_data_task >> split_data_task >> train_model_task >> evaluate_model_task
