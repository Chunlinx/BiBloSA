from configs import cfg
from src.utils.record_log import _logger
import numpy as np
import tensorflow as tf


class Evaluator(object):
    def __init__(self, model):
        self.model = model
        self.global_step = model.global_step

        ## ---- summary----
        self.build_summary()
        self.writer = tf.summary.FileWriter(cfg.summary_dir)

    def get_evaluation(self, sess, dataset_obj, n_th_fold, global_step=None):
        _logger.add()
        _logger.add('getting evaluation result for %s' % dataset_obj.dataset_type)

        logits_list, loss_list, accu_list = [], [], []
        for sample_batch, _, _, _ in dataset_obj.generate_batch_sample_iter(n_th_fold):
            feed_dict = self.model.get_feed_dict(sample_batch, 'dev')
            logits, loss, accu = sess.run([self.model.logits,
                                           self.model.loss, self.model.accuracy], feed_dict)
            logits_list.append(np.argmax(logits, -1))
            loss_list.append(loss)
            accu_list.append(accu)

        logits_array = np.concatenate(logits_list, 0)
        loss_value = np.mean(loss_list)
        accu_array = np.concatenate(accu_list, 0)
        accu_value = np.mean(accu_array)

        # todo: analysis
        # analysis_save_dir = cfg.mkdir(cfg.answer_dir, 'gs_%d' % global_step or 0)
        # OutputAnalysis.do_analysis(dataset_obj, logits_array, accu_array, analysis_save_dir,
        #                            cfg.fine_grained)

        if global_step is not None:


            summary_feed_dict = {
                self.dev_loss: loss_value,
                self.dev_accuracy: accu_value,
            }
            summary = sess.run(self.dev_summaries, summary_feed_dict)
            self.writer.add_summary(summary, global_step)


        return loss_value, accu_value


    # --- internal use ------
    def build_summary(self):
        with tf.name_scope('dev_summaries'):
            self.dev_loss = tf.placeholder(tf.float32, [], 'dev_loss')
            self.dev_accuracy = tf.placeholder(tf.float32, [], 'dev_accuracy')
            tf.add_to_collection('dev_summaries_collection', tf.summary.scalar('dev_loss',self.dev_loss))
            tf.add_to_collection('dev_summaries_collection', tf.summary.scalar('dev_accuracy',self.dev_accuracy))
            self.dev_summaries = tf.summary.merge_all('dev_summaries_collection')

