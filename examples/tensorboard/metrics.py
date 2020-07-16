import tensorflow as tf


class Recall(tf.keras.metrics.Metric):
    def __init__(self, threshold=3.5, name='recall', **kwargs):
        super(Recall, self).__init__(name=name, **kwargs)
        self.threshold = tf.constant(threshold, dtype=tf.float32)
        self.checker = tf.constant(2.0, dtype=tf.float32)
        self.tp = self.add_weight(name='true_positive', initializer='zeros')
        self.tp_fn = self.add_weight(name='relevant', initializer='zeros')

    def update_state(self, y_true, y_pred, sample_weight=None):
        relevant = tf.cast(y_true >= self.threshold, dtype=tf.float32)
        recommended = tf.cast(y_pred >= self.threshold, dtype=tf.float32)

        relevant_recommend = tf.reduce_sum(tf.cast(tf.reshape(
        relevant + recommended, (-1, 1)) >= self.checker, dtype=tf.float32))

        self.tp.assign_add(relevant_recommend)
        self.tp_fn.assign_add(tf.reduce_sum(relevant))

    def result(self):
        return tf.divide(self.tp, self.tp_fn)

    def reset_states(self):
        self.tp.assign(0.)
        self.tp_fn.assign(0.)
