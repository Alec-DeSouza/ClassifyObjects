#
# Copyright 2018 - present, ClassifyObjects contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import re
from collections import Counter

import numpy as np
import tensorflow as tf


class ClassificationService:
    def __init__(self):
        self.label_map = self.__load_label_map('static/label_map.pbtxt')
        self.detection_graph = self.__load_model('static/frozen_inference_graph.pb')

    def classify(self, image, detection_threshold, verbose):
        image_np = self.__load_image_into_numpy_array(image.convert('RGB'))
        detection_graph = self.detection_graph

        with detection_graph.as_default():
            with tf.Session(graph=detection_graph) as sess:
                image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
                detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
                detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
                detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

                image_np_expanded = np.expand_dims(image_np, axis=0)

                (scores, classes, boxes) = sess.run([detection_scores, detection_classes, detection_boxes],
                                                    feed_dict={image_tensor: image_np_expanded})

                if verbose:
                    detections = [
                        {
                            'class': self.label_map[int(detection_class)],
                            'score': float(detection_score),
                            'x1': float(bbox[1]),
                            'y1': float(bbox[0]),
                            'x2': float(bbox[3]),
                            'y2': float(bbox[2])
                        }
                        for detection_class, detection_score, bbox in zip(classes[0], scores[0], boxes[0])
                        if detection_score > detection_threshold
                    ]
                else:
                    detections = dict(Counter([
                        self.label_map[int(detection_class)]
                        for detection_class, detection_score in zip(classes[0], scores[0])
                        if detection_score > detection_threshold
                    ]))

        return detections

    @staticmethod
    def __load_image_into_numpy_array(image):
        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

    @staticmethod
    def __load_label_map(filename):
        result = {}

        with open(filename, 'r') as f:
            map_data = f.read()

        map_items = re.findall('id: (\d+)\r?\n.+display_name: \"(.+?)\"', map_data)

        for item_id, item_name in map_items:
            result[int(item_id)] = str(item_name).title()

        return result

    @staticmethod
    def __load_model(filename):
        detection_graph = tf.Graph()

        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()

            with tf.gfile.GFile(filename, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        return detection_graph
