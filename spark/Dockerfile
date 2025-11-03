FROM docker.io/library/spark:3.5.4
WORKDIR /opt/spark-data

RUN pip install python-dotenv pyspark pandas numpy matplotlib scikit-learn kafka-python

COPY jars /opt/spark/jars/