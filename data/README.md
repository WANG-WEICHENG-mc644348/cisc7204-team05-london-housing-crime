# Data

All four files are open data. No personal, confidential or restricted material is included.

| File | Rows | Granularity | Period | Source |
|---|---|---|---|---|
| `housing_in_london_monthly.csv` | 13,549 | area × month | 1995-01 … 2020-01 | Kaggle, *Housing in London* — compiled from London Datastore |
| `housing_in_london_yearly.csv` | 1,071 | area × year | 1999 … 2020 | same |
| `MPS_Borough_Level_Crime_Historical.csv` | 1,094 | borough × offence × month | 2010-04 … 2024-04 | London Datastore, *MPS Borough Level Crime (Historical)* |
| `borough_summary_2016_2018.csv` | 32 | borough | 2016–2018 means | produced by the team; **not used by `src/`** |

## Provenance

**Housing.** The two housing files are the public "Housing in London" extract published on
Kaggle, which itself was assembled from London Datastore series (UK House Price Index,
earnings by borough, jobs and job density, mid-year population estimates, recycling rates,
subjective well-being). They are redistributed here **unmodified** so the analysis can be
re-run without a network connection.

Columns used by the pipeline: `date`, `area`, `average_price`, `borough_flag` (monthly);
`date`, `area`, `median_salary`, `population_size`, `number_of_jobs` (yearly).

**Crime.** The MPS file is the borough-level historical extract from the London Datastore
(`MajorText` / `MinorText` offence labels, `BoroughName`, then one column per `YYYYMM`).
The pipeline uses the 2016–2018 months for the offence-type decomposition and the
borough totals for the cross-validation check.

## Licence

Both upstream publishers release this material under the **UK Open Government Licence**
(OGL v2 for the MPS crime series; OGL v2/v3 for the London Datastore housing series).

> Contains public sector information licensed under the Open Government Licence.

Reuse is permitted, including commercially, with attribution to the Greater London
Authority / Metropolitan Police Service and an OGL statement — which this file provides.

## Caveats

1. **Recorded crime, not crime.** Police recording practice changed over the period
   (notably 2012–13); comparisons across years carry that caveat.
2. **2019 cannot be used for rates.** Crime counts exist for 2019, but
   `population_size` and `number_of_jobs` are blank for all 33 areas, so no denominator
   is available. The rate panel therefore ends at **2018**.
3. **33 → 32 areas.** City of London appears before 2010; from 2010 the panel has 32
   boroughs. Sensitivity to including it is reported (ρ = 0.144 vs. 0.139).
4. **Geography labels are lower-cased** in the pipeline before joining, because the two
   sources differ in capitalisation and spacing.
5. `borough_summary_2016_2018.csv` comes from an earlier team step and covers only three
   years; the pipeline deliberately recomputes from the two full series instead, so that
   the longitudinal analysis is possible at all.
