from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess
import os
import sys

API_SCRIPT_PATH = "/opt/airflow/app/main.py"
DOCKERFILE_PATH = "./app/Dockerfile"
DOCKER_IMAGE_NAME = "s25098/model_app"
DOCKER_IMAGE_TAG = "latest"


# Task 1: Run API locally
def run_api_locally():
    cwd = os.getcwd()
    print(f"Current Working Directory: {cwd}")

    subprocess.Popen(
        [
            sys.executable,
            "app/main.py"
        ],
        cwd=cwd,
    )
    print("Flask application started locally on port 5000.")


# Task 2: Docker builds image
def build_docker_image():
    print(f"Building Docker image {DOCKER_IMAGE_NAME}:{DOCKER_IMAGE_TAG}...")

    command = [
        "docker", "build",
        "-t", f"{DOCKER_IMAGE_NAME}:{DOCKER_IMAGE_TAG}",
        "-f", DOCKERFILE_PATH,
        "."
    ]

    subprocess.run(command, check=True)
    print("Docker image built successfully.")


# Task 3: Push Docker image to Docker Hub
def publish_docker_image():
    print(f"Pushing Docker image {DOCKER_IMAGE_NAME}:{DOCKER_IMAGE_TAG} to Docker Hub...")

    docker_username = os.getenv("DOCKER_USERNAME")
    docker_password = os.getenv("DOCKER_PASSWORD")

    login_command = [
        "docker",
        "login",
        "-u",
        docker_username,
        "-p",
        docker_password
    ]
    push_command = [
        "docker",
        "push",
        f"{DOCKER_IMAGE_NAME}:{DOCKER_IMAGE_TAG}"
    ]

    subprocess.run(login_command, check=True)
    subprocess.run(push_command, check=True)
    print("Docker image published successfully.")


with DAG(
        dag_id="6_contenerysation_and_api_dag",
        start_date=datetime(2024, 1, 1),
        schedule_interval=None,
        catchup=False,
) as dag:
    # Task 1: Run the Flask API locally on port 5000.
    run_api_task = PythonOperator(
        task_id="run_api_locally",
        python_callable=run_api_locally,
    )

    # Task 2: Build the Docker image for the Flask app.
    build_docker_image_task = PythonOperator(
        task_id="build_docker_image",
        python_callable=build_docker_image,
    )

    # Task 3: Push the built Docker image to Docker Hub.
    publish_docker_image_task = PythonOperator(
        task_id="publish_docker_image",
        python_callable=publish_docker_image,
    )

    run_api_task >> build_docker_image_task >> publish_docker_image_task
