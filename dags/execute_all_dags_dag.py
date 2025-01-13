from airflow import DAG
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from datetime import datetime

# Define DAG
with DAG(
        dag_id="pipeline_dag",
        start_date=datetime(2023, 1, 1),
        schedule_interval=None,
        catchup=False,
) as dag:
    # Trigger 3_download-public_split_save_dag
    trigger_data_splitting = TriggerDagRunOperator(
        task_id="trigger_data_splitting",
        trigger_dag_id="3_download-public_split_save_dag",
    )

    # Trigger 3_download-cloud_clean_standard-normalisate_save_dag
    trigger_data_cleaning = TriggerDagRunOperator(
        task_id="trigger_data_cleaning",
        trigger_dag_id="3_download-cloud_clean_standard-normalisate_save_dag",
    )

    # Trigger 4_building_model_dag
    trigger_model_building = TriggerDagRunOperator(
        task_id="trigger_model_building",
        trigger_dag_id="4_building_model_dag",
    )

    # Trigger 5_monitoring_dag
    trigger_monitoring = TriggerDagRunOperator(
        task_id="trigger_monitoring",
        trigger_dag_id="5_monitoring_dag",
    )

    # Trigger 6_contenerysation_and_api_dag
    trigger_containerisation = TriggerDagRunOperator(
        task_id="trigger_containerisation",
        trigger_dag_id="6_contenerysation_and_api_dag",
    )

    # Define task dependencies
    trigger_data_splitting >> trigger_data_cleaning >> trigger_model_building >> trigger_monitoring >> trigger_containerisation
