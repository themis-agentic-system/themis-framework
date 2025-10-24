"""Jurisdiction-specific cause of action templates for personal injury complaints."""

from __future__ import annotations

from typing import Any

# Jurisdiction-specific PI causes of action
JURISDICTIONS: dict[str, dict[str, Any]] = {
    "California": {
        "code": "CA",
        "causes_of_action": {
            "negligence": {
                "name": "Negligence",
                "statute": "Cal. Civ. Code § 1714",
                "elements": [
                    "Defendant owed a duty of care to Plaintiff",
                    "Defendant breached that duty",
                    "The breach was a substantial factor in causing Plaintiff's harm",
                    "Plaintiff suffered actual damages",
                ],
                "jury_instructions": ["CACI 400", "CACI 401"],
            },
            "motor_vehicle": {
                "name": "Motor Vehicle Negligence",
                "statute": "Cal. Veh. Code §§ 21703, 22107, 22350",
                "elements": [
                    "Defendant was operating a motor vehicle",
                    "Defendant operated the vehicle negligently",
                    "Defendant's negligence was a substantial factor in causing the collision",
                    "Plaintiff was harmed as a result",
                ],
                "jury_instructions": ["CACI 700", "CACI 703"],
            },
            "premises_liability": {
                "name": "Premises Liability",
                "statute": "Cal. Civ. Code § 1714",
                "elements": [
                    "Defendant owned, leased, occupied, or controlled the property",
                    "Defendant was negligent in the use or maintenance of the property",
                    "Plaintiff was harmed",
                    "Defendant's negligence was a substantial factor in causing Plaintiff's harm",
                ],
                "jury_instructions": ["CACI 1000", "CACI 1003"],
            },
            "medical_malpractice": {
                "name": "Medical Negligence",
                "statute": "Cal. Civ. Code § 1714; Cal. Code Civ. Proc. § 364",
                "elements": [
                    "Defendant was acting within the scope of medical practice",
                    "Defendant was negligent in providing care",
                    "Defendant's negligence was a substantial factor in causing harm",
                    "Plaintiff was harmed",
                ],
                "jury_instructions": ["CACI 500", "CACI 501"],
                "special_requirements": "Certificate of merit required per CCP § 364",
            },
            "product_liability": {
                "name": "Products Liability - Design Defect",
                "statute": "Cal. Civ. Code § 1714; Barker v. Lull Engineering",
                "elements": [
                    "Defendant manufactured, distributed, or sold the product",
                    "The product had a defective design",
                    "The defect existed when the product left Defendant's possession",
                    "Plaintiff was harmed while using the product in a reasonably foreseeable way",
                    "The defect was a substantial factor in causing Plaintiff's harm",
                ],
                "jury_instructions": ["CACI 1200", "CACI 1203"],
            },
            "dog_bite": {
                "name": "Dog Bite - Strict Liability",
                "statute": "Cal. Civ. Code § 3342",
                "elements": [
                    "Defendant owned the dog",
                    "The dog bit Plaintiff",
                    "Plaintiff was in a public place or lawfully in a private place",
                    "Plaintiff was harmed",
                ],
                "jury_instructions": ["CACI 462"],
            },
        },
        "damages": {
            "economic": ["Medical expenses (past and future)", "Lost wages and earning capacity", "Property damage"],
            "non_economic": ["Pain and suffering", "Emotional distress", "Loss of enjoyment of life", "Disfigurement"],
            "punitive_standard": "Clear and convincing evidence of malice, oppression, or fraud (Cal. Civ. Code § 3294)",
        },
        "statutes_of_limitation": {
            "personal_injury": {"period": "2 years", "statute": "Cal. Code Civ. Proc. § 335.1"},
            "medical_malpractice": {"period": "3 years or 1 year from discovery", "statute": "Cal. Code Civ. Proc. § 340.5"},
            "premises_liability": {"period": "2 years", "statute": "Cal. Code Civ. Proc. § 335.1"},
        },
    },
    "New York": {
        "code": "NY",
        "causes_of_action": {
            "negligence": {
                "name": "Negligence",
                "statute": "NY PJI 2:10",
                "elements": [
                    "Defendant owed Plaintiff a duty of reasonable care",
                    "Defendant breached that duty",
                    "Plaintiff sustained injury",
                    "Defendant's breach proximately caused Plaintiff's injury",
                ],
                "jury_instructions": ["NY PJI 2:10"],
            },
            "motor_vehicle": {
                "name": "Motor Vehicle Negligence",
                "statute": "NY Veh. & Traf. Law § 1146",
                "elements": [
                    "Defendant operated a motor vehicle",
                    "Defendant's operation was careless and imprudent",
                    "Plaintiff was injured as a result",
                ],
                "jury_instructions": ["NY PJI 2:70"],
                "special_requirements": "No-fault insurance threshold requirements (NY Ins. Law § 5102)",
            },
            "premises_liability": {
                "name": "Premises Liability",
                "statute": "NY PJI 2:90",
                "elements": [
                    "Defendant owned or controlled the premises",
                    "A dangerous condition existed on the premises",
                    "Defendant knew or should have known of the condition",
                    "Defendant failed to exercise reasonable care to remedy the condition",
                    "Plaintiff was injured as a proximate result",
                ],
                "jury_instructions": ["NY PJI 2:90", "NY PJI 2:91"],
            },
            "medical_malpractice": {
                "name": "Medical Malpractice",
                "statute": "NY CPLR § 214-a",
                "elements": [
                    "Defendant was a licensed medical professional",
                    "Defendant departed from accepted medical standards",
                    "The departure proximately caused injury",
                    "Plaintiff sustained damages",
                ],
                "jury_instructions": ["NY PJI 2:150"],
                "special_requirements": "Certificate of merit required per CPLR § 3012-a",
            },
        },
        "damages": {
            "economic": ["Past and future medical expenses", "Lost earnings", "Loss of earning capacity"],
            "non_economic": ["Pain and suffering", "Loss of enjoyment of life", "Emotional distress"],
            "punitive_standard": "Intentional or reckless conduct (NY CPLR § 8701)",
        },
        "statutes_of_limitation": {
            "personal_injury": {"period": "3 years", "statute": "NY CPLR § 214"},
            "medical_malpractice": {"period": "2.5 years from malpractice or end of continuous treatment", "statute": "NY CPLR § 214-a"},
        },
    },
    "Texas": {
        "code": "TX",
        "causes_of_action": {
            "negligence": {
                "name": "Negligence",
                "statute": "Texas common law",
                "elements": [
                    "Defendant owed a legal duty to Plaintiff",
                    "Defendant breached that duty",
                    "Plaintiff suffered injury",
                    "Defendant's breach proximately caused the injury",
                ],
                "jury_instructions": ["PJC 100.1"],
            },
            "motor_vehicle": {
                "name": "Motor Vehicle Negligence",
                "statute": "Tex. Transp. Code",
                "elements": [
                    "Defendant was operating a motor vehicle",
                    "Defendant was negligent in the operation",
                    "The negligence proximately caused the collision",
                    "Plaintiff was damaged as a result",
                ],
                "jury_instructions": ["PJC 100.5"],
            },
            "premises_liability": {
                "name": "Premises Liability",
                "statute": "Texas common law; Tex. Civ. Prac. & Rem. Code § 75.001",
                "elements": [
                    "Defendant had actual or constructive knowledge of a dangerous condition",
                    "The condition posed an unreasonable risk of harm",
                    "Defendant failed to exercise reasonable care",
                    "Defendant's failure proximately caused Plaintiff's injury",
                ],
                "jury_instructions": ["PJC 120.1"],
            },
            "medical_malpractice": {
                "name": "Health Care Liability",
                "statute": "Tex. Civ. Prac. & Rem. Code § 74.001",
                "elements": [
                    "Defendant was a health care provider",
                    "Defendant's treatment fell below the accepted standard of care",
                    "The breach proximately caused injury",
                    "Plaintiff sustained damages",
                ],
                "jury_instructions": ["PJC 120.10"],
                "special_requirements": "Expert report required within 120 days (Tex. Civ. Prac. & Rem. Code § 74.351)",
            },
        },
        "damages": {
            "economic": ["Medical care expenses", "Lost wages and earning capacity", "Property damage"],
            "non_economic": ["Physical pain", "Mental anguish", "Disfigurement", "Physical impairment"],
            "punitive_standard": "Fraud, malice, or gross negligence (Tex. Civ. Prac. & Rem. Code § 41.003)",
            "caps": "Non-economic damages capped at $250,000 per defendant in medical malpractice (Tex. Civ. Prac. & Rem. Code § 74.301)",
        },
        "statutes_of_limitation": {
            "personal_injury": {"period": "2 years", "statute": "Tex. Civ. Prac. & Rem. Code § 16.003"},
            "medical_malpractice": {"period": "2 years", "statute": "Tex. Civ. Prac. & Rem. Code § 74.251"},
        },
    },
    "Florida": {
        "code": "FL",
        "causes_of_action": {
            "negligence": {
                "name": "Negligence",
                "statute": "Florida Standard Jury Instructions",
                "elements": [
                    "Defendant owed a duty of care to Plaintiff",
                    "Defendant breached that duty",
                    "The breach caused injury to Plaintiff",
                    "Plaintiff suffered damages",
                ],
                "jury_instructions": ["FSI 401.4"],
            },
            "motor_vehicle": {
                "name": "Motor Vehicle Negligence",
                "statute": "Fla. Stat. § 316.130",
                "elements": [
                    "Defendant was operating a motor vehicle",
                    "Defendant was negligent in operation",
                    "The negligence caused the accident",
                    "Plaintiff was injured",
                ],
                "jury_instructions": ["FSI 401.10"],
                "special_requirements": "PIP threshold requirements (Fla. Stat. § 627.737)",
            },
            "premises_liability": {
                "name": "Premises Liability",
                "statute": "Fla. Stat. § 768.0755",
                "elements": [
                    "Defendant owned, operated, or controlled the premises",
                    "Defendant owed a duty of care to Plaintiff",
                    "Defendant breached that duty",
                    "The breach caused Plaintiff's injury",
                ],
                "jury_instructions": ["FSI 401.16"],
            },
            "medical_malpractice": {
                "name": "Medical Negligence",
                "statute": "Fla. Stat. § 766.102",
                "elements": [
                    "Defendant was a health care provider",
                    "Defendant breached the prevailing professional standard of care",
                    "The breach resulted in injury to Plaintiff",
                    "Plaintiff suffered damages",
                ],
                "jury_instructions": ["FSI 401.23"],
                "special_requirements": "Pre-suit investigation and notice (Fla. Stat. § 766.106)",
            },
        },
        "damages": {
            "economic": ["Past and future medical expenses", "Lost wages and earning capacity", "Property damage"],
            "non_economic": ["Pain and suffering", "Mental anguish", "Loss of enjoyment of life", "Inconvenience"],
            "punitive_standard": "Intentional misconduct or gross negligence (Fla. Stat. § 768.72)",
        },
        "statutes_of_limitation": {
            "personal_injury": {"period": "4 years", "statute": "Fla. Stat. § 95.11(3)(a)"},
            "medical_malpractice": {"period": "2 years", "statute": "Fla. Stat. § 95.11(4)(b)"},
        },
    },
    "Illinois": {
        "code": "IL",
        "causes_of_action": {
            "negligence": {
                "name": "Negligence",
                "statute": "Illinois common law",
                "elements": [
                    "Defendant owed a duty of care to Plaintiff",
                    "Defendant breached that duty",
                    "Plaintiff suffered injury",
                    "The breach proximately caused the injury",
                ],
                "jury_instructions": ["IPI 10.01"],
            },
            "motor_vehicle": {
                "name": "Motor Vehicle Negligence",
                "statute": "625 ILCS 5/",
                "elements": [
                    "Defendant operated a motor vehicle",
                    "Defendant was negligent",
                    "Plaintiff was injured",
                    "Defendant's negligence proximately caused the injury",
                ],
                "jury_instructions": ["IPI 10.02"],
            },
            "premises_liability": {
                "name": "Premises Liability",
                "statute": "740 ILCS 130/",
                "elements": [
                    "Defendant was the owner or occupier of land",
                    "Defendant knew or should have known of an unreasonable risk of harm",
                    "Defendant should have expected that invitees would not discover the danger",
                    "Defendant failed to exercise reasonable care",
                    "Plaintiff was injured as a proximate result",
                ],
                "jury_instructions": ["IPI 120.01"],
            },
            "medical_malpractice": {
                "name": "Medical Malpractice",
                "statute": "735 ILCS 5/2-622",
                "elements": [
                    "Defendant was a health care professional",
                    "Defendant deviated from the standard of care",
                    "The deviation proximately caused injury",
                    "Plaintiff sustained damages",
                ],
                "jury_instructions": ["IPI 105.01"],
                "special_requirements": "Certificate of merit required (735 ILCS 5/2-622)",
            },
        },
        "damages": {
            "economic": ["Medical expenses", "Lost income", "Loss of earning capacity"],
            "non_economic": ["Pain and suffering", "Disability", "Disfigurement", "Loss of normal life"],
            "punitive_standard": "Evil motive or reckless indifference (735 ILCS 5/2-1115.05)",
        },
        "statutes_of_limitation": {
            "personal_injury": {"period": "2 years", "statute": "735 ILCS 5/13-202"},
            "medical_malpractice": {"period": "2 years", "statute": "735 ILCS 5/13-212"},
        },
    },
}


