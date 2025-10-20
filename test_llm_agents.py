#!/usr/bin/env python3
"""Test script to demonstrate LLM-powered legal agents in action."""

import asyncio
import json
import os
from dotenv import load_dotenv

from orchestrator.service import OrchestratorService


async def main():
    """Run a simple test of the legal agent system."""

    # Load environment variables
    load_dotenv()

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set in .env file")
        print("Please edit .env and add your Anthropic API key")
        print("Get one from: https://console.anthropic.com/")
        return

    if os.getenv("ANTHROPIC_API_KEY") == "your_api_key_here":
        print("ERROR: Please replace 'your_api_key_here' with your actual Anthropic API key in .env")
        return

    print("=" * 80)
    print("THEMIS LEGAL AGENT SYSTEM - LLM-POWERED DEMO")
    print("=" * 80)
    print()

    # Create a sample legal matter
    matter = {
        "summary": "Personal injury case involving a slip and fall at a grocery store",
        "description": "Client Jane Doe slipped on a wet floor at SuperMart grocery store on 2024-01-15. "
                      "She suffered a broken wrist and seeks compensation for medical bills and lost wages.",
        "parties": ["Jane Doe (Plaintiff)", "SuperMart Inc. (Defendant)"],
        "documents": [
            {
                "title": "Incident Report",
                "content": "On January 15, 2024, at approximately 2:30 PM, customer Jane Doe "
                          "slipped on a wet floor in aisle 5 near the produce section. "
                          "Store employee John Smith witnessed the incident. "
                          "No wet floor sign was present at the time. "
                          "Paramedics were called and transported Ms. Doe to General Hospital. "
                          "Security camera footage shows the floor had been wet for at least 15 minutes "
                          "before the incident.",
                "date": "2024-01-15",
            },
            {
                "title": "Medical Records",
                "content": "Patient: Jane Doe. Date: 2024-01-15. "
                          "Diagnosis: Fractured right wrist (distal radius fracture). "
                          "Treatment: Closed reduction and casting. "
                          "Follow-up required. Patient reports severe pain (8/10). "
                          "Prescribed pain medication and referred to orthopedic specialist. "
                          "Unable to work for estimated 6-8 weeks. "
                          "Total medical costs to date: $4,500.",
                "date": "2024-01-15",
            },
        ],
        "events": [
            {
                "date": "2024-01-15",
                "description": "Slip and fall incident occurred at SuperMart",
            },
            {
                "date": "2024-01-15",
                "description": "Emergency room treatment and diagnosis",
            },
            {
                "date": "2024-01-20",
                "description": "Follow-up with orthopedic specialist",
            },
        ],
        "goals": {
            "settlement": "Seeking $50,000 settlement covering medical expenses, lost wages, and pain/suffering",
            "remedy": "Full compensation for injuries sustained",
            "fallback": "Minimum $25,000 to cover documented medical expenses and lost wages",
        },
    }

    print("SAMPLE MATTER:")
    print(f"  Summary: {matter['summary']}")
    print(f"  Parties: {', '.join(matter['parties'])}")
    print(f"  Documents: {len(matter['documents'])} documents")
    print(f"  Events: {len(matter['events'])} events")
    print()
    print("-" * 80)

    # Create orchestrator
    orchestrator = OrchestratorService()

    # Step 1: Create a plan
    print("\nSTEP 1: Creating execution plan...")
    plan = await orchestrator.plan(matter)
    print(f"  Plan ID: {plan['plan_id']}")
    print(f"  Steps: {len(plan['steps'])}")
    for i, step in enumerate(plan['steps'], 1):
        print(f"    {i}. {step['agent']}: {step['description']}")
    print()

    # Step 2: Execute the plan
    print("\nSTEP 2: Executing agents (this will call the LLM - may take 30-60 seconds)...")
    print()

    execution = await orchestrator.execute(plan["plan_id"], matter)

    print("\nExecution complete!")
    print(f"  Status: {execution.get('status', 'unknown')}")
    print()
    print("=" * 80)

    # Step 3: Display results
    artifacts = await orchestrator.get_artifacts(plan["plan_id"])

    print("\nRESULTS:")
    print("=" * 80)

    # LDA Results (Facts)
    print("\n1. LEGAL DATA ANALYST (LDA) - FACT EXTRACTION")
    print("-" * 80)
    if "lda" in artifacts:
        lda_result = artifacts["lda"]
        facts = lda_result.get("facts", {})

        print("\nFact Pattern Summary:")
        for fact in facts.get("fact_pattern_summary", [])[:5]:
            print(f"  • {fact}")

        print(f"\nTimeline ({len(facts.get('timeline', []))} events):")
        for event in facts.get("timeline", [])[:5]:
            print(f"  {event.get('date', 'N/A')}: {event.get('description', 'N/A')}")

        print(f"\nParties: {', '.join(facts.get('parties', []))}")

        if lda_result.get("unresolved_issues"):
            print("\nUnresolved Issues:")
            for issue in lda_result["unresolved_issues"]:
                print(f"  ⚠ {issue}")

    # DEA Results (Legal Analysis)
    print("\n\n2. DOCTRINAL EVALUATION AGENT (DEA) - LEGAL ANALYSIS")
    print("-" * 80)
    if "dea" in artifacts:
        dea_result = artifacts["dea"]
        legal_analysis = dea_result.get("legal_analysis", {})

        print("\nLegal Issues Identified:")
        for i, issue in enumerate(legal_analysis.get("issues", []), 1):
            print(f"\n  Issue #{i}: {issue.get('issue', 'N/A')}")
            print(f"    Area of Law: {issue.get('area_of_law', 'N/A')}")
            print(f"    Strength: {issue.get('strength', 'N/A')}")
            if issue.get("facts"):
                print(f"    Supporting Facts:")
                for fact in issue['facts'][:3]:
                    print(f"      - {fact}")

        print("\n\nLegal Analysis:")
        print(legal_analysis.get("analysis", "No analysis available")[:1000])

        if dea_result.get("unresolved_issues"):
            print("\n\nUnresolved Issues:")
            for issue in dea_result["unresolved_issues"]:
                print(f"  ⚠ {issue}")

    # LSA Results (Strategy)
    print("\n\n3. LEGAL STRATEGY AGENT (LSA) - STRATEGY & RISK")
    print("-" * 80)
    if "lsa" in artifacts:
        lsa_result = artifacts["lsa"]
        strategy = lsa_result.get("strategy", {})

        print(f"\nObjectives:")
        print(f"  {strategy.get('recommended_actions', [{}])[0] if strategy.get('recommended_actions') else 'N/A'}")

        print(f"\nRecommended Actions:")
        for i, action in enumerate(strategy.get("recommended_actions", [])[:5], 1):
            print(f"  {i}. {action}")

        print(f"\nNegotiation Positions:")
        positions = strategy.get("negotiation_positions", {})
        if positions:
            for key, value in positions.items():
                print(f"  {key.title()}: {value}")

        risk = strategy.get("risk_assessment", {})
        if risk:
            print(f"\nRisk Assessment:")
            print(f"  Confidence Score: {risk.get('confidence', 'N/A')}/100")

            if risk.get("weaknesses"):
                print(f"  Weaknesses:")
                for weakness in risk["weaknesses"][:3]:
                    print(f"    • {weakness}")

            if risk.get("evidentiary_gaps"):
                print(f"  Evidentiary Gaps:")
                for gap in risk["evidentiary_gaps"][:3]:
                    print(f"    • {gap}")

    print("\n" + "=" * 80)
    print("DEMO COMPLETE!")
    print("=" * 80)
    print()
    print("What just happened:")
    print("  1. LDA agent used Claude AI to extract facts from documents")
    print("  2. DEA agent used Claude AI to identify legal issues and analyze the case")
    print("  3. LSA agent used Claude AI to create a strategic plan and risk assessment")
    print()
    print("Next steps:")
    print("  - Add your own legal matters to test different scenarios")
    print("  - Integrate with a legal database for case law citations")
    print("  - Add PDF document upload functionality")
    print("  - Implement RAG for better legal research")
    print()


if __name__ == "__main__":
    asyncio.run(main())
