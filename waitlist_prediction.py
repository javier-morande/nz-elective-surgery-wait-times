# ============================================================
# IMPORTS
# ============================================================

import pandas as pd  # imports pandas for working with dataframes

from sklearn.compose import ColumnTransformer

# Converts categorical text variables into one-hot encoded variables
from sklearn.preprocessing import OneHotEncoder

# Fills missing numerical values such as missing lag values
from sklearn.impute import SimpleImputer

# Imports Random Forest regression model
from sklearn.ensemble import RandomForestRegressor

# Lets us connect preprocessing and the model into one workflow
from sklearn.pipeline import Pipeline

# Imports the function used to calculate Mean Absolute Error
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

#Gradient boosting
from sklearn.ensemble import HistGradientBoostingRegressor

from statsmodels.tsa.holtwinters import ExponentialSmoothing


# ============================================================
# LOAD DATA
# ============================================================

waitlist = pd.read_csv("waitlist_cleaned.csv")

# Shows number of rows and columns
print(waitlist.shape)

# Shows first 5 rows
print(waitlist.head())

# Shows the names of all columns
print(waitlist.columns)

# Shows the data type Python assigned each column
print(waitlist.dtypes)


# ============================================================
# FIX DATES
# ============================================================

# Converts the month column from text into actual dates
waitlist["Month End Date"] = pd.to_datetime(
    waitlist["Month End Date"]
)

# Checks conversion worked
print(waitlist["Month End Date"].dtype)


# ============================================================
# CREATE PANEL DATA
# ============================================================

# Groups data by month, district, specialty and ethnicity
panel = (
    waitlist.groupby(
        [
            "Month End Date",
            "District",
            "Specialty",
            "Ethnicity"
        ],
        as_index=False
    )
    .agg(
        # Total waiting for each group
        Total_waiting=("Total_waiting_numeric", "sum"),

        # Number waiting under 120 days
        Under_120=("Under_120_numeric", "sum")
    )
)

# Shows number of rows and columns in panel
print(panel.shape)

# Shows first 20 rows
print(panel.head(20))


# ============================================================
# CREATE TARGET VARIABLE
# ============================================================

# Calculates how many are waiting over 120 days
panel["Over_120"] = (
    panel["Total_waiting"] -
    panel["Under_120"]
)

# Calculates percentage waiting over 120 days
panel["Percentage_over120"] = (
    panel["Over_120"] /
    panel["Total_waiting"] *
    100
)

# Shows first 10 rows including target
print(
    panel[
        [
            "Month End Date",
            "District",
            "Specialty",
            "Ethnicity",
            "Total_waiting",
            "Under_120",
            "Percentage_over120"
        ]
    ].head(10)
)

# Counts rows where nobody is on the waitlist
print(
    "Rows with Total_waiting = 0:",
    (panel["Total_waiting"] == 0).sum()
)

# Counts missing target values
print(
    "Missing Percentage_over120:",
    panel["Percentage_over120"].isna().sum()
)


# ============================================================
# SORT PANEL DATA
# ============================================================

# Defines columns that identify each waitlist group
group_cols = [
    "District",
    "Specialty",
    "Ethnicity"
]

# Sorts each group into chronological order
panel = panel.sort_values(
    group_cols + ["Month End Date"]
)

# Resets row numbers after sorting
panel = panel.reset_index(drop=True)

# Shows every column instead of hiding some with ...
pd.set_option("display.max_columns", None)

# Shows first 10 rows clearly
print(panel.head(10))


# ============================================================
# CHECK SMALL WAITLIST GROUPS
# ============================================================

print(
    "Total panel rows:",
    len(panel)
)

print(
    "Total <= 2.5:",
    (panel["Total_waiting"] <= 2.5).sum()
)

print(
    "Total < 5:",
    (panel["Total_waiting"] < 5).sum()
)

print(
    "Total < 10:",
    (panel["Total_waiting"] < 10).sum()
)

print(
    "Total < 20:",
    (panel["Total_waiting"] < 20).sum()
)


# ============================================================
# CREATE 1-MONTH LAG
# ============================================================

# Finds the previous available date within each subgroup
panel["Previous_date"] = (
    panel.groupby(group_cols)["Month End Date"]
    .shift(1)
)

# Calculates how many months separate current and previous row
panel["Month_gap"] = (
    (
        panel["Month End Date"].dt.year -
        panel["Previous_date"].dt.year
    ) * 12
    +
    (
        panel["Month End Date"].dt.month -
        panel["Previous_date"].dt.month
    )
)

# Shows how common each month gap is
print(
    panel["Month_gap"]
    .value_counts()
    .sort_index()
)

