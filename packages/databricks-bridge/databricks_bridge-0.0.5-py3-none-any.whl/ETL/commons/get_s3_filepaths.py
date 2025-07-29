import os
from datetime import datetime, timedelta
from typing import Union, List, Any, Tuple
import copy


class GetS3Files:
    def __init__(self, env: dict, breadcrumb: str, date_diff: int = 0, exact_date: str = "", date_range: dict = None, verbose: bool = True):
        self.dbutils = env["dbutils"]
        self.duration_sec = 0
        self.trigger_exceptions(exact_date, date_range)
        self.verbose = verbose

        if self.verbose:
            print(f"\nRetrieving file paths...")
        start_time = datetime.now()

        if date_range:
            date_start = datetime.strptime(date_range["start"], "%Y/%m/%d")
            date_end = datetime.strptime(date_range["end"], "%Y/%m/%d")
            date_delta = date_start - date_end
            self.date_range_diff = abs(date_delta.days)
            self.exact_date = date_range["start"] if date_delta.days > 0 else date_range["end"]
            file_paths = []
            paths_n_sizes = []
            for i in range(self.date_range_diff+1):
                self.date_diff = -i
                ret = self.get_s3_filepaths(breadcrumb)
                file_paths += ret[0] if isinstance(ret[0], list) else []
                paths_n_sizes += ret[1] if isinstance(ret[1], list) else []
            self.file_paths = file_paths
            self.paths_n_sizes = paths_n_sizes
        else:
            self.date_diff = date_diff
            self.exact_date = exact_date
            self.file_paths, self.paths_n_sizes = self.get_s3_filepaths(breadcrumb)

        self.duration_sec = (datetime.now() - start_time).total_seconds()

        if self.verbose:
            print(f"\nRetrieved all file paths - time elapsed: {self.duration_sec} seconds\n")

    def trigger_exceptions(self, exact_date, date_range):

        if exact_date:
            year_month_day = exact_date.split("/")
            if "/" not in exact_date or len(year_month_day[0]) != 4 or len(year_month_day[1]) != 2 or len(
                    year_month_day[2]) != 2:
                raise ValueError("expected exact_date format: 'YYYY/MM/DD'")

        if date_range:
            keys = list(date_range.keys())
            keys.sort()

            if keys != ["end", "start"]:
                raise ValueError('expected date_range keys: ["end_date", "start_date"]')
            elif keys == ["end", "start"]:
                start_year_month_day = date_range["start"].split("/")
                end_year_month_day = date_range["end"].split("/")
                if "/" not in date_range["start"] or "/" not in date_range["end"] or len(start_year_month_day[0]) != 4 or len(start_year_month_day[1]) != 2 or len(
                        start_year_month_day[2]) != 2 or len(end_year_month_day[0]) != 4 or len(end_year_month_day[1]) != 2 or len(
                        end_year_month_day[2]) != 2:
                    raise ValueError("expected start and end date format: 'YYYY/MM/DD'")

    @staticmethod
    def __repr__():
        print("""
        exact_date format: "YYYY/MM/DD" (str)
        date_diff: -1 (int) for previous day
        date_range format: {"start": "YYYY/MM/DD", "end": "YYYY/MM/DD"}
        
        should be called like so:
            get_filepaths = GetS3Files(env=locals(), breadcrumb="landing/salesforce/ms-salesforce-sync") # for current day
            get_filepaths = GetS3Files(env=locals(), breadcrumb="landing/salesforce/ms-salesforce-sync", date_diff=-1) # for day before
            get_filepaths = GetS3Files(env=locals(), breadcrumb="landing/salesforce/ms-salesforce-sync", exact_date="2022/07/20") # for exact date

            file_paths = get_filepaths.file_paths
            duration_sec = get_filepaths.duration_sec

        working breadcumbs:
        - landing/asset/ms_asset
        - landing/asset/preqin/csv/delta * (doesnt exist in staging)
        - landing/asset/preqin/csv/initial
        - landing/asset/public_listed/cbonds/json/emission
        - landing/asset/public_listed/cbonds/json/flows
        - landing/asset/public_listed/cbonds/json/tradings
        - landing/asset/public_listed/morningstar/json/isin/full-response
        - landing/asset/public_listed/morningstar/json/isin/live-price * (doesnt exist in staging)
        - landing/asset/public_listed/morningstar/json/msid/full-response
        - landing/asset/public_listed/morningstar/json/msid/market-price
        - landing/asset/public_listed/morningstar/json/msid/total-return-index
        - landing/asset/public_listed/morningstar/xml/isin/dataoutput
        - landing/asset/public_listed/morningstar/xml/msid/dataoutput
        - landing/asset/public_listed/reuters/json/composite
        - landing/asset/public_listed/reuters/json/fund-allocation
        - landing/asset/public_listed/reuters/json/price-history
        - landing/asset/public_listed/reuters/json/term-and-conditions
        - landing/salesforce/ms-salesforce-sync
        - landing/financial_statement/ms-integration/aj_bell
        - landing/financial_statement/ms-integration/brooks_mcdonald
        - landing/financial_statement/ms-integration/canaccord
        - landing/financial_statement/ms-integration/cazenove_capital
        - landing/financial_statement/ms-integration/charles_stanley
        - landing/financial_statement/ms-integration/citi
        - landing/financial_statement/ms-integration/citi_jersey
        - landing/financial_statement/ms-integration/citi_singapore
        - landing/financial_statement/ms-integration/credit_suisse
        - landing/financial_statement/ms-integration/credo
        - landing/financial_statement/ms-integration/goldman_sachs
        - landing/financial_statement/ms-integration/handelsbanken
        - landing/financial_statement/ms-integration/hedgeserv
        - landing/financial_statement/ms-integration/interactive_brokers
        - landing/financial_statement/ms-integration/investec
        - landing/financial_statement/ms-integration/jp_morgan
        - landing/financial_statement/ms-integration/julius_baer
        - landing/financial_statement/ms-integration/killik
        - landing/financial_statement/ms-integration/kleinwort_hambros
        - landing/financial_statement/ms-integration/lombard_international_assurance
        - landing/financial_statement/ms-integration/lombard_odier
        - landing/financial_statement/ms-integration/morgan_stanley
        - landing/financial_statement/ms-integration/pictet
        - landing/financial_statement/ms-integration/rbc
        - landing/financial_statement/ms-integration/rbc_us
        - landing/financial_statement/ms-integration/rothschild
        - landing/financial_statement/ms-integration/ruffer
        - landing/financial_statement/ms-integration/ubs
        - landing/financial_statement/ms-yapily/json/accounts
        - landing/financial_statement/ms-yapily/json/consents
        - landing/financial_statement/ms-yapily/json/transactions
        - landing/currency-rate
        - landing/client-portal
        - landing/reported_issues/calculation_error
        - landing/reported_issues/input_error
        - landing/reported_issues/mobile
        - landing/reported_issues/other * (doesnt exist in staging)
        - landing/reported_issues/technical_bug
        """)

    def get_s3_filepaths(self, breadcrumb: str, comb_file_paths={}) -> Tuple[Union[List[Any], str], list]:
        bucket = os.environ.get("BUCKET")
        if self.exact_date != "":
            try:
                target_date = datetime.strptime(self.exact_date, "%Y/%m/%d") + timedelta(days=self.date_diff)
            except:
                ret = f"Invalid date format provided for exact_date: {self.exact_date}\nThe expected date format is YYYY/MM/DD"
                print(ret)
                return ret, []
        else:
            target_date = datetime.now() + timedelta(days=self.date_diff)
        year = target_date.strftime("%Y")
        month = target_date.strftime("%m")
        day = target_date.strftime("%d")

        is_ms_integration = True if breadcrumb.split("/")[-2] == "ms-integration" else False

        date_str = "-".join([year, month, day]) if is_ms_integration else "/".join([year, month, day])
        breadcrumb = breadcrumb + "/prepared" if is_ms_integration else breadcrumb

        file_path = f"s3a://{bucket}/{breadcrumb}/{date_str}/"

        if "/".join(breadcrumb.split("/")[-2:]) == "ms_asset/legacy":
            ms_asset_isin_path = "s3a://" + bucket + "/" + breadcrumb + "/"
            isin_paths_response = self.dbutils.fs.ls(ms_asset_isin_path)
            isin_names = [isin_info.name[:-1] for isin_info in isin_paths_response]
            for i in range(len(isin_names)):
                isin = isin_names[i]
                file_paths, paths_n_sizes = self.get_s3_filepaths(f"{breadcrumb}/{isin}", comb_file_paths)
                if isinstance(file_paths, list):
                    comb_file_paths = {"file_paths": [], "paths_n_sizes": []} if not comb_file_paths else comb_file_paths
                    comb_file_paths["file_paths"] = comb_file_paths["file_paths"] + copy.copy(file_paths)
                    comb_file_paths["paths_n_sizes"] = comb_file_paths["paths_n_sizes"] + copy.copy(paths_n_sizes)

            if comb_file_paths:
                return comb_file_paths["file_paths"], comb_file_paths["paths_n_sizes"]
            else:
                return f"No file found in all isin folders for {date_str}", []

        else:

            try:
                file_info_response = self.dbutils.fs.ls(file_path)
                paths_n_sizes = [{"path": file_info.path, "size": file_info.size} for file_info in file_info_response]
                file_paths = [file_info["path"] for file_info in paths_n_sizes]
            except Exception as e:
                file_paths = str(e).split("\n")[1]
                paths_n_sizes = []

        return file_paths, paths_n_sizes
