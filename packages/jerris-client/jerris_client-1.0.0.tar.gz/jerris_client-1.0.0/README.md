# Jerris API Client for Python

[![pipeline status](http://gitlab.syrtis.be/jerris-public/python-client/badges/master/pipeline.svg)](http://gitlab.syrtis.be/jerris-public/python-client/-/commits/master)

## Overview

Jerris Client is a Python library designed to interact with Jerris' photo analysis API (https://jerris.ai). The service allows users to analyze images for professional photographic properties such as lighting, perspective, depth of field, and more.

The API returns a detailed description and analysis score for each photographic property provided.

- `analyze_url`: Analyzes an image based on its URL.
- `analyze_binary`: Analyzes an image provided in binary format.
- `analyze_file`: Analyzes an image by providing the file path.
- `analyze_file_async`: Asynchronously analyzes an image by providing the file path, returning a `process_id`.
- `analyze_binary_async`: Asynchronously analyzes an image provided in binary format, returning a `process_id`.
- `analyze_url_async`: Asynchronously analyzes an image based on its URL, returning a `process_id`.

## Installation

You can install the library using `pip`:

```bash
pip install jerris-client
```

If the package is not available on PyPI, you can install it directly from the repository:

```bash
pip install git+http://gitlab.syrtis.be/jerris-public/python-client.git
```

## Usage

### Initializing the Client

To start using the Jerris API, initialize the client:

```python
from jerris_jerris_client.utils.jerris_client import JerrisClient

client = JerrisClient(api_key="YOUR_API_KEY")
```

### Analyze an Image by URL

To analyze an image via a URL, use the `analyze_url` method. You can provide an image URL and an optional list of
parameters to specify which properties to analyze.

```python
from jerris_jerris_client.const.parameters import JERRIS_IMAGE_PARAMETER_PERSPECTIVE_LINES,
    JERRIS_IMAGE_PARAMETER_ASPECT_RATIO

result = client.analyze_url(
    image_url="https://example.com/image.jpg",
    parameters=[
        JERRIS_IMAGE_PARAMETER_PERSPECTIVE_LINES,
        JERRIS_IMAGE_PARAMETER_ASPECT_RATIO
    ]
)
```

Example result:

```json
{
  "aspect-ratio": {
    "id": 13,
    "title": "Aspect Ratio",
    "type": "string",
    "result": "Horizontal",
    "message": "The photo is wider than it is tall, indicating a horizontal aspect ratio which typically conveys a sense of space and is suitable for capturing multiple subjects."
  },
  "minimizing-distractions": {
    "id": 1,
    "title": "Minimizing Distractions",
    "type": "integer",
    "result": 0,
    "message": "No analysis"
  },
  "perspective-lines": {
    "id": 12,
    "title": "Perspective Lines",
    "type": "integer",
    "result": 0,
    "message": "No analysis"
  }
}
```

### Analyze an Image in Binary Format

To analyze an image from binary data, use the `analyze_binary` method:

```python
from jerris_jerris_client.const.parameters import JERRIS_IMAGE_PARAMETER_PERSPECTIVE_LINES,
    JERRIS_IMAGE_PARAMETER_ASPECT_RATIO

with open('path_to_image.jpg', 'rb') as image_file:
    image_binary = image_file.read()

result = client.analyze_binary(
    image_binary=image_binary,
    parameters=[
        JERRIS_IMAGE_PARAMETER_PERSPECTIVE_LINES,
        JERRIS_IMAGE_PARAMETER_ASPECT_RATIO
    ]
)
```

### Analyze an Image by File Path

To analyze an image by providing the file path, use the `analyze_file` method:

```python
result = client.analyze_file(
    file_path="path_to_image.jpg",
    parameters=[
        JERRIS_IMAGE_PARAMETER_PERSPECTIVE_LINES,
        JERRIS_IMAGE_PARAMETER_ASPECT_RATIO
    ]
)
```

This method automatically reads the image file and sends it for analysis, similar to `analyze_binary`.

### Asynchronous Analysis Methods

To perform an asynchronous analysis, use the `analyze_url_async`, `analyze_binary_async`, or `analyze_file_async` methods. These methods return a `process_id` that can be used to query the status of the analysis.

```python
# Example of initiating an asynchronous analysis
process_id = client.analyze_url_async(
    image_url="https://example.com/image.jpg"
)

# Example of retrieving the report
report = client.get_report(process_id)

# The report will return a status: 'warning' if the process is still ongoing, or the data with a status: 'success' once completed.
```

## Running demo

```bash
pip install -r requirements-dev.txt
python3 demo/analyze.py
```

## Restrictions

### File formats

This is the mime types supported by the package, based on the file metadata (not the file extension).

> HEIC, JPG, PNG, WEBP

### File dimensions

- Soft limit : 1216px x 768px, image exceeding this size will be resized before analyzing
- Hard limit : 1800px x 1800px, an error will be thrown if image exceed this limit

## License

The project follows the **MIT License** to allow broad usage of the library while ensuring that the service remains proprietary.

## Author

This library is maintained by Jerris, a Belgian company specializing in AI-driven photography and images analysis.