def get_jurisdiction(jurisdiction_name: str) -> dict[str, Any] | None:
    """Retrieve jurisdiction configuration by name."""
    return JURISDICTIONS.get(jurisdiction_name)


def get_cause_of_action(jurisdiction_name: str, cause_type: str) -> dict[str, Any] | None:
    """Retrieve a specific cause of action for a jurisdiction."""
    jurisdiction = get_jurisdiction(jurisdiction_name)
    if not jurisdiction:
        return None
    return jurisdiction.get("causes_of_action", {}).get(cause_type)


def infer_cause_of_action(matter: dict[str, Any], jurisdiction_name: str) -> str:
    """Infer the most appropriate cause of action based on matter details."""
    jurisdiction = get_jurisdiction(jurisdiction_name)
    if not jurisdiction:
        return "negligence"  # Default fallback

    # Check matter summary/description for keywords
    summary = (matter.get("summary") or matter.get("description") or "").lower()

    if any(keyword in summary for keyword in ["vehicle", "car", "truck", "collision", "rear-end", "traffic"]):
        return "motor_vehicle"
    elif any(keyword in summary for keyword in ["slip", "fall", "premises", "store", "property"]):
        return "premises_liability"
    elif any(keyword in summary for keyword in ["doctor", "medical", "hospital", "surgeon", "malpractice"]):
        return "medical_malpractice"
    elif any(keyword in summary for keyword in ["product", "defect", "manufacturing"]):
        return "product_liability"
    elif any(keyword in summary for keyword in ["dog", "bite", "animal"]):
        return "dog_bite"

    # Default to general negligence
    return "negligence"


def get_available_jurisdictions() -> list[str]:
    """Return list of supported jurisdiction names."""
    return list(JURISDICTIONS.keys())
