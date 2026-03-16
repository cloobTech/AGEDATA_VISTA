import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten
from keras.callbacks import EarlyStopping
from keras.utils import image_dataset_from_directory

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pandas as pd
import numpy as np
from typing import Union, Dict, Any
from schemas.data_processing import NeuralNetworkConfig, OptimizerType, DataType


class NeuralNetworkTrainer:
    def __init__(self, config: NeuralNetworkConfig):
        self.config = config
        self.preprocessor = None

    def build_model(self, input_shape: Union[int, tuple], output_units: int) -> tf.keras.Model:
        """Build model architecture based on data type"""
        model = Sequential()

        if self.config.data_type == DataType.TABULAR:
            # Tabular data architecture
            model.add(Dense(
                units=self.config.hidden_layers[0],
                input_dim=input_shape,
                activation=self.config.activation.value
            ))
            for units in self.config.hidden_layers[1:]:
                model.add(
                    Dense(units=units, activation=self.config.activation.value))
                if self.config.dropout_rate:
                    model.add(Dropout(self.config.dropout_rate))

        elif self.config.data_type == DataType.IMAGE:
            # CNN architecture for images
            model.add(Conv2D(32, (3, 3), activation='relu',
                      input_shape=input_shape))
            model.add(MaxPooling2D((2, 2)))
            model.add(Conv2D(64, (3, 3), activation='relu'))
            model.add(Flatten())
            for units in self.config.hidden_layers:
                model.add(
                    Dense(units=units, activation=self.config.activation.value))

        # Output layer
        output_activation = (
            'softmax' if self.config.task_type == "classification" and output_units > 1
            else 'sigmoid' if self.config.task_type == "classification"
            else 'linear'
        )
        model.add(Dense(units=output_units, activation=output_activation))

        # Compile
        loss = self._get_loss_function(output_units)
        model.compile(
            optimizer=self._get_optimizer(),
            loss=loss,
            metrics=['accuracy'] if self.config.task_type == "classification" else [
                'mae']
        )
        return model

    def _get_loss_function(self, output_units: int) -> str:
        """Determine loss function based on task"""
        if self.config.task_type == "classification":
            return ('sparse_categorical_crossentropy' if output_units > 1
                    else 'binary_crossentropy')
        return 'mse'

    def _get_optimizer(self):
        """Get configured optimizer"""
        optimizers = {
            OptimizerType.ADAM: tf.keras.optimizers.Adam,
            OptimizerType.SGD: tf.keras.optimizers.SGD,
            OptimizerType.RMSprop: tf.keras.optimizers.RMSprop
        }
        return optimizers[self.config.optimizer](learning_rate=self.config.learning_rate)

    def train(self, X: Union[pd.DataFrame, str], y: pd.Series = None) -> Dict[str, Any]:
        """Main training method that handles both data types"""
        if self.config.data_type == DataType.TABULAR:
            return self._train_tabular(X, y)
        elif self.config.data_type == DataType.IMAGE:
            return self._train_image(X)
        else:
            raise ValueError(f"Unsupported data type: {self.config.data_type}")

    def _train_tabular(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Process and train on tabular data"""
        # Preprocessing
        self.preprocessor = StandardScaler()
        X_scaled = self.preprocessor.fit_transform(X)

        if self.config.task_type == "classification" and y.dtype == object:
            le = LabelEncoder()
            y_encoded = le.fit_transform(y)
            class_names = le.classes_.tolist()
        else:
            y_encoded = y
            class_names = None

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, test_size=self.config.test_size, random_state=42
        )

        # Build and train
        model = self.build_model(input_shape=X_train.shape[1],
                                 output_units=len(np.unique(y_encoded)) if self.config.task_type == "classification" else 1)

        history = model.fit(
            X_train, y_train,
            validation_split=self.config.validation_split,
            epochs=self.config.epochs,
            batch_size=self.config.batch_size,
            callbacks=self._get_callbacks(),
            verbose=0
        )

        return self._prepare_results(model, history, X_test, y_test, class_names)

    def _train_image(self, cloudinary_url: str) -> Dict[str, Any]:
        """Process and train on image data from Cloudinary URL"""
        import tempfile
        import os
        import requests
        from urllib.parse import urlparse

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create class directory (required by Keras)
            class_dir = os.path.join(temp_dir, "class_0")
            os.makedirs(class_dir, exist_ok=True)

            # Download image from Cloudinary
            try:
                response = requests.get(cloudinary_url)
                response.raise_for_status()

                filename = os.path.basename(urlparse(cloudinary_url).path)
                if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    filename = "image.jpg"

                filepath = os.path.join(class_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)

            except Exception as e:
                raise ValueError(
                    f"Failed to download image from Cloudinary: {str(e)}")

            if not any(fname.lower().endswith(('.bmp', '.gif', '.jpeg', '.jpg', '.png'))
                       for fname in os.listdir(class_dir)):
                raise ValueError(f"No valid images found in {class_dir}")

            # Create dataset
            try:
                full_ds = image_dataset_from_directory(
                    directory=temp_dir,
                    validation_split=None,
                    seed=123,
                    image_size=self.config.image_size,
                    batch_size=self.config.batch_size,
                    label_mode='int' if self.config.task_type == "classification" else 'float'
                )

                class_names = full_ds.class_names if self.config.task_type == "classification" else None
                output_units = len(class_names) if class_names else 1

                # Shuffle and split manually
                full_ds = full_ds.shuffle(100, seed=123)
                train_size = int(
                    0.8 * tf.data.experimental.cardinality(full_ds).numpy())
                train_gen = full_ds.take(train_size)
                val_gen = full_ds.skip(train_size)

                # Prepare and return training results inside the temp dir context
                return self._prepare_image_training(train_gen, val_gen, class_names, output_units)

            except Exception as e:
                raise ValueError(
                    f"Failed to create image dataset: {str(e)}. Directory contents: {os.listdir(temp_dir)}")

    def _prepare_image_training(self, train_gen, val_gen, class_names, output_units):
        """Common training preparation for image data"""
        model = self.build_model(
            input_shape=self.config.image_size +
            (3,),  # (height, width, channels)
            output_units=output_units
        )

        history = model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=self.config.epochs,
            callbacks=self._get_callbacks(),
            verbose=0
        )

        return {
            "model": model,
            "history": history.history,
            "class_names": class_names,
            "generator": val_gen,
            "preprocessor": None
        }

    def _get_callbacks(self):
        """Configure training callbacks"""
        return [EarlyStopping(monitor='val_loss', patience=5)] if self.config.early_stopping else []

    def _prepare_results(self, model, history, X_test, y_test, class_names):
        """Package training results consistently"""
        results = {
            "model": model,
            "history": history.history,
            "class_names": class_names,
            "preprocessor": self.preprocessor
        }

        if X_test is not None and y_test is not None:
            y_pred = model.predict(X_test)
            if self.config.task_type == "classification":
                # output_shape[-1] == 1 → binary sigmoid; > 1 → multiclass softmax
                is_binary = model.output_shape[-1] == 1
                results.update({
                    "y_pred": (y_pred.flatten() > 0.5).astype(int) if is_binary else np.argmax(y_pred, axis=1),
                    "y_proba": y_pred.flatten() if is_binary else y_pred,
                    "y_test": y_test
                })
            else:
                results.update({
                    "y_pred": y_pred.flatten(),
                    "y_test": y_test
                })

        return results
