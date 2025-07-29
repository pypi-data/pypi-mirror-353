import json
from unittest.mock import patch

from jerris_jerris_client.const.parameters import (
    JERRIS_IMAGE_PARAMETER_DOUBLE_EXPOSURE,
    JERRIS_IMAGE_PARAMETER_COMPOSITION_CONTRAST,
)
from jerris_jerris_client.helpers.version_0_0_1 import v0_1_0_get_id
from jerris_jerris_client.utils.jerris_client import JerrisClient


class TestJerrisClient:
    test_api_key: str = "test-api-key"

    def _load_mock_response(self, version):
        """
        Utility function to load the mock response from the appropriate file.
        """
        with open(f'tests/resources/{version}/analyze-all-01.json', 'r') as f:
            return json.load(f)

    def _perform_test(self, mock_post, method, expected_response, data=None, files=None):
        # Initialize the Jerris client
        api_client = JerrisClient(api_key=self.test_api_key)

        # Call the method (either analyze_url or analyze_binary)
        result = method(api_client)

        # Assert that the result matches the expected response
        assert result == expected_response

        # Verify that the POST request was made with the correct data and files
        mock_post.assert_called_once_with(
            f'{api_client.get_base_url()}/photo-academy/analyze-photo-parameters',
            data=data,
            files=files,
            headers={'Authorization': f'Bearer {self.test_api_key}'}
        )

    def _setup_mock(self, mock_post):
        """
        Utility function to set up the mock for POST requests.
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = self._load_mock_response('version_0_1_0')

    def _get_expected_response(self):
        """
        Utility function to load the expected response.
        """
        return self._load_mock_response('version_1_0_0')

    @patch('requests.post')
    def test_analyze_url(self, mock_post):
        self._setup_mock(mock_post)
        expected_response = self._get_expected_response()

        # Call the helper function with analyze_url as the method to test
        self._perform_test(
            mock_post=mock_post,
            method=lambda client: client.analyze_url(
                image_url='https://example.com/image.jpg',
                parameters=[
                    JERRIS_IMAGE_PARAMETER_DOUBLE_EXPOSURE,
                    JERRIS_IMAGE_PARAMETER_COMPOSITION_CONTRAST
                ]
            ),
            expected_response=expected_response,
            data={
                'image_string': 'https://example.com/image.jpg',
                'parameters': [
                    v0_1_0_get_id(JERRIS_IMAGE_PARAMETER_DOUBLE_EXPOSURE),
                    v0_1_0_get_id(JERRIS_IMAGE_PARAMETER_COMPOSITION_CONTRAST)
                ]
            },
            files=None
        )

    @patch('requests.post')
    def test_analyze_binary(self, mock_post):
        self._setup_mock(mock_post)
        expected_response = self._get_expected_response()

        # Simulate a binary image
        image_binary = b'\x89PNG\r\n\x1a\n\x00\x00\x00IHDR...'

        # Call the helper function with analyze_binary as the method to test
        self._perform_test(
            mock_post=mock_post,
            method=lambda client: client.analyze_binary(
                image_binary=image_binary,
                parameters=[
                    JERRIS_IMAGE_PARAMETER_DOUBLE_EXPOSURE,
                    JERRIS_IMAGE_PARAMETER_COMPOSITION_CONTRAST
                ]
            ),
            expected_response=expected_response,
            data={
                'parameters': [
                    v0_1_0_get_id(JERRIS_IMAGE_PARAMETER_DOUBLE_EXPOSURE),
                    v0_1_0_get_id(JERRIS_IMAGE_PARAMETER_COMPOSITION_CONTRAST)
                ]
            },
            files={'image_file': image_binary}
        )

    @patch('requests.post')
    def test_analyze_file(self, mock_post):
        self._setup_mock(mock_post)
        expected_response = self._get_expected_response()

        # Get binary for validation purpose.
        file_path = 'tests/resources/test-image.png'
        with open(file_path, 'rb') as image_file:
            image_binary = image_file.read()

        self._perform_test(
            mock_post=mock_post,
            method=lambda client: client.analyze_file(
                file_path=file_path,
                parameters=[
                    JERRIS_IMAGE_PARAMETER_DOUBLE_EXPOSURE,
                    JERRIS_IMAGE_PARAMETER_COMPOSITION_CONTRAST
                ]
            ),
            expected_response=expected_response,
            data={
                'parameters': [
                    v0_1_0_get_id(JERRIS_IMAGE_PARAMETER_DOUBLE_EXPOSURE),
                    v0_1_0_get_id(JERRIS_IMAGE_PARAMETER_COMPOSITION_CONTRAST)
                ]
            },
            files={'image_file': image_binary}
        )
