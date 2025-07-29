from ETL.scripts.ms_integration.df_utils.brooks_mcdonald_df_utils import BrooksMcdonaldTable
from ETL.scripts.ms_integration.df_utils.canaccord_df_utils import CanaccordTable
from ETL.scripts.ms_integration.df_utils.cazenove_capital_df_utils import CazenoveCapitalTable
from ETL.scripts.ms_integration.df_utils.charles_stanley_df_utils import CharlesStanleyTable
from ETL.scripts.ms_integration.df_utils.citi_df_utils import CitiTable
from ETL.scripts.ms_integration.df_utils.credo_df_utils import CredoTable
from ETL.scripts.ms_integration.df_utils.hedgeserv_df_utils import HedgeservTable
from ETL.scripts.ms_integration.df_utils.interactive_brokers_df_utils import InteractiveBrokersTable
from ETL.scripts.ms_integration.df_utils.investec_df_utils import InvestecTable
from ETL.scripts.ms_integration.df_utils.jp_morgan_df_utils import JPMorganTable
from ETL.scripts.ms_integration.df_utils.killik_df_utils import KillikTable
from ETL.scripts.ms_integration.df_utils.kleinwort_hambros_df_utils import KleinwortHambrosTable
from ETL.scripts.ms_integration.df_utils.lombard_international_assurance_df_utils import LombardInternationalAssuranceTable
from ETL.scripts.ms_integration.df_utils.morgan_stanley_df_utils import MorganStanleyTable
from ETL.scripts.ms_integration.df_utils.rbc_us_df_utils import RBCUSTable
from ETL.scripts.ms_integration.df_utils.rbc_wealth_df_utils import RBCWealthTable
from ETL.scripts.ms_integration.df_utils.rothschild_df_utils import RothschildTable
from ETL.scripts.ms_integration.df_utils.ruffer_df_utils import RufferTable
from ETL.scripts.ms_integration.df_utils.credit_suisse_df_utils import CreditSuisseTable
from ETL.scripts.ms_integration.df_utils.goldman_sachs_df_utils import GoldmanSachsTable
from ETL.scripts.ms_integration.df_utils.lombard_odier_df_utils import LombardOdierTable
from ETL.scripts.ms_integration.df_utils.ubs_df_utils import UBSTable
from ETL.scripts.ms_integration.df_utils.julius_baer_df_utils import JuliusBaerTable
from ETL.scripts.ms_integration.df_utils.pictet_df_utils import PictetTable

from ETL.scripts.ms_integration.df_utils.aj_bell_df_utils import AJBellTable

from ETL.scripts.ms_integration.df_utils.handelsbanken_df_utils import HandelsbankenTable


db_name = "ms_integration"
data_source = "ms_integration"


def source_data_class_mapper(data_name, file_name):

    if data_name == "brooks_mcdonald":
        return BrooksMcdonaldTable(get_brooks_mcdonald_file_tag(file_name), db_name)
    elif data_name == "canaccord":
        return CanaccordTable(get_canaccord_file_tag(file_name), db_name)
    elif data_name == "cazenove_capital":
        return CazenoveCapitalTable(get_cazenove_capital_file_tag(file_name), db_name)
    elif data_name == "charles_stanley":
        return CharlesStanleyTable(get_charles_stanley_file_tag(file_name), db_name)
    elif data_name in ["citi", "citi_jersey", "citi_singapore"]:
        return CitiTable(get_citi_file_tag(file_name), data_name, db_name)
    elif data_name == "credo":
        return CredoTable(get_credo_file_tag(file_name), db_name)
    elif data_name == "hedgeserv":
        return HedgeservTable(db_name)
    elif data_name == "interactive_brokers":
        return InteractiveBrokersTable(get_interactive_brokers_file_tag(file_name), db_name)
    elif data_name == "investec":
        return InvestecTable(get_investec_file_tag(file_name), db_name)
    elif data_name == "jp_morgan":
        return JPMorganTable(get_jp_morgan_file_tag(file_name), db_name)
    elif data_name == "killik":
        return KillikTable(get_killik_file_tag(file_name), db_name)
    elif data_name == "kleinwort_hambros":
        return KleinwortHambrosTable(get_kleinwort_hambros_file_tag(file_name), db_name)
    elif data_name == "lombard_international_assurance":
        return LombardInternationalAssuranceTable(get_lombard_international_assurance_file_tag(file_name), db_name)
    elif data_name == "morgan_stanley":
        return MorganStanleyTable(get_morgan_stanley_file_tag(file_name), db_name)
    elif data_name == "rbc_us":
        return RBCUSTable(get_rbc_us_file_tag(file_name), db_name)
    elif data_name == "rbc":
        return RBCWealthTable(get_rbc_wealth_file_tag(file_name), db_name)
    elif data_name == "rothschild":
        return RothschildTable(get_rothschild_file_tag(file_name), db_name)
    elif data_name == "ruffer":
        return RufferTable(get_ruffer_file_tag(file_name), db_name)
    elif data_name == "credit_suisse":
        return CreditSuisseTable(get_credit_suisse_file_tag(file_name), db_name)
    elif data_name == "goldman_sachs":
        return GoldmanSachsTable(get_goldman_sachs_file_tag(file_name), db_name)
    elif data_name == "lombard_odier":
        return LombardOdierTable(get_lombard_odier_file_tag(file_name), db_name)
    elif data_name == "ubs":
        return UBSTable(get_ubs_file_tag(file_name), db_name)
    elif data_name == "julius_baer":
        return JuliusBaerTable(get_julius_baer_file_tag(file_name), db_name)
    elif data_name == "pictet":
        return PictetTable(get_pictet_file_tag(file_name), db_name)
    elif data_name == "aj_bell":
        return AJBellTable(get_aj_bell_file_tag(file_name), db_name)
    elif data_name == "handelsbanken":
        return HandelsbankenTable(db_name)

    return None


