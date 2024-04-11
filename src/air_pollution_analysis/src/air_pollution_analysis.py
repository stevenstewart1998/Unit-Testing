# To run locally, add path to sys path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pyspark 
from pyspark.sql.window import Window 

from pyspark.sql import SparkSession, DataFrame, Column
from pyspark.sql.functions import (col, lit, max, min, substring, try_divide, coalesce, lead, lag, avg, round)
from pyspark.sql.types import IntegerType, FloatType

from kaggle.api.kaggle_api_extended import KaggleApi
from zipfile import ZipFile
from typing import Optional, List

spark: SparkSession = SparkSession.Builder().getOrCreate()

def instantiate_kaggle_api():
    api = KaggleApi()
    api.authenticate()
    return api

def unzip_file(file_name, path) -> bool:
    zipped_file_name =  f"{path}/{file_name}.zip"
    try:
        with ZipFile(zipped_file_name, "r") as unzipped_file:
            unzipped_file.extractall(path)
        return True
    except Exception as e:
        print(e)
        return False
    
def read_dataset(spark: SparkSession, 
                 api: KaggleApi, 
                 dataset_name: str, 
                 file_name: str, 
                 path:str) -> Optional[DataFrame]:
    try:
        api.dataset_download_file(dataset_name, file_name, path, True)
    except Exception as e: 
        print(e)
        return None
    unzip_file(file_name, path)
    unzipped_file_path = f"{path}/{file_name}"
    df = spark.read.csv(path=unzipped_file_path, header=True)
    return df

def write_to_csv(df: DataFrame):
    df.show(100, truncate=False)

# BEGIN FUNC

def get_columns(df: DataFrame, metrics: List[str] = []) -> DataFrame:
    return (
        df.select(
            *metrics, 
            col("Start_Date"),
            col("Data Value").alias("value")
        )
    )


def parse_year(col: Column) -> Column:
    parsed_column = substring(col, -4, 4).cast(IntegerType())
    return parsed_column

def get_annual_percent_change(max_value: Column, min_value: Column, max_year: Column = lit(1), min_year: Column = lit(1)) -> DataFrame:
    time_period = coalesce(try_divide(lit(1),(max_year - min_year)), lit(1))
    total_change = (max_value - min_value).cast(FloatType())
    percentage_change = coalesce(try_divide(total_change, min_value), max_value)
    annual_percent_change = round(percentage_change * time_period, 4)
    return annual_percent_change * 100

def agg_by_metric(df: DataFrame, metrics: List[col]) -> DataFrame:
    return (
        df.groupBy(metrics).agg(
            round(get_annual_percent_change(
            max("value").alias("max_value"),
            min("value").alias("min_value"),
            max("year").alias("max_year"),
            min("year").alias("min_year")
            ), 4).alias("total_percent_change")          
            )
        )

# END FUNC

if __name__ == "__main__":

    dataset_name = "sahirmaharajj/air-pollution-dataset"
    file_name = "Air_Quality.csv"
    data_path = "src/harvard_rankings_transform/data"


    api = instantiate_kaggle_api()
    df = read_dataset(spark, api, dataset_name, file_name, data_path)

    if not df:
        raise Exception("Dataset failed to be returned")


    metric_list = ["Indicator ID", "Name", "Geo Join ID", "Geo Place Name"]

    df_metrics = get_columns(df, metric_list) 
    df_metrics = df_metrics.withColumn("year", parse_year(col("Start_Date")))
    df_metrics = df_metrics.drop("Start_Date")
    df_agg = agg_by_metric(df_metrics, metric_list)


    write_to_csv(df_agg)

    spark.stop()

