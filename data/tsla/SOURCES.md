# TSLA 数据来源与口径（FY2016–FY2025）

- 公司：Tesla, Inc.（CIK 0001318605），NASDAQ，代码 TSLA
- 财年：12 月 31 日结束；FY2025 10-K 于 2026-01-29 提交（accession 0001628280-26-003952）
- 单位：报表原始单位百万美元；`data/tsla/company.json` 统一换算为 US$ bn、保留三位小数（÷1000，无二次四舍五入）

## 字段来源

| 字段 | 取自 | 口径 |
|---|---|---|
| revenue | 合并经营表 "Total revenues" | `Revenues` 年度值 |
| gross_profit | 合并经营表 "Gross profit" | `GrossProfit` |
| operating_income | 合并经营表 "Income (loss) from operations" | `OperatingIncomeLoss` |
| net_income | 合并经营表 "Net income (loss)" | `NetIncomeLoss`，含少数股东损益 |
| assets / liabilities | 合并资产负债表 "Total assets" / "Total liabilities" | 期末值 |
| equity / total_equity | "Total stockholders' equity" | `StockholdersEquity` + `MinorityInterest`；含少数股东权益 |
| cash | "Cash and cash equivalents" | 仅现金及现金等价物 |
| debt | 流动 "Debt and finance leases" + 非流动 "Debt and finance leases" | `DebtCurrent` + `LongTermDebt`（计算值，含融资租赁） |
| ocf | 合并现金流量表 "Net cash provided by operating activities" | 2016–2017 用 `...ContinuingOperations` 科目 |
| capex | "Purchases of property and equipment" | 取绝对值 |
| dividends / buybacks | 无 | FY2016–FY2025 未派息、未回购，记 0 |

## 逐年 10-K

| 财年 | 10-K accession | 提交日 |
|---|---|---|
| FY2016 | 0001564590-17-003118 | 2017-03-01 |
| FY2017 | 0001564590-18-002956 | 2018-02-23 |
| FY2018 | 0001564590-19-003165 | 2019-02-19 |
| FY2019 | 0001564590-20-004475 | 2020-02-13 |
| FY2020 | 0001564590-21-004599 | 2021-02-08 |
| FY2021 | 0000950170-22-000796 | 2022-02-07 |
| FY2022 | 0000950170-23-001409 | 2023-01-31 |
| FY2023 | 0001628280-24-002390 | 2024-01-29 |
| FY2024 | 0001628280-25-003063 | 2025-01-30 |
| FY2025 | 0001628280-26-003952 | 2026-01-29 |

## 核对结果

- 10 个财年 "总资产 = 总负债 + 股东权益 + 可赎回少数股东权益（temporary equity）" 全部相等（百万美元口径，误差 0）。
- FY2025 与 10-K 报表页逐项一致：营收 94,827；毛利 17,094；营业利润 4,355；净利润 3,794；总资产 137,806；总负债 54,941；股东权益 82,807；现金 16,513；债务 8,153；经营现金流 14,747；资本开支 8,527（百万美元）。
- FY2025 分部收入：汽车 69,526、能源 12,771、服务及其他 12,530，合计 94,827（百万美元）。
- FY2024 资本开支：FY2024 10-K 报 11,339 百万美元；FY2025 10-K 的比较数重分类为 11,342 百万美元（差 3 百万美元，0.03%）。本表用最新比较数 11,342，其余科目不受影响。
- 员工数 134,785（FY2025 10-K "Human Capital Resources"）。
- HTML 两次生成字节一致：sha256 CFA97B341106BCAA1B24EA35118702C45764D60E434836101FAFB10AABD86ACB
- 默认打印 4 页：664,141 字节，sha256 F670CAB21D1D73E2B7EAD33B24E7FA842CC68538B08A202DCE2504FEFF968271（含打印时间戳，重打会变）；正文 6,065 字。

## 口径说明

- 权益含少数股东权益；2016–2025 年公司另列可赎回少数股东权益（temporary equity），因此资产 = 负债 + 权益 + temporary equity，而非仅资产 = 负债 + 权益。
- 债务含融资租赁，按资产负债表两个披露行相加。
- 未引入调整数、预测数或第三方估算；未派息、未回购，资本配置表省略。

## 复现

```bash
python bin/manual.py --company tsla --out out
python scripts/print-manual-pdf.py out/manual-tsla.html out/manual-tsla.pdf
```
