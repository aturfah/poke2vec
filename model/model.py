"""
Model Class with Architecture
"""

import tensorflow as tf
from config import ModelConfig

class Model():
    def __init__(self, train_data, train_labels, train_weights):
        self._model = None
        self.hidden_dim = ModelConfig().hiddenLayerSize
        self.train_data = train_data
        self.train_labels = train_labels
        self.train_weights = train_weights

        self._init_model()

    def _init_model(self):
        self._model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(self.hidden_dim, input_shape=(self.train_data.shape[1], ), name="V-layer", use_bias=False),
            tf.keras.layers.Dense(self.train_data.shape[1], use_bias=False, name="U-layer",)
        ])

        loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        self._model.compile(optimizer='adam',
              loss=loss_fn,
              metrics=['accuracy'])

    def train(self, n_epochs=5):
        self._model.fit(self.train_data, self.train_labels,
                        epochs=n_epochs, batch_size=ModelConfig().batchSize,
                        sample_weight=self.train_weights,
                        shuffle=True, validation_split=0)

    def predict(self, data):
        probability_model = tf.keras.Sequential([
            self._model,
            tf.keras.layers.Softmax()
        ])

        return probability_model(data)

    def layer_weights(self, name):
        return self._model.get_layer(name).variables