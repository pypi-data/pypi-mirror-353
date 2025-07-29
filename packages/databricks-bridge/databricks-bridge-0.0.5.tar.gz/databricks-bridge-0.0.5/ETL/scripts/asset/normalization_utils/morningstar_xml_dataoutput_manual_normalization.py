import humps
import json
from ETL.commons.normalize_data import get_dict_key_paths
from ETL.commons.reformat_data import convert_nested_dict_to_nested_list_of_dict


def xml_dict_normalization(dict_data: dict, sort_id: str) -> dict:
    if "test" in sort_id: #for unittesting
        new_dict = {}
        keys_lists = get_dict_key_paths(dict_data, False)
        for keys_list in keys_lists:
            new_key = humps.decamelize("_".join(keys_list))
            new_dict[new_key] = eval("dict_data" + "".join([f"['{el}']" for el in keys_list]))
        return new_dict

    keys_lists = xml_isin_keys() if sort_id == "isin" else xml_msid_keys()
    normalized_dict_data = {}
    for keys_list in keys_lists:
        new_key = humps.decamelize("_".join(keys_list))
        try:
            field_data = eval("dict_data" + "".join([f"['{el}']" for el in keys_list]))
            if isinstance(field_data, (dict, list)):
                json_dict = {new_key: convert_nested_dict_to_nested_list_of_dict(field_data)}
                normalized_dict_data[new_key] = json.dumps(json_dict)
            else:
                normalized_dict_data[new_key] = field_data
        except:
            normalized_dict_data[new_key] = None

    return normalized_dict_data


def generate_spark_schema_str_from_key_paths(key_paths: list):
    str_schema_list = [f"StructField(\"{humps.decamelize('_'.join([key for key in key_path]))}\", StringType())," for key_path in key_paths]
    print("\n".join(str_schema_list))


def status_keys():
    return