# Gets previous available percentage within subgroup
panel["lag1_pct"] = (
    panel.groupby(group_cols)["Percentage_over120"]
    .shift(1)
)

# Removes lag value if previous observation was not exactly 1 month earlier
panel.loc[
    panel["Month_gap"] != 1,
    "lag1_pct"
] = pd.NA

# Checks valid and missing lag values
print(
    "Valid 1-month lags:",
    panel["lag1_pct"].notna().sum()
)

print(
    "Missing 1-month lags:",
    panel["lag1_pct"].isna().sum()
)


# ============================================================
# CREATE 3-MONTH LAG
# ============================================================

# Creates copy containing historical percentages
lag3_data = panel[
    [
        "Month End Date",
        "District",
        "Specialty",
        "Ethnicity",
        "Percentage_over120"
    ]
].copy()

# Moves historical dates forward by 3 months
lag3_data["Month End Date"] = (
    lag3_data["Month End Date"] +
    pd.DateOffset(months=3)
)

# Renames historical percentage
lag3_data = lag3_data.rename(
    columns={
        "Percentage_over120": "lag3_pct"
    }
)

# Matches each row with observation exactly 3 months earlier
panel = panel.merge(
    lag3_data,
    on=[
        "Month End Date",
        "District",
        "Specialty",
        "Ethnicity"
    ],
    how="left"
)

print(
    "Valid 3-month lags:",
    panel["lag3_pct"].notna().sum()
)

print(
    "Missing 3-month lags:",
    panel["lag3_pct"].isna().sum()
)


# ============================================================
# CREATE 12-MONTH LAG
# ============================================================

# Creates copy containing historical percentages
lag12_data = panel[
    [
        "Month End Date",
        "District",
        "Specialty",
        "Ethnicity",
        "Percentage_over120"
    ]
].copy()

# Moves each historical date forward by 12 months
lag12_data["Month End Date"] = (
    lag12_data["Month End Date"] +
    pd.DateOffset(months=12)
)

# Renames historical percentage
lag12_data = lag12_data.rename(
    columns={
        "Percentage_over120": "lag12_pct"
    }
)

# Matches each row with observation exactly 12 months earlier
panel = panel.merge(
    lag12_data,
    on=[
        "Month End Date",
        "District",
        "Specialty",
        "Ethnicity"
    ],
    how="left"
)

print(
    "Valid 12-month lags:",
    panel["lag12_pct"].notna().sum()
)

print(
    "Missing 12-month lags:",
    panel["lag12_pct"].isna().sum()
)


# ============================================================
# CREATE CALENDAR VARIABLES
# ============================================================

# Extracts year from the date
panel["Year"] = (
    panel["Month End Date"].dt.year
)

# Extracts month number
# January = 1 through December = 12
panel["Month"] = (
    panel["Month End Date"].dt.month
)

# Checks date and lag predictors
print(
    panel[
        [
            "Month End Date",
            "Year",
            "Month",
            "Percentage_over120",
            "lag1_pct",
            "lag3_pct",
            "lag12_pct"
        ]
    ].head(20)
)


# ============================================================
# TRAIN / VALIDATION / TEST SPLIT
# ============================================================

# Training data:
# model learns from 2015 through 2023
train = panel[
    panel["Month End Date"] <= "2023-12-31"
].copy()

# Validation data:
# used to compare and tune models
validation = panel[
    (
        panel["Month End Date"] >= "2024-01-01"
    )
    &
    (
        panel["Month End Date"] <= "2024-12-31"
    )
].copy()

# Final test data:
# 2025 is kept untouched for final evaluation
test = panel[
    panel["Month End Date"] >= "2025-01-01"
].copy()

# Checks that split worked correctly
print(
    "Training rows:",
    len(train)
)

print(
    "Validation rows:",
    len(validation)
)

print(
    "Testing rows:",
    len(test)
)

print(
    "Training dates:",
    train["Month End Date"].min(),
    "to",
    train["Month End Date"].max()
)

print(
    "Validation dates:",
    validation["Month End Date"].min(),
    "to",
    validation["Month End Date"].max()
)

print(
    "Testing dates:",
    test["Month End Date"].min(),
    "to",
    test["Month End Date"].max()
)


# ============================================================
# MODEL FEATURES
# ============================================================

# Predictor variables given to the models
feature_cols = [
    "District",
    "Specialty",
    "Ethnicity",
    "Year",
    "Month",
    "lag1_pct",
    "lag3_pct",
    "lag12_pct"
]


# ============================================================
# TRAINING DATA
# ============================================================

