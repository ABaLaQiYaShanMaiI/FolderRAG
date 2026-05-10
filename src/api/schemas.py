from pydantic import BaseModel
from typing import List, Optional, Dict


class SearchRequest(BaseModel):
    query: str
    k: int = 5
    filters: Optional[Dict] = None


class SearchResult(BaseModel):
    id: str
    text: str
    source: str
    offset: int
    score: float
    mime: Optional[str] = None
    extract_type: Optional[str] = None
    hex_preview: Optional[str] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]


class DocResponse(BaseModel):
    id: str
    text: Optional[str] = None
    source: Optional[str] = None
    offset: Optional[int] = None
    mime: Optional[str] = None
    extract_type: Optional[str] = None
    hex_preview: Optional[str] = None
