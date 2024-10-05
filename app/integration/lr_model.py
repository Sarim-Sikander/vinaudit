import json
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np


class VehiclePriceEstimator:
    def __init__(self, model_path="app/regression_model.json"):
        self.model_path = model_path
        self.scaler = None
        self.poly = None
        self.model = None

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

        self.scaler = StandardScaler().fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)

        self.poly = PolynomialFeatures(degree=2).fit(X_train_scaled)
        X_train_poly = self.poly.transform(X_train_scaled)

        self.model = Ridge(alpha=1.0).fit(X_train_poly, y_train)

        self.save_model()

    def save_model(self):
        if self.scaler is None or self.poly is None or self.model is None:
            raise ValueError("No model found. Train the model before saving.")

        model_data = {
            "scaler_mean": self.scaler.mean_.tolist(),
            "scaler_scale": self.scaler.scale_.tolist(),
            "poly_degree": self.poly.degree,
            "model_coef": self.model.coef_.tolist(),
            "model_intercept": self.model.intercept_,
        }

        with open(self.model_path, "w") as json_file:
            json.dump(model_data, json_file)

    def load_model(self):
        try:
            with open(self.model_path, "r") as json_file:
                model_data = json.load(json_file)

            self.scaler = StandardScaler()
            self.scaler.mean_ = np.array(model_data["scaler_mean"])
            self.scaler.scale_ = np.array(model_data["scaler_scale"])

            self.poly = PolynomialFeatures(degree=model_data["poly_degree"])
            self.poly.fit(np.zeros((1, len(self.scaler.mean_))))

            self.model = Ridge(alpha=1.0)
            self.model.coef_ = np.array(model_data["model_coef"])
            self.model.intercept_ = model_data["model_intercept"]

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}. Train and save the model first."
            )

    def predict_price(self, mileage, year):
        if self.scaler is None or self.poly is None or self.model is None:
            raise ValueError(
                "Model not loaded. Load the model before making predictions."
            )

        input_df = pd.DataFrame([[mileage, year]], columns=["listing_mileage", "year"])
        input_scaled = self.scaler.transform(input_df)

        input_poly = self.poly.transform(input_scaled)

        log_predicted_price = self.model.predict(input_poly)[0]
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
#     print(f"Predicted price: {predicted_price}")
