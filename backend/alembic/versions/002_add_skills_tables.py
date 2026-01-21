"""Add skills and skill_categories tables

Revision ID: 002_add_skills_tables
Revises: d8b2dae3fc2e
Create Date: 2026-01-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_add_skills_tables'
down_revision: Union[str, None] = 'd8b2dae3fc2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create skill_categories table
    op.create_table(
        'skill_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    # Create skills table
    op.create_table(
        'skills',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug'),
        sa.ForeignKeyConstraint(['category_id'], ['skill_categories.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_skills_category_id', 'skills', ['category_id'])
    op.create_index('ix_skills_slug', 'skills', ['slug'])
    op.create_index('ix_skills_is_active', 'skills', ['is_active'])

    # Seed initial categories
    op.execute("""
        INSERT INTO skill_categories (id, name, description, color, icon, display_order, is_active)
        VALUES
            (gen_random_uuid(), 'Research Methods', 'Research methodology and data collection skills', '#3B82F6', '🔬', 1, true),
            (gen_random_uuid(), 'Data & Analytics', 'Data analysis, statistics, and machine learning', '#10B981', '📊', 2, true),
            (gen_random_uuid(), 'Domain Expertise', 'Subject matter expertise in specific fields', '#8B5CF6', '🎓', 3, true),
            (gen_random_uuid(), 'Technical Skills', 'Programming and technical capabilities', '#F59E0B', '💻', 4, true),
            (gen_random_uuid(), 'Communication', 'Writing, documentation, and presentation skills', '#EC4899', '✍️', 5, true),
            (gen_random_uuid(), 'Languages', 'Language proficiency for local research', '#06B6D4', '🌍', 6, true)
    """)

    # Seed initial skills
    op.execute("""
        INSERT INTO skills (id, name, slug, description, category_id, display_order, is_active)
        SELECT gen_random_uuid(), s.name, s.slug, s.description, c.id, s.display_order, true
        FROM (VALUES
            -- Research Methods
            ('Data Collection', 'data-collection', 'Gathering primary data through surveys, interviews, or observations', 'Research Methods', 1),
            ('Survey Design', 'survey-design', 'Creating effective questionnaires and surveys', 'Research Methods', 2),
            ('Interviews', 'interviews', 'Conducting structured or semi-structured interviews', 'Research Methods', 3),
            ('Literature Review', 'literature-review', 'Systematic review of academic literature', 'Research Methods', 4),
            ('Mapping', 'mapping', 'Geographic or conceptual mapping of data', 'Research Methods', 5),
            ('Photography', 'photography', 'Documentation through photographs', 'Research Methods', 6),
            ('Field Research', 'field-research', 'On-ground research and data gathering', 'Research Methods', 7),

            -- Data & Analytics
            ('Data Analysis', 'data-analysis', 'Analyzing and interpreting datasets', 'Data & Analytics', 1),
            ('Statistics', 'statistics', 'Statistical analysis and modeling', 'Data & Analytics', 2),
            ('Python', 'python', 'Python programming for data analysis', 'Data & Analytics', 3),
            ('R', 'r-programming', 'R programming for statistical analysis', 'Data & Analytics', 4),
            ('Machine Learning', 'machine-learning', 'ML model development and application', 'Data & Analytics', 5),
            ('Data Visualization', 'data-visualization', 'Creating charts, graphs, and visual reports', 'Data & Analytics', 6),
            ('Excel/Spreadsheets', 'excel-spreadsheets', 'Advanced spreadsheet analysis', 'Data & Analytics', 7),

            -- Domain Expertise
            ('Economics', 'economics', 'Economic theory and analysis', 'Domain Expertise', 1),
            ('Medicine', 'medicine', 'Medical and health sciences', 'Domain Expertise', 2),
            ('Biology', 'biology', 'Biological sciences', 'Domain Expertise', 3),
            ('Sociology', 'sociology', 'Social structures and behavior', 'Domain Expertise', 4),
            ('Agriculture', 'agriculture', 'Agricultural practices and science', 'Domain Expertise', 5),
            ('Public Health', 'public-health', 'Population health and epidemiology', 'Domain Expertise', 6),
            ('Environmental Science', 'environmental-science', 'Environmental studies and sustainability', 'Domain Expertise', 7),

            -- Technical Skills
            ('NLP', 'nlp', 'Natural Language Processing', 'Technical Skills', 1),
            ('Web Scraping', 'web-scraping', 'Automated data extraction from websites', 'Technical Skills', 2),
            ('API Integration', 'api-integration', 'Working with APIs and web services', 'Technical Skills', 3),
            ('Database Management', 'database-management', 'SQL and database operations', 'Technical Skills', 4),
            ('GIS', 'gis', 'Geographic Information Systems', 'Technical Skills', 5),

            -- Communication
            ('Academic Writing', 'academic-writing', 'Scholarly article and paper writing', 'Communication', 1),
            ('Report Writing', 'report-writing', 'Professional report composition', 'Communication', 2),
            ('Documentation', 'documentation', 'Technical and process documentation', 'Communication', 3),
            ('Translation', 'translation', 'Language translation services', 'Communication', 4),
            ('Transcription', 'transcription', 'Audio/video to text conversion', 'Communication', 5),

            -- Languages
            ('English', 'english', 'English language proficiency', 'Languages', 1),
            ('Hausa', 'hausa', 'Hausa language proficiency', 'Languages', 2),
            ('Yoruba', 'yoruba', 'Yoruba language proficiency', 'Languages', 3),
            ('Igbo', 'igbo', 'Igbo language proficiency', 'Languages', 4),
            ('Pidgin', 'pidgin', 'Nigerian Pidgin proficiency', 'Languages', 5),
            ('French', 'french', 'French language proficiency', 'Languages', 6),
            ('Arabic', 'arabic', 'Arabic language proficiency', 'Languages', 7)
        ) AS s(name, slug, description, category_name, display_order)
        JOIN skill_categories c ON c.name = s.category_name
    """)


def downgrade() -> None:
    op.drop_table('skills')
    op.drop_table('skill_categories')
