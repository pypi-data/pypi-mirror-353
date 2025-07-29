import os
import subprocess
from datetime import date, timedelta

from pyspark.sql import SparkSession, functions as f


class AssetDataGetter:
    def __init__(self, spark: SparkSession, date_from: date, date_to: date = None, isin: str = "", msid: str = "", s3_bucket: str = None):
        self.spark = spark
        self.isin = isin.upper()
        self.msid = msid.upper()
        self.s3_bucket = s3_bucket if s3_bucket else os.environ.get("BUCKET")
        self.date_from = date_from
        self.date_to = date_to
        self.date_partitions = self.generate_date_list()

        if not self.isin and not self.msid:
            raise Exception("Isin or Msid is required")
        elif self.isin and self.msid:
            raise Exception("Only Isin or Msid is required, not both")

    def load_json_files_as_df(self, paths: list):
        _paths = [el for el in paths if ".json" in el]
        if not _paths:
            raise Exception("No json files found")
        try:
            # for json files with all \n and \r characters replaced with " "
            df = self.spark.read.options(mode="FAILFAST").json(_paths)
        except Exception as e:
            # for json files with all \n and \r characters retained
            df = self.spark.read.json(_paths, multiLine=True)

        df = df.withColumn("file_path", f.input_file_name())
        df = df.withColumn("file_arrival_date", f.expr("reverse(split(file_path, '/'))")) \
            .withColumn(
            "file_arrival_date",
            f.concat_ws(
                "-",
                f.array(
                    f.col("file_arrival_date").getItem(3),
                    f.col("file_arrival_date").getItem(2),
                    f.col("file_arrival_date").getItem(1)
                )
            )
        )
        return df

    def generate_date_list(self):
        if self.date_to is None:
            return [self.date_from.strftime("%Y/%m/%d")]
        return [(self.date_from + timedelta(days=dt)).strftime("%Y/%m/%d") for dt in range((self.date_to-self.date_from).days + 1)]

    def generate_id_named_paths(self, breadcrumbs: list, ext: str = ""):
        return [
            f"s3://{self.s3_bucket}/{breadcrumb}/{date_partition}/{self.isin if self.isin else self.msid}{ext}"
            for date_partition in self.date_partitions
            for breadcrumb in breadcrumbs
        ]

    @staticmethod
    def get_s3_file_paths(prefix_dir: str, target_substring: str):
        ls_cmd = f"aws s3 ls {prefix_dir} --recursive | grep '{target_substring}'"
        ret = subprocess.Popen(ls_cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].decode().split('\n')
        s3_paths = [el.split(" ")[-1] for el in ret if el]
        return s3_paths

    def validate_paths(self, paths: list):
        validated_path = []
        for path in paths:
            file_name = path.split("/")[-1]
            prefix_dir = "/".join(path.split("/")[:-1])
            s3_paths = self.get_s3_file_paths(prefix_dir=prefix_dir, target_substring=file_name)
            if f"{prefix_dir.replace(f's3://{self.s3_bucket}/', '')}/{file_name}" in s3_paths:
                validated_path.append(path)

        return validated_path

    def get_cbonds_json_files(self):
        breadcrumbs = [
            "landing/asset/public_listed/cbonds/json/emission",
            "landing/asset/public_listed/cbonds/json/flows",
            "landing/asset/public_listed/cbonds/json/tradings",
        ] if self.isin else []
        if not breadcrumbs:
            raise Exception("No msid dir breadcrumbs available")
        paths = self.generate_id_named_paths(breadcrumbs, ext=".json")
        paths = self.validate_paths(paths)
        return paths

    def get_morningstar_json_files(self):
        breadcrumbs = [
            "landing/asset/public_listed/morningstar/json/isin/live-price",
            "landing/asset/public_listed/morningstar/json/isin/full-response",
        ] if self.isin else [
            "landing/asset/public_listed/morningstar/json/msid/full-response",
            "landing/asset/public_listed/morningstar/json/msid/market-price",
            "landing/asset/public_listed/morningstar/json/msid/total-return-index",
        ]
        paths = self.generate_id_named_paths(breadcrumbs, ext=".json")
        paths = self.validate_paths(paths)
        return paths

    def get_morningstar_xml_files(self):
        breadcrumbs = [
            "landing/asset/public_listed/morningstar/xml/isin/dataoutput",
        ] if self.isin else [
            "landing/asset/public_listed/morningstar/xml/msid/dataoutput",
        ]
        paths = self.generate_id_named_paths(breadcrumbs, ext=".xml")
        paths = self.validate_paths(paths)
        return paths

    def get_reuters_json_files(self):
        breadcrumbs = [
            "landing/asset/public_listed/reuters/json/composite",
            "landing/asset/public_listed/reuters/json/fund-allocation",
            "landing/asset/public_listed/reuters/json/price-history",
            "landing/asset/public_listed/reuters/json/term-and-conditions",
        ] if self.isin else []
        if not breadcrumbs:
            raise Exception("No msid dir breadcrumbs available")
        paths = self.generate_id_named_paths(breadcrumbs, ext=".json")
        paths = self.validate_paths(paths)
        return paths

    def get_ms_asset_json_files(self):
        breadcrumbs = ["landing/asset/ms_asset"] if self.isin else []
        if not breadcrumbs:
            raise Exception("No msid dir breadcrumbs available")
        paths = self.generate_id_named_paths(breadcrumbs)
        s3_paths = []
        for path in paths:
            prefix_dir = "/".join(path.split("/")[:-1])
            _paths = self.get_s3_file_paths(prefix_dir=prefix_dir, target_substring=self.isin)
            s3_paths += [f"s3://{self.s3_bucket}/{el}" for el in _paths]

        return s3_paths


# asset_getter = AssetDataGetter(spark, msid="0P000111F7", date_from=date(2024, 11, 19), date_to=date(2024, 11, 22))
# paths = asset_getter.get_morningstar_json_files()
