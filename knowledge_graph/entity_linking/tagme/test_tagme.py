# -*- coding: utf-8 -*-
import tagme
import wikipedia
# Set the authorization token for subsequent calls.
tagme.GCUBE_TOKEN = "1e1a9d3f-47ab-4df1-a063-45301072978f-843339462"

TEXT = 'The man saw a Jaguar speed on the highway'
TEXT = 'Consumer protection legislation typically labels vehicles as "lemons" if the same problem recurs despite multiple repair attempts.'
# TEXT = 'Democrats not invited to DOJ briefing on FBI informant'
# TEXT = 'Zuckerberg avoided tough questions thanks to short EU testimony format'
TEXT = 'The prey saw the jaguar cross the jungle.'
TEXT = """
Table Name Hong Kong stocks financial indicators HK_FinancialIndex
Description Introduce the basic attributes of Hong Kong stocks financial indicators, data per share, assets and liabilities, profit and loss and cash flow and other related information.
Primary key: ID
Uniqueness constraint: (CompanyCode, EndDate, IfAdjusted, PeriodMark)
Last modified date: 2015-01-15 10:49
      
No. Column name Chinese name Type Empty No Remarks
1 ID ID bigint
2 CompanyCode Company code int
3 InfoPublDate Latest Post Date datetime √
4 InfoSource Source of information varchar(100) √
5 AbstrPublDate Abstract release date datetime √
6 PerformancePublDate Results Announcement Release Datetime √
7 PeriodicReportPublDate Regular report release date datetime √
8 ChangePublDate Correction date datetime √
9 IfAdjusted adjustment flag int √ Note 1
10 EndDate due date datetime √
11 PeriodMark Date Flag int √ Note 2
12 FinancialYear fiscal year datetime √
13 Currency Currency unit int √ Note 3
14 OpinionType Auditor Opinion Type int √ Note 4
15 EPSBasic Basic earnings per share (yuan) decimal(18,8) √
16 EPS Diluted earnings per share (yuan) decimal(18,8) √
17 TotalAssets Total Assets (RMB) money √
18 NoncurrentAssets Non-current assets (yuan) money √
19 CurrentAssets Current Assets (yuan) money √
20 CurrentLiability Current Liabilities (yuan) money √
21 NonurrentLiability Non-current liabilities (yuan) money √
22 TotalLiability Total liabilities (yuan) money √
23 MinorityInterests Minority Interests (yuan) money √
24 TotalShareholderEquity Shareholders' equity / Net asset value (yuan) money √
25 ShareCapital share capital (yuan) money √
26 Reserves Reserve (yuan) money √
27 OperatingIncome Turnover\Banking income (yuan) money √
28 OperatingProfit Operating profit (yuan) money √
29 FinancialExpense Financing Cost / Financial Expenses (yuan) money √
30 AffiliatedComapnyprofit attributable share of associate profit (yuan) money √
31 Cooperate Business Profit Attributable to the profit of the jointly controlled entity (joint venture company) (yuan) money √
32 EarningBeforeTax Profit before tax (yuan) money √
33 TaxExpense Tax (yuan) money √
34 EarningAfterTax Profit after tax (yuan) money √
35 MinorityProfit Minority Shareholders' Profit and Loss (RMB) money √
36 ProfitToShareholders Net profit attributable to shareholders (deductible and profit after minority interest) (yuan) money √
37 GrowthRate is increased or decreased relative to the previous period decimal(18,8) √
38 Dividend Dividend (yuan) money √
39 SpecialItemProfit Non-recurring item income (yuan) money √
40 ProfitExSpecialItem After deducting non-recurring items, profit (yuan) money √
41 NetOperateCashFlow Net cash flow from operating business (yuan) money √
42 NetInvestCashFlow Net cash flow from investing activities (yuan) money √
43 NetFinanceCashFlow Net cash flow from financing activities (yuan) money √
44 NetCashFlow Net Cash Flow (yuan) money √
45 CashEquivalentBeginPer Cash and cash equivalents (yuan) money √
46 EffectOfFERChanges Foreign Currency Exchange Rate Conversion (RMB) money √
47 CashEquivalentEndPer Cash and cash equivalents (yuan) money √
48 XGRQ modification date datetime


"""
text_annotations = tagme.annotate(TEXT)

# Print annotations with a score higher than 0.1
for ann in text_annotations.get_annotations(0.001):
    print(ann)
    print(ann.uri())
    # print(wikipedia.summary(ann.entity_title)[:250] + '...')

# tomatoes_mentions = tagme.mentions(
#     "I definitely like ice cream better than tomatoes.")

# for mention in tomatoes_mentions.mentions:
#     print(mention)
