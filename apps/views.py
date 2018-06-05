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

import json
from io import BytesIO

from PIL import Image
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .services import ClassificationService

# Cache the service instance
service = ClassificationService()


@csrf_exempt
def classify(request):
    if request.method != 'POST':
        msg = json.dumps({'error': 'Invalid request method'})
        return HttpResponse(msg, 'application/json')

    if len(request.body) == 0:
        msg = json.dumps({'error': 'No image provided'})
        return HttpResponse(msg, 'application/json')

    image = Image.open(BytesIO(request.body))
    detection_threshold = float(request.GET.get('threshold', 0.75))
    verbose = parse_bool(request.GET.get("verbose", False))

    classifications = service.classify(image, detection_threshold, verbose)
    print(classifications)

    msg = json.dumps(classifications)
    return HttpResponse(msg, 'application/json')


def parse_bool(value):
    if type(value) == bool:
        return value
    return value.lower() == "true"
