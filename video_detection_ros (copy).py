
import rospy
from sensor_msgs.msg import Image as ros_img

import numpy as np
import os
import sys
import tensorflow as tf

from cv_bridge import CvBridge

if tf.__version__ < '1.4.0':
  raise ImportError('Please upgrade your tensorflow installation to v1.4.* or later!')

import cv2

cap = cv2.VideoCapture(0)
fps=30

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")


#from utils import label_map_util
from object_detection.utils import label_map_util

from object_detection.utils import visualization_utils as vis_util

class rostensorflow():
    def __init__(self):
        self.image_pub = rospy.Publisher("/detected_object_topic",ros_img, queue_size=0)
        self.rate = rospy.Rate(30)
        self.bridge = CvBridge()
        
        with detection_graph.as_default():
            with tf.Session(graph=detection_graph) as sess:
                # Definite input and output Tensors for detection_graph
                image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
                # Each box represents a part of the image where a particular object was detected.
                detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
                # Each score represent how level of confidence for each of the objects.
                # Score is shown on the result image, together with the class label.
                detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
                detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = detection_graph.get_tensor_by_name('num_detections:0')
                while not rospy.is_shutdown():
                  ret, image_np = cap.read()
                  # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                  image_np_expanded = np.expand_dims(image_np, axis=0)
                  # Actual detection.
                  (boxes, scores, classes, num) = sess.run(
                      [detection_boxes, detection_scores, detection_classes, num_detections],
                      feed_dict={image_tensor: image_np_expanded})
                  # Visualization of the results of a detection.
                  vis_util.visualize_boxes_and_labels_on_image_array(
                      image_np,
                      np.squeeze(boxes),
                      np.squeeze(classes).astype(np.int32),
                      np.squeeze(scores),
                      category_index,
                      use_normalized_coordinates=True,
                      line_thickness=8)
                  self.rate.sleep()
                  cv2.imshow('object detection', cv2.resize(image_np, (800,600)))
                  if num>0:
                    self.image_pub.publish(self.bridge.cv2_to_imgmsg(image_np, "bgr8")) # publisher (detected object)
                  if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break

if __name__ == '__main__':
    rospy.init_node('rostensorflow')
    
    # What model to download.
    MODEL_NAME = '/home/nvidia/ssd_mobilenet_v1_coco_2018_01_28'

    # Path to frozen detection graph. This is the actual model that is used for the object detection.
    PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
    
    # List of the strings that is used to add correct label for each box.
    PATH_TO_LABELS = os.path.join('/home/nvidia/tf_trt_models/third_party/models/research/object_detection/data', 'mscoco_label_map.pbtxt')

    NUM_CLASSES = 90
    
    
    detection_graph = tf.Graph()
    with detection_graph.as_default():
      od_graph_def = tf.GraphDef()
      with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')


    # ## Loading label map
    
    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)
    
    obj_det = rostensorflow()
    
    rospy.spin()
    
    

