from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns


def get_data_lineage(table_name, s3_endpoint, etl_path):
    return {
        'target_type': "lakehouse",
        'target_endpoint': table_name,
        'src0_type': "s3",
        'src0_endpoint': s3_endpoint,
        'etl_script_path': etl_path,
        'src1_type': "service",
        'src1_endpoint': "ms-datalake-connector",
        'src1_script_path': "src/main/kotlin/com/ytree/msdatalakeconnector/adapter/driver/kafka/listener/FinancialStatementEventListener.kt",
        'src2_type': "kafka",
        'src2_endpoint': "MS_DATALAKE_CONNECTOR_FINANCIALSTATEMENT_EVENT_TOPIC",
        'src2_script_path': ""
    }


class TablesDynamic(ABC):
    @abstractmethod
    def create_table(self):
        raise NotImplementedError

    @staticmethod
    def get_spark_schema():
        raise NotImplementedError

    @abstractmethod
    def delete_table(self):
        raise NotImplementedError


class HandelsbankenTable(TablesDynamic):

    def __init__(self, db_name):
        self.table_name = f"{db_name}.handelsbanken"
        # self.unappendable_parent_keys = []
        s3_endpoint = "landing/financial_statement/ms-integration/handelsbanken"
        etl_path = "ETL/scripts/ms_integration/all_ms_integration_xml.py"
        self.data_lineage = get_data_lineage(self.table_name, s3_endpoint, etl_path)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    def get_dict_roi(self, dict_data):
        return dict_data["Document"]["BkToCstmrStmt"]

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("grp_hdr_msg_id", StringType()),
            StructField("grp_hdr_cre_dt_tm", TimestampType()),
            StructField("stmt_id", StringType()),
            StructField("stmt_elctrnc_seq_nb", StringType()),
            StructField("stmt_cre_dt_tm", TimestampType()),
            StructField("stmt_acct_id_iban", StringType()),
            StructField("stmt_acct_ccy", StringType()),
            StructField("stmt_acct_ownr_id_org_id_othr_id", StringType()),
            StructField("stmt_acct_ownr_id_org_id_othr_schme_nm_cd", StringType()),
            StructField("stmt_acct_svcr_fin_instn_id_bic", StringType()),
            StructField("stmt_txs_summry_ttl_cdt_ntries_nb_of_ntries", DoubleType()),
            StructField("stmt_txs_summry_ttl_cdt_ntries_sum", DoubleType()),
            StructField("stmt_txs_summry_ttl_dbt_ntries_nb_of_ntries", StringType()),
            StructField("stmt_txs_summry_ttl_dbt_ntries_sum", StringType()),
            StructField("stmt_ntry", StringType()),
            StructField("stmt_ntry_ntry_ref", StringType()),
            StructField("stmt_ntry_amt_ccy", StringType()),
            StructField("stmt_ntry_amt_value", DoubleType()),
            StructField("stmt_ntry_cdt_dbt_ind", StringType()),
            StructField("stmt_ntry_sts", StringType()),
            StructField("stmt_ntry_bookg_dt_dt", DateType()),
            StructField("stmt_ntry_val_dt_dt", DateType()),
            StructField("stmt_ntry_bk_tx_cd_domn_cd", StringType()),
            StructField("stmt_ntry_bk_tx_cd_domn_fmly_cd", StringType()),
            StructField("stmt_ntry_bk_tx_cd_domn_fmly_sub_fmly_cd", StringType()),
            StructField("stmt_ntry_ntry_dtls_tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id",
                        StringType()),
            StructField("stmt_ntry_ntry_dtls_tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_clr_sys_mmb_id_clr_sys_id_cd",
                        StringType()),
            StructField("stmt_ntry_ntry_dtls_tx_dtls_rltd_pties_cdtr_nm", StringType()),
            StructField("stmt_ntry_ntry_dtls_tx_dtls_rltd_pties_dbtr_nm", StringType()),
            StructField("stmt_ntry_ntry_dtls_tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_nm", StringType()),
            StructField("stmt_ntry_ntry_dtls_tx_dtls_addtl_tx_inf", StringType()),
            StructField("stmt_ntry_addtl_ntry_inf", StringType()),
            StructField("stmt_ntry_ntry_dtls_tx_dtls_rmt_inf_ustrd", StringType()),
            StructField("stmt_bal", StringType()),
            StructField("stmt_bal_cdt_dbt_ind", StringType()),
            StructField("stmt_bal_tp_cd_or_prtry_cd", StringType()),
            StructField("stmt_bal_amt_ccy", StringType()),
            StructField("stmt_bal_amt_value", DoubleType()),
            StructField("stmt_bal_dt_dt", DateType()),
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
