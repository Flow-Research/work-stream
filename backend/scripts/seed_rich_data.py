#!/usr/bin/env python3
"""Seed rich demo data for Flow platform."""
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.session import async_session_maker as async_session
from app.models import User, Task, Subtask
from app.models.submission import Submission
from app.models.dispute import Dispute
from app.models.skill import Skill, SkillCategory


def slugify(name: str) -> str:
    """Convert a name to a slug."""
    return name.lower().replace(" ", "-").replace("&", "and")


def tz_now() -> datetime:
    """Return current time as timezone-aware UTC."""
    return datetime.now(timezone.utc)


def naive_now() -> datetime:
    """Return current time as naive UTC (for columns without timezone)."""
    return datetime.utcnow()


def to_naive(dt: datetime) -> datetime:
    """Convert timezone-aware datetime to naive UTC datetime."""
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


async def clear_data():
    """Clear existing data."""
    print("Clearing existing data...")
    async with async_session() as session:
        await session.execute(text("DELETE FROM disputes"))
        await session.execute(text("DELETE FROM submissions"))
        await session.execute(text("DELETE FROM subtasks"))
        await session.execute(text("DELETE FROM tasks"))
        await session.execute(text("DELETE FROM skills"))
        await session.execute(text("DELETE FROM skill_categories"))
        await session.execute(text("DELETE FROM users"))
        await session.commit()
    print("Data cleared!")


async def seed_skills():
    """Seed skill categories and skills."""
    print("Seeding skills...")
    async with async_session() as session:
        categories = [
            SkillCategory(name="Research", description="Research and analysis skills", icon="🔬"),
            SkillCategory(name="Data", description="Data collection and processing", icon="📊"),
            SkillCategory(name="Writing", description="Writing and documentation", icon="✍️"),
            SkillCategory(name="Technical", description="Technical and coding skills", icon="💻"),
            SkillCategory(name="Languages", description="Language proficiency", icon="🌍"),
        ]
        session.add_all(categories)
        await session.flush()

        skills_data = [
            # Research
            (categories[0].id, "Literature Review", "Systematic literature search and review"),
            (categories[0].id, "Data Analysis", "Statistical and qualitative data analysis"),
            (categories[0].id, "Survey Design", "Creating and validating surveys"),
            (categories[0].id, "Interviews", "Conducting structured interviews"),
            # Data
            (categories[1].id, "Data Collection", "Field data collection"),
            (categories[1].id, "Data Entry", "Accurate data entry and validation"),
            (categories[1].id, "Data Cleaning", "Data preprocessing and cleaning"),
            (categories[1].id, "Web Scraping", "Automated data extraction"),
            # Writing
            (categories[2].id, "Technical Writing", "Technical documentation"),
            (categories[2].id, "Report Writing", "Research report writing"),
            (categories[2].id, "Editing", "Proofreading and editing"),
            (categories[2].id, "Translation", "Document translation"),
            # Technical
            (categories[3].id, "Python", "Python programming"),
            (categories[3].id, "Data Visualization", "Charts and graphs"),
            (categories[3].id, "GIS Mapping", "Geographic information systems"),
            (categories[3].id, "Machine Learning", "ML model development"),
            # Languages
            (categories[4].id, "English", "English fluency"),
            (categories[4].id, "Hausa", "Hausa fluency"),
            (categories[4].id, "Yoruba", "Yoruba fluency"),
            (categories[4].id, "French", "French fluency"),
        ]

        skills = [Skill(category_id=cat_id, name=name, slug=slugify(name), description=desc) for cat_id, name, desc in skills_data]
        session.add_all(skills)
        await session.commit()
    print(f"  Created {len(categories)} categories and {len(skills)} skills")


async def seed_users():
    """Seed users with varied profiles."""
    print("Seeding users...")
    users = []

    # Admin
    users.append(User(
        wallet_address="0xAdmin0000000000000000000000000000000001",
        name="Dr. Amara Chen",
        country="NG",
        is_admin=True,
        skills=["management", "review", "research"],
        bio="Platform administrator and research director",
        reputation_score=5000,
        reputation_tier="expert",
    ))

    # Clients / Task Owners
    users.append(User(
        wallet_address="0xClient000000000000000000000000000000001",
        name="Lagos Research Institute",
        country="NG",
        skills=["funding", "research"],
        bio="Leading research institution focused on West African economic studies",
        reputation_score=2500,
        reputation_tier="established",
    ))

    users.append(User(
        wallet_address="0xClient000000000000000000000000000000002",
        name="HealthTech Africa",
        country="KE",
        skills=["healthcare", "technology"],
        bio="Healthcare technology company improving access across Africa",
        reputation_score=1800,
        reputation_tier="established",
    ))

    # Workers with various reputation levels
    workers_data = [
        ("0xWorker000000000000000000000000000000001", "Kofi Mensah", "GH", True,
         ["data-collection", "surveys", "local-knowledge"], "Senior field researcher with 5 years experience",
         850, "expert", 45, 43),
        ("0xWorker000000000000000000000000000000002", "Fatima Al-Hassan", "NG", True,
         ["technical-writing", "translation", "hausa"], "Technical writer and translator",
         620, "established", 32, 30),
        ("0xWorker000000000000000000000000000000003", "Yuki Tanaka", "JP", True,
         ["data-visualization", "python", "machine-learning"], "Data scientist specializing in visualization",
         480, "established", 28, 27),
        ("0xWorker000000000000000000000000000000004", "Adaeze Okonkwo", "NG", True,
         ["interviews", "surveys", "yoruba"], "Experienced interviewer and survey specialist",
         320, "active", 18, 17),
        ("0xWorker000000000000000000000000000000005", "Emeka Nnamdi", "NG", True,
         ["photography", "gis-mapping", "documentation"], "Visual documentation and mapping expert",
         280, "active", 15, 14),
        ("0xWorker000000000000000000000000000000006", "Chiamaka Eze", "NG", False,
         ["data-entry", "data-cleaning"], "Data entry specialist",
         150, "active", 8, 8),
        ("0xWorker000000000000000000000000000000007", "Ibrahim Musa", "NG", False,
         ["surveys", "hausa", "interviews"], "New contributor from Kano",
         45, "new", 2, 2),
        ("0xWorker000000000000000000000000000000008", "Grace Obi", "NG", False,
         ["literature-review", "report-writing"], "Graduate researcher",
         30, "new", 1, 1),
        ("0xWorker000000000000000000000000000000009", "Tunde Adeyemi", "NG", False,
         ["web-scraping", "python"], "Just joined the platform",
         0, "new", 0, 0),
        ("0xWorker000000000000000000000000000000010", "Blessing Okoro", "NG", False,
         ["editing", "translation"], "Freelance editor",
         0, "new", 0, 0),
    ]

    for wallet, name, country, verified, skills, bio, rep, tier, completed, approved in workers_data:
        users.append(User(
            wallet_address=wallet,
            name=name,
            country=country,
            id_verified=verified,
            id_verified_at=datetime.utcnow() - timedelta(days=30) if verified else None,
            skills=skills,
            bio=bio,
            reputation_score=rep,
            reputation_tier=tier,
            tasks_completed=completed,
            tasks_approved=approved,
        ))

    async with async_session() as session:
        session.add_all(users)
        await session.commit()

        # Refetch to get IDs
        result = await session.execute(text("SELECT id, wallet_address, name FROM users"))
        user_map = {row[1]: (row[0], row[2]) for row in result.fetchall()}

    print(f"  Created {len(users)} users")
    return user_map


