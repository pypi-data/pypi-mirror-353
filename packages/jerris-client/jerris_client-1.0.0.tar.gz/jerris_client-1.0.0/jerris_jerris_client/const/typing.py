from typing import Optional, TypedDict


class AnalyzeParameter(TypedDict):
    id: int
    title: str


class AnalyseResponseData(TypedDict):
    status: str
    error: Optional[str]
    message: Optional[str]
    analysis: dict[str, AnalyzeParameter]
