import numpy as np
import tensorflow as tf
from tensorflow.keras.metrics import Precision, Recall
from tensorflow.python.keras import backend as K
from tensorflow.python.keras.utils import metrics_utils
from tensorflow.python.keras.utils.generic_utils import to_list
from tensorflow.python.ops import init_ops
from tensorflow.python.ops import math_ops


class Specificity(tf.keras.metrics.Metric):
    def __init__(self,
                 thresholds=None,
                 top_k=None,
                 class_id=None,
                 name=None,
                 dtype=None):
        super(Specificity, self).__init__(name=name, dtype=dtype)
        self.init_thresholds = thresholds
        self.top_k = top_k
        self.class_id = class_id

        default_threshold = 0.5 if top_k is None else metrics_utils.NEG_INF
        self.thresholds = metrics_utils.parse_init_thresholds(
            thresholds, default_threshold=default_threshold)
        self.true_negatives = self.add_weight(
            'true_negatives',
            shape=(len(self.thresholds),),
            initializer=init_ops.zeros_initializer)
        self.false_positives = self.add_weight(
            'false_positives',
            shape=(len(self.thresholds),),
            initializer=init_ops.zeros_initializer)

    def update_state(self, y_true, y_pred, sample_weight=None):
        return metrics_utils.update_confusion_matrix_variables(
            {
                metrics_utils.ConfusionMatrix.TRUE_NEGATIVES: self.true_negatives,
                metrics_utils.ConfusionMatrix.FALSE_POSITIVES: self.false_positives
            },
            y_true,
            y_pred,
            thresholds=self.thresholds,
            top_k=self.top_k,
            class_id=self.class_id,
            sample_weight=sample_weight)

    def result(self):
        result = math_ops.div_no_nan(
            self.true_negatives,
            self.true_negatives + self.false_positives
        )
        return result[0] if len(self.thresholds) == 1 else result

    def reset_states(self):
        num_thresholds = len(to_list(self.thresholds))
        K.batch_set_value(
            [(v, np.zeros((num_thresholds,)))
            for v in self.variables
        ])

    def get_config(self):
        config = {
            'thresholds': self.init_thresholds,
            'top_k': self.top_k,
            'class_id': self.class_id
        }
        base_config = super(Specificity, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))


class F1Score(tf.keras.metrics.Metric):
    def __init__(self, class_id=0, name='f1score', **kwargs):
        super(F1Score, self).__init__(name=name, **kwargs)
        self.recall = Recall(class_id=class_id, name=f'recall_{class_id}')
        self.precision = Precision(class_id=class_id, name=f'precision_{class_id}')

    def update_state(self, y_true, y_pred, sample_weight=None):
        self.recall.update_state(y_true, y_pred)
        self.precision.update_state(y_true, y_pred)

    def result(self):
        precision = self.precision.result()
        recall = self.recall.result()
        return tf.multiply(2.0, tf.multiply(precision, recall) / tf.add(precision, recall))

    def reset_states(self):
        self.recall.reset_states()
        self.precision.reset_states()
