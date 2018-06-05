# ClassifyObjects - Deploy TensorFlow Object Detection Models in the Cloud

ClassifyObjects is a hosted Python application that allows developers to deploy object detection models built with TensorFlow. It can be used to create an endpoint on a server (e.g. Amazon EC2) that predicts what objects appear within a given image.

The service is designed to run with any of the TensorFlow [Object Detection](https://github.com/tensorflow/models/tree/master/research/object_detection) models.


## Installation

### Dependencies

In order to deploy the service, you will need to install Python and a list of packages. The following packages are required and can be installed with pip:

- TensorFlow
- Django
- Pillow

### Object Detection Model

The following steps are required to configure a model with the project:

1. Prepare an object detection model. A list of models pre-trained on the COCO dataset can be found [here](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md#coco-trained-models-coco-models).

2. Create a folder named `static` in root directory of the project.

3. Copy the `frozen_inference_graph.pb` file from the downloaded model to the newly created `static` folder.

4. Prepare the label map associated with the object detection model. If using the pre-trained model on the COCO dataset as mentioned above, the label map can be found [here](https://github.com/tensorflow/models/blob/master/research/object_detection/data/mscoco_label_map.pbtxt).

5. Copy the label map file to the `static` folder that was created earlier and rename the file to `label_map.pbtxt`.

The final directory structure should appear as follows:
```
<root>/
    apps/
        ...
    classifyobjects/
        ...
    static/
        frozen_inference_graph.pb
        label_map.pbtxt
    ...
```

NOTE: Depending on your usecase, you may need to retrain the models on your own datasets in order to perform classifications on additional classes.


## API

The classification service provides a simple API that can be used for classifying objects. Once deployed, you can use a POST request with the image data to the endpoint with optional parameters. The resulting value will be a JSON encoded list of detected objects with their respective quantities.

The following is a breakdown of the request:

```
POST /classify?threshold=[Detection threshold]&verbose=[true or false] HTTP/1.1
Host: [Your host]
Content-Type: [image/jpeg or image/png]

[Image data]
```

The threshold parameter is used for filtering out results based on the confidence level. If no threshold is provided, a default value of 0.75 will be used.

The verbose parameter is used for changing the output format of the results. When enabled, the output includes a list of classes, scores, and normalized bounds. If disabled, the output will use a compact form which includes the classes with the number of occurences. By default, verbosity is disabled.

## Testing

For testing the deployment of the service, you can use the built-in Django server. Simply open a terminal window and change directories to the inside the root directory. Then, issue the following command:
```
python manage.py runserver 80
```

This command will bind the service to localhost on port 80. Depending on the size of the model, this command may take up to a minute to complete.

The endpoint can be easily tested by using programs or through a command-line tool (e.g curl).
The following are examples of how you can use curl to test the endpoint with an image named `image.jpg` in the current working directory:

<div align="center">
    <br>
    <img src="https://github.com/tensorflow/models/raw/f87a58cd96d45de73c9a8330a06b2ab56749a7fa/research/object_detection/test_images/image1.jpg" width="600" height="373">
    <br>
    <i>Image retrieved from <a href="https://github.com/tensorflow/models/tree/master/research/object_detection/test_images">test image set</a> in TensorFlow's Object Detection API repository</i>
</div>

Request with threshold of 0.8:
```
curl -X POST -H "Content-Type: image/jpeg" --data-binary "@image.jpg" "http://localhost/classify?threshold=0.8"
```

```json
{
    "Dog": 2
}
```

Request with threshold of 0.8 and verbose output:
```
curl -X POST -H "Content-Type: image/jpeg" --data-binary "@image.jpg" "http://localhost/classify?threshold=0.8&verbose=true"
```

Response:
```json
[
    {
        "class": "Dog",
        "score": 0.9788029193878174,
        "x1": 0.3925120234489441,
        "y1": 0.10611796379089355,
        "x2": 0.979144275188446,
        "y2": 0.9395240545272827
    },
    {
        "class": "Dog",
        "score": 0.9340201616287231,
        "x1": 0.012712955474853516,
        "y1": 0.03568807244300842,
        "x2": 0.30899322032928467,
        "y2": 0.8408676385879517
    }
]
```


## Deployment

It is recommended that you do not use the Django test server that was previously mentioned for deployment in a production environment. Instead, run the program behind a reliable web server like nginx.

For best practices with deployment, a checklist can be found [here](https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/).