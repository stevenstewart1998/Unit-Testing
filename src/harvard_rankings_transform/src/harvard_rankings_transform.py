# To run locally, add path to sys path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pyspark 
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col
import pandas
from kaggle.api.kaggle_api_extended import KaggleApi
from zipfile import ZipFile


dataset_name = "sahirmaharajj/air-pollution-dataset"
file_name = "Air_Quality.csv"
data_path = "src/harvard_rankings_transform/data"
spark = SparkSession.builder.getOrCreate()

def instantiate_kaggle_api():
    api = KaggleApi()
    api.authenticate()
    return api

def unzip_file(file_name, path):
    zipped_file_name =  f"{path}/{file_name}.zip"
    with ZipFile(zipped_file_name, "r") as unzipped_file:
        unzipped_file.extractall(path)
    
def read_dataset(spark: SparkSession, 
                 api: KaggleApi, 
                 dataset_name: str, 
                 file_name: str, 
                 path:str) -> DataFrame:
    dataset = api.dataset_download_file(dataset_name, file_name, path, True)
    print(dataset)
    unzip_file(file_name, path)
    unzipped_file_path = f"{path}/{file_name}"
    df = spark.read.csv(path=unzipped_file_path, header=True)
    return df
# metrics
    # distinct measure name
    # 

# BEGIN FUNC
def get_distinct_name(df: DataFrame) -> DataFrame:
    pass


# END FUNC

api = instantiate_kaggle_api()
df = read_dataset(spark, api, dataset_name, file_name, data_path)



    

