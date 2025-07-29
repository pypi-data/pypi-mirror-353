from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, ConfigDict, field_serializer

UTC = timezone.utc


# Helper function for datetime serialization
def _serialize_datetime(dt: datetime, _info: Any) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)  # Assume UTC if naive
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


class BaseKeyModel(BaseModel):
    pass


class IssuerKeyFileModel(BaseKeyModel):
    privateKeyMultibase: str
    did: Optional[str] = None
    publicKeyMultibase: Optional[str] = None


class WebKeyFileModel(BaseKeyModel):
    publicKeyMultibase: str


class ProofModel(BaseModel):
    type: str = "Ed25519Signature2020"
    created: datetime
    proofPurpose: str
    verificationMethod: str
    proofValue: str

    model_config = ConfigDict(populate_by_name=True)

    @field_serializer("created")
    def serialize_created(self, dt: datetime, _info: Any) -> str:
        return _serialize_datetime(dt, _info)


class VerifiableCredentialModel(BaseModel):
    context: Union[List[Union[str, Dict]], str] = Field(
        alias="@context",
        default=[
            "https://www.w3.org/2018/credentials/v1",
            "https://w3id.org/security/suites/ed25519-2020/v1",
        ],
    )
    id: str
    type: List[str]
    issuer: str
    issuanceDate: datetime
    expirationDate: Optional[datetime] = None
    credentialSubject: Dict[str, Any]
    evidence: Optional[List[Dict[str, Any]]] = None
    proof: Optional[ProofModel] = None

    model_config = ConfigDict(populate_by_name=True, validate_assignment=True)

    @field_serializer("issuanceDate", "expirationDate", when_used="json-unless-none")
    def serialize_dates(self, dt: datetime, _info: Any) -> str:
        return _serialize_datetime(dt, _info)


class VerificationMethodModel(BaseModel):
    id: str
    type: str = "Ed25519VerificationKey2020"
    controller: str  # DID string
    publicKeyMultibase: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class DIDKeyModel(BaseModel):
    did: str
    publicKeyMultibase: str
    privateKeyMultibase: Optional[str] = None


class DIDDocumentModel(BaseModel):
    context: Union[str, List[str]] = Field(alias="@context")
    id: str  # The DID itself
    verificationMethod: List[VerificationMethodModel] = Field(default_factory=list)
    authentication: Optional[List[Union[str, VerificationMethodModel]]] = Field(
        default_factory=list
    )
    assertionMethod: Optional[List[Union[str, VerificationMethodModel]]] = Field(
        default_factory=list
    )
    keyAgreement: Optional[List[Union[str, VerificationMethodModel]]] = Field(
        default_factory=list
    )
    capabilityInvocation: Optional[List[Union[str, VerificationMethodModel]]] = Field(
        default_factory=list
    )
    capabilityDelegation: Optional[List[Union[str, VerificationMethodModel]]] = Field(
        default_factory=list
    )
    service: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class DIDWebModel(BaseModel):
    did: str
    did_document: DIDDocumentModel
    privateKeyMultibase: str
    publicKeyMultibase: str
    key_id: str


class AgentCardModel(BaseModel):
    name: str
    did: str
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)


class SkillModel(BaseModel):
    scope: str
    granted: bool


class CredentialSubjectWithSkillsModel(BaseModel):
    id: str
    skills: List[SkillModel] = Field(default_factory=list)
    conditions: Optional[Dict[str, Any]] = None
    delegationDetails: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="allow")


class MapGenerationParams(BaseModel):
    region: str
    style: str


class MapGenerationResponse(BaseModel):
    status: str
    region: Optional[str] = None
    style: Optional[str] = None