async def seed_tasks_and_subtasks(user_map):
    """Seed tasks with various statuses and subtasks."""
    print("Seeding tasks and subtasks...")

    admin_id = user_map["0xAdmin0000000000000000000000000000000001"][0]
    client1_id = user_map["0xClient000000000000000000000000000000001"][0]
    client2_id = user_map["0xClient000000000000000000000000000000002"][0]
    worker1_id = user_map["0xWorker000000000000000000000000000000001"][0]
    worker2_id = user_map["0xWorker000000000000000000000000000000002"][0]
    worker3_id = user_map["0xWorker000000000000000000000000000000003"][0]
    worker4_id = user_map["0xWorker000000000000000000000000000000004"][0]
    worker5_id = user_map["0xWorker000000000000000000000000000000005"][0]

    async with async_session() as session:
        # Task 1: Completed
        task1 = Task(
            title="AI Safety Mechanisms in Autonomous Vehicles - Literature Review",
            description="Comprehensive systematic review of AI safety mechanisms used in autonomous vehicles, covering 2020-2025 publications.",
            research_question="What are the current AI safety mechanisms in autonomous vehicles and what gaps exist?",
            client_id=client1_id,
            status="completed",
            total_budget_cngn=Decimal("250000.00"),
            skills_required=["literature-review", "data-analysis", "technical-writing"],
            deadline=datetime.now(timezone.utc) - timedelta(days=5),
            funded_at=datetime.now(timezone.utc) - timedelta(days=45),
            completed_at=datetime.now(timezone.utc) - timedelta(days=5),
            escrow_tx_hash="0xabc123completed456",
            escrow_contract_task_id=1,
        )

        # Task 2: In Progress (with mix of subtask statuses)
        task2 = Task(
            title="Lagos Market Price Survey Q1 2025",
            description="Comprehensive survey of commodity prices across 15 major markets in Lagos State.",
            research_question="How do commodity prices vary across different markets in Lagos?",
            background_context="Part of a larger study on economic resilience in West African urban centers.",
            client_id=client1_id,
            status="in_progress",
            total_budget_cngn=Decimal("180000.00"),
            skills_required=["data-collection", "surveys", "local-knowledge"],
            deadline=datetime.now(timezone.utc) + timedelta(days=21),
            funded_at=datetime.now(timezone.utc) - timedelta(days=14),
            escrow_tx_hash="0xdef456inprogress789",
            escrow_contract_task_id=2,
        )

        # Task 3: Funded (ready to start)
        task3 = Task(
            title="Rural Healthcare Access Mapping - Kano State",
            description="Map and document healthcare facilities in rural Kano State.",
            research_question="What is the current state of healthcare accessibility in rural Kano?",
            client_id=client2_id,
            status="funded",
            total_budget_cngn=Decimal("320000.00"),
            skills_required=["gis-mapping", "photography", "interviews", "hausa"],
            deadline=datetime.now(timezone.utc) + timedelta(days=45),
            funded_at=datetime.now(timezone.utc) - timedelta(days=2),
            escrow_tx_hash="0xghi789funded012",
            escrow_contract_task_id=3,
        )

        # Task 4: Decomposed (subtasks created, not funded)
        task4 = Task(
            title="Agricultural Supply Chain Documentation - Oyo State",
            description="Document the journey of agricultural products from farm to market.",
            research_question="How do agricultural products move from farms to consumers in Oyo?",
            client_id=client1_id,
            status="decomposed",
            total_budget_cngn=Decimal("150000.00"),
            skills_required=["interviews", "photography", "documentation"],
            deadline=datetime.now(timezone.utc) + timedelta(days=60),
        )

        # Task 5: Draft
        task5 = Task(
            title="Digital Literacy Assessment - Secondary Schools",
            description="Assess digital literacy levels among secondary school students in Lagos.",
            research_question="What is the current state of digital literacy among Lagos secondary students?",
            client_id=client2_id,
            status="draft",
            total_budget_cngn=Decimal("200000.00"),
            skills_required=["surveys", "data-analysis", "report-writing"],
            deadline=datetime.now(timezone.utc) + timedelta(days=90),
        )

        # Task 6: In Review (all subtasks submitted)
        task6 = Task(
            title="Fintech Adoption Survey - SMEs in Nigeria",
            description="Survey small and medium enterprises on fintech adoption patterns.",
            research_question="What factors influence fintech adoption among Nigerian SMEs?",
            client_id=client1_id,
            status="in_review",
            total_budget_cngn=Decimal("175000.00"),
            skills_required=["surveys", "interviews", "data-analysis"],
            deadline=datetime.now(timezone.utc) + timedelta(days=10),
            funded_at=datetime.now(timezone.utc) - timedelta(days=30),
            escrow_tx_hash="0xjkl012inreview345",
            escrow_contract_task_id=4,
        )

        session.add_all([task1, task2, task3, task4, task5, task6])
        await session.flush()

        # Subtasks for Task 1 (Completed) - Total: 250k CNGN
        subtasks_t1 = [
            Subtask(
                task_id=task1.id,
                title="Paper Discovery & Collection",
                subtask_type="discovery",
                description="Conduct a systematic search of academic databases to identify relevant papers on AI safety mechanisms in autonomous vehicles published between 2020-2025. Focus on peer-reviewed journals and major conference proceedings.",
                description_html="<p>Conduct a <strong>systematic search</strong> of academic databases to identify relevant papers on AI safety mechanisms in autonomous vehicles published between 2020-2025.</p><h4>Focus Areas:</h4><ul><li>Peer-reviewed journals (IEEE, ACM, Springer)</li><li>Major conference proceedings (NeurIPS, ICML, CVPR)</li><li>ArXiv preprints with significant citations</li></ul>",
                acceptance_criteria=[
                    "Minimum 50 relevant papers identified and catalogued",
                    "Search strategy documented with keywords, databases, and filters used",
                    "Papers organized by safety mechanism category",
                    "Citation information complete for all papers",
                    "Duplicates removed and noted"
                ],
                deliverables={
                    "primary": "papers_catalog.csv",
                    "format": "CSV with columns: title, authors, year, journal, doi, abstract, safety_category",
                    "secondary": ["search_methodology.md", "database_coverage_report.pdf"]
                },
                example_output="Example row: 'Redundant Neural Networks for AV Safety', Smith et al., 2023, IEEE T-ITS, 10.1109/xxx, 'This paper proposes...', sensor_fusion",
                tools_required=["Google Scholar", "IEEE Xplore", "Semantic Scholar API", "Zotero", "Python pandas"],
                estimated_hours=Decimal("20.00"),
                references={
                    "guidelines": "https://www.prisma-statement.org/",
                    "databases": ["https://ieeexplore.ieee.org", "https://scholar.google.com", "https://www.semanticscholar.org"]
                },
                sequence_order=1,
                budget_allocation_percent=Decimal("20.00"),
                budget_cngn=Decimal("50000.00"),
                status="approved",
                claimed_by=worker1_id,
                approved_at=datetime.now(timezone.utc) - timedelta(days=30)
            ),
            Subtask(
                task_id=task1.id,
                title="Data Extraction - Safety Mechanisms",
                subtask_type="extraction",
                description="Extract and categorize safety mechanisms from collected papers. Create a structured dataset identifying mechanism type, implementation approach, validation method, and reported effectiveness metrics.",
                description_html="<p>Extract and categorize safety mechanisms from collected papers.</p><h4>Data Points to Extract:</h4><ol><li><strong>Mechanism Type:</strong> sensor redundancy, fail-safe protocols, anomaly detection, etc.</li><li><strong>Implementation:</strong> hardware vs software, real-time vs offline</li><li><strong>Validation:</strong> simulation, real-world testing, formal verification</li><li><strong>Metrics:</strong> accuracy, latency, failure rate</li></ol>",
                acceptance_criteria=[
                    "All 50+ papers processed with complete data extraction",
                    "Mechanism taxonomy created with at least 5 main categories",
                    "Quantitative metrics extracted where available",
                    "Data validated by second reviewer (collaborator)",
                    "Inter-rater reliability score > 0.8"
                ],
                deliverables={
                    "primary": "safety_mechanisms_dataset.json",
                    "schema": {"paper_id": "string", "mechanisms": [{"type": "string", "implementation": "string", "metrics": {}}]},
                    "secondary": ["extraction_codebook.md", "taxonomy_diagram.png"]
                },
                example_output='{"paper_id": "smith2023", "mechanisms": [{"type": "sensor_fusion", "implementation": "software_realtime", "metrics": {"latency_ms": 15, "accuracy": 0.97}}]}',
                tools_required=["Python", "JSON Schema validator", "Excel/Sheets", "Miro for taxonomy"],
                estimated_hours=Decimal("35.00"),
                references={
                    "codebook_template": "https://example.com/extraction-template",
                    "taxonomy_guide": "https://example.com/safety-taxonomy"
                },
                sequence_order=2,
                budget_allocation_percent=Decimal("30.00"),
                budget_cngn=Decimal("75000.00"),
                status="approved",
                claimed_by=worker2_id,
                collaborators=[worker3_id],
                collaborator_splits=[Decimal("30.00")],
                approved_at=datetime.now(timezone.utc) - timedelta(days=20)
            ),
            Subtask(
                task_id=task1.id,
                title="Gap Analysis & Research Mapping",
                subtask_type="mapping",
                description="Analyze the extracted data to identify research gaps, underexplored areas, and emerging trends in AI safety for autonomous vehicles. Create visual maps showing the research landscape.",
                description_html="<p>Analyze extracted data to identify:</p><ul><li><strong>Research Gaps:</strong> Areas with limited study</li><li><strong>Underexplored Mechanisms:</strong> Safety approaches mentioned but not validated</li><li><strong>Emerging Trends:</strong> Growing research directions</li><li><strong>Geographic Distribution:</strong> Where research is concentrated</li></ul>",
                acceptance_criteria=[
                    "Gap analysis identifies at least 5 significant research gaps",
                    "Trend analysis covers 2020-2025 with year-over-year comparison",
                    "Visual research map created showing mechanism relationships",
                    "Statistical analysis of publication trends included",
                    "Recommendations prioritized by impact potential"
                ],
                deliverables={
                    "primary": "gap_analysis_report.md",
                    "visualizations": ["research_landscape_map.html", "trend_charts.png", "gap_heatmap.svg"],
                    "data": "analysis_statistics.json"
                },
                example_output="Gap identified: Only 3 papers address adversarial attacks on LiDAR-camera fusion systems, despite 45 papers on sensor fusion generally.",
                tools_required=["Python matplotlib/plotly", "D3.js or similar", "Statistical analysis (scipy)", "Markdown"],
                estimated_hours=Decimal("25.00"),
                sequence_order=3,
                budget_allocation_percent=Decimal("24.00"),
                budget_cngn=Decimal("60000.00"),
                status="approved",
                claimed_by=worker3_id,
                approved_at=datetime.now(timezone.utc) - timedelta(days=12)
            ),
            Subtask(
                task_id=task1.id,
                title="Final Synthesis Report",
                subtask_type="narrative",
                description="Compile all findings into a comprehensive synthesis report suitable for academic publication. Include executive summary, methodology, findings, gap analysis, and actionable recommendations.",
                description_html="<h3>Report Structure</h3><ol><li><strong>Executive Summary</strong> (1 page)</li><li><strong>Introduction & Methodology</strong> (2-3 pages)</li><li><strong>Taxonomy of Safety Mechanisms</strong> (5-7 pages)</li><li><strong>Gap Analysis & Trends</strong> (3-4 pages)</li><li><strong>Recommendations</strong> (2-3 pages)</li><li><strong>Appendices</strong> (data tables, full bibliography)</li></ol>",
                acceptance_criteria=[
                    "Report follows academic writing standards (APA/IEEE format)",
                    "All claims supported by extracted data with citations",
                    "Executive summary readable by non-technical stakeholders",
                    "Minimum 15 pages excluding appendices",
                    "Proofread with no spelling/grammar errors",
                    "All visualizations high-resolution and accessible"
                ],
                deliverables={
                    "primary": "ai_safety_av_systematic_review.pdf",
                    "formats": ["PDF", "LaTeX source", "Word doc"],
                    "supplementary": ["data_package.zip", "presentation_slides.pptx"]
                },
                example_output="Section 4.2: 'Our analysis reveals that while sensor redundancy mechanisms are well-studied (n=23 papers), formal verification approaches remain limited to simulation environments...'",
                tools_required=["LaTeX/Overleaf", "Grammarly", "Citation manager", "PDF tools"],
                estimated_hours=Decimal("30.00"),
                sequence_order=4,
                budget_allocation_percent=Decimal("26.00"),
                budget_cngn=Decimal("65000.00"),
                status="approved",
                claimed_by=worker2_id,
                approved_at=datetime.now(timezone.utc) - timedelta(days=5)
            ),
        ]

        # Subtasks for Task 2 (In Progress - mixed statuses) - Total: 180k CNGN
        subtasks_t2 = [
            Subtask(
                task_id=task2.id,
                title="Market Identification & Mapping",
                subtask_type="discovery",
                description="Identify and create detailed profiles of 15 major markets in Lagos State. Document market locations, operating hours, primary commodities, vendor demographics, and accessibility information.",
                description_html="<p>Create comprehensive profiles for <strong>15 major markets</strong> in Lagos State.</p><h4>Required Information per Market:</h4><ul><li>GPS coordinates and physical address</li><li>Operating days and hours</li><li>Estimated daily foot traffic</li><li>Primary commodity categories (minimum 5)</li><li>Infrastructure assessment (electricity, water, storage)</li></ul>",
                acceptance_criteria=[
                    "15 markets identified across different Lagos LGAs",
                    "GPS coordinates verified for each market",
                    "Market profiles complete with all required fields",
                    "Photos taken of main entrance and key areas (min 5 per market)",
                    "Market association contacts obtained where possible"
                ],
                deliverables={
                    "primary": "market_profiles.json",
                    "maps": ["lagos_markets_map.geojson", "market_locations.kml"],
                    "photos": "market_photos/ (organized by market name)"
                },
                example_output='{"market_name": "Balogun Market", "lga": "Lagos Island", "coordinates": [6.4541, 3.3947], "operating_hours": "Mon-Sat 7AM-7PM", "primary_commodities": ["textiles", "electronics", "household"]}',
                tools_required=["Google Maps", "GPS device/smartphone", "Camera", "Survey form app"],
                estimated_hours=Decimal("15.00"),
                sequence_order=1,
                budget_allocation_percent=Decimal("15.00"),
                budget_cngn=Decimal("27000.00"),
                status="approved",
                claimed_by=worker5_id,
                approved_at=datetime.now(timezone.utc) - timedelta(days=10)
            ),
            Subtask(
                task_id=task2.id,
                title="Price Data Collection - Week 1",
                subtask_type="extraction",
                description="Collect retail and wholesale prices for 50 standardized commodity items across all 15 identified markets. Use consistent units and quality grades for accurate comparison.",
                description_html="<h4>Data Collection Protocol</h4><ol><li>Visit each market between 9AM-2PM for consistent pricing</li><li>Collect from <strong>3 different vendors</strong> per item per market</li><li>Record both retail (single unit) and wholesale (bulk) prices</li><li>Note any price variations by quality grade</li><li>Document currency and date for each entry</li></ol><h4>Commodity Categories (50 items total):</h4><ul><li>Grains & Cereals (10 items)</li><li>Proteins (8 items)</li><li>Vegetables (12 items)</li><li>Fruits (8 items)</li><li>Oils & Condiments (7 items)</li><li>Processed Foods (5 items)</li></ul>",
                acceptance_criteria=[
                    "All 50 commodities priced at all 15 markets (750 data points minimum)",
                    "3 vendor quotes per item per market where possible",
                    "Prices recorded in NGN with unit specifications",
                    "Quality grades noted (Grade A, B, C where applicable)",
                    "Collection timestamp within specified hours",
                    "No more than 5% missing data points"
                ],
                deliverables={
                    "primary": "week1_prices.csv",
                    "schema": "market_id, commodity_id, vendor_id, retail_price, wholesale_price, unit, quality_grade, timestamp",
                    "validation": "data_quality_report_w1.md"
                },
                example_output="balogun_001, rice_50kg, vendor_023, 42000, 40000, 50kg bag, grade_a, 2025-01-15T10:23:00",
                tools_required=["KoboToolbox", "Smartphone", "Weighing scale", "Price reference sheet"],
                estimated_hours=Decimal("40.00"),
                references={
                    "commodity_list": "https://example.com/ng-commodities-standard",
                    "collection_protocol": "protocol_week1.pdf"
                },
                sequence_order=2,
                budget_allocation_percent=Decimal("25.00"),
                budget_cngn=Decimal("45000.00"),
                status="submitted",
                claimed_by=worker1_id,
                claimed_at=datetime.now(timezone.utc) - timedelta(days=8)
            ),
            Subtask(
                task_id=task2.id,
                title="Price Data Collection - Week 2",
                subtask_type="extraction",
                description="Repeat price collection for all 50 commodities to capture weekly price variations. Compare with Week 1 data to identify trends and anomalies.",
                description_html="<h4>Week 2 Collection Goals</h4><ul><li>Replicate Week 1 methodology exactly</li><li>Visit markets in <strong>same order</strong> as Week 1</li><li>Flag any significant price changes (&gt;10%)</li><li>Document reasons for price changes where known</li></ul><h4>Additional Data Points:</h4><ul><li>Stock availability (in_stock, limited, out_of_stock)</li><li>Vendor sentiment on price direction</li></ul>",
                acceptance_criteria=[
                    "Same 50 commodities at same 15 markets",
                    "Collection within same time windows as Week 1",
                    "Price change analysis completed",
                    "Anomalies flagged and explained where possible",
                    "Combined dataset validated for week-over-week comparison"
                ],
                deliverables={
                    "primary": "week2_prices.csv",
                    "analysis": "week_comparison.json",
                    "report": "price_trends_preliminary.md"
                },
                tools_required=["KoboToolbox", "Smartphone", "Week 1 reference data"],
                estimated_hours=Decimal("40.00"),
                sequence_order=3,
                budget_allocation_percent=Decimal("25.00"),
                budget_cngn=Decimal("45000.00"),
                status="in_progress",
                claimed_by=worker4_id,
                claimed_at=datetime.now(timezone.utc) - timedelta(days=3)
            ),
            Subtask(
                task_id=task2.id,
                title="Vendor Interviews",
                subtask_type="extraction",
                description="Conduct semi-structured interviews with 30 market vendors (2 per market) to understand supply chains, pricing decisions, and market dynamics.",
                description_html="<h4>Interview Topics</h4><ol><li><strong>Supply Chain:</strong> Where do they source goods? How often?</li><li><strong>Pricing:</strong> How do they set prices? What factors influence changes?</li><li><strong>Competition:</strong> How many similar vendors? Price coordination?</li><li><strong>Challenges:</strong> Storage, transport, regulation, security</li><li><strong>Trends:</strong> Customer behavior changes, seasonal patterns</li></ol><h4>Vendor Selection Criteria:</h4><ul><li>1 large-scale vendor per market</li><li>1 small-scale vendor per market</li><li>Mix of commodity types</li></ul>",
                acceptance_criteria=[
                    "30 interviews completed (2 per market)",
                    "Each interview 15-30 minutes",
                    "Audio recorded with consent",
                    "Transcripts completed within 48 hours",
                    "Key themes coded and tagged",
                    "Vendor demographics captured (years in business, employee count)"
                ],
                deliverables={
                    "primary": "vendor_interviews/",
                    "contents": ["audio_recordings/", "transcripts/", "coding_summary.xlsx"],
                    "analysis": "vendor_insights_summary.md"
                },
                example_output="Vendor 012 (Balogun, rice seller, 15 years): 'Prices follow the Naira-Dollar rate closely. When dollar goes up, my supplier in Kano increases prices within 2 days...'",
                tools_required=["Voice recorder", "Interview guide", "Consent forms", "Translation support (Yoruba)"],
                estimated_hours=Decimal("25.00"),
                sequence_order=4,
                budget_allocation_percent=Decimal("20.00"),
                budget_cngn=Decimal("36000.00"),
                status="claimed",
                claimed_by=worker1_id,
                collaborators=[worker4_id],
                collaborator_splits=[Decimal("40.00")],
                claimed_at=datetime.now(timezone.utc) - timedelta(days=1)
            ),
            Subtask(
                task_id=task2.id,
                title="Data Compilation & Final Report",
                subtask_type="assembly",
                description="Compile all collected data into a comprehensive research report with statistical analysis, visualizations, and actionable insights for policymakers and researchers.",
                description_html="<h4>Report Components</h4><ol><li><strong>Executive Summary</strong> - Key findings in 2 pages</li><li><strong>Methodology</strong> - Data collection process, limitations</li><li><strong>Market Profiles</strong> - Summary of 15 markets</li><li><strong>Price Analysis</strong> - Commodity-by-commodity breakdown</li><li><strong>Vendor Insights</strong> - Qualitative findings</li><li><strong>Recommendations</strong> - For policymakers, researchers, vendors</li></ol><h4>Required Visualizations:</h4><ul><li>Price heatmap across markets</li><li>Week-over-week trend charts</li><li>Market location map</li><li>Commodity price distribution boxplots</li></ul>",
                acceptance_criteria=[
                    "All data sources integrated and cross-referenced",
                    "Statistical analysis includes mean, median, std dev, price ranges",
                    "Minimum 5 data visualizations",
                    "Report reviewed for accuracy by team",
                    "Executive summary suitable for non-technical audience",
                    "Raw data package prepared for reproducibility"
                ],
                deliverables={
                    "primary": "lagos_market_survey_q1_2025.pdf",
                    "data_package": "lagos_markets_data.zip",
                    "visualizations": "charts/",
                    "presentation": "findings_presentation.pptx"
                },
                tools_required=["Python pandas/matplotlib", "LaTeX or Word", "QGIS for mapping"],
                estimated_hours=Decimal("20.00"),
                sequence_order=5,
                budget_allocation_percent=Decimal("15.00"),
                budget_cngn=Decimal("27000.00"),
                status="open"
            ),
        ]

        # Subtasks for Task 3 (Funded - all open) - Total: 320k CNGN
        subtasks_t3 = [
            Subtask(
                task_id=task3.id,
                title="LGA Selection & Field Planning",
                subtask_type="discovery",
                description="Select 5 Local Government Areas in rural Kano State for the healthcare access study. Develop selection criteria based on population density, distance from urban centers, and preliminary healthcare indicators.",
                description_html="<h4>Selection Criteria</h4><ul><li><strong>Rural Classification:</strong> Minimum 30km from Kano city center</li><li><strong>Population:</strong> 50,000-200,000 residents</li><li><strong>Healthcare Indicators:</strong> Areas with known gaps in coverage</li><li><strong>Accessibility:</strong> Must be reachable by road year-round</li><li><strong>Diversity:</strong> Mix of different economic activities</li></ul><h4>Planning Deliverables:</h4><ul><li>Selection matrix with scoring</li><li>Preliminary logistics plan</li><li>Local contact establishment</li></ul>",
                acceptance_criteria=[
                    "5 LGAs selected with documented justification",
                    "Selection matrix shows scoring against all criteria",
                    "Preliminary population and health data gathered",
                    "Local government contacts established in each LGA",
                    "Field logistics plan covering transport, accommodation, timing",
                    "Risk assessment completed (security, weather, accessibility)"
                ],
                deliverables={
                    "primary": "lga_selection_report.pdf",
                    "data": ["selection_matrix.xlsx", "lga_profiles.json"],
                    "logistics": "field_plan.md"
                },
                example_output='{"lga": "Gaya", "score": 87, "population": 156000, "nearest_hospital_km": 45, "selection_rationale": "High population, significant distance from secondary care, active local government health committee"}',
                tools_required=["Nigeria LGA database", "Health facility registry", "Google Earth", "Local contacts"],
                estimated_hours=Decimal("12.00"),
                references={
                    "population_data": "https://nigerianstat.gov.ng",
                    "health_indicators": "Nigeria DHS reports"
                },
                sequence_order=1,
                budget_allocation_percent=Decimal("10.00"),
                budget_cngn=Decimal("32000.00"),
                status="open"
            ),
            Subtask(
                task_id=task3.id,
                title="Healthcare Facility Survey - Phase 1 (2 LGAs)",
                subtask_type="extraction",
                description="Conduct comprehensive facility surveys in the first 2 selected LGAs. Document all healthcare facilities including primary health centers, clinics, pharmacies, and traditional medicine providers.",
                description_html="<h4>Facility Data Collection</h4><p>For <strong>each healthcare facility</strong>, collect:</p><ol><li><strong>Location Data:</strong> GPS coordinates, address, directions</li><li><strong>Facility Type:</strong> PHC, clinic, pharmacy, patent medicine store, traditional</li><li><strong>Services:</strong> Available treatments, specializations, referral capabilities</li><li><strong>Staff:</strong> Number and qualifications of healthcare workers</li><li><strong>Infrastructure:</strong> Electricity, water, equipment condition</li><li><strong>Operating Hours:</strong> Days/times of operation, emergency availability</li><li><strong>Costs:</strong> Consultation fees, common treatment costs</li></ol><h4>Documentation Requirements:</h4><ul><li>Minimum 10 photos per facility (exterior, interior, equipment)</li><li>Interview with facility manager/head</li><li>Patient flow observation (30 min minimum)</li></ul>",
                acceptance_criteria=[
                    "All healthcare facilities in 2 LGAs identified and catalogued",
                    "Complete data collected for each facility",
                    "GPS coordinates verified with < 10m accuracy",
                    "Photo documentation meets requirements",
                    "Facility manager interviews completed",
                    "Data entered into standardized form within 24 hours of collection"
                ],
                deliverables={
                    "primary": "phase1_facilities.geojson",
                    "detailed_data": "facility_surveys_phase1.json",
                    "photos": "phase1_photos/ (organized by facility_id)",
                    "interviews": "manager_interviews_phase1/"
                },
                example_output='{"facility_id": "GAY_PHC_001", "name": "Gaya Primary Health Center", "type": "PHC", "coordinates": [11.8234, 8.9456], "services": ["maternal_care", "immunization", "malaria_treatment"], "staff_count": 12}',
                tools_required=["GPS device", "Camera", "KoboToolbox", "Hausa interpreter", "Vehicle"],
                estimated_hours=Decimal("50.00"),
                references={
                    "survey_form": "facility_survey_template.pdf",
                    "photo_guide": "documentation_standards.md"
                },
                sequence_order=2,
                budget_allocation_percent=Decimal("20.00"),
                budget_cngn=Decimal("64000.00"),
                status="open"
            ),
            Subtask(
                task_id=task3.id,
                title="Healthcare Facility Survey - Phase 2 (3 LGAs)",
                subtask_type="extraction",
                description="Complete facility surveys in the remaining 3 LGAs. Apply lessons learned from Phase 1 to improve data quality and efficiency.",
                description_html="<h4>Phase 2 Enhancements</h4><p>Building on Phase 1 experience:</p><ul><li>Refined survey instruments based on Phase 1 feedback</li><li>Improved photo documentation protocol</li><li>Standardized interview approach</li></ul><h4>Additional Data Collection:</h4><ul><li>Supply chain information (medicine sourcing)</li><li>Referral network mapping</li><li>Community perception quick survey (5 patients per facility)</li></ul>",
                acceptance_criteria=[
                    "All facilities in remaining 3 LGAs surveyed",
                    "Data quality matches or exceeds Phase 1",
                    "Supply chain data collected for government facilities",
                    "Referral patterns documented",
                    "Patient quick surveys completed (minimum 100 total)",
                    "Combined dataset validated and cleaned"
                ],
                deliverables={
                    "primary": "phase2_facilities.geojson",
                    "combined": "all_facilities_combined.geojson",
                    "supply_chain": "medicine_supply_analysis.json",
                    "referrals": "referral_network.json"
                },
                tools_required=["GPS device", "Camera", "KoboToolbox", "Hausa interpreter", "Vehicle"],
                estimated_hours=Decimal("75.00"),
                sequence_order=3,
                budget_allocation_percent=Decimal("30.00"),
                budget_cngn=Decimal("96000.00"),
                status="open"
            ),
            Subtask(
                task_id=task3.id,
                title="Community Healthcare Access Interviews",
                subtask_type="extraction",
                description="Conduct in-depth interviews with 50 community members across all 5 LGAs to understand healthcare-seeking behavior, barriers to access, and community health priorities.",
                description_html="<h4>Interview Demographics (50 total)</h4><ul><li>10 per LGA, balanced for:</li><li>Gender: 25 male, 25 female</li><li>Age: Youth (5), Adults (35), Elderly (10)</li><li>Include: Mothers with young children, chronic disease patients, traditional medicine users</li></ul><h4>Interview Topics</h4><ol><li><strong>Healthcare Seeking:</strong> Where do they go when sick? Why?</li><li><strong>Barriers:</strong> Cost, distance, quality, cultural factors</li><li><strong>Experiences:</strong> Positive and negative healthcare interactions</li><li><strong>Priorities:</strong> What health services are most needed?</li><li><strong>Traditional Medicine:</strong> Role and integration with modern care</li></ol>",
                acceptance_criteria=[
                    "50 interviews completed across all 5 LGAs",
                    "Demographic quotas met (gender, age, special populations)",
                    "Audio recordings with informed consent",
                    "Transcripts in English (translated from Hausa)",
                    "Thematic coding completed",
                    "Community health priorities ranked by frequency"
                ],
                deliverables={
                    "primary": "community_interviews/",
                    "analysis": "access_barriers_analysis.md",
                    "summary": "community_priorities_ranking.json",
                    "quotes": "key_quotes_compilation.md"
                },
                example_output='"The clinic is 15km away. When my child had fever at night, I had to wait until morning for transport. By then, the fever was very high." - Mother, 32, Gaya LGA',
                tools_required=["Voice recorder", "Interview guide (Hausa)", "Consent forms", "Transcription service"],
                estimated_hours=Decimal("45.00"),
                sequence_order=4,
                budget_allocation_percent=Decimal("20.00"),
                budget_cngn=Decimal("64000.00"),
                status="open"
            ),
            Subtask(
                task_id=task3.id,
                title="Healthcare Access Maps & Visualization",
                subtask_type="mapping",
                description="Create interactive maps and visualizations showing healthcare facility distribution, service coverage gaps, travel time analysis, and community access patterns.",
                description_html="<h4>Required Maps</h4><ol><li><strong>Facility Distribution Map:</strong> All facilities by type with popup details</li><li><strong>Service Coverage:</strong> Heatmap showing areas within 5km, 10km, 15km+ of care</li><li><strong>Travel Time Analysis:</strong> Isochrone maps for walking and vehicle access</li><li><strong>Service Gap Analysis:</strong> Areas lacking specific services (maternal care, emergency)</li><li><strong>Population Overlay:</strong> Facilities per capita visualization</li></ol><h4>Interactive Features:</h4><ul><li>Filter by facility type, services, LGA</li><li>Click for facility details</li><li>Toggle population density layer</li></ul>",
                acceptance_criteria=[
                    "All 5 map types created",
                    "Maps interactive with filtering capabilities",
                    "Travel time calculated using local road conditions",
                    "Population data accurately overlaid",
                    "Maps accessible via web browser",
                    "Static versions exported for print reports"
                ],
                deliverables={
                    "primary": "healthcare_access_maps/",
                    "interactive": "index.html (Leaflet/Mapbox)",
                    "static": ["facility_map.png", "coverage_map.png", "gap_analysis_map.png"],
                    "data": "processed_geospatial_data.zip"
                },
                tools_required=["QGIS", "Leaflet.js", "Python geopandas", "Mapbox (optional)", "WorldPop data"],
                estimated_hours=Decimal("25.00"),
                references={
                    "population": "https://www.worldpop.org",
                    "roads": "OpenStreetMap Nigeria"
                },
                sequence_order=5,
                budget_allocation_percent=Decimal("10.00"),
                budget_cngn=Decimal("32000.00"),
                status="open"
            ),
            Subtask(
                task_id=task3.id,
                title="Final Report & Recommendations",
                subtask_type="assembly",
                description="Compile all findings into a comprehensive report with evidence-based recommendations for improving healthcare access in rural Kano State.",
                description_html="<h4>Report Structure</h4><ol><li><strong>Executive Summary</strong> (2 pages)</li><li><strong>Background & Methodology</strong> (5 pages)</li><li><strong>LGA Profiles</strong> (10 pages, 2 per LGA)</li><li><strong>Facility Inventory</strong> (variable, with summary statistics)</li><li><strong>Access Analysis</strong> (8 pages)</li><li><strong>Community Perspectives</strong> (5 pages)</li><li><strong>Recommendations</strong> (5 pages)</li><li><strong>Appendices</strong> (data, maps, interview guides)</li></ol><h4>Recommendation Categories:</h4><ul><li>Infrastructure investments</li><li>Human resources deployment</li><li>Service delivery improvements</li><li>Community health programs</li><li>Policy recommendations</li></ul>",
                acceptance_criteria=[
                    "Report follows structure with all sections complete",
                    "All data sources cited and cross-referenced",
                    "Recommendations specific, actionable, and prioritized",
                    "Maps and visualizations embedded appropriately",
                    "Executive summary standalone and compelling",
                    "Report reviewed by at least 2 team members",
                    "Data package prepared for government handover"
                ],
                deliverables={
                    "primary": "rural_kano_healthcare_access_report.pdf",
                    "data_package": "kano_healthcare_data_package.zip",
                    "presentation": "findings_presentation.pptx",
                    "policy_brief": "policy_recommendations_brief.pdf"
                },
                tools_required=["Word/LaTeX", "Data visualization tools", "PDF editor"],
                estimated_hours=Decimal("30.00"),
                sequence_order=6,
                budget_allocation_percent=Decimal("10.00"),
                budget_cngn=Decimal("32000.00"),
                status="open"
            ),
        ]

        # Subtasks for Task 4 (Decomposed - not funded yet) - Total: 150k CNGN
        subtasks_t4 = [
            Subtask(
                task_id=task4.id,
                title="Supply Chain Network Mapping",
                subtask_type="discovery",
                description="Map the complete agricultural supply chain for 3 key crops (tomatoes, maize, cassava) in Oyo State from farm gate to final consumer. Identify all actors, nodes, and pathways.",
                description_html="<h4>Supply Chain Actors to Identify</h4><ul><li><strong>Production:</strong> Smallholder farmers, commercial farms, cooperatives</li><li><strong>Aggregation:</strong> Local buying agents, collection centers</li><li><strong>Processing:</strong> Mills, storage facilities, cold chain</li><li><strong>Distribution:</strong> Transporters, wholesalers, distributors</li><li><strong>Retail:</strong> Market traders, supermarkets, restaurants</li></ul><h4>Network Documentation:</h4><ul><li>Geographic flow patterns</li><li>Volume estimates at each node</li><li>Seasonal variations</li></ul>",
                acceptance_criteria=[
                    "Complete supply chain mapped for 3 crops",
                    "All actor categories identified with estimates of numbers",
                    "Geographic flow patterns documented",
                    "Key bottlenecks and inefficiencies identified",
                    "Seasonal variation patterns noted"
                ],
                deliverables={
                    "primary": "supply_chain_maps.json",
                    "visualizations": ["tomato_chain.svg", "maize_chain.svg", "cassava_chain.svg"],
                    "report": "chain_mapping_findings.md"
                },
                tools_required=["Miro/Lucidchart", "GPS", "Local guide/translator"],
                estimated_hours=Decimal("20.00"),
                sequence_order=1,
                budget_allocation_percent=Decimal("20.00"),
                budget_cngn=Decimal("30000.00"),
                status="open"
            ),
            Subtask(
                task_id=task4.id,
                title="Farmer Interviews & Production Analysis",
                subtask_type="extraction",
                description="Conduct structured interviews with 30 farmers across the 3 crop types to understand production practices, sales decisions, price information access, and challenges faced.",
                description_html="<h4>Farmer Sample</h4><ul><li>10 tomato farmers (mix of dry/wet season)</li><li>10 maize farmers (different scales)</li><li>10 cassava farmers (food vs industrial variety)</li></ul><h4>Interview Topics</h4><ol><li>Production costs and yields</li><li>Selling decisions (when, where, to whom)</li><li>Price negotiation and information</li><li>Post-harvest handling and losses</li><li>Access to inputs, credit, extension services</li><li>Cooperative/association membership</li></ol>",
                acceptance_criteria=[
                    "30 farmer interviews completed",
                    "Geographic spread across Oyo State",
                    "Production cost data collected (per hectare)",
                    "Sales channel preferences documented",
                    "Post-harvest loss estimates obtained",
                    "Farmer typology created based on findings"
                ],
                deliverables={
                    "primary": "farmer_interviews.json",
                    "analysis": "production_cost_analysis.xlsx",
                    "report": "farmer_perspectives_report.md"
                },
                tools_required=["Interview guide", "Calculator", "Yoruba interpreter", "Voice recorder"],
                estimated_hours=Decimal("35.00"),
                sequence_order=2,
                budget_allocation_percent=Decimal("30.00"),
                budget_cngn=Decimal("45000.00"),
                status="open"
            ),
            Subtask(
                task_id=task4.id,
                title="Middleman & Trader Documentation",
                subtask_type="extraction",
                description="Document the roles, operations, and margins of intermediaries in the supply chain including local buying agents, transporters, wholesalers, and market traders.",
                description_html="<h4>Intermediary Types to Interview</h4><ul><li><strong>Local Buying Agents:</strong> 6 interviews (2 per crop)</li><li><strong>Transporters:</strong> 6 interviews</li><li><strong>Wholesalers:</strong> 6 interviews (major markets)</li><li><strong>Retailers:</strong> 6 interviews</li></ul><h4>Data Collection Focus</h4><ul><li>Buying/selling prices and margins</li><li>Volume handled</li><li>Value addition activities</li><li>Relationships and loyalty patterns</li><li>Risk and loss management</li></ul>",
                acceptance_criteria=[
                    "24 intermediary interviews completed",
                    "Price margins documented at each stage",
                    "Volume flow estimates obtained",
                    "Value addition activities catalogued",
                    "Business model canvas for each type"
                ],
                deliverables={
                    "primary": "intermediary_profiles.json",
                    "margins": "margin_analysis.xlsx",
                    "flows": "volume_flow_estimates.json"
                },
                tools_required=["Interview guide", "Calculator", "Market access"],
                estimated_hours=Decimal("30.00"),
                sequence_order=3,
                budget_allocation_percent=Decimal("30.00"),
                budget_cngn=Decimal("45000.00"),
                status="open"
            ),
            Subtask(
                task_id=task4.id,
                title="Price & Efficiency Analysis Report",
                subtask_type="mapping",
                description="Synthesize all data to analyze price transmission, efficiency losses, and opportunities for improvement across the supply chains.",
                description_html="<h4>Analysis Components</h4><ol><li><strong>Price Breakdown:</strong> Farm gate to retail price decomposition</li><li><strong>Margin Analysis:</strong> Who captures value at each stage</li><li><strong>Efficiency Metrics:</strong> Post-harvest losses, transport costs, time delays</li><li><strong>Comparison:</strong> Across 3 crops and different pathways</li><li><strong>Opportunity Identification:</strong> Where can improvements be made?</li></ol><h4>Visualizations Required:</h4><ul><li>Waterfall charts showing price buildup</li><li>Sankey diagrams for volume flows</li><li>Efficiency scorecards by chain</li></ul>",
                acceptance_criteria=[
                    "Complete price decomposition for each crop",
                    "Efficiency metrics calculated and compared",
                    "Minimum 3 improvement opportunities identified per crop",
                    "All visualizations created",
                    "Recommendations prioritized by impact and feasibility"
                ],
                deliverables={
                    "primary": "supply_chain_analysis_report.pdf",
                    "data": "analysis_data_package.xlsx",
                    "visualizations": "charts/",
                    "recommendations": "intervention_recommendations.md"
                },
                tools_required=["Python/Excel for analysis", "Visualization tools", "Report writing"],
                estimated_hours=Decimal("25.00"),
                sequence_order=4,
                budget_allocation_percent=Decimal("20.00"),
                budget_cngn=Decimal("30000.00"),
                status="open"
            ),
        ]

        # Subtasks for Task 6 (In Review - all submitted) - Total: 175k CNGN
        subtasks_t6 = [
            Subtask(
                task_id=task6.id,
                title="Survey Instrument Design & Pilot Testing",
                subtask_type="discovery",
                description="Design a comprehensive survey instrument to measure fintech adoption patterns among Nigerian SMEs. Pilot test with 50 respondents and refine based on feedback.",
                description_html="<h4>Survey Sections</h4><ol><li><strong>Business Profile:</strong> Size, sector, years operating, revenue range</li><li><strong>Current Financial Services:</strong> Banking, payments, credit access</li><li><strong>Fintech Awareness:</strong> Knowledge of available solutions</li><li><strong>Fintech Usage:</strong> Specific platforms used, frequency, purposes</li><li><strong>Adoption Barriers:</strong> Trust, cost, knowledge, infrastructure</li><li><strong>Future Intent:</strong> Planned adoption, desired features</li></ol><h4>Pilot Testing Protocol:</h4><ul><li>50 SME respondents (diverse sectors)</li><li>Time survey completion</li><li>Note comprehension issues</li><li>Refine wording and flow</li></ul>",
                acceptance_criteria=[
                    "Survey covers all 6 sections",
                    "Likert scales properly calibrated",
                    "Average completion time < 20 minutes",
                    "Pilot feedback incorporated",
                    "Final survey approved by client",
                    "Digital version ready in KoboToolbox"
                ],
                deliverables={
                    "primary": "fintech_survey_final.pdf",
                    "digital": "kobotoolbox_survey_export.xls",
                    "pilot": ["pilot_results.xlsx", "refinement_notes.md"]
                },
                example_output="Q15: 'On a scale of 1-5, how concerned are you about the security of mobile payment platforms?' 1=Not concerned, 5=Extremely concerned",
                tools_required=["Survey design software", "KoboToolbox", "Google Forms (pilot)", "Statistical consultation"],
                estimated_hours=Decimal("25.00"),
                references={
                    "similar_surveys": "World Bank Enterprise Surveys",
                    "fintech_taxonomy": "CB Insights Fintech Report 2024"
                },
                sequence_order=1,
                budget_allocation_percent=Decimal("20.00"),
                budget_cngn=Decimal("35000.00"),
                status="approved",
                claimed_by=worker1_id,
                approved_at=datetime.now(timezone.utc) - timedelta(days=20)
            ),
            Subtask(
                task_id=task6.id,
                title="Data Collection - Lagos Mainland",
                subtask_type="extraction",
                description="Administer the fintech adoption survey to 100 SMEs in Lagos Mainland areas including Ikeja, Yaba, Surulere, and Mushin business districts.",
                description_html="<h4>Geographic Coverage</h4><ul><li><strong>Ikeja:</strong> 30 SMEs (Computer Village focus)</li><li><strong>Yaba:</strong> 25 SMEs (tech startups, retail)</li><li><strong>Surulere:</strong> 25 SMEs (services, retail)</li><li><strong>Mushin:</strong> 20 SMEs (manufacturing, wholesale)</li></ul><h4>Sector Quotas:</h4><ul><li>Retail/Trading: 40%</li><li>Services: 30%</li><li>Manufacturing: 15%</li><li>Tech/Digital: 15%</li></ul><h4>Collection Protocol:</h4><ul><li>In-person interviews preferred</li><li>Business owner or financial decision-maker</li><li>Incentive: Fintech guide booklet</li></ul>",
                acceptance_criteria=[
                    "100 complete surveys collected",
                    "Geographic quotas met within 10%",
                    "Sector quotas met within 10%",
                    "Response rate > 60% of approached businesses",
                    "Data quality checks passed (no duplicates, complete responses)",
                    "Daily submission to central database"
                ],
                deliverables={
                    "primary": "mainland_survey_responses.csv",
                    "quality": "data_quality_report_mainland.md",
                    "field_notes": "collection_notes_mainland.md"
                },
                tools_required=["Tablet with KoboToolbox", "Business directory", "Area maps", "Incentive materials"],
                estimated_hours=Decimal("45.00"),
                sequence_order=2,
                budget_allocation_percent=Decimal("30.00"),
                budget_cngn=Decimal("52500.00"),
                status="submitted",
                claimed_by=worker4_id,
                claimed_at=datetime.now(timezone.utc) - timedelta(days=15)
            ),
            Subtask(
                task_id=task6.id,
                title="Data Collection - Lagos Island & Victoria Island",
                subtask_type="extraction",
                description="Administer the fintech adoption survey to 100 SMEs in Lagos Island and Victoria Island, focusing on formal sector businesses and higher-end service providers.",
                description_html="<h4>Geographic Coverage</h4><ul><li><strong>Lagos Island:</strong> 40 SMEs (Marina, Broad Street, Balogun adjacent)</li><li><strong>Victoria Island:</strong> 35 SMEs (Adeola Odeku, Adetokunbo Ademola)</li><li><strong>Lekki Phase 1:</strong> 25 SMEs (retail centers, professional services)</li></ul><h4>Sector Focus:</h4><ul><li>Professional Services: 35%</li><li>Hospitality: 20%</li><li>Retail (formal): 25%</li><li>Finance-adjacent: 20%</li></ul><h4>Special Considerations:</h4><ul><li>Appointment scheduling often required</li><li>Higher formality expected</li><li>More tech-savvy respondents likely</li></ul>",
                acceptance_criteria=[
                    "100 complete surveys collected",
                    "Geographic and sector quotas met",
                    "Comparable demographics to Mainland where possible",
                    "Higher-value businesses included (revenue > ₦50M)",
                    "Data quality validated"
                ],
                deliverables={
                    "primary": "island_survey_responses.csv",
                    "comparison": "mainland_island_comparison_preliminary.md",
                    "field_notes": "collection_notes_island.md"
                },
                tools_required=["Tablet with KoboToolbox", "Business cards", "Professional attire", "Appointment scheduler"],
                estimated_hours=Decimal("50.00"),
                sequence_order=3,
                budget_allocation_percent=Decimal("30.00"),
                budget_cngn=Decimal("52500.00"),
                status="submitted",
                claimed_by=worker1_id,
                collaborators=[worker5_id],
                collaborator_splits=[Decimal("35.00")],
                claimed_at=datetime.now(timezone.utc) - timedelta(days=12)
            ),
            Subtask(
                task_id=task6.id,
                title="Data Analysis & Final Report",
                subtask_type="assembly",
                description="Analyze combined survey data (200 responses) and produce a comprehensive report on fintech adoption patterns among Lagos SMEs with actionable insights.",
                description_html="<h4>Analysis Plan</h4><ol><li><strong>Descriptive Statistics:</strong> Adoption rates, platform preferences, sector breakdowns</li><li><strong>Comparative Analysis:</strong> Mainland vs Island, sector differences, size effects</li><li><strong>Regression Analysis:</strong> Factors predicting adoption (business size, sector, owner demographics)</li><li><strong>Barrier Analysis:</strong> Ranking and clustering of adoption barriers</li><li><strong>Segment Identification:</strong> SME archetypes based on fintech behavior</li></ol><h4>Report Deliverables:</h4><ul><li>Executive summary (2 pages)</li><li>Full analytical report (25+ pages)</li><li>Infographic summary</li><li>Data tables appendix</li></ul>",
                acceptance_criteria=[
                    "All 200 responses cleaned and analyzed",
                    "Statistical tests appropriate and correctly applied",
                    "Key findings clearly articulated",
                    "Segment profiles actionable for fintech providers",
                    "Policy recommendations evidence-based",
                    "Visualizations publication-quality"
                ],
                deliverables={
                    "primary": "lagos_sme_fintech_adoption_report.pdf",
                    "data": "analysis_dataset.csv",
                    "code": "analysis_scripts/",
                    "visualizations": "charts_and_graphs/",
                    "infographic": "key_findings_infographic.png"
                },
                example_output="Finding: SMEs using mobile payments are 2.3x more likely to report revenue growth in the past year (p<0.01), controlling for sector and business size.",
                tools_required=["Python/R for analysis", "SPSS/Stata optional", "Data visualization", "Report design"],
                estimated_hours=Decimal("35.00"),
                sequence_order=4,
                budget_allocation_percent=Decimal("20.00"),
                budget_cngn=Decimal("35000.00"),
                status="submitted",
                claimed_by=worker2_id,
                claimed_at=datetime.now(timezone.utc) - timedelta(days=5)
            ),
        ]

        all_subtasks = subtasks_t1 + subtasks_t2 + subtasks_t3 + subtasks_t4 + subtasks_t6
        session.add_all(all_subtasks)
        await session.flush()

        # Create submissions for submitted/approved subtasks
        submissions = []

        # Submissions for approved subtasks in Task 1
        for st in subtasks_t1:
            submissions.append(Submission(
                subtask_id=st.id,
                submitted_by=st.claimed_by,
                content_summary=f"Completed work for: {st.title}",
                artifact_ipfs_hash=f"Qm{''.join(['abcdef123456'[i % 12] for i in range(44)])}",
                status="approved",
                review_notes="Excellent work, meets all criteria.",
                reviewed_by=admin_id,
                reviewed_at=to_naive(st.approved_at) if st.approved_at else None,
                payment_tx_hash=f"0xpay{str(st.id)[:8]}",
            ))

        # Submissions for submitted subtasks in Task 2
        for st in [subtasks_t2[1]]:  # Week 1 submitted
            submissions.append(Submission(
                subtask_id=st.id,
                submitted_by=st.claimed_by,
                content_summary="Week 1 price data collected from 14 of 15 markets. One market was closed for renovation.",
                artifact_ipfs_hash=f"QmWeek1Data{''.join(['xyz789'[i % 6] for i in range(33)])}",
                status="submitted",
            ))

        # Submissions for Task 6 (all submitted)
        for st in subtasks_t6[1:]:  # Skip first which is approved
            submissions.append(Submission(
                subtask_id=st.id,
                submitted_by=st.claimed_by,
                content_summary=f"Submitted work for: {st.title}",
                artifact_ipfs_hash=f"QmTask6{''.join(['abc123'[i % 6] for i in range(37)])}",
                status="submitted",
            ))

        # Add approved submission for Task 6 first subtask
        submissions.append(Submission(
            subtask_id=subtasks_t6[0].id,
            submitted_by=subtasks_t6[0].claimed_by,
            content_summary="Survey designed and piloted with 50 respondents. Validated questionnaire attached.",
            artifact_ipfs_hash=f"QmSurveyPilot{''.join(['def456'[i % 6] for i in range(31)])}",
            status="approved",
            review_notes="Well-designed survey with good validation.",
            reviewed_by=admin_id,
            reviewed_at=to_naive(subtasks_t6[0].approved_at) if subtasks_t6[0].approved_at else None,
            payment_tx_hash=f"0xpaysurvey001",
        ))

        session.add_all(submissions)

        # Create one dispute
        dispute = Dispute(
            subtask_id=subtasks_t2[1].id,  # Week 1 price collection
            raised_by=worker1_id,
            reason="Payment amount disputed - original agreement was for higher rate due to additional markets covered.",
            status="pending",
        )
        session.add(dispute)

        await session.commit()

    print(f"  Created 6 tasks and {len(all_subtasks)} subtasks")
    print(f"  Created {len(submissions)} submissions")
    print("  Created 1 dispute")


async def main():
    """Main entry point."""
    print("=" * 60)
    print("Seeding Rich Demo Data for Flow Platform")
    print("=" * 60)

    await clear_data()
    await seed_skills()
    user_map = await seed_users()
    await seed_tasks_and_subtasks(user_map)

    print("=" * 60)
    print("Seeding complete!")
    print("")
    print("Summary:")
    print("  - 20 skills across 5 categories")
    print("  - 13 users (1 admin, 2 clients, 10 workers)")
    print("  - 6 tasks (completed, in_progress, funded, decomposed, draft, in_review)")
    print("  - 23 subtasks with various statuses")
    print("  - Multiple submissions and 1 dispute")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
