# 🎮 Project 1A: Steam Market Intelligence (EDA)

---

### 📌 Project Strategy

| Category | Details |
| :--- | :--- |
| **Project Name** | Steam Store Exploratory Data Analysis (EDA) |
| **Dataset** | [Nikdavis Steam Store Games](https://www.kaggle.com/datasets/nikdavis/steam-store-games) |
| **Primary Objective** | Engineer a robust Python local environment to answer 5 focused analytical questions using real-world data. |
| **Philosophy** | Shifting from "passive visualization" to "intentional data interrogation." Define the question first, write the code second. |

---

### 🛠️ The Engineering Core

| Module | Technical Value |
| :--- | :--- |
| **Schema Management** | Mastering Pandas `dtypes` to ensure memory efficiency and type-safety. |
| **Aggregation Logic** | Using `groupby()` and `agg()` to synthesize complex multi-dimensional insights. |
| **Vectorized Filtering** | Implementing Boolean Masking for high-performance data selection — no Python loops. |
| **Relational Algebra** | Leveraging `merge()` and joins to handle multi-table relational logic within Python. |
| **Data Integrity** | Applying `fillna()`, `dropna()`, and type coercion patterns to resolve real-world data decay. |
| **Binning & Segmentation** | Using `pd.cut()` and `pd.qcut()` to engineer categorical features from continuous columns. |
| **Statistical Viz** | Using Matplotlib/Seaborn to surface distributions, outliers, and correlations — every chart answers a question. |
| **Vectorization** | Using NumPy to perform mathematical operations across entire columns without iteration. |

---

### 🚫 Constraints for Mastery

| Rule | Reasoning |
| :--- | :--- |
| **No Jupyter Notebooks** | Notebooks encourage fragmented, non-linear thinking. Use `.py` scripts organized into functions. |
| **No Kaggle Forking** | You cannot build intuition by reading someone else's solution. Type every line. Own every bug. |
| **No Aimless Graphing** | Every chart must answer one of your five questions. Plots without a question are just noise. |
| **No Advanced Modeling Yet** | Do not reach for ML until `groupby`, boolean masking, and `merge` feel like reflexes. |

---

### 📋 The Five Core Questions

Define what you want to find out before touching the data. Each question below targets a specific skill and produces one clear, readable output.

---

**Q1 — Genre Engagement**
Which genres have the highest average playtime, and how far does the median fall from the mean within those genres?

> The gap between mean and median tells you whether a genre genuinely retains most players or whether a small number of extreme players are inflating the average. A large gap means the "average" is misleading.

*Primary skills: `groupby`, `agg` with multiple functions, sorting, bar chart*

---

**Q2 — Price vs. Sentiment**
What is the approval ratio (`positive / total ratings`) across price tiers — and does a higher price actually produce better sentiment when you filter out games with fewer than 500 total ratings?

> Without the rating count filter, one five-star game with 12 reviews skews an entire tier. The filter forces the question to be about games with a real audience, not statistical noise.

*Primary skills: derived column creation, `pd.cut` for price binning, boolean masking, grouped bar chart*

---

**Q3 — Platinum Tier Over Time**
How many Platinum Tier games (approval ratio above 90%) were released each year compared to total releases, and has that ratio improved or declined since Steam Direct launched in 2017?

> Steam Direct replaced Steam Greenlight and made publishing significantly easier. If quality dilution is real, the Platinum Tier ratio should drop post-2017 despite total releases climbing.

*Primary skills: date parsing, year extraction, conditional column creation, dual-series line chart*

---

**Q4 — Achievement Design: F2P vs. Paid**
Do Free-to-Play games have more achievements on average than paid games, and does that difference hold across all platforms or only on Windows?

> F2P games are incentivized to use achievements as a retention and engagement mechanic rather than a reward for genuine progression. More achievements in F2P games would support that pattern.

*Primary skills: boolean masking, multi-column `groupby`, `crosstab`, grouped comparison chart*

---

**Q5 — Developer Revenue Efficiency**
Who are the top 10 developers by estimated gross revenue (`price × owners_avg`), and how does their approval ratio compare to the platform average?

> High revenue with a below-average approval ratio flags a developer who sells well on marketing but underdelivers on product. High revenue with a strong ratio is the actual target benchmark.

*Primary skills: vectorized column math, `groupby` + `agg`, `merge`, horizontal bar chart with dual metric*

---

## 📈 Level-Up Challenges

Once the five core questions are answered cleanly, the following challenges move you from basic aggregation toward feature engineering, temporal reasoning, and market-level thinking. Do them in order — each one builds on the previous.

---

### 🟡 Level 1 — Feature Engineering & Segmentation

The goal here is learning to create new analytical columns from raw data, then using those engineered features to answer questions the raw schema cannot answer directly.

---
**Genre Saturation**
For each genre, calculate two numbers: the count of games published (supply) and the average `owners` per game (demand proxy). Plot supply against demand to identify which genres are oversaturated (many games, few owners each) and which are underserved (few games, high owners each).

> Oversaturation means entering that genre as a developer is a bad bet. Underserved genres with high ownership are the actual market opportunity. This is how real market research works.

*Skills: `groupby` with `count` and `mean`, scatter plot with genre labels, quadrant annotation*

---

### 🔴 Level 2 — Temporal & Revenue Intelligence

The goal here is reasoning across time and building revenue models that account for the limitations of your data.

---

**Price Creep Over Time**
Extract the release year from `release_date` and calculate the average game price per year from 2000 to present. Plot the trend. Has the average price of a Steam game increased over time, and did the introduction of Steam Direct in 2017 correlate with any change?

> If average price is rising it could mean premium games are more common, or it could mean the budget/free tier is shrinking as a proportion. The raw average does not distinguish these — so also plot the median alongside the mean.

*Skills: date parsing, year extraction, `groupby` by year, dual-line chart (mean vs. median)*

---

### 🚀 Level 3 — Cross-Dimensional Analysis

The goal here is combining multiple columns and dimensions simultaneously to answer questions that cannot be answered by looking at one thing at a time.

---
**Black Swan Detection**
Plot `positive_ratings` on the x-axis against `owners` on the y-axis on a log scale. Games in the top-right quadrant (high ratings, high ownership) are expected successes. The interesting targets are games in the top-left quadrant — high ownership despite low or mediocre rating ratios. Find and name them.

> These are games that sold exceptionally well despite poor reception. Understanding why — early access hype, aggressive marketing, IP recognition — is more analytically interesting than studying straightforward successes.

*Skills: log-scale scatter plot, quadrant filtering using boolean masks, `nlargest` on `owners` within a filtered subset, annotation*