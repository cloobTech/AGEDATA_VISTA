import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

import pandas as pd
import numpy as np
from schemas.data_processing import NeuralNetworkConfig, OptimizerType

def build_neural_network(
    input_shape: int,
    output_units: int,
    config: NeuralNetworkConfig,
    task_type: str
) -> tf.keras.Model:
    """Build and compile neural network model"""
    model = Sequential()
    
    # Input layer
    model.add(Dense(
        units=config.hidden_layers[0],
        input_dim=input_shape,
        activation=config.activation.value
    ))
    
    # Hidden layers
    for units in config.hidden_layers[1:]:
        model.add(Dense(units=units, activation=config.activation.value))
        if config.dropout_rate:
            model.add(Dropout(config.dropout_rate))
    
    # Output layer
    output_activation = (
        'softmax' if task_type == "classification" and output_units > 1 
        else 'sigmoid' if task_type == "classification" 
        else 'linear'
    )
    model.add(Dense(units=output_units, activation=output_activation))
    
    # Compile model
    loss = (
        'sparse_categorical_crossentropy' if task_type == "classification" and output_units > 1
        else 'binary_crossentropy' if task_type == "classification"
        else 'mse'
    )
    
    optimizer_map = {
        OptimizerType.ADAM: tf.keras.optimizers.Adam(learning_rate=config.learning_rate),
        OptimizerType.SGD: tf.keras.optimizers.SGD(learning_rate=config.learning_rate),
        OptimizerType.RMSprop: tf.keras.optimizers.RMSprop(learning_rate=config.learning_rate)
    }
    
    model.compile(
        optimizer=optimizer_map[config.optimizer],
        loss=loss,
        metrics=['accuracy'] if task_type == "classification" else ['mae']
    )
    
    return model

def train_neural_network(
    X: pd.DataFrame,
    y: pd.Series,
    config: NeuralNetworkConfig,
    test_size: float,
    task_type: str
) -> dict:
    """Train and evaluate neural network"""
    # Preprocessing
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    if task_type == "classification" and y.dtype == object:
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        class_names = le.classes_.tolist()
    else:
        y_encoded = y
        class_names = None
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded, test_size=test_size, random_state=42
    )
    
    # Build model
    model = build_neural_network(
        input_shape=X_train.shape[1],
        output_units=len(np.unique(y_encoded)) if task_type == "classification" else 1,
        config=config,
        task_type=task_type
    )
    
    # Callbacks
    callbacks = []
    if config.early_stopping:
        callbacks.append(EarlyStopping(monitor='val_loss', patience=5))
    
    # Train model
    history = model.fit(
        X_train, y_train,
        validation_split=config.validation_split,
        epochs=config.epochs,
        batch_size=config.batch_size,
        callbacks=callbacks,
        verbose=0
    )
    
    # Generate predictions
    y_pred = model.predict(X_test)
    if task_type == "classification":
        y_pred_classes = np.argmax(y_pred, axis=1) if len(model.output_shape) > 1 else (y_pred > 0.5).astype(int)
        y_proba = y_pred[:, 1] if len(model.output_shape) == 1 else y_pred
    else:
        y_pred_classes = y_pred.flatten()
        y_proba = None
    
    return {
        "model": model,
        "history": history.history,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred_classes,
        "y_proba": y_proba,
        "class_names": class_names,
        "scaler": scaler
    }