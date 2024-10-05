from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import joblib


class VehiclePriceEstimator:
    def __init__(self, model_path="app/regression_model.pkl"):
        self.model_path = model_path
        self.pipeline = None

    def train_model(self, data_file_path):
        df = pd.read_csv(data_file_path, delimiter="|", on_bad_lines="skip")

        df_filtered = df.dropna(
            subset=["listing_mileage", "listing_price", "make", "model", "year"]
        )

        X = df_filtered[["listing_mileage", "year"]]
        y = df_filtered["listing_price"]

        y = np.log(y + 1)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.1, random_state=40
        )

        self.pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("poly", PolynomialFeatures(degree=2)),
                ("model", Ridge(alpha=1.0)),
            ]
        )
        self.pipeline.fit(X_train, y_train)

        self.save_model()

    def save_model(self):
        if self.pipeline is None:
            raise ValueError("No model found. Train the model before saving.")
        joblib.dump(self.pipeline, self.model_path)

    def load_model(self):
        try:
            self.pipeline = joblib.load(self.model_path)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}. Train and save the model first."
            )

    def predict_price(self, mileage, year):
        if self.pipeline is None:
            raise ValueError(
                "Model not loaded. Load the model before making predictions."
            )

        input_df = pd.DataFrame([[mileage, year]], columns=["listing_mileage", "year"])
        log_predicted_price = self.pipeline.predict(input_df)[0]
        predicted_price = np.exp(log_predicted_price) - 1

        return max(predicted_price, 0)

    def calculate_adjusted_price(self, base_price, mileage, year):
        if mileage is None:
            return base_price

        predicted_price = self.predict_price(mileage, year)

        return predicted_price


# if __name__ == "__main__":
#     estimator = VehiclePriceEstimator()

#     estimator.train_model(
#         data_file_path="data/NEWTEST-inventory-listing-2022-08-17.txt"
#     )
#     estimator.load_model()

#     mileage = 50000
#     year = 2018
#     predicted_price = estimator.predict_price(mileage, year)
