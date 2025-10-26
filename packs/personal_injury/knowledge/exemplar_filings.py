"""Exemplar filings and authorities."""

from __future__ import annotations

from packs.personal_injury.llm_support import run_structured_prompt

EXEMPLAR_COMPLAINTS: dict[str, str] = {
    "california": "Doe v. DeliveryCo, Los Angeles Superior Court, No. 21STCV12345",
    "texas": "Smith v. BigBox LLC, Harris County District Court, No. 2021-54321",
}

KEY_AUTHORITIES: dict[str, list[str]] = {
    "california": [
        "Li v. Yellow Cab Co. (1975) 13 Cal.3d 804",
        "Rowland v. Christian (1968) 69 Cal.2d 108",
    ],
    "new york": [
        "Palsgraf v. Long Island R.R. Co., 248 N.Y. 339 (1928)",
        "Toure v. Avis Rent A Car Sys., 98 N.Y.2d 345 (2002)",
    ],
    "texas": [
        "Nabors Well Servs., Ltd. v. Romero, 456 S.W.3d 553 (Tex. 2015)",
        "Jefferson Assocs. Corp. v. Boyd, 452 S.W.2d 160 (Tex. 1970)",
    ],
}

_CAPTION_PROMPT = """You provide exemplar case captions for personal injury matters."""
_AUTHORITY_PROMPT = (
    "You list leading personal injury negligence authorities for the requested jurisdiction."
)

DEFAULT_CAPTION = "[Jurisdiction] Superior Court Personal Injury Complaint"
DEFAULT_AUTHORITIES = [
    "Restatement (Second) of Torts § 281",
    "Prosser & Keeton on Torts § 30",
]


def exemplar_complaint_captions(jurisdiction: str) -> str | None:
    key = _normalize_key(jurisdiction)
    if key is None:
        return DEFAULT_CAPTION.replace("[Jurisdiction]", "").strip()
    if key in EXEMPLAR_COMPLAINTS:
        return EXEMPLAR_COMPLAINTS[key]

    payload = run_structured_prompt(
        system_prompt=_CAPTION_PROMPT,
        user_prompt=f"Jurisdiction: {jurisdiction}",
        response_format={"caption": ""},
    )
    caption = payload.get("caption") if isinstance(payload, dict) else None
    normalized = caption.strip() if isinstance(caption, str) else ""
    template = DEFAULT_CAPTION.replace("[Jurisdiction]", jurisdiction.strip() or "")
    result = (normalized or template).strip()
    EXEMPLAR_COMPLAINTS[key] = result
    return result


def key_authorities(jurisdiction: str) -> list[str]:
    key = _normalize_key(jurisdiction)
    if key is None:
        return list(DEFAULT_AUTHORITIES)
    if key in KEY_AUTHORITIES:
        return KEY_AUTHORITIES[key]

    payload = run_structured_prompt(
        system_prompt=_AUTHORITY_PROMPT,
        user_prompt=f"Jurisdiction: {jurisdiction}",
        response_format={"authorities": []},
    )
    values = []
    if isinstance(payload, dict):
        items = payload.get("authorities")
        if isinstance(items, list):
            values = [str(item).strip() for item in items if str(item).strip()]
    if not values:
        values = [
            DEFAULT_AUTHORITIES[0],
            DEFAULT_AUTHORITIES[1],
        ]
    KEY_AUTHORITIES[key] = values
    return values


def _normalize_key(jurisdiction: str | None) -> str | None:
    if jurisdiction is None:
        return None
    cleaned = jurisdiction.strip().lower()
    return cleaned or None
