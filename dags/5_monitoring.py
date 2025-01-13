from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from datetime import datetime
import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

MODEL_PATH = "/opt/airflow/models/model.pkl"
TEST_DATA_PATH = "/opt/airflow/datasets/processed_data.csv"
REPORT_PATH = "/opt/airflow/reports/evaluation_report.txt"


# Task 1: Analiza dokładności modelu
def analyze_model_quality(**kwargs):
    print("Loading model and test data...")
    model = joblib.load(MODEL_PATH)
    test_data = pd.read_csv(TEST_DATA_PATH)

    X_test = test_data.drop(columns=["Status"])
    y_test = test_data["Status"]

    print("Making predictions and calculating metrics...")
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, pos_label='Alive')
    recall = recall_score(y_test, y_pred, pos_label='Alive')
    f1 = f1_score(y_test, y_pred, pos_label='Alive')
    report = classification_report(y_test, y_pred, target_names=['Alive', 'Dead'])

    # Save metrics to a report file
    print("Saving quality report...")
    with open(REPORT_PATH, "w") as file:
        file.write(f"Accuracy: {accuracy:.2f}\n")
        file.write(f"Precision: {precision:.2f}\n")
        file.write(f"Recall: {recall:.2f}\n")
        file.write(f"F1-Score: {f1:.2f}\n")
        file.write(f"Classification Report:\n{report}\n")

    kwargs['ti'].xcom_push(key="metrics",
                           value={"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1})
    print("Model quality analyzed and metrics pushed to XCom.")


# Task 2: Model tests
def run_model_tests(**kwargs):
    print("Fetching metrics from XCom...")
    metrics = kwargs['ti'].xcom_pull(key="metrics", task_ids="analyze_model_quality")

    # Define thresholds
    accuracy_threshold = 0.85
    f1_threshold = 0.85

    print("Running tests on model quality metrics...")
    if metrics["accuracy"] < accuracy_threshold or metrics["f1"] < f1_threshold:
        kwargs['ti'].xcom_push(key="test_result", value="below_threshold")
        print(f"Model quality is below thresholds: Accuracy={metrics['accuracy']}, F1={metrics['f1']}")
    else:
        kwargs['ti'].xcom_push(key="test_result", value="passed")
        print("Model quality tests passed successfully.")


# Task 3: Email notification function
def email_notification(**kwargs):
    print("Fetching test result from XCom...")
    test_result = kwargs['ti'].xcom_pull(key="test_result", task_ids="run_model_tests")
    metrics = kwargs['ti'].xcom_pull(key="metrics", task_ids="analyze_model_quality")

    # Set message body based on test result
    if test_result == "below_threshold":
        subject = "Airflow Alert: Model Quality Below Threshold"
        body = f"""
        Task failed due to model quality being below thresholds.

        Details:
        Accuracy: {metrics['accuracy']:.2f}
        F1-Score: {metrics['f1']:.2f}
        """
    else:
        subject = "Airflow Alert: Model Quality Passed"
        body = f"""
        Task passed successfully with satisfactory model quality metrics.

        Details:
        Accuracy: {metrics['accuracy']:.2f}
        F1-Score: {metrics['f1']:.2f}
        """

    # Sending an email manually in the task
    email_operator = EmailOperator(
        task_id='send_email_on_failure',
        to='s25098@pjwstk.edu.pl',
        subject=subject,
        html_content=body
    )

    # Execute the email operator
    email_operator.execute(context=kwargs)
    print(f"Failure notification email sent to {email_operator.to}.")


with DAG(
        dag_id="5_monitoring_dag",
        start_date=datetime(2023, 1, 1),
        schedule_interval=None,
        catchup=False,
) as dag:
    # Task 1: Analyze model quality
    analyze_model_quality_task = PythonOperator(
        task_id="analyze_model_quality",
        python_callable=analyze_model_quality,
    )

    # Task 2: Run model tests
    run_model_tests_task = PythonOperator(
        task_id="run_model_tests",
        python_callable=run_model_tests,
    )

    # Task 3: Send email notification based on results
    notify_failure_task = PythonOperator(
        task_id="notify_failure",
        python_callable=email_notification,
    )

    analyze_model_quality_task >> run_model_tests_task >> notify_failure_task
