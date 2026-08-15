"""
Pydantic models for onboarding document extraction.

Design notes:
- Every field is Optional. A missing/null field is a data point in itself
  (e.g. "no source_of_funds stated") and should be handled deliberately at
  the vectorization stage, not forced to look "complete" here.
- Fields split by WHEN they get filled:
    1. Extracted directly from the onboarding document by Gemma.
    2. Populated later by a separate screening/sanctions service.
  Screening fields default to None and are filled by calling
  `.apply_screening_result(...)` after your screening step runs — this
  keeps "what the document says" and "what we independently verified"
  clearly separate, which matters both for the ML pipeline and for
  audit/compliance defensibility.
"""

from __future__ import annotations
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Shared enums
# ---------------------------------------------------------------------------

class EntityType(str, Enum):
    SOLE_PROPRIETORSHIP = "sole_proprietorship"
    PARTNERSHIP = "partnership"
    LLP = "llp"
    PRIVATE_LIMITED = "private_limited"
    PUBLIC_LIMITED = "public_limited"
    TRUST = "trust"
    HUF = "huf"
    OTHER = "other"


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------

class WatchlistChecks(BaseModel):
    """Entity-level (or individual-level) screening results.

    These are SCREENING fields — they should be populated by your
    screening service, not guessed by Gemma from document text, unless
    the document itself is literally a screening report.
    """
    pep_status: Optional[bool] = None
    unsc_consolidated_list_status: Optional[bool] = None
    uapa_mha_status: Optional[bool] = None


class BeneficialOwner(BaseModel):
    name: str
    ownership_pct: Optional[float] = Field(default=None, ge=0, le=100)
    nationality: Optional[str] = None

    # --- screening fields, filled post-extraction ---
    is_pep: Optional[bool] = None
    pep_position: Optional[str] = None
    sanctions_match: Optional[bool] = None


# ---------------------------------------------------------------------------
# Individual onboarding profile
# ---------------------------------------------------------------------------

class IndividualIDNumbers(BaseModel):
    passport_number: Optional[str] = None
    aadhaar_last4: Optional[str] = None
    pan_number: Optional[str] = None
    voter_id_number: Optional[str] = None

    @field_validator("aadhaar_last4")
    @classmethod
    def enforce_masking(cls, v: Optional[str]) -> Optional[str]:
        """Defensive check: never let a full Aadhaar number slip through.

        If something longer than 4 digits arrives here (e.g. Gemma returned
        the full number despite instructions), mask it down rather than
        raise — logging a warning is your job at the call site, but we
        should never persist the full number.
        """
        if v is None:
            return v
        digits = "".join(ch for ch in v if ch.isdigit())
        if len(digits) > 4:
            return digits[-4:]
        return v


