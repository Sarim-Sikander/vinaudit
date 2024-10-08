import json
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np

class VehiclePriceEstimator:
    def __init__(self, model_path="app/regression_model.json"):
        self.model_path = model_path
        self.model = None
        self.label_encoder_make = LabelEncoder()
        self.label_encoder_model = LabelEncoder()

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
        return df.dropna(subset=["listing_mileage", "listing_price", "make", "model", "year"])

    def _prepare_features_and_target(self, df):
        X = df[["listing_mileage", "year", "make", "model"]]
        y = df["listing_price"]

        X["make"] = self.label_encoder_make.fit_transform(X["make"])
        X["model"] = self.label_encoder_model.fit_transform(X["model"])

        return X, y

    def _fit_model(self, X_train, y_train):
        self.model = LinearRegression().fit(X_train, y_train)

    def save_model(self):
        if self.model is None:
            raise ValueError("No model found. Train the model before saving.")

        model_data = {
            "model_coef": self.model.coef_.tolist(),
            "model_intercept": self.model.intercept_,
            "label_encoder_make_classes": self.label_encoder_make.classes_.tolist(),
            "label_encoder_model_classes": self.label_encoder_model.classes_.tolist(),
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

            self.label_encoder_make.classes_ = np.array(model_data["label_encoder_make_classes"])
            self.label_encoder_model.classes_ = np.array(model_data["label_encoder_model_classes"])

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}. Train and save the model first."
            )

    def predict_price(self, mileage, year, make, model):
        if self.model is None:
            raise ValueError("Model not loaded. Load the model before making predictions.")

        make_encoded = self.label_encoder_make.transform([make])[0] if make in self.label_encoder_make.classes_ else 0
        model_encoded = self.label_encoder_model.transform([model])[0] if model in self.label_encoder_model.classes_ else 0

        input_data = np.array([[mileage, year, make_encoded, model_encoded]])
        return self.model.predict(input_data)[0]/2

    def calculate_adjusted_price(self, base_price, mileage, year, make, model):
        if mileage is None:
            return base_price

        predicted_price = self.predict_price(mileage, year, make, model)
        return predicted_price

# if __name__ == "__main__":
#     estimator = VehiclePriceEstimator()

#     estimator.train_model(
#         data_file_path="data/NEWTEST-inventory-listing-2022-08-17.txt"
#     )

#     estimator.load_model()

#     mileage = 5000
#     year = 2010
#     make = "Honda"
#     model = "Civic"
#     predicted_price = estimator.predict_price(mileage, year, make, model)
#     print(f"Predicted price: {predicted_price}")