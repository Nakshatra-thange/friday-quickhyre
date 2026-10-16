from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field


class Job(BaseModel):
    id: str
    title: str
    company: str
    city: str
    state: str
    work_mode: Literal["Remote", "Hybrid", "On-site"]
    skills: list[str]
    exp_min: int
    exp_max: int
    category: str
    description: str
    posted_at: str
    company_type: Literal["startup", "mnc", "unicorn", "services"]
    is_internship: bool



class ResumeProfile(BaseModel):
    name: str | None = None
    skills: list[str] = Field(default_factory=list)
    years_experience: float = 0
    education: list[str] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)
    suspicious: bool = False  # resume contains instruction-like text (we treat it as data)


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=8, max_length=64)
    message: str = Field(min_length=1, max_length=2000)