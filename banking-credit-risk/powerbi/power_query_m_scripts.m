// 1. Fact_Credit_Clients
let
    Source = Csv.Document(File.Contents("data/processed/powerbi_credit_risk_dataset.csv"),[Delimiter=",", Columns=54, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"ID", Int64.Type}, {"LIMIT_BAL", type number}, {"SEX", Int64.Type}, {"EDUCATION", Int64.Type}, {"MARRIAGE", Int64.Type},
        {"AGE", Int64.Type}, {"PAY_0", Int64.Type}, {"DEFAULT", Int64.Type}, {"AVG_UTIL", type number}, {"OVER_LIMIT_FLAG", Int64.Type},
        {"AVG_BILL_AMT", type number}, {"AVG_PAY_AMT", type number}, {"PAY_TO_BILL_1", type number}, {"TOTAL_PAY_TO_BILL", type number},
        {"RECENT_DELAY", Int64.Type}, {"CONSEC_DELAY", Int64.Type}, {"DELAY_MONTHS_COUNT", Int64.Type}, {"SPLIT", type text},
        {"EDUCATION_LABEL", type text}, {"MARRIAGE_LABEL", type text}, {"SEX_LABEL", type text}, {"AGE_GROUP", type text},
        {"LIMIT_BAL_TIER", type text}, {"PAY_0_LABEL", type text}, {"AVG_UTIL_TIER", type text}, {"CHAMPION_PRED_PROB", type number},
        {"FLAGGED_AT_0_56", Int64.Type}
    })
in
    #"Changed Type"