# X = information the model receives
X_train = train[
    feature_cols
].copy()

# y = correct answer the model learns to predict
y_train = train[
    "Percentage_over120"
].copy()


# ============================================================
# VALIDATION DATA
# ============================================================

# 2024 predictors used to compare models
X_validation = validation[
    feature_cols
].copy()

# Real 2024 results
y_validation = validation[
    "Percentage_over120"
].copy()


# ============================================================
# FINAL TEST DATA
# ============================================================

# 2025 predictors reserved for final evaluation
X_test = test[
    feature_cols
].copy()

# Real 2025 results
y_test = test[
    "Percentage_over120"
].copy()

# Checks dimensions
print(
    "X_train:",
    X_train.shape
)

print(
    "X_validation:",
    X_validation.shape
)

print(
    "X_test:",
    X_test.shape
)


# ============================================================
# PREPROCESSING
# ============================================================

# Text/category predictors
categorical_features = [
    "District",
    "Specialty",
    "Ethnicity"
]

# Numerical predictors
numeric_features = [
    "Year",
    "Month",
    "lag1_pct",
    "lag3_pct",
    "lag12_pct"
]

# Creates preprocessing instructions
preprocessor = ColumnTransformer(
    transformers=[

        # Converts categories into 0/1 columns
        (
            "categories",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            ),
            categorical_features
        ),

        # Replaces missing numeric values with median
        (
            "numbers",
            SimpleImputer(
                strategy="median",
                add_indicator=True
            ),
            numeric_features
        )
    ]
)


# ============================================================
# 2024 BASELINE VALIDATION
# ============================================================

# Keeps only rows with real previous-month value
validation_baseline = (
    validation.dropna(
        subset=["lag1_pct"]
    ).copy()
)

# Baseline prediction:
# current month = previous month
validation_baseline_predictions = (
    validation_baseline["lag1_pct"]
)

# Real 2024 percentages
validation_actual = (
    validation_baseline[
        "Percentage_over120"
    ]
)

# Calculates baseline MAE
validation_baseline_mae = (
    mean_absolute_error(
        validation_actual,
        validation_baseline_predictions
    )
)

print(
    "2024 baseline observations:",
    len(validation_baseline)
)

print(
    "2024 baseline MAE:",
    validation_baseline_mae
)


# ============================================================
# FINAL RANDOM FOREST MODEL
# ============================================================

# Best Random Forest settings found during validation tuning
random_forest = RandomForestRegressor(
    n_estimators=200,
    max_depth=8,
    min_samples_leaf=50,
    random_state=42,
    n_jobs=-1
)

# Connects preprocessing and Random Forest
random_forest_model = Pipeline(
    steps=[
        (
            "preprocessing",
            preprocessor
        ),
        (
            "random_forest",
            random_forest
        )
    ]
)

# Trains using only 2015-2023
random_forest_model.fit(
    X_train,
    y_train
)

# Predicts unseen 2024 validation data
rf_validation_predictions = (
    random_forest_model.predict(
        X_validation
    )
)

# Keeps same rows used by baseline
validation_mask = (
    X_validation[
        "lag1_pct"
    ].notna()
)

# Calculates Random Forest MAE
rf_validation_mae = (
    mean_absolute_error(
        y_validation[
            validation_mask
        ],
        rf_validation_predictions[
            validation_mask
        ]
    )
)

print(
    "Random Forest 2024 validation MAE:",
    rf_validation_mae
)

print(
    "Baseline 2024 validation MAE:",
    validation_baseline_mae
)


# ============================================================
# BASELINE ERROR BY WAITLIST SIZE
# ============================================================

# Different minimum waitlist sizes to investigate
size_limits = [
    0,
    5,
    10,
    20,
    50,
    100
]

for minimum_size in size_limits:

    # Keeps rows with previous-month value
    # and at least specified waitlist size
    size_group = validation[
        (
            validation["lag1_pct"].notna()
        )
        &
        (
            validation["Total_waiting"]
            >= minimum_size
        )
    ].copy()

    # Calculates baseline MAE for this group
    size_mae = mean_absolute_error(
        size_group[
            "Percentage_over120"
        ],
        size_group[
            "lag1_pct"
        ]
    )

    print(
        "Minimum waitlist:",
        minimum_size,
        "- Observations:",
        len(size_group),
        "- Baseline MAE:",
        size_mae
    )


 # ============================================================

    # GRADIENT BOOSTING MODEL

# ============================================================

# creates the gradient boosting regression model
gradient_boosting =HistGradientBoostingRegressor(
random_state=42)

