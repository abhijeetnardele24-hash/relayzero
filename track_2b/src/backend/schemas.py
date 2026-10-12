"""
RelayZero: Air-gapped, multimodal incident-brief compiler.
Pydantic v2 domain schemas and data contracts.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ModalityEnum(str, Enum):
    TEXT = "text"
    IMAGE_DOCUMENT = "image_document"
    VOICE_AUDIO = "voice_audio"


class LanguageEnum(str, Enum):
    DE = "de"
    FR = "fr"
    IT = "it"
    EN = "en"
    UNKNOWN = "und"


class ExtractionStatusEnum(str, Enum):
    ACCEPTED = "accepted"
    REVIEW_REQUIRED = "review_required"
    SYNTAX_REPAIRED = "syntax_repaired"
    REJECTED = "rejected"


class OperatorStatusEnum(str, Enum):
    UNREVIEWED = "unreviewed"
    CONFIRMED = "confirmed"
    EDITED = "edited"
    REJECTED = "rejected"


class ClusterStatusEnum(str, Enum):
    CORROBORATED = "corroborated"
    CONFLICT = "conflict"
    SINGLE_SOURCE = "single_source"
    MISSING = "missing"


class SourceReport(BaseModel):
    report_id: str = Field(..., description="Unique source identifier (e.g., SRC-DE-01)")
    incident_id: str = Field(..., description="Target incident ID")
    modality: ModalityEnum = Field(..., description="Modality of incoming report")
    language: LanguageEnum = Field(..., description="Report language")
    author_role: str = Field("Field Responder", description="Declared or inferred sender role")
    received_at: str = Field(..., description="ISO 8601 timestamp of reception")
    source_channel: str = Field("Radio/SMS", description="Source transmission channel")
    reliability_tier: str = Field("unverified", description="Verified First Responder, Citizen, Dispatch, etc.")
    raw_content: str = Field(..., description="Raw text, OCR transcription, or audio transcript")
    media_url: Optional[str] = Field(None, description="Optional relative path to artifact")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExtractedClaim(BaseModel):
    claim_id: str = Field(..., description="Unique claim ID (e.g., CLM-001)")
    incident_id: str
    source_id: str
    field: str = Field(..., description="Standardized slot name (e.g. location_primary, casualty_count)")
    normalized_value: str = Field(..., description="Canonical value representation")
    original_value: str = Field(..., description="Exact string slice from original report")
    evidence_pointer: str = Field(..., description="Quote or character offset in the source report")
    language: LanguageEnum
    confidence: float = Field(..., ge=0.0, le=1.0)
    extraction_status: ExtractionStatusEnum = ExtractionStatusEnum.ACCEPTED
    operator_status: OperatorStatusEnum = OperatorStatusEnum.UNREVIEWED
    operator_edited_value: Optional[str] = None
    model_name: str = "swiss-ai/Apertus-v1.5-8B"
    prompt_version: str = "v1.2-airgap-strict"
    timestamp: str


class ClaimCluster(BaseModel):
    cluster_id: str
    field: str
    status: ClusterStatusEnum
    claims: List[ExtractedClaim] = Field(default_factory=list)
    reconciled_value: Optional[str] = None
    conflict_explanation: Optional[str] = None
    operator_resolution: Optional[str] = None
    is_critical_field: bool = False


class SituationBrief(BaseModel):
    incident_id: str
    title: str
    executive_summary: str
    confirmed_facts: Dict[str, str] = Field(default_factory=dict)
    unresolved_conflicts: List[str] = Field(default_factory=list)
    critical_missing_fields: List[str] = Field(default_factory=list)
    recommended_priorities: List[str] = Field(default_factory=list)
    multilingual_summaries: Dict[str, str] = Field(default_factory=dict)
    generated_at: str
    model_name: str = "swiss-ai/Apertus-v1.5-8B"
    approved_by_operator: bool = False
    operator_notes: Optional[str] = None
    audit_hash: Optional[str] = None


class AuditEntry(BaseModel):
    entry_id: str
    timestamp: str
    action: str
    actor: str
    details: Dict[str, Any]
    hash_prev: str
    hash_curr: str


class Incident(BaseModel):
    incident_id: str
    title: str
    preset_id: Optional[str] = None
    status: str = "active"
    deployment_mode: str = "air_gapped"  # air_gapped, sovereign_cloud, replay
    created_at: str
    updated_at: str
    sources: List[SourceReport] = Field(default_factory=list)
    claims: List[ExtractedClaim] = Field(default_factory=list)
    clusters: List[ClaimCluster] = Field(default_factory=list)
    brief: Optional[SituationBrief] = None
    audit_trail: List[AuditEntry] = Field(default_factory=list)


class OperatorActionRequest(BaseModel):
    claim_id: Optional[str] = None
    cluster_id: Optional[str] = None
    action: str  # confirm, edit, reject, resolve_cluster
    new_value: Optional[str] = None
    notes: Optional[str] = None
    operator_id: str = "OP-CH-01"


class BriefApprovalRequest(BaseModel):
    approved: bool
    operator_notes: Optional[str] = None
    operator_id: str = "OP-CH-01"


class OfflineExportBundle(BaseModel):
    export_id: str
    incident_id: str
    exported_at: str
    system_version: str = "RelayZero v1.0.0"
    deployment_fingerprint: str
    air_gapped_verified: bool = True
    egress_zero_verified: bool = True
    incident_data: Dict[str, Any]
    audit_manifest: List[Dict[str, Any]]
    sha256_checksum: str
