"""
RelayZero: Air-gapped, multilingual, multi-source incident-brief compiler.
Strict Pydantic v2 schemas and domain models.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator


class ModalityEnum(str, Enum):
    TEXT = "text"
    DOCUMENT_TRANSCRIPT = "document_transcript"
    VOICE_TRANSCRIPT = "voice_transcript"


class LanguageEnum(str, Enum):
    DE = "de"
    FR = "fr"
    IT = "it"
    EN = "en"
    UNKNOWN = "und"


class ExtractionStatusEnum(str, Enum):
    ACCEPTED = "accepted"
    REVIEW_REQUIRED = "review_required"
    REJECTED = "rejected"


class OperatorClaimStatusEnum(str, Enum):
    UNREVIEWED = "unreviewed"
    OPERATOR_CONFIRMED = "operator_confirmed"
    EDITED = "edited"
    REJECTED = "rejected"


class ClusterStatusEnum(str, Enum):
    CORROBORATED = "corroborated"
    SINGLE_SOURCE_UNVERIFIED = "single_source_unverified"
    CONFLICTING = "conflicting"
    MISSING = "missing"
    OPERATOR_CONFIRMED = "operator_confirmed"


class AppModeEnum(str, Enum):
    LIVE = "live"
    FIXTURE = "fixture"


class EgressStatusEnum(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"


class EvidenceSpan(BaseModel):
    exact_quote: str = Field(..., description="Verbatim quote from source text")
    start_char: int = Field(..., ge=0, description="0-indexed start character offset")
    end_char: int = Field(..., ge=0, description="0-indexed end character offset")

    @model_validator(mode="after")
    def validate_offsets(self) -> EvidenceSpan:
        if self.end_char <= self.start_char:
            raise ValueError("end_char must be strictly greater than start_char")
        if len(self.exact_quote) != (self.end_char - self.start_char):
            raise ValueError("len(exact_quote) must equal end_char - start_char")
        return self


class SourceReport(BaseModel):
    report_id: str = Field(..., description="Unique source identifier (e.g. SRC-DE-01)")
    incident_id: str = Field(..., description="Incident ID to which report belongs")
    modality: ModalityEnum = Field(..., description="Ingested report modality")
    language: LanguageEnum = Field(..., description="Report language")
    author_role: str = Field("Field Responder", description="Author or transmitter role")
    received_at: str = Field(..., description="ISO 8601 timestamp of reception")
    source_channel: str = Field("Radio/SMS", description="Source channel name")
    reliability_tier: str = Field("unverified", description="Verified Responder, Citizen, Dispatch")
    raw_content: str = Field(..., min_length=1, max_length=50000, description="Raw report text or transcript")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExtractedClaim(BaseModel):
    claim_id: str = Field(..., description="Unique claim identifier (e.g. CLM-001)")
    incident_id: str
    source_id: str
    field: str = Field(..., description="Standard operational slot name")
    normalized_value: str = Field(..., description="Canonical slot representation")
    original_value: str = Field(..., description="Verbatim slice extracted from text")
    evidence_span: EvidenceSpan = Field(..., description="Exact verifiable character offset span")
    language: LanguageEnum
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Model confidence if reported; None if omitted")
    extraction_status: ExtractionStatusEnum = ExtractionStatusEnum.ACCEPTED
    operator_status: OperatorClaimStatusEnum = OperatorClaimStatusEnum.UNREVIEWED
    operator_edited_value: Optional[str] = None
    model_name: str = Field("Synthetic Demo Fixture", description="Model identifier or fixture source")
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
    confirmed_facts: Dict[str, str] = Field(default_factory=dict, description="Only operator_confirmed or corroborated facts")
    unverified_single_source_facts: Dict[str, str] = Field(default_factory=dict, description="Single-source claims awaiting independent verification")
    unresolved_conflicts: List[str] = Field(default_factory=list)
    critical_missing_fields: List[str] = Field(default_factory=list)
    recommended_priorities: List[str] = Field(default_factory=list)
    multilingual_summaries: Dict[str, str] = Field(default_factory=dict)
    generated_at: str
    model_name: str = "Synthetic Demo Fixture"
    approved_by_operator: bool = False
    operator_notes: Optional[str] = None
    emergency_override: bool = False
    override_reason: Optional[str] = None
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
    deployment_mode: str = "air_gapped"
    app_mode: AppModeEnum = AppModeEnum.FIXTURE
    created_at: str
    updated_at: str
    sources: List[SourceReport] = Field(default_factory=list)
    claims: List[ExtractedClaim] = Field(default_factory=list)
    clusters: List[ClaimCluster] = Field(default_factory=list)
    brief: Optional[SituationBrief] = None
    audit_trail: List[AuditEntry] = Field(default_factory=list)


class OperatorActionTypeEnum(str, Enum):
    CONFIRM_CLAIM = "confirm_claim"
    EDIT_CLAIM = "edit_claim"
    REJECT_CLAIM = "reject_claim"
    RESOLVE_CLUSTER = "resolve_cluster"


class OperatorActionRequest(BaseModel):
    action: OperatorActionTypeEnum
    claim_id: Optional[str] = None
    cluster_id: Optional[str] = None
    new_value: Optional[str] = None
    notes: Optional[str] = None
    operator_id: str = Field("OP-SWISS-01", min_length=2)


class BriefApprovalRequest(BaseModel):
    approved: bool
    operator_notes: Optional[str] = None
    operator_id: str = Field("OP-SWISS-01", min_length=2)
    emergency_override: bool = False
    override_reason: Optional[str] = None


class ChecksummedExportBundle(BaseModel):
    bundle_id: str
    incident_id: str
    exported_at: str
    system_version: str = "RelayZero v1.0.0"
    app_mode: AppModeEnum
    model_name: str
    egress_verification: EgressStatusEnum
    incident_data: Dict[str, Any]
    audit_manifest: List[Dict[str, Any]]
    sha256_checksum: str
