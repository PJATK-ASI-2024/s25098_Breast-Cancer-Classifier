FROM apache/airflow:2.10.4

# Add the requirements file
COPY requirements.txt /requirements.txt

# Install dependencies from requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt

