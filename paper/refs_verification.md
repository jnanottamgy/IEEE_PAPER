# Reference verification report (2026-11-23)

Method: web search only. Direct fetches of arxiv.org, dblp.org, openreview.net, proceedings.mlr.press, ojs.aaai.org and crossref were blocked by this session's network policy, so each entry was checked against search-indexed copies of those pages. GitHub repos were checked with `git ls-remote`.

Totals: 51 keys. 45 VERIFIED, 6 CORRECTED, 0 NOT FOUND. All 51 are in refs.bib.

## 2026 / recent
- seer: VERIFIED (arxiv.org/abs/2602.00589; icml.cc/virtual/2026/poster/61675; github.com/decisionintelligence/SEER). 7 authors. Cited as ICML 2026, PMLR 306. The PMLR page range was not found, so the entry has no pages.
- apt: VERIFIED (ojs.aaai.org/index.php/AAAI/article/view/38542). AAAI-26 vol. 40, no. 18, pp. 15180-15188. Added arXiv:2511.12945. The DOI could not be confirmed, so the entry uses the OJS URL instead.
- tamer: VERIFIED, with a caveat (icml.cc/virtual/2026/poster/62481; github.com/NetManAIOps/TameR). The 9-author list and pp. 141265-141295 come from a secondary GitHub issue that quotes the PMLR v306 citation. The PMLR page itself could not be opened.
- tps: VERIFIED, with a caveat (arxiv.org/abs/2604.09067). There are 4 authors. The arXiv PDF and the author's blog give a different title, "Sliding-Window Reordering with Overlap Averaging: A Simple Time-Domain Augmentation for Multivariate Forecasting", and say it is a CIKM 2026 paper. That venue and its DOI could not be confirmed, so the entry is cited as arXiv with the title on the abstract page. Check arXiv and ACM DL before submission.
- revinrole: VERIFIED (arxiv.org/abs/2603.11869). 6 authors (Berthelier et al.).
- tsadam: CORRECTED. The paper is also published in Neurocomputing (2026) (sciencedirect.com/science/article/pii/S0925231226006764). Authors are Yuze Dong and Jinsong Wu. Searches gave conflicting volume, article number and DOI (DOI ...133279 versus vol. 706, art. 135006), so the entry has the journal, the year, the PII URL and the arXiv ID only. Fill in the volume and article number from ScienceDirect.
- xpatch: VERIFIED (ojs.aaai.org/index.php/AAAI/article/view/34270). Full title is "xPatch: Dual-Stream Time Series Forecasting with Exponential Seasonal-Trend Decomposition". AAAI 39(19):20601-20609, DOI 10.1609/aaai.v39i19.34270.
- synthbench: VERIFIED (arxiv.org/abs/2505.20048). Forootani and Khosravi. No venue found, so it is cited as arXiv.
- fan: VERIFIED (neurips.cc/virtual/2024/poster/95063). Ye, Deng, Zou, Gui. NeurIPS 37 (2024). No pages, because the NeurIPS proceedings use none.
- tfps: CORRECTED. Published at NeurIPS 2025, vol. 38 (papers.neurips.cc/paper_files/paper/2025/hash/8491a7fcc218946b471b600a915c8b02-Abstract-Conference.html). 6 authors (Sun et al.). The entry cites the venue version.
- robusttsf: VERIFIED (proceedings.iclr.cc 2024; mlanthology.org/iclr/2024/cheng2024iclr-robusttsf). ICLR 2024. Cheng, Wen, Liu, Sun.
- timemixer: VERIFIED (iclr.cc/virtual/2024/poster/19347). 8 authors.
- itransformer: VERIFIED (iclr.cc/virtual/2024/poster/18933). 7 authors.
- chronos: VERIFIED (openreview.net/forum?id=gerNCVqqtR; TMLR 10/2024). 18 authors, including Hao Wang, who is missing from arXiv v1.
- tslib: CORRECTED. Now published in IEEE TPAMI, vol. 48, no. 10, pp. 11642-11662, 2026, DOI 10.1109/TPAMI.2026.3690845. 7 authors, including Jianmin Wang.
- solid: CORRECTED. Confirmed as KDD '24, pp. 341-352, DOI 10.1145/3637528.3671926. Arxiv v1 had a different title ("...Forecasting Transformers..."). The published title is used.

