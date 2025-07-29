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

    @abstractmethod
    def get_spark_schema(self):
        raise NotImplementedError

    @abstractmethod
    def delete_table(self):
        raise NotImplementedError


class LombardOdierTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.file_tag = file_tag
        self.date_format = {"*": "yyyyMMdd"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "posit":
            self.table_tag = "positions"
            self.sep = ";"
            self.date_format = {"c_date_cours": "dd.MM.yyyy", "c_date_echeance_contrat": "dd.MM.yyyy",
                                "c_date_ouverture_contrat": "dd.MM.yyyy", "fc_open_date_account": "dd.MM.yyyy",
                                "fc_date_debut_calc_perf": "dd.MM.yyyy",

                                "fc_date_f": "yyyyMMdd", "v_expiration_date": "yyyyMMdd", "v_first_pay_date": "yyyyMMdd",
                                "v_payment_date": "yyyyMMdd", "fc_date_expiration": "yyyyMMdd",
                                "fc_date_ouverture": "yyyyMMdd"}
        elif file_tag == "trans":
            self.table_tag = "transactions"
            self.sep = "\t"
        elif file_tag == "ytree_pos_d":
            self.table_tag = "ytree_pos_d"
            self.sep = ";"
            self.date_format = {
                "valuation_date": "yyyy-MM-dd", "last_accounting_date": "yyyy-MM-dd", "contract_open_date": "yyyy-MM-dd",
                 "contract_close_date": "yyyy-MM-dd", "instrument_maturity_date": "yyyy-MM-dd", "price_date": "yyyy-MM-dd"}
        elif file_tag == "ytree_tra_d":
            self.table_tag = "ytree_tra_d"
            self.sep = ";"
            self.date_format = {
                "accounting_date": "yyyy-MM-dd", "operation_date": "yyyy-MM-dd", "value_date": "yyyy-MM-dd"}
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.lombard_odier_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/lombard_odier"
        etl_path = "ETL/scripts/ms_integration/all_ms_integration_csv_txt.py"
        self.data_lineage = get_data_lineage(self.table_name, s3_endpoint, etl_path)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    def get_spark_schema(self):
        return non_essentialize_all_other_columns(get_table_schema(self.table_tag))

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


def get_table_schema(table_tag: str) -> StructType:
    spark_schema_dict = {
        "positions": StructType([
            StructField("fc_date_f", DateType()),
            StructField("c_amount_of_the_next_coupon_me", DoubleType()),
            StructField("c_avec_prix_client", StringType()),  # LongType()
            StructField("c_avec_taux_avance_spec", StringType()),  # LongType()
            StructField("cbl_instr_virtuel", StringType()),  # *
            StructField("cbp_dev_total_mepo", DoubleType()),
            StructField("cbp_mar_total_mepo", DoubleType()),
            StructField("cbpnr_dev_mepo", DoubleType()),
            StructField("cbpnr_mar_mepo", DoubleType()),
            StructField("cbpnrmb", DoubleType()),
            StructField("cbpnrmc", DoubleType()),
            StructField("cbpnr_mon_chif_po", DoubleType()),
            StructField("cbpnr_mon_cot_po", DoubleType()),
            StructField("cbpr_dev_mepo", DoubleType()),
            StructField("cbp_res_mb", DoubleType()),
            StructField("cbp_res_mc", DoubleType()),
            StructField("cbpr_mar_mepo", StringType()),  # DoubleType()
            StructField("cbprmb", DoubleType()),
            StructField("cbprmc", DoubleType()),
            StructField("cbpr_mon_chif_po", DoubleType()),
            StructField("cbpr_mon_cot_po", DoubleType()),
            StructField("cbp_tot_mcpo", DoubleType()),
            StructField("cbp_tot_mepo", DoubleType()),
            StructField("c_brut_irr", StringType()),  # DoubleType()
            StructField("c_camb", DoubleType()),
            StructField("c_camc", DoubleType()),
            StructField("cca_mon_chif_po", DoubleType()),
            StructField("cca_mon_cot_po", DoubleType()),
            StructField("c_cd_depot", StringType()),
            StructField("c_dollar_duration", DoubleType()),
            StructField("c_dollar_duration_contrib", DoubleType()),
            StructField("c_cd_rub_val_avance", StringType()),  # *
            StructField("c_desc_reduction_noval", StringType()),  # *
            StructField("c_desc_reduction_pays", StringType()),  # *
            StructField("c_desc_reduction_ultimate", StringType()),  # *
            StructField("cdts", StringType()),  # *
            StructField("cdts_contribution", StringType()),  # *
            StructField("c_code_isin", StringType()),
            StructField("c_code_rubrique", StringType()),
            StructField("c_code_usance", StringType()),
            StructField("c_contr_echeancier", StringType()),  # *
            StructField("c_contrib_duration", DoubleType()),
            StructField("c_contrib_duration_mod", DoubleType()),
            StructField("c_contribution_perf", DoubleType()),
            StructField("c_contribution_perf_mwpo", DoubleType()),
            StructField("c_contribution_perf_weight", DoubleType()),
            StructField("c_convexite", StringType()),  # *
            StructField("c_convexity_comp", DoubleType()),
            StructField("c_convexity_contribution", DoubleType()),
            StructField("c_convexite_rbt_ant", StringType()),  # *
            StructField("fc_cours", DoubleType()),
            StructField("c_crmb", DoubleType()),
            StructField("c_crmc", DoubleType()),
            StructField("ccr_mon_chif_po", DoubleType()),
            StructField("ccr_mon_cot_po", DoubleType()),
            StructField("c_date_apport_echeancier", StringType()),  # *
            StructField("c_date_cours", DateType()),
            StructField("c_date_echeance_contrat", DateType()),
            StructField("c_date_ouverture_contrat", DateType()),
            StructField("c_days_accrued", StringType()),  # DoubleType()
            StructField("cde_change_regl", DoubleType()),
            StructField("c_derive_delta", StringType()),  # DoubleType()
            StructField("c_devise", StringType()),
            StructField("c_devise_contrepartie", StringType()),
            StructField("c_diff_est_mb", DoubleType()),
            StructField("c_diff_poids", DoubleType()),
            StructField("c_diff_poids_pos_cli", DoubleType()),
            StructField("c_dirty_price", DoubleType()),
            StructField("c_dur_anticipe", StringType()),  # DoubleType()
            StructField("c_duration", StringType()),  # *
            StructField("c_duration_comp", DoubleType()),
            StructField("c_duration_mod_comp", DoubleType()),
            StructField("c_duration_modifiee", StringType()),  # *
            StructField("c_duration_mod_rbt_ant", StringType()),  # *
            StructField("c_duration_rbt_ant", StringType()),  # *
            StructField("c_duree_vie_moyenne", StringType()),  # *
            StructField("c_dur_finale", DoubleType()),
            StructField("c_effet_change_mcr", DoubleType()),
            StructField("c_effet_change_mcrpo", DoubleType()),
            StructField("c_effet_chg_mw", DoubleType()),
            StructField("c_emetteur", StringType()),
            StructField("c_ent_ju_client", StringType()),
            StructField("c_est_documente", StringType()),  # DoubleType()
            StructField("fc_estimation_totale", DoubleType()),
            StructField("c_est_pos_deb_mb", DoubleType()),
            StructField("c_expo_actuelle_marche", DoubleType()),
            StructField("c_expo_contractuelle", DoubleType()),
            StructField("c_expo_contractuelle_marche", DoubleType()),
            StructField("c_expo_credit", DoubleType()),
            StructField("c_expo_delta_marche", DoubleType()),
            StructField("c_expo_derive", DoubleType()),
            StructField("c_expo_derive_delta", DoubleType()),
            StructField("c_expo_monetaire", DoubleType()),
            StructField("c_first_notice_date", StringType()),  # *
            StructField("c_fiscal_efficiency", StringType()),
            StructField("c_fiscal_non_efficiency_reason", StringType()),
            StructField("c_fiscalnon_efficiency_reason_txt", StringType()),
            StructField("c_frais", DoubleType()),
            StructField("c_gain_loss_taxable", StringType()),  # *
            StructField("c_handle_actif", StringType()),  # LongType()
            StructField("c_handle_instr", StringType()),  # LongType()
            StructField("c_hst_perf_mbpo", StringType()),  # *
            StructField("c_hst_perf_mcpo", StringType()),  # *
            StructField("cid_rating", StringType()),
            StructField("c_ind_investissement", StringType()),  # DoubleType()
            StructField("c_influence_perf", DoubleType()),
            StructField("c_influence_risque", StringType()),  # DoubleType()
            StructField("c_instr_cat_prod_asps", StringType()),  # DoubleType()
            StructField("c_instr_cat_prod_asps_lib", StringType()),
            StructField("c_instr_clean_price", StringType()),  # *
            StructField("c_instr_clean_ratio", StringType()),  # *
            StructField("c_instr_code_prod_asps", StringType()),  # *
            StructField("c_instr_code_prod_asps_lib", StringType()),
            StructField("c_instr_code_prod_lodh", StringType()),  # DoubleType()
            StructField("c_instr_code_prod_lodh_lib", StringType()),
            StructField("c_instr_conditionnel", StringType()),  # DoubleType()
            StructField("c_instr_in_the_money", StringType()),  # *
            StructField("c_instr_nature", StringType()),
            StructField("c_instr_transparent", StringType()),  # *
            StructField("fc_int_courus", DoubleType()),
            StructField("c_int_courus_deb", DoubleType()),
            StructField("c_int_courus_me", DoubleType()),
            StructField("c_intitule_val_avance", StringType()),  # *
            StructField("c_int_paye_recu", StringType()),  # DoubleType()
            StructField("c_invest_grade", StringType()),
            StructField("fc_libelle", StringType()),
            StructField("c_libelle_estimation", StringType()),
            StructField("c_logical_key_pos", StringType()),
            StructField("c_master_list_level", StringType()),
            StructField("cmcrmb", StringType()),  # LongType()
            StructField("cmcr_mbmc", StringType()),
            StructField("cmcr_mbmc_zero", StringType()),
            StructField("cmcrmb_zero", DoubleType()),
            StructField("cmcrmc", StringType()),  # LongType()
            StructField("cmcrmc_zero", DoubleType()),
            StructField("cmcr_mon_chif_po", StringType()),  # LongType()
            StructField("cmcr_mon_chif_po_zero", DoubleType()),
            StructField("cmcr_mon_cot_po", StringType()),  # DoubleType()
            StructField("cmcr_mon_cot_po_zero", DoubleType()),
            StructField("c_mnt_remb_final", StringType()),  # LongType()
            StructField("c_mode_expr_positions_loc", StringType()),
            StructField("c_nb_contrats", StringType()),  # *
            StructField("c_net_irr", StringType()),  # DoubleType()
            StructField("c_nm_depot", StringType()),
            StructField("c_no_cli_dos_corresp", StringType()),
            StructField("c_no_cli_dos_fcp", StringType()),
            StructField("c_nocli_nodos", StringType()),
            StructField("c_no_contrat", StringType()),
            StructField("c_nom_echeancier", StringType()),  # *
            StructField("c_no_obj", StringType()),
            StructField("fc_no_val", StringType()),
            StructField("c_noval_instr_lie", StringType()),  # *
            StructField("c_no_val_int", StringType()),
            StructField("c_no_val_sous_jacent", StringType()),
            StructField("cpamc", DoubleType()),
            StructField("c_perf_instr", DoubleType()),
            StructField("c_perf_mon_chif", DoubleType()),
            StructField("c_perf_mwmc_non_po", DoubleType()),
            StructField("c_perf_mwmcpo", DoubleType()),
            StructField("c_perf_mw_non_po", DoubleType()),
            StructField("c_per_mon_cot", DoubleType()),
            StructField("c_plus_value", DoubleType()),
            StructField("c_poids_date_deb", DoubleType()),
            StructField("c_poids_pos_cli_date_deb", DoubleType()),
            StructField("c_poids_pos_cli_date_fin", DoubleType()),
            StructField("c_poids_valeur_brute", DoubleType()),
            StructField("c_pos_bloquee", StringType()),  # *
            StructField("c_position_state", StringType()),  # IntegerType()
            StructField("c_pos_with_eur_tax", StringType()),
            StructField("fc_pourcent_p_poste", DoubleType()),
            StructField("cprmbmc", DoubleType()),
            StructField("cprmc", DoubleType()),
            StructField("c_rating", StringType()),
            StructField("c_rating_credit_delta", StringType()),
            StructField("c_rating_fitch", StringType()),
            StructField("c_rating_lodh", StringType()),
            StructField("c_rating_lodhsbi", StringType()),
            StructField("c_rating_sand_p", StringType()),
            StructField("c_rating_sbi", StringType()),
            StructField("c_rdt_anticipe", StringType()),  # *
            StructField("c_rdt_final", StringType()),  # *
            StructField("c_rdt_imm", DoubleType()),
            StructField("c_rdt_moyen", StringType()),  # DoubleType()
            StructField("c_rdt_prix_achat", DoubleType()),
            StructField("c_recommendation", StringType()),  # IntegerType()
            StructField("c_rep_gen", StringType()),
            StructField("c_rep_gen_key", StringType()),
            StructField("c_rep_lpp_key", StringType()),
            StructField("c_rep_lpp_lb", StringType()),
            StructField("c_rep_mon", StringType()),
            StructField("c_rep_mon_key", StringType()),
            StructField("c_rep_mon_libelle", StringType()),
            StructField("c_rep_msci_key", StringType()),
            StructField("c_rep_msci_lb", StringType()),
            StructField("c_rep_native_country", StringType()),
            StructField("c_rep_obl_key", StringType()),
            StructField("fc_barra_rep_pays", StringType()),
            StructField("c_rep_pays_key", StringType()),
            StructField("c_rep_pays_libelle", StringType()),
            StructField("c_rep_pays_ultimate_key", StringType()),
            StructField("c_rep_pays_ultimate_lb_court", StringType()),
            StructField("c_rep_pays_ultimate_libelle", StringType()),
            StructField("c_rep_poche_dim1", StringType()),  # *
            StructField("c_rep_poche_dim2", StringType()),  # *
            StructField("c_rep_poche_dim3", StringType()),  # *
            StructField("c_rep_poche_dim4", StringType()),  # *
            StructField("c_rep_rubrique", StringType()),
            StructField("c_rep_schema_actif_realloc", StringType()),
            StructField("c_rep_schema_asps", StringType()),
            StructField("c_rep_schema_gen", StringType()),
            StructField("c_rep_schema_gen_lb", StringType()),
            StructField("c_rep_schema_geo", StringType()),  # *
            StructField("c_rep_schema_lpp", StringType()),
            StructField("c_rep_schema_lpp_lb", StringType()),
            StructField("c_rep_schema_mon", StringType()),
            StructField("c_rep_schema_msci", StringType()),
            StructField("c_rep_schema_msci_libelle", StringType()),
            StructField("fc_barra_rep_schema_pays", StringType()),
            StructField("c_rep_schema_pocket", StringType()),
            StructField("c_rep_schema_rating", StringType()),
            StructField("c_rep_schema_sec_obl", StringType()),
            StructField("c_rep_schema_type_vehicule", StringType()),
            StructField("c_rep_sec", StringType()),
            StructField("c_rep_sec_ft", StringType()),  # *
            StructField("c_rep_sec_libelle", StringType()),
            StructField("c_rep_sec_msci", StringType()),
            StructField("c_rep_sec_obl", StringType()),
            StructField("c_rep_sec_obl_key", StringType()),
            StructField("c_rep_ultimate_parent_lb", StringType()),
            StructField("c_rev_echeancier", StringType()),  # *
            StructField("c_revenus", StringType()),  # DoubleType()
            StructField("c_risque_credit", StringType()),
            StructField("c_sect_lb_level1", StringType()),
            StructField("c_sect_lb_level2", StringType()),
            StructField("c_sect_lb_level3", StringType()),
            StructField("c_seuil_diversification", StringType()),  # IntegerType()
            StructField("c_simulation_scenario_type", StringType()),  # *
            StructField("fc_solde", DoubleType()),
            StructField("c_solde_actif_virtuel", StringType()),  # IntegerType()
            StructField("c_spread_to_gouv", StringType()),  # *
            StructField("c_spread_to_libor", StringType()),  # *
            StructField("c_src_prix_reconnue", StringType()),  # *
            StructField("c_symb_telekurs", StringType()),
            StructField("c_taux_change_moyen_achat", DoubleType()),
            StructField("c_taux_change_moyen_achat_po", DoubleType()),
            StructField("c_taux_reduction_monetaire", DoubleType()),
            StructField("c_taux_reduction_noval", StringType()),  # IntegerType()
            StructField("c_taux_reduction_pays", StringType()),  # IntegerType()
            StructField("c_taux_reduction_ultimate", StringType()),  # IntegerType()
            StructField("c_taux_val_avance", StringType()),  # IntegerType()
            StructField("c_time_to_next_coupon", StringType()),  # IntegerType()
            StructField("fc_total_pos", DoubleType()),
            StructField("fc_total_pos_chf", DoubleType()),
            StructField("fc_total_pos_mc", DoubleType()),
            StructField("c_tp_instrument", StringType()),  # LongType()
            StructField("c_tp_ope_ctr_devise", StringType()),  # IntegerType()
            StructField("c_type_actif", StringType()),
            StructField("c_type_blocage", StringType()),  # *
            StructField("c_type_court_terme", StringType()),
            StructField("c_type_position", StringType()),
            StructField("c_valeur_avance", DoubleType()),
            StructField("c_valeur_brute", DoubleType()),
            StructField("c_yield_comp", DoubleType()),
            StructField("c_yield_contribution", DoubleType()),
            StructField("v_accrued_interest_ch", DoubleType()),
            StructField("v_accrued_interest_eu", DoubleType()),
            StructField("v_act_interest_rate", DoubleType()),
            StructField("v_call_date", DoubleType()),
            StructField("v_call_price", DoubleType()),
            StructField("v_cours", DoubleType()),
            StructField("v_cours_mb_port", DoubleType()),
            StructField("v_cours_mon_pos", DoubleType()),
            StructField("v_curr_exch_number_mb_port", StringType()),  # IntegerType()
            StructField("v_curr_exch_number_mon_pos", StringType()),  # IntegerType()
            StructField("v_exercice_price", StringType()),  # *
            StructField("v_expiration_date", DateType()),
            StructField("v_first_pay_date", DateType()),
            StructField("v_frequence", StringType()),
            StructField("v_geo_unit_iso", StringType()),
            StructField("v_industry_symbol", StringType()),
            StructField("v_insti_id", StringType()),  # IntegerType()
            StructField("v_insti_id_scheme_id", StringType()),  # IntegerType()
            StructField("v_insti_lo_name", StringType()),
            StructField("v_insti_sh_name", StringType()),
            StructField("v_insti_status", StringType()),
            StructField("v_insti_symbol", StringType()),  # LongType()
            StructField("v_insti_symbol_bcn", StringType()),  # LongType()
            StructField("v_insti_symbol_mic", StringType()),
            StructField("v_insti_type", StringType()),  # LongType()
            StructField("v_instr_lo_name_de", StringType()),
            StructField("v_instr_lo_name_en", StringType()),
            StructField("v_instr_lo_name_fr", StringType()),
            StructField("v_instr_lo_name_it", StringType()),
            StructField("v_instr_lo_name_nl", StringType()),
            StructField("v_instr_subclass", StringType()),  # LongType()
            StructField("v_instrument_factor", StringType()),  # *
            StructField("v_interest_calcul", StringType()),
            StructField("fcv_isin", StringType()),
            StructField("is_performance_twn_pondere", DoubleType()),
            StructField("fc_barra_mon", StringType()),
            StructField("v_issuer_sh_name", StringType()),
            StructField("v_listing_type_id", StringType()),  # IntegerType()
            StructField("v_location_id", StringType()),
            StructField("vloc_instr_nature", StringType()),
            StructField("v_main_trd_place_id", StringType()),  # LongType()
            StructField("v_main_trd_place_mic", StringType()),
            StructField("v_number_of_shares", DoubleType()),
            StructField("v_option_style_type", StringType()),  # *
            StructField("v_payment_date", DateType()),
            StructField("v_rating_scheme_id", StringType()),
            StructField("v_rating_symbol", StringType()),
            StructField("v_redeemable", StringType()),
            StructField("v_ric", StringType()),
            StructField("v_under_instr_no", StringType()),  # *
            StructField("fc_portefeuille_f", StringType()),
            StructField("fc_intitule_portefeuille", StringType()),
            StructField("fc_mon_base_portefeuille", StringType()),
            StructField("fc_estimation_portefeuille", DoubleType()),
            StructField("fc_barra_type", StringType()),
            StructField("fc_payable_currency", StringType()),
            StructField("fc_receivable_currency", StringType()),
            StructField("fc_amount_to_pay_mb", DoubleType()),
            StructField("fc_amount_to_receive_mb", StringType()),  # LongType()
            StructField("fc_amount_to_pay_chf", DoubleType()),
            StructField("fc_amount_to_receive_chf", DoubleType()),
            StructField("fc_amount_to_pay_mc", DoubleType()),
            StructField("fc_amount_to_receive_mc", StringType()),  # DoubleType()
            StructField("fc_date_expiration", DateType()),
            StructField("fc_date_ouverture", DateType()),
            StructField("fccde_change_regl", DoubleType()),
            StructField("fc_code_compte", StringType()),  # *
            StructField("fcug", StringType()),
            StructField("fc_code_gerant1", StringType()),
            StructField("fc_gerant1", StringType()),
            StructField("fc_gerant2", StringType()),
            StructField("fc_mandat", StringType()),  # IntegerType()
            StructField("fc_profil", StringType()),
            StructField("fc_profil_risque", StringType()),
            StructField("fc_libelle_gerant", StringType()),
            StructField("fc_description", StringType()),  # *
            StructField("fc_tracking_error", StringType()),  # *
            StructField("fc_benchmark_id", StringType()),  # *
            StructField("fc_benchmark_libelle", StringType()),  # *
            StructField("fc_info_ratio", StringType()),  # *
            StructField("fc_perf_relative", StringType()),  # *
            StructField("fc_beta", StringType()),  # *
            StructField("fc_open_date_account", DateType()),
            StructField("fc_close_date_account", StringType()),  # *
            StructField("fc_langue_client", StringType()),
            StructField("fc_valeur_avance", DoubleType()),
            StructField("fc_hst_mon_base", StringType()),
            StructField("fc_nature_dossier", StringType()),  # *
            StructField("fc_entite_juridique", StringType()),
            StructField("fc_cd_unite_client", StringType()),
            StructField("fc_cd_profil_uc", StringType()),
            StructField("fc_cd_profil_ug", StringType()),
            StructField("fc_cd_associe_rel", StringType()),  # *
            StructField("fc_balancement", StringType()),
            StructField("fc_code_relation2", StringType()),
            StructField("fc_date_debut_calc_perf", DateType()),
            StructField("fc_lib_dossier", StringType()),  # *
            StructField("fc_libelle_e_services", StringType()),  # *
            StructField("fc_domicile", StringType()),  # IntegerType()
            StructField("fc_nationalite", StringType()),  # IntegerType()
            StructField("fccd_document_us_signe", StringType()),
            StructField("fc_type_portf", StringType()),
            StructField("fc_instr_reference", StringType()),  # *
            StructField("fc_coupon_brut", StringType()),  # IntegerType()
            StructField("fc_has_constraint", StringType()),  # IntegerType()
            StructField("fc_has_es_doc_sign", StringType()),  # IntegerType()
            StructField("fc_cd_associe_level", StringType()),  # *
            StructField("fcmb_homogene", StringType()),  # IntegerType()
            StructField("fc_entite_denormalisee", StringType()),
            StructField("fc_is_pea", StringType()),  # IntegerType()
            StructField("fc_intitule_externe", StringType()),  # *
            StructField("is_performance_mw", DoubleType()),
            StructField("is_risque_d", StringType()),
            StructField("v_instr_ident_symbol", StringType()),  # LongType()
            StructField("v_instr_id_scheme_id", StringType()),
            StructField("v_instr_symbol", StringType()),
            # StructField("", StringType()),
        ]),
        "transactions": StructType([
            StructField("accn_nb", StringType()),
            StructField("accn_cur", StringType()),
            StructField("client_cur", StringType()),
            StructField("accn_type", StringType()),
            StructField("contract_nb", StringType()),  # *
            StructField("countprty_id", StringType()),  # *
            StructField("countprty_desc", StringType()),  # *
            StructField("trans_desc", StringType()),
            StructField("trans_type", StringType()),
            StructField("external_id", StringType()),
            StructField("trans_date", DateType()),
            StructField("value_date", DateType()),
            StructField("trade_date", DateType()),
            StructField("matur_date", DateType()),
            StructField("dbcr_indic", StringType()),
            StructField("revsl_indic", StringType()),  # *
            StructField("amt_accn_cur", DoubleType()),
            StructField("amt_trade_cur", DoubleType()),
            StructField("amt_client_cur", DoubleType()),
            StructField("int_rate", StringType()),  # *
            StructField("exch_rate", StringType()),  # *
            StructField("stock_qty", DoubleType()),
            StructField("price", DoubleType()),
            StructField("trade_cur", StringType()),
            StructField("price_cur", StringType()),
            StructField("oper_code", StringType()),  # IntegerType()
            StructField("isin_code", StringType()),
            StructField("sec_code", StringType()),
            StructField("stock_desc", StringType()),
            StructField("sec_type", StringType()),
            StructField("price_unit", StringType()),
            StructField("appl_code", StringType()),
            StructField("cash_mvt_code", StringType()),  # IntegerType()
            StructField("amt_ref_cur", DoubleType()),
            StructField("ref_cur", StringType()),
            StructField("internal_id", StringType()),
            StructField("perf_date", DateType()),
            StructField("int_trans_id", StringType()),  # *
            StructField("fid_contract", StringType()),  # *
            StructField("mic_code", StringType()),  # *
            StructField("amt_vat", StringType()),  # *
            StructField("portf_id_spec", StringType()),  # *
            StructField("amt_ref_tax", StringType()),  # *
            StructField("stamp_duty", StringType()),  # *
            StructField("accr_int", StringType()),  # *
            StructField("taxes", StringType()),  # *
            StructField("lodh_broker_fees", StringType()),  # *
            StructField("foreign_broker_fees", StringType()),  # *
            StructField("withholding_tax", StringType()),  # *
            StructField("useu_backup_withholding_tax", StringType()),  # *
            StructField("lodh_ticket_fee", StringType()),  # *
            StructField("investment_fond_fees", StringType()),  # *
            StructField("other_fees", DoubleType()),
        ]),
        "ytree_pos_d": StructType([
            StructField("id", StringType()),
            StructField("booking_center", StringType()),
            StructField("valuation_date", DateType()),
            StructField("last_accounting_date", DateType()),
            StructField("portfolio_ref", StringType()),
            StructField("portfolio_currency", StringType()),
            StructField("portfolio_short_name", StringType()),
            StructField("rubrique", StringType()),
            StructField("type", StringType()),
            StructField("currency", StringType()),
            StructField("contract_no", StringType()),
            StructField("contract_open_date", DateType()),
            StructField("contract_close_date", DateType()),
            StructField("interest_rate", StringType()),
            StructField("call_delay", StringType()),
            StructField("instrument_symbol", StringType()),
            StructField("instrument_isin", StringType()),
            StructField("instrument_name", StringType()),
            StructField("instrument_class", StringType()),
            StructField("instrument_type", StringType()),
            StructField("instrument_unit", StringType()),
            StructField("instrument_maturity_date", DateType()),
            StructField("instrument_currency", StringType()),
            StructField("instrument_issuer_name", StringType()),
            StructField("instrument_underlying_instrument_symbol", StringType()),
            StructField("instrument_ric", StringType()),
            StructField("custodian_code", StringType()),
            StructField("custodian_name", StringType()),
            StructField("quantity", StringType()),
            StructField("description", StringType()),
            StructField("valuation_price", DoubleType()),
            StructField("price_date", DateType()),
            StructField("valuation_in_quotation_currency", DoubleType()),
            StructField("accrued_interests_in_quotation_currency", DoubleType()),
            StructField("valuation_in_portfolio_currency", DoubleType()),
            StructField("accrued_interests_in_portfolio_currency", DoubleType()),
            StructField("purchase_cost_in_quotation_currency", DoubleType()),
            StructField("purchase_cost_in_portfolio_currency", DoubleType()),
            StructField("cost_price_in_quotation_currency", DoubleType()),
            StructField("cost_price_in_portfolio_currency", DoubleType()),
            StructField("purchase_price_in_quotation_currency", DoubleType()),
            StructField("market_cost_ratio_in_quotation_currency", DoubleType()),
            StructField("market_cost_ratio_in_portfolio_currency", DoubleType()),
            StructField("number_of_contracts", StringType()),
            StructField("number_of_days_accrued", StringType()),
        ]),
        "ytree_tra_d": StructType([
            StructField("id", StringType()),
            StructField("external_id", StringType()),
            StructField("booking_center", StringType()),
            StructField("accounting_date", DateType()),
            StructField("operation_date", DateType()),
            StructField("value_date", DateType()),
            StructField("source_application", StringType()),
            StructField("reversal_status", StringType()),
            StructField("category", StringType()),
            StructField("nature", StringType()),
            StructField("nature_sub", StringType()),
            StructField("side", StringType()),
            StructField("step", StringType()),
            StructField("direction", StringType()),
            StructField("contract_no", StringType()),
            StructField("interest_rate", StringType()),
            StructField("countervalue_ccy", StringType()),
            StructField("exchange_rate_forward", StringType()),
            StructField("counterparty_name", StringType()),
            StructField("quantity", DoubleType()),
            StructField("price", DoubleType()),
            StructField("instrument_symbol", StringType()),
            StructField("instrument_isin", StringType()),
            StructField("instrument_name", StringType()),
            StructField("instrument_type", StringType()),
            StructField("instrument_unit", StringType()),
            StructField("instrument_maturity_date", StringType()),
            StructField("instrument_currency", StringType()),
            StructField("movement_id", StringType()),
            StructField("movement_origin_code", StringType()),
            StructField("movement_variation_code", StringType()),
            StructField("movement_description", StringType()),
            StructField("movement_quantity", DoubleType()),
            StructField("movement_operation_ccy", StringType()),
            StructField("movement_net_amount_in_operation_ccy", DoubleType()),
            StructField("movement_gross_amount_in_operation_ccy", DoubleType()),
            StructField("movement_net_amount_in_portfolio_ccy", DoubleType()),
            StructField("movement_gross_amount_in_portfolio_ccy", DoubleType()),
            StructField("movement_invoice_ccy", StringType()),
            StructField("movement_net_amount_in_invoice_ccy", DoubleType()),
            StructField("movement_gross_amount_in_invoice_ccy", DoubleType()),
            StructField("movement_purchase_cost_in_position_ccy", DoubleType()),
            StructField("movement_purchase_cost_in_portfolio_ccy", DoubleType()),
            StructField("movement_cost_price_in_position_ccy", DoubleType()),
            StructField("movement_cost_price_in_portfolio_ccy", DoubleType()),
            StructField("portfolio_ref", StringType()),
            StructField("portfolio_currency", StringType()),
            StructField("position_id", StringType()),
            StructField("position_rubrique", StringType()),
            StructField("position_type", StringType()),
            StructField("position_currency", StringType()),
            StructField("position_contract_no", StringType()),
            StructField("position_contract_close_date", StringType()),
            StructField("position_interest_rate", DoubleType()),
            StructField("movement_instrument_symbol", StringType()),
            StructField("movement_instrument_isin", StringType()),
            StructField("movement_instrument_name", StringType()),
            StructField("movement_instrument_type", StringType()),
            StructField("movement_instrument_unit", StringType()),
            StructField("movement_instrument_maturity_date", StringType()),
            StructField("movement_instrument_currency", StringType()),
            StructField("fee_detail_amount_in_portfolio_ccy", DoubleType()),
            StructField("fee_detail_amount_in_operation_ccy", DoubleType()),
            StructField("fee_detail_amount_in_invoice_ccy", DoubleType()),
            StructField("fee_detail_vat_amount_in_portfolio_ccy", StringType()),
            StructField("fee_detail_vat_amount_in_operation_ccy", StringType()),
            StructField("fee_detail_vat_amount_in_invoice_ccy", StringType()),
            StructField("fee_code", StringType()),
            StructField("fee_description", StringType()),
        ]),
    }

    return spark_schema_dict[table_tag]
