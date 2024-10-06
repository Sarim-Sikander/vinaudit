import json
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler, PolynomialFeatures, LabelEncoder
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np


class VehiclePriceEstimator:
    def __init__(self, model_path="app/regression_model.json"):
        self.model_path = model_path
        self.scaler = None
        self.poly = None
        self.model = None
        self.label_encoder_make = None
        self.label_encoder_model = None

    def train_model(self, data_file_path):
        df = self._load_and_clean_data(data_file_path)

        X, y = self._prepare_features_and_target(df)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.1, random_state=40
        )

        X_train_transformed = self._fit_preprocessing(X_train)
        self._fit_model(X_train_transformed, y_train)

        self.save_model()

    def _load_and_clean_data(self, data_file_path):
        df = pd.read_csv(data_file_path, delimiter="|", on_bad_lines="skip")
        return df.dropna(
            subset=["listing_mileage", "listing_price", "make", "model", "year"]
        )

    def _prepare_features_and_target(self, df):
        X = df[["listing_mileage", "year", "make", "model"]]
        y = df["listing_price"]

        y = np.log(y + 1)
        X = self._encode_categorical_features(X)

        return X, y

    def _encode_categorical_features(self, X):
        if not self.label_encoder_make:
            self.label_encoder_make = LabelEncoder().fit(X["make"])
            self.label_encoder_model = LabelEncoder().fit(X["model"])

        X["make"] = self.label_encoder_make.transform(X["make"])
        X["model"] = self.label_encoder_model.transform(X["model"])
        return X

    def _fit_preprocessing(self, X_train):
        self.scaler = StandardScaler().fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)

        self.poly = PolynomialFeatures(degree=2).fit(X_train_scaled)
        X_train_poly = self.poly.transform(X_train_scaled)

        return X_train_poly

    def _fit_model(self, X_train, y_train):
        self.model = Ridge(alpha=1.0).fit(X_train, y_train)

    def save_model(self):
        if self.model is None or self.poly is None or self.scaler is None:
            raise ValueError("No model found. Train the model before saving.")

        model_data = {
            "scaler_mean": self.scaler.mean_.tolist(),
            "scaler_scale": self.scaler.scale_.tolist(),
            "label_encoder_make_classes": self.label_encoder_make.classes_.tolist(),
            "label_encoder_model_classes": self.label_encoder_model.classes_.tolist(),
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

            self.label_encoder_make = LabelEncoder()
            self.label_encoder_make.classes_ = np.array(
                model_data["label_encoder_make_classes"]
            )

            self.label_encoder_model = LabelEncoder()
            self.label_encoder_model.classes_ = np.array(
                model_data["label_encoder_model_classes"]
            )

            self.poly = PolynomialFeatures(degree=model_data["poly_degree"])
            self.poly.fit(np.zeros((1, len(self.scaler.mean_))))

            self.model = Ridge(alpha=1.0)
            self.model.coef_ = np.array(model_data["model_coef"])
            self.model.intercept_ = model_data["model_intercept"]

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}. Train and save the model first."
            )

    def predict_price(self, mileage, year, make, model):
        if self.model is None or self.poly is None or self.scaler is None:
            raise ValueError(
                "Model not loaded. Load the model before making predictions."
            )

        X_input = self._prepare_input(mileage, year, make, model)
        input_scaled = self.scaler.transform(X_input)
        input_poly = self.poly.transform(input_scaled)

        log_predicted_price = self.model.predict(input_poly)[0]
        predicted_price = np.exp(log_predicted_price) - 1

        return max(predicted_price, 0)

    def _prepare_input(self, mileage, year, make, model):
        make_encoded = (
            self.label_encoder_make.transform([make])[0]
            if make in self.label_encoder_make.classes_
            else 0
        )
        model_encoded = (
            self.label_encoder_model.transform([model])[0]
            if model in self.label_encoder_model.classes_
            else 0
        )

        input_df = pd.DataFrame(
            [[mileage, year, make_encoded, model_encoded]],
            columns=["listing_mileage", "year", "make", "model"],
        )
        return input_df

    def calculate_adjusted_price(self, base_price, mileage, year, make, model):
        if mileage is None:
            return base_price

        predicted_price = self.predict_price(mileage, year, make, model)
        return predicted_price


if __name__ == "__main__":
    estimator = VehiclePriceEstimator()

    estimator.train_model(
        data_file_path="data/NEWTEST-inventory-listing-2022-08-17.txt"
    )

    estimator.load_model()

    mileage = 50000
    year = 2018
    make = "Toyota"
    model = "Highlander"
    predicted_price = estimator.predict_price(mileage, year, make, model)
    print(f"Predicted price: {predicted_price}")