## Backbones and baselines
- dlinear: VERIFIED (doi.org/10.1609/aaai.v37i9.26317). AAAI 37(9):11121-11128.
- patchtst: VERIFIED (iclr.cc/virtual/2023/poster/10876). Full title "A Time Series is Worth 64 Words: Long-term Forecasting with Transformers".
- revin: VERIFIED (iclr.cc/virtual/2022/poster/6034). 6 authors, in ICLR-listed order.
- informer: VERIFIED (ojs.aaai.org/index.php/AAAI/article/view/17325). AAAI 35(12):11106-11115, DOI 10.1609/aaai.v35i12.17325.
- patchtst_code: VERIFIED (github.com/yuqinie98/PatchTST, repository exists).
- tslib_code: VERIFIED (github.com/thuml/Time-Series-Library, repository exists).
- ettdata: VERIFIED (github.com/zhouhaoyi/ETDataset, repository exists).
- vaswani: VERIFIED (proceedings.neurips.cc/paper/7181). NeurIPS 30. Pages 5998-6008 are the standard DBLP pages; no search result in this session re-confirmed them.
- autoformer: CORRECTED. Full title "Autoformer: Decomposition Transformers with Auto-Correlation for Long-Term Series Forecasting". NeurIPS 34, pp. 22419-22430 (ACM DL).
- fedformer: VERIFIED (proceedings.mlr.press/v162/zhou22g). PMLR 162:27268-27286.
- nstransformer: VERIFIED (neurips.cc/virtual/2022/poster/55235). Full title "...Exploring the Stationarity in Time Series Forecasting". NeurIPS 35. Pages were not confirmed and are omitted.
- dishts: VERIFIED (ojs.aaai.org/index.php/AAAI/article/view/25914). AAAI 37(6):7522-7529, DOI 10.1609/aaai.v37i6.25914.
- timesnet: VERIFIED (iclr.cc/virtual/2023/poster/11976). 6 authors, including Jianmin Wang and Mingsheng Long.

## General deep learning
- vit: VERIFIED (arxiv.org/abs/2010.11929; ICLR 2021). 12 authors.
- batchnorm: VERIFIED (proceedings.mlr.press/v37/ioffe15). PMLR 37:448-456.
- adam: VERIFIED (arxiv.org/abs/1412.6980; the comments field says ICLR 2015, San Diego).
- gelu: VERIFIED (arxiv.org/abs/1606.08415). Arxiv only.
- realformer: CORRECTED. There are 4 authors: He, Ravula, Kanagal, Ainslie. Pages 929-943, DOI 10.18653/v1/2021.findings-acl.81 (aclanthology.org/2021.findings-acl.81).
- hendrycks_corrupt: VERIFIED (iclr.cc/virtual/2019/poster/731).
- senet: VERIFIED (openaccess.thecvf.com, CVPR 2018). pp. 7132-7141, DOI 10.1109/CVPR.2018.00745. Uses the 3-author CVPR version.
- lstm: VERIFIED (DOI 10.1162/neco.1997.9.8.1735). Neural Computation 9(8):1735-1780.
- glu: VERIFIED (proceedings.mlr.press/v70/dauphin17a). PMLR 70:933-941.
- pytorch: VERIFIED (papers.nips.cc/paper/9015). NeurIPS 32. 21 authors; the count and the first and last names were confirmed. Pages 8024-8035 are the standard DBLP pages and were not re-confirmed in this session.
- dropout: VERIFIED (jmlr.org/papers/v15/srivastava14a.html). JMLR 15(56):1929-1958.

## Time-series methods, surveys, statistics
- brits: VERIFIED (papers.nips.cc 2018 hash 734e6bfc...). NeurIPS 31. 6 authors.
- tsaug_survey: VERIFIED (ijcai.org/proceedings/2021/631). pp. 4653-4660, DOI 10.24963/ijcai.2021/631. 7 authors.
- gama_drift: VERIFIED (DOI 10.1145/2523813). ACM CSUR 46(4), Art. 44, 2014.
- datasetshift: VERIFIED (library catalogs, ISBN 9780262170055). Edited by Quiñonero-Candela, Sugiyama, Schwaighofer, Lawrence. MIT Press, 2009. No DOI found, so none is included.
- lim_survey: VERIFIED (royalsocietypublishing.org/doi/10.1098/rsta.2020.0209). Vol. 379, no. 2194, 20200209, 2021.
- deepar: VERIFIED (econpapers RePEc:eee:intfor:v:36:y:2020:i:3:p:1181-1191). IJF 36(3):1181-1191, DOI 10.1016/j.ijforecast.2019.07.001.
- nbeats: VERIFIED (iclr.cc/virtual_2020/poster_r1ecqn4YwB).
- hyndman: VERIFIED (OTexts 2021, 3rd ed., ISBN 9780987507136, otexts.com/fpp3). The place "Melbourne, Australia" comes from the book's imprint and was not shown in the search results.
- kunsch: VERIFIED (projecteuclid.org/euclid.aos/1176347265). Ann. Statist. 17(3):1217-1241, DOI 10.1214/aos/1176347265.
- blazquez_anomaly: VERIFIED (DOI 10.1145/3444690). ACM CSUR 54(3), pp. 1-33, 2021. Article no. 56 was not confirmed and is omitted.
- saits: VERIFIED (DOI 10.1016/j.eswa.2023.119619). ESWA vol. 219, 119619, 2023.