#connects preprocessing and Gradient boosdting into one workflow
gradient_boosting_model=Pipeline(
    steps=[
        ("preprocessing", preprocessor), ##X data → Preprocessing → Gradient Boosting → Prediction
        ("gradient_boosting",gradient_boosting)
    ]

)
# Trains Gradient Boosting using the 2015-2023 training data
gradient_boosting_model.fit(
    X_train,
    y_train
)

#Create model → connect preprocessing → train on 2015–2023 → predict 2024

#uses tje trained gradient boosting model to predict 2024
gb_validation_predictions= gradient_boosting_model.predict(
    X_validation)

# ============================================================
# GRADIENT BOOSTING 2024 VALIDATION
# ============================================================

# Calculates Gradient Boosting MAE using the same 2024 rows as the baseline
gb_validation_mae = mean_absolute_error(
    y_validation[validation_mask],
    gb_validation_predictions[validation_mask]
)

# Shows the Gradient Boosting result
print(
    "Gradient Boosting 2024 validation MAE:",
    gb_validation_mae
)

# Compares all models
print(
    "Random Forest 2024 validation MAE:",
    rf_validation_mae
)

print(
    "Baseline 2024 validation MAE:",
    validation_baseline_mae
)

# ============================================================
# FINAL 2025 BASELINE TEST
# ============================================================

# Keeps only 2025 rows that have a real previous-month value
test_baseline = test.dropna(
    subset=["lag1_pct"]
).copy()

# Baseline prediction:
# predicts that the current month equals the previous month
test_baseline_predictions = test_baseline["lag1_pct"]

# Real 2025 results
test_actual = test_baseline["Percentage_over120"]

# Calculates the final 2025 MAE
test_baseline_mae = mean_absolute_error(
    test_actual,
    test_baseline_predictions
)

# Shows final test results
print(
    "2025 test observations:",
    len(test_baseline)
)

print(
    "Final 2025 baseline MAE:",
    test_baseline_mae
)

# ============================================================
# FINAL 2025 BASELINE RMSE
# ============================================================

# Calculates RMSE
# Squaring the errors makes large prediction mistakes matter more
test_baseline_rmse = root_mean_squared_error(
    test_actual,
    test_baseline_predictions
)

print(
    "Final 2025 baseline RMSE:",
    test_baseline_rmse
)

# ============================================================
# NATIONAL MONTHLY WAITLIST
# ============================================================

# Adds all district/specialty/ethnicity groups together
# for each month to create one national monthly series
national_monthly = (
    panel
    .groupby("Month End Date")
    .agg(
        Total_waiting=("Total_waiting", "sum"),
        Over_120=("Over_120", "sum")
    )
    .reset_index()
)

# Calculates the national percentage waiting over 120 days
national_monthly["Percentage_over120"] = (
    national_monthly["Over_120"]
    / national_monthly["Total_waiting"]
    * 100
)

print(
    national_monthly.tail(12)
)

# ============================================================
# PREPARE NATIONAL FORECAST DATA
# ============================================================

# Sorts the national data into date order
national_monthly = national_monthly.sort_values(
    "Month End Date"
).copy()

# Makes the date the time-series index
national_monthly = national_monthly.set_index(
    "Month End Date"
)

# Forces the data onto a regular monthly month-end frequency
national_monthly = national_monthly.asfreq("ME")

# Check the final months
print(
    national_monthly.tail()
)

# Check whether any months are missing
print(
    "\nMissing months:"
)

print(
    national_monthly.isna().sum()
)

# ============================================================
# NATIONAL FORECAST BACKTEST
# ============================================================

# Uses data up to the end of 2023 for training
national_train = national_monthly.loc[
    :"2023-12-31",
    "Percentage_over120"
]

# Uses 2024 as unseen validation data
national_validation = national_monthly.loc[
    "2024-01-31":"2024-12-31",
    "Percentage_over120"
]

# Builds a trend + seasonal forecasting model
national_model = ExponentialSmoothing(
    national_train,
    trend="add",
    seasonal="add",
    seasonal_periods=12
)

# Trains the model
national_model_fit = national_model.fit()

# Predicts the 12 months of 2024
national_validation_predictions = national_model_fit.forecast(
    len(national_validation)
)

# Measures how far the predictions were from reality
national_validation_mae = mean_absolute_error(
    national_validation,
    national_validation_predictions
)

national_validation_rmse = root_mean_squared_error(
    national_validation,
    national_validation_predictions
)

print(
    "National 2024 MAE:",
    national_validation_mae
)

print(
    "National 2024 RMSE:",
    national_validation_rmse
)