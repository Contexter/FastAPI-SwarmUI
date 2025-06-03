# app/schemas.py

from __future__ import annotations
from typing import List, Dict, Optional
from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    uptime: str


class ConfigReference(BaseModel):
    name: str
    target: str


class ConfigDetail(BaseModel):
    env: Dict[str, str]
    ports: Dict[str, int]


class ConfigPatch(BaseModel):
    env: Optional[Dict[str, str]] = None
    ports: Optional[Dict[str, int]] = None


class ServiceSpec(BaseModel):
    image: str
    ports: Optional[Dict[str, int]] = {}
    secrets: Optional[List[str]] = []
    configs: Optional[List[ConfigReference]] = []


class ServiceDetail(BaseModel):
    name: str
    status: str
    ports: Dict[str, int]
    secrets: List[str]
    configs: List[ConfigReference]


class ServiceListResponse(BaseModel):
    services: List[ServiceDetail]
    total: int
    limit: int
    offset: int


class DeployRequest(BaseModel):
    services: List[str]


class DeployResponse(BaseModel):
    status: str
    message: str


class BatchDeployResponse(BaseModel):
    # <— must have a “results” array of DeployResponse, so the linter stops complaining
    results: List[DeployResponse]


class ErrorResponse(BaseModel):
    code: int
    message: str


class ClientStatusResponse(BaseModel):
    service: str
    last_generated_at: datetime
    checksum: str
    status: str
    error: Optional[str] = None


class ValidationError(BaseModel):
    loc: list
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    detail: List[ValidationError]
