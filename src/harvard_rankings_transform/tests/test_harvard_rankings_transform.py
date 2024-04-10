import pytest
import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from copy import deepcopy
from pyspark.sql import SparkSession, DataFrame


@pytest.fixture(name="spark")
def spark_fixture():
    spark = SparkSession.builder.appName("Testing PySpark Example").getOrCreate()
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

def test_modules(spark, modules_list):
    module = modules_list.get("get_distinct_name")
    raise Exception(module)