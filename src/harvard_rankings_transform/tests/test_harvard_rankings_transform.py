import pytest
import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from copy import deepcopy
from pyspark.sql import SparkSession, DataFrame, Column
from pyspark.testing.utils import assertDataFrameEqual
from typing import Optional, List
from pyspark.sql.functions import (col, lit, max, min, substring, try_divide, coalesce, lead, lag, avg, round)
import pandas as pd
from pyspark.sql.types import IntegerType, FloatType
import os
import sys

@pytest.fixture(name="spark")
def spark_fixture():
    
    os.environ['PYSPARK_PYTHON'] = sys.executable
    os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
    spark:SparkSession = SparkSession.Builder().master("local[1]").getOrCreate()
    spark.sparkContext.setLogLevel('WARN')

    yield spark

@pytest.fixture
def modules_list():
    file_name = "src\harvard_rankings_transform\src\harvard_rankings_transform.py"
    f = open(file_name, "r").read()
    pattern = r"(# BEGIN FUNC)[\s\S.]*(# END FUNC)"
    funcs = re.search(pattern=pattern, string=f).group()
    exec(funcs)
    local_clone = deepcopy(locals())
    return local_clone


def test_get_columns(spark: SparkSession, modules_list):
    get_columns = modules_list.get("get_columns")

    df_input = spark.createDataFrame(
        data=[["val1",  "val2", "12/01/2021",  "val1",   "1",  "2"]],
        schema=["col1", "col2", "Start_Date", "Data Value", "extra1", "extra2"]
    )
    df_expected = spark.createDataFrame(
        data=[["val1", "val2", "12/01/2021","val1"]],
                schema=["col1", "col2", "Start_Date", "value"]
    )
    metrics = ("col1", "col2")
    df_actual: DataFrame = get_columns(df_input, metrics)
    # assert df_actual.collect() == df_expected.collect()

    assertDataFrameEqual(df_actual, df_expected)

def test_parse_year(spark, modules_list):
    parse_year = modules_list.get("parse_year")
    df_input = spark.createDataFrame(
        data=[["12/27/2018"]],
        schema=["col1"]
    )
    df_expected = spark.createDataFrame(
        data=[["12/27/2018", 2018]],
                schema=["col1", "year"]
    ).withColumn("year", col("year").cast(IntegerType()))

    df_actual = df_input.withColumn(
        "year", parse_year("col1")
    )
    assertDataFrameEqual(df_actual, df_expected)

@pytest.mark.parametrize(
    "max,min,max_year,min_year,result",
    [
        (100, 50, 2022, 2021, 100.0),
        (75, 50, None, None, 50.0)
    ]
)
def test_get_annual_percent_change(spark: SparkSession, modules_list,
                                   max, min, max_year, min_year, result):
    get_annual_percent_change = modules_list.get("get_annual_percent_change")

    data = [["val1"]]
    df_input = spark.createDataFrame(data=data, schema=["col1"])

    if max_year is None or min_year is None:
        df_actual = df_input.select(get_annual_percent_change(lit(max), lit(min)).alias("result"))
    else:
        df_actual = df_input.select(get_annual_percent_change(lit(max), lit(min), lit(max_year), lit(min_year)).alias("result"))
    df_expected = spark.createDataFrame(data= [[result]], schema=["result"])

    assertDataFrameEqual(df_actual, df_expected)





