from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, max, count
import os

# 1 Spark 세션 생성
spark = SparkSession.builder.appName("AnalyzeCSV").getOrCreate()

# 2 CSV 로드
csv_path = "/opt/spark-data/data.csv"  # ConfigMap이나 PVC 마운트 경로
df = spark.read.option("header", True).csv(csv_path, inferSchema=True)

print("\n[1] CSV Schema:")
df.printSchema()

print("\n[2] 데이터 샘플:")
df.show(10, truncate=False)

# 3 컬럼 분석 (예시: score 컬럼 기준)
target_col = "age"

if target_col not in df.columns:
    raise ValueError(f"'{target_col}' 컬럼이 CSV에 존재하지 않습니다. 현재 컬럼들: {df.columns}")

# 4 평균, 최대, 개수 계산
result_df = df.select(
    avg(col(target_col)).alias("avg_age"),
    max(col(target_col)).alias("max_age"),
    count(col(target_col)).alias("count_rows")
)

print("\n[3] 통계 결과:")
result_df.show()

# 5 결과 파일로 저장 (Spark Operator에서는 driver pod 내부 경로)
output_dir = "/opt/spark-data/output"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "result.csv")

result_df.coalesce(1).write.mode("overwrite").option("header", True).csv(output_path)

print(f"\n[4] 결과 파일 저장 완료 → {output_path}")

# 6 Spark 종료
spark.stop()
