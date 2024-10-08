import json
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

class VehiclePriceEstimator:
    def __init__(self, model_path="app/regression_model.json"):
        self.model_path = model_path
        self.model = None

    def train_model(self, data_file_path):
        df = self._load_and_clean_data(data_file_path)

        X, y = self._prepare_features_and_target(df)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.1, random_state=40
        )

        self._fit_model(X_train, y_train)

        self.save_model()

    def _load_and_clean_data(self, data_file_path):
        df = pd.read_csv(data_file_path, delimiter="|", on_bad_lines="skip")
        return df.dropna(subset=["listing_mileage", "listing_price"])

    def _prepare_features_and_target(self, df):
        X = df[["listing_mileage"]]
        y = df["listing_price"]

        return X, y

    def _fit_model(self, X_train, y_train):
        self.model = LinearRegression().fit(X_train, y_train)

    def save_model(self):
        if self.model is None:
            raise ValueError("No model found. Train the model before saving.")

        model_data = {
            "model_coef": self.model.coef_.tolist(),
            "model_intercept": self.model.intercept_,
        }

        with open(self.model_path, "w") as json_file:
            json.dump(model_data, json_file)

    def load_model(self):
        try:
            with open(self.model_path, "r") as json_file:
                model_data = json.load(json_file)

            self.model = LinearRegression()
            self.model.coef_ = np.array(model_data["model_coef"])
            self.model.intercept_ = model_data["model_intercept"]

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}. Train and save the model first."
            )

    def predict_price(self, mileage):
        if self.model is None:
            raise ValueError("Model not loaded. Load the model before making predictions.")

        return self.model.predict(np.array([[mileage]]))[0]
    
    def calculate_adjusted_price(self, base_price, mileage):
        if mileage is None:
            return base_price

        predicted_price = self.predict_price(mileage)
        return predicted_price

# if __name__ == "__main__":
#     estimator = VehiclePriceEstimator()

#     estimator.train_model(
#         data_file_path="data/NEWTEST-inventory-listing-2022-08-17.txt"
#     )

#     estimator.load_model()

#     mileage = 5000
#     predicted_price = estimator.predict_price(mileage)
#     print(f"Predicted price: {predicted_price}")