class IndividualOnboardingProfile(BaseModel):
    # --- extracted from document ---
    legal_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    place_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    id_numbers: IndividualIDNumbers = Field(default_factory=IndividualIDNumbers)
    document_id: Optional[str] = None
    document_expiry_date: Optional[date] = None
    document_issuing_authority: Optional[str] = None

    # --- filled by screening service, after extraction ---
    watchlist_checks: WatchlistChecks = Field(default_factory=WatchlistChecks)
    screening_timestamp: Optional[datetime] = None

    def apply_screening_result(
        self,
        pep_status: Optional[bool] = None,
        unsc_status: Optional[bool] = None,
        uapa_status: Optional[bool] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Mutate in place once your screening service returns results."""
        if pep_status is not None:
            self.watchlist_checks.pep_status = pep_status
        if unsc_status is not None:
            self.watchlist_checks.unsc_consolidated_list_status = unsc_status
        if uapa_status is not None:
            self.watchlist_checks.uapa_mha_status = uapa_status
        self.screening_timestamp = timestamp or datetime.now(timezone.utc)

    def is_screening_complete(self) -> bool:
        return all(
            v is not None
            for v in (
                self.watchlist_checks.pep_status,
                self.watchlist_checks.unsc_consolidated_list_status,
                self.watchlist_checks.uapa_mha_status,
            )
        )


# ---------------------------------------------------------------------------
# Business onboarding profile
# ---------------------------------------------------------------------------

class BusinessOnboardingProfile(BaseModel):
    # --- extracted from document ---
    entity_type: Optional[EntityType] = None
    legal_name: Optional[str] = None
    trade_name: Optional[str] = None
    alias_names: list[str] = Field(default_factory=list)
    beneficial_owners: list[BeneficialOwner] = Field(default_factory=list)
    principal_business_activity: Optional[str] = None
    nic_code: Optional[str] = None
    registered_address: Optional[str] = None
    operating_address: Optional[str] = None
    jurisdiction: Optional[str] = None
    incorporation_number: Optional[str] = None
    corporate_id_number: Optional[str] = None
    gst_id: Optional[str] = None
    registration_number: Optional[str] = None
    date_of_incorporation: Optional[date] = None
    expected_monthly_volume: Optional[float] = None
    expected_monthly_transaction_frequency: Optional[float] = None
    source_of_funds: Optional[str] = None
    source_of_income: Optional[str] = None
    operating_countries: list[str] = Field(default_factory=list)
    document_number: Optional[str] = None
    document_expiry_date: Optional[date] = None
    document_issuing_authority: Optional[str] = None

    # --- filled by screening service, after extraction ---
    watchlist_checks: WatchlistChecks = Field(default_factory=WatchlistChecks)
    screening_timestamp: Optional[datetime] = None

    def apply_screening_result(
        self,
        pep_status: Optional[bool] = None,
        unsc_status: Optional[bool] = None,
        uapa_status: Optional[bool] = None,
        owner_screening: Optional[dict[str, dict]] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Mutate in place once your screening service returns results.

        owner_screening: optional dict keyed by beneficial owner name,
        e.g. {"Jane Doe": {"is_pep": True, "pep_position": "MP", "sanctions_match": False}}
        """
        if pep_status is not None:
            self.watchlist_checks.pep_status = pep_status
        if unsc_status is not None:
            self.watchlist_checks.unsc_consolidated_list_status = unsc_status
        if uapa_status is not None:
            self.watchlist_checks.uapa_mha_status = uapa_status

        if owner_screening:
            for owner in self.beneficial_owners:
                result = owner_screening.get(owner.name)
                if result:
                    owner.is_pep = result.get("is_pep", owner.is_pep)
                    owner.pep_position = result.get("pep_position", owner.pep_position)
                    owner.sanctions_match = result.get("sanctions_match", owner.sanctions_match)

        self.screening_timestamp = timestamp or datetime.now(timezone.utc)

    def is_screening_complete(self):

        entity_done = all(
            v is not None 
            for v in (self.watchlist_checks.pep_status, self.watchlist_checks.unsc_consolidated_list_status, self.watchlist_checks.uapa_mha_status)
        )

        owners_done = all(
            o.is_pep is not None and o.sanctions_match is not None 
            for o in self.beneficial_owners
        )

        return entity_done and owners_done

    # --- derived features, computed in code, never by the LLM ---
    def has_pep_owner(self) -> bool:
        return any(o.is_pep for o in self.beneficial_owners if o.is_pep)

    def max_ownership_by_pep(self) -> float:
        pcts = [o.ownership_pct or 0 for o in self.beneficial_owners if o.is_pep]
        return max(pcts, default=0.0)

    def any_owner_sanctioned(self) -> bool:
        return any(o.sanctions_match for o in self.beneficial_owners if o.sanctions_match)


def strip_quotes(gemma_op):
    gemma_op.strip()

    if gemma_op.startswith("```"):
        gemma_op = gemma_op.split("\n", 1)[1] if "\n" in gemma_op else gemma_op

    if gemma_op.endswith("```"):
        gemma_op = gemma_op[:-3]

    return gemma_op.strip()


def parse_gemma_op(clean_json):
    
    

if __name__ == "__main__":
    # quick smoke test
    biz = BusinessOnboardingProfile(
        legal_name="Acme Pvt Ltd",
        entity_type="private_limited",
        beneficial_owners=[
            BeneficialOwner(name="Jane Doe", ownership_pct=60, nationality="Indian"),
            BeneficialOwner(name="John Roe", ownership_pct=40, nationality="Indian"),
        ],
    )
    print(biz.model_dump_json(indent=2))
    biz.apply_screening_result(
        pep_status=False,
        unsc_status=False,
        uapa_status=False,
        owner_screening={"Jane Doe": {"is_pep": True, "pep_position": "State MLA", "sanctions_match": False}},
    )
    print("has_pep_owner:", biz.has_pep_owner())
    print("max_ownership_by_pep:", biz.max_ownership_by_pep())
    print("screening_complete:", biz.is_screening_complete())