def get_brooks_mcdonald_file_tag(file_name):
    if "bmam_ytree_tran_" in file_name:
        return "".join([char for char in file_name.split("_")[-2] if not char.isdigit()]).lower()
    else:
        return "".join([char for char in file_name.split("-")[-1].replace(".csv", "") if not char.isdigit()]).lower()


def get_canaccord_file_tag(file_name):
    return "_".join(file_name.split("_")[2:]).replace(".csv", "").lower()


def get_cazenove_capital_file_tag(file_name):
    return file_name.split("_")[1].lower()


def get_charles_stanley_file_tag(file_name):
    return file_name.split("_")[1].lower()


def get_citi_file_tag(file_name):
    file_name_split = file_name.lower().split("_")
    return file_name_split[3] if len(file_name_split) > 3 else file_name_split[2].replace(".csv", "")[2:-7]


def get_credo_file_tag(file_name):
    return file_name.split("-")[-1].replace(".csv", "").lower()


def get_interactive_brokers_file_tag(file_name):
    return file_name.split("_")[1].lower()


def get_investec_file_tag(file_name):
    return file_name.split("-")[1].lower()


def get_jp_morgan_file_tag(file_name):
    return file_name.split("_")[1].lower()


def get_killik_file_tag(file_name):
    return file_name.split("_")[1].lower()


def get_kleinwort_hambros_file_tag(file_name):
    file_tag = file_name.split("_")[-1].replace(".csv", "").lower()
    if file_tag.isnumeric():
        file_tag = file_name.split("_")[-2].lower()
    return file_tag


def get_lombard_international_assurance_file_tag(file_name):
    return file_name.split("_")[3].lower()


def get_morgan_stanley_file_tag(file_name):
    return "".join([char for char in file_name.split("_")[-1].replace(".csv", "") if not char.isdigit()]).lower()


def get_rbc_us_file_tag(file_name):
    return file_name[:2].lower()


def get_rbc_wealth_file_tag(file_name):
    return file_name.split("_")[-2][:3].lower()


def get_rothschild_file_tag(file_name):
    return file_name.split("_")[-1].replace(".csv", "").lower()


def get_ruffer_file_tag(file_name):
    return file_name.split("_")[-1].replace(".csv", "").lower()


def get_credit_suisse_file_tag(file_name):
    return "xml" if file_name.split(".")[-1] == "xml" else file_name.split("_")[2].split(".")[0].replace("Positions", "").lower()


def get_goldman_sachs_file_tag(file_name):
    return file_name.split("_")[2].lower()


def get_lombard_odier_file_tag(file_name):
    return "_".join(file_name.split("_")[1:-1]).lower() if "ytree" in file_name.lower() else file_name.replace("_", "")[5:10].lower()


def get_ubs_file_tag(file_name):
    return file_name.split("_")[1].lower()


def get_julius_baer_file_tag(file_name):
    return file_name.split("_")[1].lower()


def get_pictet_file_tag(file_name):
    return file_name.split("_")[0][2:].lower()


def get_aj_bell_file_tag(file_name):
    return file_name.split("_")[-1].replace(".json", "").lower()
