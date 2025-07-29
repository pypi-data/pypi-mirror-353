from typing import Dict, Optional

from pydantic import BaseModel

from jerris_jerris_client.const.typing import AnalyseResponseData

API_STATUS_ERROR = "error"
API_STATUS_SUCCESS = "success"
API_STATUS_WARNING = "warning"


class AnalyzeResponse(BaseModel):
    data: Optional[Dict] = None
    error: Optional[str] = None

    @classmethod
    def from_api_response(cls, response_data: AnalyseResponseData):
        return cls(data=response_data)

    def is_success(self) -> bool:
        if self.data["status"] == API_STATUS_SUCCESS:
            return True
        return False

    def get_data(self) -> Optional[Dict]:
        if self.data["status"]:
            return self.data
        raise ValueError("Analysis failed, no data to return.")

    def get_process_id(self) -> str:
        return self.data["process_id"]

    def get_error(self) -> Optional[str]:
        if not self.data["status"]:
            return self.error
        return None
