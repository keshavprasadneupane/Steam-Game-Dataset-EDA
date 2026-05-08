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

**L1-Q1 — Price Tier Volume**
Engineer a `price_category` column using `pd.cut()` with four tiers: Free, Budget ($0.01–$9.99), Mid-Range ($10–$29.99), and Premium ($30+). Which tier has the highest total estimated ownership volume, and which has the best average approval ratio?

> This is not just binning practice — it forces you to think about whether the market rewards accessibility or premium positioning.

*Skills: `pd.cut`, labeled bins, `groupby`, multi-metric summary table*

---

**L1-Q2 — Genre Saturation**
For each genre, calculate two numbers: the count of games published (supply) and the average `owners` per game (demand proxy). Plot supply against demand to identify which genres are oversaturated (many games, few owners each) and which are underserved (few games, high owners each).

> Oversaturation means entering that genre as a developer is a bad bet. Underserved genres with high ownership are the actual market opportunity. This is how real market research works.

*Skills: `groupby` with `count` and `mean`, scatter plot with genre labels, quadrant annotation*

---

**L1-Q3 — True Crowd Favorites**
Build an `approval_ratio` column and filter to games with more than 1,000 total ratings for statistical significance. Among those, find the top 20 games by approval ratio. What do they have in common — genre, price tier, release era, platform?

> With fewer than 1,000 ratings, a 95% approval ratio is meaningless. With 50,000+ ratings, it is a genuine signal. The filter is the whole point of this question.

*Skills: derived column, boolean masking, `nlargest`, cross-referencing multiple columns*

---

### 🔴 Level 2 — Temporal & Revenue Intelligence

The goal here is reasoning across time and building revenue models that account for the limitations of your data.

---

**L2-Q1 — Paid Game Revenue by Category**
Calculate estimated revenue (`price × owners_avg`) only for games where `price > 0`. Group by `categories` and find which categories generate the most total revenue and the best revenue per game. Free-to-play is excluded intentionally — their revenue model is not captured in this dataset.

> Mixing F2P and paid games in a revenue calculation produces a meaningless number. F2P games report $0 price but generate real money through DLC and microtransactions. Excluding them is not a limitation to hide — it is the correct analytical decision to document.

*Skills: boolean filter before aggregation, `groupby` on a multi-value string column, sorting, bar chart*

---

**L2-Q2 — Price Creep Over Time**
Extract the release year from `release_date` and calculate the average game price per year from 2000 to present. Plot the trend. Has the average price of a Steam game increased over time, and did the introduction of Steam Direct in 2017 correlate with any change?

> If average price is rising it could mean premium games are more common, or it could mean the budget/free tier is shrinking as a proportion. The raw average does not distinguish these — so also plot the median alongside the mean.

*Skills: date parsing, year extraction, `groupby` by year, dual-line chart (mean vs. median)*

---

**L2-Q3 — Cult Classic vs. Obscure: Rare Tag Analysis**
Find the 10 rarest `steamspy_tags` by frequency. For each, calculate the median playtime and total owner count. Does rarity correlate with cult status (high median playtime, small audience) or genuine obscurity (low playtime, low owners)?

> A cult classic has a small but deeply engaged audience. An obscure game has a small audience that also does not play it much. These are very different outcomes and require two metrics to distinguish.

*Skills: tag frequency counting, `value_counts`, filtered `groupby`, scatter plot*

---

### 🚀 Level 3 — Cross-Dimensional Analysis

The goal here is combining multiple columns and dimensions simultaneously to answer questions that cannot be answered by looking at one thing at a time.

---

**L3-Q1 — Platform Support and Ownership**
Parse the `platforms` column to create boolean flags for Windows, Mac, and Linux support. Compare average `owners` across four groups: Windows-only, Windows+Mac, Windows+Linux, and all three platforms. Does broader platform support correlate with higher ownership?

> Causality cannot be established here — bigger studios both support more platforms and have larger marketing budgets. But the correlation itself is worth measuring, and documenting that limitation is part of the analysis.

*Skills: string parsing, boolean column engineering, multi-group comparison, bar chart*

---

**L3-Q2 — Maturity Rating and Playtime**
Group games by `required_age` (0, 13, 17, 18+) and compare average and median playtime. Do games with a higher maturity rating retain players longer, or is the relationship flat?

> Mature games often have more complex mechanics and longer stories, which could explain higher playtime. But they also have a smaller addressable audience, which could suppress the owner count. Measuring both lets you see the full picture.

*Skills: `groupby` on a discrete numeric column, dual-metric `agg`, bar chart*

---

**L3-Q3 — Black Swan Detection**
Plot `positive_ratings` on the x-axis against `owners` on the y-axis on a log scale. Games in the top-right quadrant (high ratings, high ownership) are expected successes. The interesting targets are games in the top-left quadrant — high ownership despite low or mediocre rating ratios. Find and name them.

> These are games that sold exceptionally well despite poor reception. Understanding why — early access hype, aggressive marketing, IP recognition — is more analytically interesting than studying straightforward successes.

*Skills: log-scale scatter plot, quadrant filtering using boolean masks, `nlargest` on `owners` within a filtered subset, annotation*