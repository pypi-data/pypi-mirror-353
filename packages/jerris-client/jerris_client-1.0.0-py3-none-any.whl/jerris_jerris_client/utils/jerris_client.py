import io
import requests
from PIL import Image
from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, List, Optional

from jerris_jerris_client.const.globals import (
    HARD_LIMIT_HEIGHT,
    HARD_LIMIT_WIDTH,
    MAX_FILE_SIZE_MB,
    SOFT_LIMIT_HEIGHT,
    SOFT_LIMIT_WIDTH,
    SUPPORTED_IMAGES_FORMATS,
)
from jerris_jerris_client.const.typing import AnalyseResponseData
from jerris_jerris_client.helpers.version_0_0_1 import v0_1_0_get_id
from jerris_jerris_client.utils.analyze_response import (
    API_STATUS_ERROR,
    AnalyzeResponse,
)


class JerrisClient(BaseModel):
    api_version: str = "0.2.0"

    base_url: Optional[HttpUrl] = Field(
        default="https://api.jerris.ai/",
        description="The base URL for the Jerris API",
    )

    api_key: str = Field(
        description="The API key for authenticating requests"
    )

    def get_base_url(self) -> Optional[str]:
        return self.base_url

    def _make_request(
            self,
            path: str,
            data: Optional[Dict] = None,
            files: Optional[Dict] = None,
            parameters: Optional[Dict] = None,
            method: str = "POST",
    ) -> AnalyzeResponse:
        return AnalyzeResponse.from_api_response(
            response_data=AnalyseResponseData(
                self._make_api_request(
                    path=path,
                    data=data,
                    files=files,
                    parameters=parameters,
                    method=method,
                )
            )
        )

    def _has_valid_mime_type(self, image: Image.Image) -> bool:
        mime_type = Image.MIME.get(image.format)

        for format_type, info in SUPPORTED_IMAGES_FORMATS.items():
            if mime_type in info["mime"]:
                return True

        return False

    def _get_binary_file_size(self, image_bytes: bytes) -> float:
        return len(image_bytes) / (1024 * 1024)

    def _make_api_request(
            self,
            path: str,
            data: Optional[Dict] = None,
            files: Optional[Dict] = None,
            parameters: Optional[Dict] = None,
            method: str = "POST",
    ) -> Dict:
        headers = {}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        if data is None:
            data = {}

        warning = {}

        if parameters is not None:
            parameters_ids = []
            for parameter in parameters:
                id = v0_1_0_get_id(parameter)

                if id is not None:
                    parameters_ids.append(id)
                else:
                    return {
                        "code": 404,
                        "status": API_STATUS_ERROR,
                        "error": "ResourceNotFound",
                        "message": f"Undefined requested parameter {parameter}.",
                    }

            data["parameters"] = parameters_ids

        response = None
        url = f"{self.get_base_url()}{path}"

        try:
            response = requests.request(
                method=method,
                url=url,
                data=data,
                files=files,
                headers=headers,
            )
            response.raise_for_status()  # Raise an error for 4xx/5xx responses

        except requests.exceptions.HTTPError as http_err:
            if response is not None:
                if response.status_code == 404:
                    return {
                        "code": response.status_code,
                        "status": API_STATUS_ERROR,
                        "error": "ResourceNotFound",
                        "message": f"API Resource not found, please check the API base URL: {url}",
                    }
                elif response.status_code == 401:
                    return {
                        "code": response.status_code,
                        "status": API_STATUS_ERROR,
                        "error": "AuthenticationError",
                        "message": "Bad credentials, please check your API key.",
                    }
                elif response.status_code == 400:
                    return {
                        "code": response.status_code,
                        "status": API_STATUS_ERROR,
                        "error": "InvalidRequest",
                        "message": "The request is invalid, please check the input data.",
                    }

            return {
                "code": 500,
                "status": API_STATUS_ERROR,
                "error": "ServerError",
                "message": f"Unexpected server error: {str(http_err)}",
            }

        except requests.exceptions.RequestException as err:
            return {
                "code": 500,
                "status": API_STATUS_ERROR,
                "error": "RequestError",
                "message": f"An error occurred while making the request: {str(err)}",
            }

        import traceback

        try:
            data = response.json()

            if len(warning.values()) > 0:
                data["warning"] = warning

            return data
        except Exception as err:
            error_type = type(err).__name__
            full_traceback = traceback.format_exc()

            return {
                "code": 400,
                "status": API_STATUS_ERROR,
                "error": "ResponseParsingError",
                "message": f"An error occurred while parsing the response: {error_type}",
                "trace": full_traceback,
                "data": response.json() if response else None,
            }

    def _check_analyze_url(self, image_url: Optional[str] = None) -> Optional[Dict]:
        try:
            response = requests.head(image_url)

            if response.status_code == 200:
                return self._check_file_size_error(
                    # Convert to MB
                    int(response.headers.get("Content-Length"))
                    / (1024 * 1024)
                )
        except:
            return {
                "code": 400,
                "status": API_STATUS_ERROR,
                "error": "InvalidURL",
                "message": "The provided image URL is invalid or empty.",
            }

        return None

    def analyze_url(
            self, image_url: Optional[str] = None, parameters: Optional[List[str]] = None
    ) -> AnalyzeResponse:
        return self._make_analyze_url_request(
            image_url=image_url, parameters=parameters
        )

    # TODO No more available, remove.
    # def analyze_url_async(
    #     self, image_url: Optional[str] = None, parameters: Optional[List[str]] = None
    # ) -> AnalyzeResponse:
    #     return self._make_analyze_url_request(
    #         image_url=image_url, parameters=parameters, path="/async"
    #     )

    def get_report(self, process_id: str) -> AnalyzeResponse:
        return self._make_request(
            path=f"mega-analyze/url/async/report?analyze_photo_result_id={process_id}",
            method="GET",
        )

    def _make_analyze_url_request(
            self,
            image_url: Optional[str] = None,
            parameters: Optional[List[str]] = None,
            path: str = "",
    ) -> AnalyzeResponse:
        error = self._check_analyze_url(image_url)
        if error:
            return self._wrap_response_data(error)

        data = {"image_url": image_url}
        if parameters:
            data["parameters"] = parameters

        return self._make_request(
            path=f"mega-analyze/url{path}",
            data={"image_url": image_url},
            parameters=parameters,
        )

    def _check_file_size_error(self, file_size: float):
        if file_size > MAX_FILE_SIZE_MB:
            return {
                "code": 413,
                "status": API_STATUS_ERROR,
                "error": "PayloadTooLarge",
                "message": f"The uploaded image size of {file_size} MB exceeds the maximum allowed size of {MAX_FILE_SIZE_MB} MB. "
                           f"Please reduce the file size and try again.",
            }

        return None

    def _check_analyze_binary(self, image_binary: bytes, image) -> Optional[Dict]:
        error = self._check_file_size_error(self._get_binary_file_size(image_binary))

        if error:
            return error

        if not self._has_valid_mime_type(image):
            return {
                "code": 415,
                "status": API_STATUS_ERROR,
                "error": "UnsupportedMediaType",
                "message": f"The uploaded file format is not supported. "
                           f"Please provide a valid image in one of the following formats: "
                           f"{', '.join([key.upper() for key in SUPPORTED_IMAGES_FORMATS.keys()])}.",
            }

        width, height = image.size
        if width > HARD_LIMIT_WIDTH or height > HARD_LIMIT_HEIGHT:
            return {
                "code": 415,
                "status": API_STATUS_ERROR,
                "error": "ImageTooLarge",
                "message": f"Image dimensions exceed the hard limit of {HARD_LIMIT_WIDTH}x{HARD_LIMIT_HEIGHT} pixels.",
            }

        return None

    def _wrap_response_data(self, response_data) -> AnalyzeResponse:
        return AnalyzeResponse.from_api_response(
            response_data=AnalyseResponseData(response_data)
        )

    def analyze_binary(
            self, image_binary: bytes, parameters: Optional[List[str]] = None
    ) -> AnalyzeResponse:
        return self._make_analyze_binary_request(
            image_binary=image_binary, parameters=parameters
        )

    # TODO No more available, remove.
    # def analyze_binary_async(
    #     self, image_binary: bytes, parameters: Optional[List[str]] = None
    # ) -> AnalyzeResponse:
    #     return self._make_analyze_binary_request(
    #         image_binary=image_binary, parameters=parameters, path="/async"
    #     )

    def _make_analyze_binary_request(
            self,
            image_binary: bytes,
            parameters: Optional[List[str]] = None,
            path: str = "",
    ) -> AnalyzeResponse:
        try:
            image = Image.open(io.BytesIO(image_binary))

            # Return binary specific errors.
            error = self._check_analyze_binary(image_binary, image)
        except:
            error = {
                "code": 400,
                "status": API_STATUS_ERROR,
                "error": "InvalidImageFile",
                "message": "The uploaded file could not be processed as an image. "
                           "Please ensure that the file is a valid image format and is not corrupted.",
            }

        if error:
            return self._wrap_response_data(error)

        response = self._make_request(
            path=f"mega-analyze/binary{path}",
            files={"image_file": image_binary},
            parameters=parameters,
        )

        # Complete with warnings in needed.
        if response.is_success():
            width, height = image.size
            if width > SOFT_LIMIT_WIDTH or height > SOFT_LIMIT_HEIGHT:
                response.data["warning"] = {
                    "image-resized": f"Image dimensions exceed the soft limit of {SOFT_LIMIT_WIDTH}x{SOFT_LIMIT_HEIGHT} and has been resized before analysis."
                }

        return response

    def analyze_file(
            self, file_path: str, parameters: Optional[List[str]] = None
    ) -> AnalyzeResponse:
        return self.analyze_binary(
            image_binary=self._get_file_binary(file_path=file_path),
            parameters=parameters,
        )

    def analyze_file_async(
            self, file_path: str, parameters: Optional[List[str]] = None
    ) -> AnalyzeResponse:
        return self.analyze_binary_async(
            image_binary=self._get_file_binary(file_path=file_path),
            parameters=parameters,
        )

    def _get_file_binary(self, file_path: str) -> bytes:
        from pathlib import Path

        file = Path(file_path)

        if not file.is_file():
            raise FileNotFoundError(
                f"The file {file_path} does not exist or is not accessible."
            )

        with open(file_path, "rb") as image_file:
            image_binary = image_file.read()

        return image_binary
