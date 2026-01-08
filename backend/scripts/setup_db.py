#!/usr/bin/env python3
import asyncio
import subprocess
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.base import Base
from app.db.session import engine, async_session_maker as async_session
from app.models import User, Task, Subtask


def run_migrations():
    print("Running database migrations...")
    backend_dir = Path(__file__).parent.parent
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=backend_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Migration failed: {result.stderr}")
        sys.exit(1)
    print(result.stdout)
    print("Migrations completed successfully!")


async def seed_data():
    print("Seeding sample data...")
    
    async with async_session() as session:
        existing = await session.execute(text("SELECT COUNT(*) FROM users"))
        if existing.scalar() > 0:
            print("Data already exists, skipping seed.")
            return
        
        admin = User(
            wallet_address="0xAdmin0000000000000000000000000000000001",
            name="Admin User",
            country="NG",
            is_admin=True,
            skills=["management", "review"],
            bio="Platform administrator",
            reputation_score=1000,
            reputation_tier="expert",
        )
        
        client1 = User(
            wallet_address="0xClient000000000000000000000000000000001",
            name="Research Lab Inc",
            country="US",
            skills=["research", "funding"],
            bio="Research institution seeking data collection services",
            reputation_score=500,
            reputation_tier="established",
        )
        
        worker1 = User(
            wallet_address="0xWorker000000000000000000000000000000001",
            name="Adaeze Okonkwo",
            country="NG",
            id_verified=True,
            id_verified_at=datetime.utcnow(),
            skills=["data-collection", "surveys", "local-knowledge"],
            bio="Experienced field researcher based in Lagos",
            reputation_score=250,
            reputation_tier="active",
            tasks_completed=12,
            tasks_approved=11,
        )
        
        worker2 = User(
            wallet_address="0xWorker000000000000000000000000000000002",
            name="Emeka Nnamdi",
            country="NG",
            id_verified=True,
            id_verified_at=datetime.utcnow(),
            skills=["photography", "documentation", "mapping"],
            bio="Visual documentation specialist in Abuja",
            reputation_score=180,
            reputation_tier="active",
            tasks_completed=8,
            tasks_approved=8,
        )
        
        worker3 = User(
            wallet_address="0xWorker000000000000000000000000000000003",
            name="Fatima Yusuf",
            country="NG",
            skills=["translation", "interviews", "hausa"],
            bio="Multilingual researcher fluent in Hausa, Yoruba, and English",
            reputation_score=50,
            reputation_tier="new",
            tasks_completed=2,
            tasks_approved=2,
        )
        
        session.add_all([admin, client1, worker1, worker2, worker3])
        await session.flush()
        
        task1 = Task(
            title="Lagos Market Price Survey Q1 2025",
            description="Comprehensive survey of commodity prices across 15 major markets in Lagos State. Data will be used for economic research on inflation patterns in urban Nigeria.",
            description_html="<p>Comprehensive survey of commodity prices across <strong>15 major markets</strong> in Lagos State.</p><p>Data will be used for economic research on inflation patterns in urban Nigeria.</p>",
            research_question="How do commodity prices vary across different markets in Lagos, and what factors influence price disparities?",
            background_context="This research is part of a larger study on economic resilience in West African urban centers. Previous studies have shown significant price variations between markets, but the factors driving these differences remain poorly understood.",
            methodology_notes="Use standardized price collection forms. Visit markets at similar times (morning) for consistency. Record both wholesale and retail prices where available.",
            expected_outcomes=["Dataset of 750+ price points across 15 markets", "Analysis of price variation patterns", "Identification of key pricing factors"],
            references=[
                {"id": "ref-1", "type": "paper", "title": "Urban Market Dynamics in Nigeria", "url": "https://example.com/paper1", "required": False},
                {"id": "ref-2", "type": "dataset", "title": "Previous Lagos Price Survey 2023", "url": "https://example.com/data", "required": True},
            ],
            client_id=client1.id,
            status="in_progress",
            total_budget_cngn=Decimal("150000.00"),
            skills_required=["data-collection", "surveys", "local-knowledge"],
            deadline=datetime.utcnow() + timedelta(days=30),
            funded_at=datetime.utcnow() - timedelta(days=5),
        )
        
        task2 = Task(
            title="Rural Healthcare Access Mapping - Kano State",
            description="Map and document healthcare facilities in rural Kano State, including distance to nearest facilities, services offered, and accessibility challenges.",
            research_question="What is the current state of healthcare accessibility in rural Kano State?",
            client_id=client1.id,
            status="funded",
            total_budget_cngn=Decimal("200000.00"),
            skills_required=["mapping", "photography", "documentation", "hausa"],
            deadline=datetime.utcnow() + timedelta(days=45),
            funded_at=datetime.utcnow() - timedelta(days=2),
        )
        
        task3 = Task(
            title="Agricultural Supply Chain Documentation - Oyo State",
            description="Document the journey of agricultural products from farm to market in Oyo State, identifying key stakeholders and bottlenecks.",
            research_question="How do agricultural products move from farms to consumers in Oyo State, and where are the inefficiencies?",
            client_id=client1.id,
            status="draft",
            total_budget_cngn=Decimal("100000.00"),
            skills_required=["interviews", "photography", "documentation"],
            deadline=datetime.utcnow() + timedelta(days=60),
        )
        
        session.add_all([task1, task2, task3])
        await session.flush()
        
        subtasks_task1 = [
            Subtask(
                task_id=task1.id,
                title="Market Identification & Mapping",
                description="Identify and map 15 major markets in Lagos State with GPS coordinates and basic information",
                description_html="<p>Identify and map <strong>15 major markets</strong> in Lagos State with GPS coordinates and basic information.</p>",
                subtask_type="discovery",
                sequence_order=1,
                budget_allocation_percent=Decimal("15.00"),
                budget_cngn=Decimal("22500.00"),
                status="approved",
                claimed_by=worker1.id,
                claimed_at=datetime.utcnow() - timedelta(days=4),
                approved_at=datetime.utcnow() - timedelta(days=2),
                acceptance_criteria=[
                    "All 15 markets have been identified with names and addresses",
                    "GPS coordinates are accurate to within 10 meters",
                    "Each market has photos of main entrance and interior",
                    "Operating hours documented for each market",
                ],
                deliverables=[
                    {"id": "d1", "title": "Market List CSV", "description": "List of all markets with coordinates", "type": "dataset", "required": True, "format_hint": "CSV"},
                    {"id": "d2", "title": "Market Photos", "description": "At least 3 photos per market", "type": "file", "required": True, "format_hint": "JPEG"},
                ],
                estimated_hours=Decimal("8.00"),
                tools_required=["GPS-enabled smartphone", "Camera"],
            ),
            Subtask(
                task_id=task1.id,
                title="Price Data Collection - Week 1",
                description="Collect prices for 50 commodity items across all 15 markets",
                description_html="<p>Collect prices for <strong>50 commodity items</strong> across all 15 markets using the standardized price collection form.</p>",
                subtask_type="extraction",
                sequence_order=2,
                budget_allocation_percent=Decimal("25.00"),
                budget_cngn=Decimal("37500.00"),
                status="in_progress",
                claimed_by=worker1.id,
                claimed_at=datetime.utcnow() - timedelta(days=2),
                acceptance_criteria=[
                    "Prices collected for all 50 items in at least 12 of 15 markets",
                    "Both retail and wholesale prices recorded where available",
                    "Unit of measurement clearly documented",
                    "Date and time of collection recorded",
                ],
                deliverables=[
                    {"id": "d1", "title": "Week 1 Price Dataset", "description": "Complete price data for week 1", "type": "dataset", "required": True, "format_hint": "CSV"},
                    {"id": "d2", "title": "Collection Notes", "description": "Any observations or anomalies noted", "type": "text", "required": False, "format_hint": "Markdown"},
                ],
                references=[
                    {"id": "ref-1", "type": "document", "title": "Price Collection Form Template", "url": "https://example.com/form", "required": True},
                    {"id": "ref-2", "type": "document", "title": "Commodity List with Descriptions", "url": "https://example.com/commodities", "required": True},
                ],
                estimated_hours=Decimal("20.00"),
                tools_required=["Smartphone", "Price collection app"],
                example_output="Market: Balogun | Item: Rice (50kg) | Retail: ₦45,000 | Wholesale: ₦42,000 | Date: 2025-01-15 09:30",
            ),
            Subtask(
                task_id=task1.id,
                title="Price Data Collection - Week 2",
                description="Second round of price collection for trend analysis",
                subtask_type="extraction",
                sequence_order=3,
                budget_allocation_percent=Decimal("25.00"),
                budget_cngn=Decimal("37500.00"),
                status="open",
                acceptance_criteria=[
                    "Prices collected for same 50 items as Week 1",
                    "Same markets visited as Week 1",
                    "Collection done at similar times as Week 1",
                ],
                deliverables=[
                    {"id": "d1", "title": "Week 2 Price Dataset", "description": "Complete price data for week 2", "type": "dataset", "required": True, "format_hint": "CSV"},
                ],
                estimated_hours=Decimal("20.00"),
            ),
            Subtask(
                task_id=task1.id,
                title="Vendor Interviews",
                description="Conduct structured interviews with 30 vendors about pricing factors",
                description_html="<p>Conduct <strong>structured interviews</strong> with 30 vendors to understand factors affecting pricing decisions.</p>",
                subtask_type="extraction",
                sequence_order=4,
                budget_allocation_percent=Decimal("20.00"),
                budget_cngn=Decimal("30000.00"),
                status="open",
                acceptance_criteria=[
                    "At least 30 vendors interviewed",
                    "Vendors from at least 10 different markets",
                    "Mix of commodity types represented",
                    "Audio recordings or detailed notes for each interview",
                ],
                deliverables=[
                    {"id": "d1", "title": "Interview Transcripts", "description": "Transcribed or summarized interviews", "type": "text", "required": True, "format_hint": "Markdown"},
                    {"id": "d2", "title": "Vendor Demographics", "description": "Basic info about interviewed vendors", "type": "dataset", "required": True, "format_hint": "CSV"},
                ],
                references=[
                    {"id": "ref-1", "type": "document", "title": "Interview Question Guide", "url": "https://example.com/interview-guide", "required": True},
                ],
                estimated_hours=Decimal("15.00"),
                tools_required=["Voice recorder or smartphone", "Interview guide printout"],
            ),
            Subtask(
                task_id=task1.id,
                title="Data Compilation & Report",
                description="Compile all data and prepare final research report with analysis",
                subtask_type="assembly",
                sequence_order=5,
                budget_allocation_percent=Decimal("15.00"),
                budget_cngn=Decimal("22500.00"),
                status="open",
                acceptance_criteria=[
                    "All datasets merged and cleaned",
                    "Statistical analysis of price variations completed",
                    "Key findings clearly summarized",
                    "Report follows provided template",
                ],
                deliverables=[
                    {"id": "d1", "title": "Final Dataset", "description": "Merged and cleaned dataset", "type": "dataset", "required": True, "format_hint": "CSV"},
                    {"id": "d2", "title": "Analysis Report", "description": "Final research report with findings", "type": "text", "required": True, "format_hint": "PDF"},
                    {"id": "d3", "title": "Visualizations", "description": "Charts and graphs of key findings", "type": "file", "required": True, "format_hint": "PNG"},
                ],
                estimated_hours=Decimal("12.00"),
                tools_required=["Spreadsheet software", "Data visualization tool"],
            ),
        ]
        
        subtasks_task2 = [
            Subtask(
                task_id=task2.id,
                title="LGA Selection & Planning",
                description="Select 5 Local Government Areas for study and plan logistics",
                subtask_type="discovery",
                sequence_order=1,
                budget_allocation_percent=Decimal("10.00"),
                budget_cngn=Decimal("20000.00"),
                status="open",
            ),
            Subtask(
                task_id=task2.id,
                title="Healthcare Facility Survey - LGA 1",
                description="Visit and document all healthcare facilities in first LGA",
                subtask_type="extraction",
                sequence_order=2,
                budget_allocation_percent=Decimal("18.00"),
                budget_cngn=Decimal("36000.00"),
                status="open",
            ),
            Subtask(
                task_id=task2.id,
                title="Healthcare Facility Survey - LGA 2",
                description="Visit and document all healthcare facilities in second LGA",
                subtask_type="extraction",
                sequence_order=3,
                budget_allocation_percent=Decimal("18.00"),
                budget_cngn=Decimal("36000.00"),
                status="open",
            ),
            Subtask(
                task_id=task2.id,
                title="Community Interviews",
                description="Interview community members about healthcare access challenges",
                subtask_type="extraction",
                sequence_order=4,
                budget_allocation_percent=Decimal("20.00"),
                budget_cngn=Decimal("40000.00"),
                status="open",
            ),
            Subtask(
                task_id=task2.id,
                title="Map Generation & Visualization",
                description="Create visual maps showing facility locations and coverage",
                subtask_type="mapping",
                sequence_order=5,
                budget_allocation_percent=Decimal("15.00"),
                budget_cngn=Decimal("30000.00"),
                status="open",
            ),
            Subtask(
                task_id=task2.id,
                title="Final Report Assembly",
                description="Compile findings into comprehensive report",
                subtask_type="assembly",
                sequence_order=6,
                budget_allocation_percent=Decimal("19.00"),
                budget_cngn=Decimal("38000.00"),
                status="open",
            ),
        ]
        
        session.add_all(subtasks_task1 + subtasks_task2)
        await session.commit()
        
    print("Sample data seeded successfully!")
    print("\nCreated:")
    print("  - 5 users (1 admin, 1 client, 3 workers)")
    print("  - 3 tasks (1 in_progress, 1 funded, 1 draft)")
    print("  - 11 subtasks")


async def main():
    run_migrations()
    await seed_data()
    await engine.dispose()
    print("\nDatabase setup complete!")


if __name__ == "__main__":
    asyncio.run(main())