def xml_isin_keys() -> list:
    return [
        ['FundShareClass', 'Id'],
        ['FundShareClass', 'FundId'],
        ['FundShareClass', 'Status'],
        ['FundShareClass', 'ClientSpecific'],
        ['FundShareClass', 'Fund', 'Id'],
        ['FundShareClass', 'Fund', 'FundAttributes'],
        ['FundShareClass', 'Fund', 'FundBasics'],
        ['FundShareClass', 'Fund', 'FundFeatures'],
        ['FundShareClass', 'Fund', 'FundNarratives'],
        ['FundShareClass', 'MultilingualVariation'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundAttributes'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'AdministratorList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'AdvisorList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'AdvocateList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'AuditorList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'BankerList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'BrokerList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'CustodianList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'FundCompanyList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'LegalCounselList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'ListingSponsorList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'PlacingAgentList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'ProviderCompany'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'RegisteredOfficeList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'RegistrarList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'SecretaryList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'SubAdvisorList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'TransferAgentList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'TaxAdvisorList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'InvestmentManagerList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundManagementHistory', 'FinancialAdvisorList'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundNarratives', 'InvestmentCriteria', 'BorrowingLimits'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'FundNarratives', 'LanguageId'],
        ['FundShareClass', 'Fund', 'ClosedEndFundOperation', 'Operation'],
        ['FundShareClass', 'Fund', 'DealingSchedule', 'DealingTime', 'CutOffTimeDetail'],
        ['FundShareClass', 'Fund', 'DealingSchedule', 'DealingTime', 'DealingTimeDetail'],
        ['FundShareClass', 'Fund', 'DealingSchedule', 'ValuationTime', 'CountryId'],
        ['FundShareClass', 'Fund', 'DealingSchedule', 'ValuationTime', 'Value'],
        ['FundShareClass', 'Fund', 'ExtendedProperty', 'DealingSchedule'],
        ['FundShareClass', 'Fund', 'MultilingualVariation'],
        ['FundShareClass', 'Fund', 'InternationalFeature'],
        ['FundShareClass', 'Fund', 'CollateralMasterPortfolioId'],
        ['FundShareClass', 'Fund', 'MasterPortfolioId'],
        ['FundShareClass', 'Fund', 'PortfolioList'],
        ['FundShareClass', 'Fund', 'StrategyId'],
        ['FundShareClass', 'InternationalFeature'],
        ['FundShareClass', 'Operation', 'AnnualReport'],
        ['FundShareClass', 'Operation', 'CountryOfSales', 'SalesArea'],
        ['FundShareClass', 'Operation', 'Prospectus', 'Date'],
        ['FundShareClass', 'Operation', 'Prospectus', 'LatestProspectusDate'],
        ['FundShareClass', 'Operation', 'Prospectus', 'ActualFrontLoad'],
        ['FundShareClass', 'Operation', 'Prospectus', 'ActualManagementFee'],
        ['FundShareClass', 'Operation', 'Prospectus', 'AdministrativeFee'],
        ['FundShareClass', 'Operation', 'Prospectus', 'DistributionFee'],
        ['FundShareClass', 'Operation', 'Prospectus', 'CustodianFee'],
        ['FundShareClass', 'Operation', 'Prospectus', 'MaximumCustodianFee'],
        ['FundShareClass', 'Operation', 'Prospectus', 'ManagementFee'],
        ['FundShareClass', 'Operation', 'Prospectus', 'PerformanceFee'],
        ['FundShareClass', 'Operation', 'Prospectus', 'SwitchingFee'],
        ['FundShareClass', 'Operation', 'Prospectus', 'TransactionFee'],
        ['FundShareClass', 'Operation', 'Prospectus', 'SubscriptionFee'],
        ['FundShareClass', 'Operation', 'Prospectus', 'OtherFee'],
        ['FundShareClass', 'Operation', 'Prospectus', 'ExpenseRatio'],
        ['FundShareClass', 'Operation', 'Prospectus', 'FeeNegotiable'],
        ['FundShareClass', 'Operation', 'Prospectus', 'OperatingExpenseRatio'],
        ['FundShareClass', 'Operation', 'Purchase', 'PurchaseDetail'],
        ['FundShareClass', 'Operation', 'Purchase', 'PlatformList'],
        ['FundShareClass', 'Operation', 'ShareClassBasics'],
        ['FundShareClass', 'ProprietaryData', 'AggregatedHoldingCurrency'],
        ['FundShareClass', 'ProprietaryData', 'AggregatedHoldingGeographicZone'],
        ['FundShareClass', 'ProprietaryData', 'Currency'],
        ['FundShareClass', 'ProprietaryData', 'GeographicZone'],
        ['FundShareClass', 'ProprietaryData', 'LatestDocuments'],
        ['FundShareClass', 'ProprietaryData', 'LatestDocuments', 'DocumentType'],
        ['FundShareClass', 'Regulation'],
        ['FundShareClass', 'ShareClassAttributes'],
        ['FundShareClass', 'Strategy', 'Id'],
        ['FundShareClass', 'Strategy', 'InvestmentApproach'],
        ['FundShareClass', 'Strategy', 'Status'],
        ['FundShareClass', 'Strategy', 'StrategyBasics'],
        ['FundShareClass', 'Strategy', 'StrategyAttributes'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature', 'CompanyAttributes'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature', 'ManagedPortfolio'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature', 'GIPSCompliance'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature', 'Disciplinarity'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature', 'TradingPolicy'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature', 'LoadReduction', 'Date'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature', 'LoadReduction', 'ExchangePrivilege'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature', 'LoadReduction', 'ReinstatementPrivilege'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature',
         'LoadReduction', 'LetterOfIntent'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature',
         'LoadReduction', 'RightsOfAccumulation', 'CalculationMethodId'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature',
         'LoadReduction', 'RightsOfAccumulation', 'ROAQualification', 'AccountList'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature',
         'LoadReduction', 'RightsOfAccumulation', 'ROAQualification', 'BalanceAggregation'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature',
         'LoadReduction', 'RightsOfAccumulation', 'ROAQualification', 'OwnerList'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature',
         'LoadReduction', 'RightsOfAccumulation', 'ROAQualification', 'Reduction'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature',
         'LoadReduction', 'RightsOfAccumulation', 'OtherConsideration'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature',
         'RegulatoryRegistration'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature',
         'TradingPolicy', 'ExcessiveTradingPolicy', 'Date'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'AssetManagementFeature',
         'TradingPolicy', 'ExcessiveTradingPolicy', 'PolicyDescription'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'BrandingId'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'CompanyNarratives'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'CompanyOperation',
         'CompanyAttributes'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'CompanyOperation',
         'CompanyBasics'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'CompanyOperation',
         'CompanyIdentifiers'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'CompanyOperation',
         'CompanyOwnership'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'CompanyOperation',
         'KeyPersonnelList'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'CompanyOperation',
         'PersonnelSummary'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'CompanyOperation',
         'BusinessTypeClassification'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'CompanyOperation',
         'TopClientList'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'Headquarter',
         'CountryHeadquarter'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'Id'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'Status'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'IsMultiIdentifiers'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'IsUltimateParent'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ProviderCompany', 'Company', 'LegacyFamilyId'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'PercentFromExternalResearch'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'ContractualLimit'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'MinimumInvestment'],
        ['FundShareClass', 'Strategy', 'StrategyManagement', 'StrategyAvailability'],
        ['FundShareClass', 'TradingInformation', 'ExchangeListing'],
        ['FundShareClass', 'TradingInformation', 'IPO', 'CurrencyId'],
        ['FundShareClass', 'TradingInformation', 'IPO', 'Date'],
        ['FundShareClass', 'TradingInformation', 'IPO', 'Exchange'],
        ['FundShareClass', 'TradingInformation', 'IPO', 'IPOAssetRaised'],
        ['FundShareClass', 'TradingInformation', 'IPO', 'IPOExtraShareIssued'],
        ['FundShareClass', 'TradingInformation', 'IPO', 'IPOManagerShares'],
        ['FundShareClass', 'TradingInformation', 'IPO', 'IPONetAssetsRaised'],
        ['FundShareClass', 'TradingInformation', 'IPO', 'IPOSharePubliclyTraded'],
        ['FundShareClass', 'TradingInformation', 'IPO', 'IPOWarrants'],
        ['FundShareClass', 'TradingInformation', 'IPO', 'NAV'],
        ['FundShareClass', 'TradingInformation', 'IPO', 'OfferPrice'],
        ['FundShareClass', 'TradingInformation', 'LeverageMethod', 'BankCredit'],
        ['FundShareClass', 'TradingInformation', 'LeverageMethod', 'Futures'],
        ['FundShareClass', 'TradingInformation', 'LeverageMethod', 'MarginBorrowing'],
        ['FundShareClass', 'TradingInformation', 'LeverageMethod', 'Option'],
        ['FundShareClass', 'TradingInformation', 'LeverageMethod', 'Swap'],
        ['StatusCode'],
        ['StatusMessage']
    ]


def xml_msid_keys() -> list:
    return xml_isin_keys()[:-2] + [ #[:-2] to avoid ['StatusCode'] and ['StatusMessage'],
        ['Policy', 'Id'],
        ['Policy', 'InternationalFeature'],
        ['Policy', 'PolicyAttributes', 'GroupPolicy'],
        ['Policy', 'PolicyAttributes', 'LimitedAvailability'],
        ['Policy', 'PolicyAttributes', 'NonGroupPolicy'],
        ['Policy', 'PolicyAttributes', 'PartialAnnuitization'],
        ['Policy', 'PolicyAttributes', 'TerminalFunding'],
        ['Policy', 'PolicyBasics', 'Currency', 'Id'],
        ['Policy', 'PolicyBasics', 'Currency', 'Value'],
        ['Policy', 'PolicyBasics', 'Domicile', 'Id'],
        ['Policy', 'PolicyBasics', 'Domicile', 'Value'],
        ['Policy', 'PolicyBasics', 'ISIN'],
        ['Policy', 'PolicyBasics', 'InceptionDate'],
        ['Policy', 'PolicyBasics', 'LegalName'],
        ['Policy', 'PolicyBasics', 'Name'],
        ['Policy', 'PolicyBasics', 'PolicyType', 'Id'],
        ['Policy', 'PolicyBasics', 'PolicyType', 'Value'],
        ['Policy', 'Status'],
        ['Policy', 'TradingInformation', 'ExchangeListing'],
        ['SubAccount', 'ClientSpecific'],
        ['SubAccount', 'Id'],
        ['SubAccount', 'PolicyId'],
        ['SubAccount', 'ProprietaryData', 'AggregatedHoldingCurrency'],
        ['SubAccount', 'ProprietaryData', 'AggregatedHoldingGeographicZone'],
        ['SubAccount', 'ProprietaryData', 'Currency'],
        ['SubAccount', 'ProprietaryData', 'GeographicZone'],
        ['SubAccount', 'ProprietaryData', 'LatestDocuments'],
        ['SubAccount', 'Status'],
        ['SubAccount', 'SubAccountBasics', 'InceptionDate'],
        ['SubAccount', 'SubAccountBasics', 'LegalName'],
        ['SubAccount', 'SubAccountBasics', 'Name'],
        ['StatusCode'],
        ['StatusMessage']
    ]
