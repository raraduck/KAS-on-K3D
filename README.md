# KAS-on-K3D

## 1. Install K3D cluster
Setting up with Port exposure and Host volume 
```bash
k3d cluster create kafka-cluster \
  --agents 3 \
    --port "30092:30092@server:*" \
    --port "30093:30093@server:*" \
    --port "30094:30094@server:*" \
    --port "30095:30095@server:*" \
    --port "30096:30096@server:*" \
    --port "30097:30097@server:*" \
  --volume <HOSTPATH_KAFKA>:/opt/kafka@all \
  --volume <HOSTPATH_AIRFLOW>:/opt/airflow@all \
  --volume <HOSTPATH_SPARK>:/opt/spark@all
```
## 1.1. Check Host and Local Path
```bash
k3d node list
docker exec -it k3d-airflow-cluster-agent-0 sh
~ $ ls -l /opt/kafka
~ $ ls -l /opt/airflow
~ $ ls -l /opt/spark
```

## 2. Install Kafka
```bash
helm repo add \
    bitnami https://charts.bitnami.com/bitnami
helm repo update
```
```bash
helm install kafka bitnami/kafka \
  --namespace kafka \
  --create-namespace \
  -f values.yaml
```
## 2.0. (manual installation tips)
```bash
helm template kafka bitnami/kafka \
  --namespace kafka \
  -f values.yaml > kafka-cluster.yaml
```
### 2.1. kafka-ui (manual install)
```bash
# kubectl create namespace kafka
kubectl apply -f kafka-ui.yaml
```

### 3. Producer and Consumer for Kafka Test
Producer
```bash
docker build -f Dockerfile.producer -t dwnusa/my-producer:v0.1.1 .

kubectl run kafka-producer --restart='Never'   --image dwnusa/my-producer:v0.1.1-amd64
```
Consumer
```bash
docker build -f Dockerfile.consumer -t dwnusa/my-consumer:v0.0.1 .

kubectl run kafka-consumer --restart='Never'   --image dwnusa/my-consumer:v0.0.1-amd64
```


## 4. Install Airflow (version 3.xx)
### 4.0. Customize Airflow Image
```bash
docker build -t dwnusa/airflow:v3.0.2-jdk17-pyspark-3.5.5-amd64 .
```
### 4.1. Mount PV, PVC
```bash
kubectl create -f pv-airflow.yaml
kubectl create -f pvc-airflow.yaml -n airflow
```
### 4.2. Helm Install Airflow
```bash
helm repo add \
    --force-update apache-airflow https://airflow.apache.org
helm repo update
```
```bash
helm upgrade \
    --install airflow apache-airflow/airflow \
    --namespace airflow \
    -f airflow-values.yaml

# or 

# helm upgrade --install airflow apache-airflow/airflow  \
#     --namespace airflow \
#     --create-namespace \
#     --set dags.persistence.enabled=true \
#     --set dags.persistence.existingClaim=airflow-dags \
#     --set airflow.extraPipPackages="{apache-airflow-providers-apache-spark,apache-airflow-providers-cncf-kubernetes}" \
#     --set postgresql.image.tag=latest
```
### 4.3. RBAC for cross namespace between airflow and spark-operator
```bash
kubectl create -f airflow-spark-rbac.yaml
```

### 4.4. Open NodePort Access
```bash
kubectl patch svc airflow-api-server -n airflow \
  -p '{"spec": {"type": "NodePort", "ports": [{"port": 8080, "targetPort": 8080, "nodePort": 30097}]}}'
```

## 5. Install Spark (version 3.xx)
### 5.0. Customize Spark Image
```bash
docker build -t dwnusa/spark:v3.5.4-amd64 .
```
### 5.1. Helm Install Spark
```bash
helm repo add \
    --force-update spark-operator https://kubeflow.github.io/spark-operator
helm repo update
```

- job script 경로는 sparkapp 용 yaml 파일에서 정의하고 airflow namespace 에서 관리
- airflow-spark-rbac 설정으로 airflow 가 spark-operator 자원을 접근하도록 허용

```bash
helm install spark-operator spark-operator/spark-operator \
    --namespace spark-operator \
    --create-namespace \
    --set sparkJobNamespace=default \
    --set rbac.create=true \
    --set webhook.enable=true \
    --set serviceAccounts.spark.name=spark \
    --wait
```