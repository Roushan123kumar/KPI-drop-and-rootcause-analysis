import pandas as pd


class RootCauseAnalyzer:

    def __init__(self, df):
        self.df = df.copy()

    # -----------------------------
    # Utility: Compare Two Months
    # -----------------------------
    def _compare_dimension(self, dimension, problem_month):

        months = sorted(self.df["year_month"].unique())
        idx = months.index(problem_month)

        if idx == 0:
            raise ValueError("No previous month available for comparison.")

        previous_month = months[idx - 1]

        current = (
            self.df[self.df["year_month"] == problem_month]
            .groupby(dimension)["sales"]
            .sum()
            .reset_index(name="current_sales")
        )

        previous = (
            self.df[self.df["year_month"] == previous_month]
            .groupby(dimension)["sales"]
            .sum()
            .reset_index(name="previous_sales")
        )

        merged = current.merge(previous, on=dimension, how="left").fillna(0)

        merged["pct_change"] = (
            (merged["current_sales"] - merged["previous_sales"])
            / merged["previous_sales"].replace(0, 1)
        ) * 100

        return merged.sort_values("pct_change")


    # -----------------------------
    # Category Level Analysis
    # -----------------------------
    def analyze_category(self, problem_month):
        return self._compare_dimension("category", problem_month)


    # -----------------------------
    # Sub-Category Drill Down
    # -----------------------------
    def analyze_sub_category(self, problem_month, category):
        filtered = self.df[self.df["category"] == category]
        analyzer = RootCauseAnalyzer(filtered)
        return analyzer._compare_dimension("sub_category", problem_month)


    # -----------------------------
    # Region Drill Down
    # -----------------------------
    def analyze_region(self, problem_month, sub_category=None):

        df_filtered = self.df

        if sub_category:
            df_filtered = df_filtered[df_filtered["sub_category"] == sub_category]

        analyzer = RootCauseAnalyzer(df_filtered)
        return analyzer._compare_dimension("region", problem_month)


    # -----------------------------
    # Segment Drill Down
    # -----------------------------
    def analyze_segment(self, problem_month, region=None):

        df_filtered = self.df

        if region:
            df_filtered = df_filtered[df_filtered["region"] == region]

        analyzer = RootCauseAnalyzer(df_filtered)
        return analyzer._compare_dimension("segment", problem_month)


    # -----------------------------
    # Full Automatic Root Cause
    # -----------------------------
    def full_root_cause(self, problem_month):

        result = {}

        # Level 1: Category
        cat_analysis = self.analyze_category(problem_month)
        worst_category = cat_analysis.iloc[0]["category"]
        result["category"] = worst_category

        # Level 2: Subcategory
        sub_analysis = self.analyze_sub_category(problem_month, worst_category)
        worst_sub = sub_analysis.iloc[0]["sub_category"]
        result["sub_category"] = worst_sub

        # Level 3: Region
        region_analysis = self.analyze_region(problem_month, worst_sub)
        worst_region = region_analysis.iloc[0]["region"]
        result["region"] = worst_region

        # Level 4: Segment
        segment_analysis = self.analyze_segment(problem_month, worst_region)
        worst_segment = segment_analysis.iloc[0]["segment"]
        result["segment"] = worst_segment

        return result
