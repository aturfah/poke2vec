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
                        shuffle=True, validation_split=0.15)

    def predict(self, data, species_clause):
        probability_model = tf.keras.Sequential([
            self._model,
            tf.keras.layers.Softmax()
        ])

        results = probability_model(data)

        if species_clause:
            mask = tf.cast(tf.equal(data, 0), tf.float32)
            results = tf.math.multiply(results, mask)

        return results

    def test(self, test_data, test_lab, species_clause):
        results = self.predict(test_data, species_clause)
        results = tf.math.argmax(results, 1)

        # [print(test_lab[i], tf.keras.backend.get_value(results[i])) for i in range(len(test_lab))]

        confusion_matrix = tf.math.confusion_matrix(results, test_lab)

        correct_incorrect = tf.math.equal(results, test_lab)
        num_correct = tf.math.count_nonzero(correct_incorrect)

        pct_correct = num_correct / results.shape[0]

        print("Test Error: {pct} ({n_c}/{tot})".format(
            pct=round(tf.keras.backend.get_value(pct_correct), 3),
            n_c = tf.keras.backend.get_value(num_correct),
            tot=results.shape[0]
        ))

        return confusion_matrix.numpy()

    def layer_weights(self, name):
        return self._model.get_layer(name).variables