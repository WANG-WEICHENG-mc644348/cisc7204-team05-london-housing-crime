
## 1. Borough-year panel

- borough-years kept: **585**
- years: **2001–2018**
- boroughs per year: 2001:33, 2002:33, 2003:33, 2004:33, 2005:33, 2006:33, 2007:33, 2008:33, 2009:33, 2010:32, 2011:32, 2012:32, 2013:32, 2014:32, 2015:32, 2016:32, 2017:32, 2018:32

Why the panel stops at 2018 — crime is populated through 2019, but `population_size` and `number_of_jobs` are blank for 2019:

| year | crime months | population present | jobs present |
|---|---|---|---|
| 2016 | 12 | 33 of 33 | 33 of 33 |
| 2017 | 12 | 33 of 33 | 33 of 33 |
| 2018 | 12 | 33 of 33 | 33 of 33 |
| 2019 | 12 | 0 of 33 | 0 of 33 |

## 2. Cross-section: 2016-2018 borough means

n = **32** boroughs

| pair | Spearman rho | permutation p |
|---|---|---|
| crime rate / residents vs price | **0.470** | 0.0084 |
| crime count vs price | **0.252** | 0.1680 |
| median earnings vs price | **0.512** | 0.0036 |
| crime rate vs median earnings | **0.589** | 0.0004 |
| jobs per resident vs price | **0.655** | 0.0002 |
| jobs per resident vs crime rate | **0.508** | 0.0034 |

Baseline check: rho = **0.470** (the proposal reports 0.47, so the panel reproduces).

## 3. Partialling out earnings

| comparison | rho | 95% bootstrap CI |
|---|---|---|
| crime rate vs price (raw) | **0.470** | [0.065, 0.760] |
| crime rate vs price, earnings partialled out | **0.243** | — |
| crime rate / (residents + jobs) vs price | **0.084** | [-0.301, 0.435] |
| same, earnings partialled out | **0.053** | — |

## 4. Denominator sensitivity: residents + k x jobs

| k | rho |
|---|---|
| 0.0 | 0.469 |
| 0.1 | 0.469 |
| 0.2 | 0.452 |
| 0.3 | 0.434 |
| 0.4 | 0.410 |
| 0.5 | 0.367 |
| 0.6 | 0.315 |
| 0.7 | 0.284 |
| 0.8 | 0.202 |
| 0.9 | 0.125 |
| 1.0 | 0.084 |
| 1.1 | 0.042 |
| 1.2 | 0.006 |
| 1.3 | -0.034 |
| 1.4 | -0.064 |
| 1.5 | -0.112 |
| 1.6 | -0.116 |
| 1.7 | -0.141 |
| 1.8 | -0.159 |
| 1.9 | -0.172 |
| 2.0 | -0.197 |

- zero crossing at **k ≈ 1.22**
- rho at k = 0: 0.469; at k = 1: 0.084; at k = 2: -0.197

## 5. Inner and outer London

- inner London, n = 11: rho = **0.827** (permutation p = 0.0020)
- outer London, n = 21: rho = **-0.294** (permutation p = 0.2012)
- pooled, n = 32: rho = **0.470**

## 6. Within-borough year-to-year changes

- year-pairs: **552** across **33** boroughs
- change in crime rate vs change in price: rho = **0.144**, cluster-bootstrap 95% CI [0.068, 0.220]
- excluding City of London: rho = **0.139** (n = 544 pairs, 32 boroughs)
- log-change version: rho = 0.098

Lead and lag:
- d crime(t) vs d price(t+1): rho = **-0.074** (n = 519)
- d price(t) vs d crime(t+1): rho = **0.223** (n = 519)

## 7. Leave-one-out

- range: **0.417 – 0.546**
- lowest when dropping `camden` (0.417); highest when dropping `richmond upon thames` (0.546)
- dropping Westminster: 0.417

## 8. Offence types (MPS borough file, 2016-2018)

- file rows = 1094; months used = 36 (201601 to 201812)

| offence | n | rho vs price | earnings-partialled | rho vs earnings | rho vs price, jobs-adjusted rate |
|---|---|---|---|---|---|
| Arson And Criminal Damage | 32 | **-0.007** | -0.345 | 0.491 | -0.648 |
| Burglary | 32 | **0.742** | 0.650 | 0.514 | 0.094 |
| Drug Offences | 32 | **0.384** | 0.156 | 0.528 | 0.118 |
| Fraud And Forgery | 32 | (skipped) | | | |
| Miscellaneous Crimes Against Society | 32 | **0.045** | -0.248 | 0.457 | -0.441 |
| Nfib Fraud | 9 | (skipped) | | | |
| Possession Of Weapons | 32 | **0.314** | 0.107 | 0.455 | -0.058 |
| Public Order Offences | 32 | **0.516** | 0.275 | 0.662 | 0.102 |
| Robbery | 32 | **0.364** | 0.201 | 0.404 | 0.158 |
| Sexual Offences | 32 | **0.422** | 0.162 | 0.608 | -0.243 |
| Theft | 32 | **0.638** | 0.458 | 0.692 | 0.563 |
| Vehicle Offences | 32 | **0.310** | 0.260 | 0.175 | -0.179 |
| Violence Against The Person | 32 | **0.262** | 0.031 | 0.466 | -0.429 |

- MPS areas with no match in the panel: london heathrow and london city airports, unknown

## 9. Notes for the write-up

- Crime is populated 2001–2019, but `population_size` and `number_of_jobs` stop at 2018 in the annual file, so the crime **rate** panel is 2001–2018.
- 33 areas carry crime data before 2010 (City of London included); 32 from 2010 on.
- `number_of_jobs` complete for 100% of panel borough-years.
- Westminster has 3.07 jobs per resident; the median borough has 0.46.
- Median earnings missing in a few borough-years (0 of 32 in the cross-section after dropna).