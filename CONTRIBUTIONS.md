# Contribution statement — Team 05

**Project:** Crime and House Prices in London Boroughs
**Course:** CISC7204 Data Science and Data Visualization · University of Macau · 2026/27
**Basis:** *Team Work Plan 1* (29 October 2026), Table 1 (roles) and Table 2 (lead products),
cross-checked against the artefacts committed in this repository.

---

## My contribution — WANG Weicheng (MC644348)

**Roles:** Team reporter · Project analyst
**Lead product:** Within-borough year-to-year changes and the change figure
**Second product:** Year-pair rule, rubric checklist, introductory video

### What that meant in practice

| Area | What I owned | Where it lives in this repo |
|---|---|---|
| Within-borough analysis | Built the change sample from the borough-year panel — consecutive year-pairs per borough, 552 pairs across 33 boroughs — and estimated the association with a **cluster bootstrap** (resampling boroughs, not pairs). Ran the City of London sensitivity and the log-change variant. | `src/build_analysis.py` § 6–7 · `analysis.ipynb` § 8–9 |
| The change figure | Designed and produced the scatter of Δ crime rate against Δ price, with the fitted direction and the bootstrap interval. | `figures/fig6_within.png` |
| Year-pair rule | Defined which consecutive observations are admissible (both endpoints must have a complete denominator), which is why the sample is 552 pairs rather than 585 rows. | `src/build_analysis.py` · `analysis.ipynb` § 8 |
| Reproducible pipeline | Assembled the analysis workspace that recomputes **every** statistic and **every** figure from the two source CSVs, and regenerated the notebook from it — so no number in the report depends on a hand-typed value. Re-running `build_analysis.py` reproduces `out/results.md` byte-for-byte. | `src/` · `out/` · `analysis.ipynb` |
| Denominator sweep & robustness | The `residents + k × jobs` sweep (k = 0.0 … 2.0, zero crossing at k ≈ 1.22), earnings partialling, inner/outer stratification, leave-one-borough-out, offence-type decomposition, lead/lag. | `figures/fig3–fig5, fig7–fig8` |
| Reporting | Wrote and delivered the project presentation; ordered the video script and edited the recordings; maintained the rubric checklist. | Team submission (not versioned here) |

### Why the change analysis mattered

The cross-section says ρ = 0.47. The within-borough panel says **0.144** (CI [0.07, 0.22]).
That gap is the project's central argument: most of the apparent "crime raises prices"
pattern is a **between-borough** difference — dense, expensive, job-rich boroughs record more
crime *and* cost more — not something that happens when a borough's crime rate actually moves.
Without the within-borough check, the headline number would have been reported at more than
three times its defensible size.

---

## Full team

### Roles (Work Plan 1, Table 1)

| Role | Member | Duty |
|---|---|---|
| Team coordinator | FAN ZI QIAN | Organises meetings, prepares agendas, keeps the team on schedule |
| Project tracker | FAN ZI QIAN | Schedule, milestones, task board, deadlines, progress |
| Team scribe | WONG SI IEONG | Minutes, decisions, action items, scope changes |
| **Team reporter** | **WANG WEI CHENG** | **Orders the video script, edits the recordings** |
| Team liaison | WONG SI IEONG | Instructor contact; sends only team-approved updates |
| Project developer | LI SI WEI | Builds and maintains the data pipeline and the notebook |
| Project analyst | HE YING | Refines the question against the earnings data, evaluates the rubric |
| Quality reviewer | HE YING | Data quality, calculation correctness, visual clarity |
| **Project analyst** | **WANG WEI CHENG** | **Prepares the year-pair sample, runs the within-borough analysis** |
| Project analyst | LI LU SHI | Robustness rows, source log, checks new rows |
| All members | All six | Finish assigned work on time, report blockers before meetings |

### Lead and second products (Work Plan 1, Table 2)

| Member | Lead product | Second product |
|---|---|---|
| FAN ZI QIAN | Aggregation, baseline correlations, Figure 1 and its fitted line | Coverage note, baseline and closing paragraphs, sample |
| WONG SI IEONG | Assembles the interpretation from each owner's paragraph | Minutes, video recordings, pass on the captions |
| LI SI WEI | Notebook pipeline and one clean-kernel rerun | The empty correlation table in that notebook |
| HE YING | Earnings-adjusted association and the residual figure | Earnings join, missing years, filled rubric |
| **WANG WEI CHENG** | **Within-borough changes and the change figure** | **Year-pair rule, checklist, introductory video** |
| LI LU SHI | Robustness rows: without Westminster, count vs. rate | Reference list, check on new rows, submission file |

---

## Note on this repository

The repository is maintained by WANG Weicheng. It ships one coherent, reproducible pipeline
covering the whole team's analysis rather than six separate scripts, because the project's
argument depends on the *comparison* between the cross-section and the panel — those numbers
have to come from the same code path to be comparable.

Individual contributions above follow the work plan. Where the pipeline in `src/` computes a
statistic that another member owns (for example the earnings adjustment), that reflects the
consolidation, not a reassignment of authorship: the substantive design of each step follows
the owner named in the table.
