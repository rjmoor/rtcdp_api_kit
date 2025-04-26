select distinct
    _citgroup.CustomerAccountFactSummary.BankNumber,
    _citgroup.CustomerAccountFactSummary.CustomerNumber,
    _citgroup.CustomerAccountFactSummary.IngestionTimestamp,
    _citgroup.CustomerAccountFactSummary.WealthSegment,
    _citgroup.CustomerAccountFactSummary.Trust_Customer_Flag
from
    customer_account_fact_schema_v2