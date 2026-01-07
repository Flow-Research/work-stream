# Enhanced Tasks & Subtasks

## Problem Statement

Current tasks and subtasks have minimal content structure:
- Basic title and description fields only
- No support for file attachments
- No embedded links or references
- No rich formatting for instructions
- Subtasks lack clear deliverable specifications

Workers need detailed context to complete work effectively.

## Proposed Enhancements

### 1. Rich Content Fields

#### Task Enhancements

| Field | Type | Description |
|-------|------|-------------|
| description_html | Text | Rich HTML description with formatting |
| background_context | Text | Background information and motivation |
| expected_outcomes | Text[] | List of expected deliverables |
| references | JSONB | Embedded links with metadata |
| attachments | JSONB | File attachments metadata |
| methodology_notes | Text | Suggested approach or methodology |

#### Subtask Enhancements

| Field | Type | Description |
|-------|------|-------------|
| description_html | Text | Rich HTML instructions |
| deliverables | JSONB | Specific deliverable specifications |
| acceptance_criteria | Text[] | Criteria for approval |
| references | JSONB | Relevant links and resources |
| attachments | JSONB | Supporting files |
| example_output | Text | Example of expected output format |
| tools_required | Text[] | Required tools or APIs |
| estimated_hours | Decimal | Estimated completion time |

### 2. References Schema

Embedded links with rich metadata:

```json
{
  "references": [
    {
      "id": "ref-1",
      "type": "paper",
      "title": "Machine Learning in Healthcare: A Review",
      "url": "https://doi.org/10.1234/example",
      "description": "Key background paper on ML applications",
      "required": true
    },
    {
      "id": "ref-2", 
      "type": "dataset",
      "title": "Nigeria Health Facilities Database",
      "url": "https://example.com/dataset",
      "description": "Primary data source for facility locations",
      "required": true
    },
    {
      "id": "ref-3",
      "type": "documentation",
      "title": "Data Collection Guidelines",
      "url": "https://example.com/guidelines",
      "description": "Standard procedures for field work",
      "required": false
    }
  ]
}
```

Reference types:
- `paper` - Academic papers, DOIs
- `dataset` - Data sources
- `documentation` - Guidelines, manuals
- `website` - General web resources
- `api` - API documentation
- `example` - Example outputs or templates

### 3. Attachments Schema

File attachments stored on IPFS:

```json
{
  "attachments": [
    {
      "id": "att-1",
      "filename": "survey_template.xlsx",
      "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "size_bytes": 45056,
      "ipfs_hash": "QmXxx...",
      "description": "Survey template to use for data collection",
      "uploaded_at": "2025-01-06T10:30:00Z",
      "uploaded_by": "uuid-of-uploader"
    },
    {
      "id": "att-2",
      "filename": "market_locations.geojson",
      "mime_type": "application/geo+json",
      "size_bytes": 12800,
      "ipfs_hash": "QmYyy...",
      "description": "GeoJSON of target market locations",
      "uploaded_at": "2025-01-06T10:35:00Z",
      "uploaded_by": "uuid-of-uploader"
    }
  ]
}
```

### 4. Deliverables Schema

Specific output requirements for subtasks:

```json
{
  "deliverables": [
    {
      "id": "del-1",
      "title": "Market Location Data",
      "description": "GPS coordinates and basic info for each market",
      "format": "csv",
      "required_fields": ["market_name", "latitude", "longitude", "address", "operating_days"],
      "min_records": 15,
      "template_attachment_id": "att-1"
    },
    {
      "id": "del-2",
      "title": "Market Photos",
      "description": "At least 3 photos per market showing entrance, interior, and vendors",
      "format": "jpeg",
      "min_count": 45,
      "max_size_mb": 5
    },
    {
      "id": "del-3",
      "title": "Summary Report",
      "description": "Brief report on methodology and observations",
      "format": "markdown",
      "min_words": 500
    }
  ]
}
```

### 5. Acceptance Criteria

Clear pass/fail criteria:

```json
{
  "acceptance_criteria": [
    "All 15 markets documented with GPS coordinates",
    "Coordinates accurate within 50 meters",
    "Photos are clear and properly labeled",
    "All required CSV fields populated",
    "No duplicate entries",
    "Summary report covers methodology"
  ]
}
```

## Database Changes

### New Task Fields

```sql
ALTER TABLE tasks ADD COLUMN description_html TEXT;
ALTER TABLE tasks ADD COLUMN background_context TEXT;
ALTER TABLE tasks ADD COLUMN expected_outcomes TEXT[];
ALTER TABLE tasks ADD COLUMN references JSONB DEFAULT '[]';
ALTER TABLE tasks ADD COLUMN attachments JSONB DEFAULT '[]';
ALTER TABLE tasks ADD COLUMN methodology_notes TEXT;
```

### New Subtask Fields

```sql
ALTER TABLE subtasks ADD COLUMN description_html TEXT;
ALTER TABLE subtasks ADD COLUMN deliverables JSONB DEFAULT '[]';
ALTER TABLE subtasks ADD COLUMN acceptance_criteria TEXT[];
ALTER TABLE subtasks ADD COLUMN references JSONB DEFAULT '[]';
ALTER TABLE subtasks ADD COLUMN attachments JSONB DEFAULT '[]';
ALTER TABLE subtasks ADD COLUMN example_output TEXT;
ALTER TABLE subtasks ADD COLUMN tools_required TEXT[];
ALTER TABLE subtasks ADD COLUMN estimated_hours DECIMAL(5,2);
```

## API Changes

### Upload Attachment

```
POST /api/tasks/{task_id}/attachments
POST /api/subtasks/{subtask_id}/attachments

Request: multipart/form-data
- file: binary
- description: string

Response:
{
  "id": "att-1",
  "filename": "survey_template.xlsx",
  "ipfs_hash": "QmXxx...",
  "size_bytes": 45056
}
```

### Add Reference

```
POST /api/tasks/{task_id}/references
POST /api/subtasks/{subtask_id}/references

Request:
{
  "type": "paper",
  "title": "Example Paper",
  "url": "https://example.com",
  "description": "Relevant background",
  "required": true
}

Response:
{
  "id": "ref-1",
  ...
}
```

### Update Deliverables

```
PUT /api/subtasks/{subtask_id}/deliverables

Request:
{
  "deliverables": [...]
}
```

## UI Changes

### Task Creation/Edit

1. Rich text editor for description (Markdown or WYSIWYG)
2. "References" section with add/remove links
3. "Attachments" section with file upload
4. "Expected Outcomes" as editable list
5. "Methodology" text area

### Subtask Creation/Edit

1. Rich text editor for instructions
2. "Deliverables" builder with:
   - Title, description, format
   - Validation rules (min records, required fields)
   - Template attachment links
3. "Acceptance Criteria" checklist builder
4. "References" section
5. "Attachments" section
6. Estimated hours input
7. Required tools/APIs selection

### Task/Subtask View

1. Formatted description rendering
2. Reference links with icons by type
3. Attachment download buttons
4. Deliverables checklist for workers
5. Acceptance criteria as checklist
6. Progress indicators

## Implementation Priority

### Phase 1: Core Fields
1. Add `description_html` to Task and Subtask
2. Add `acceptance_criteria` to Subtask
3. Add `estimated_hours` to Subtask
4. Update schemas and API

### Phase 2: References
1. Add `references` JSONB field
2. Create add/remove reference endpoints
3. Build reference UI component

### Phase 3: Attachments
1. Add `attachments` JSONB field
2. Create IPFS upload endpoint
3. Build file upload UI component

### Phase 4: Deliverables
1. Add `deliverables` JSONB field
2. Create deliverable builder UI
3. Add validation in submission flow

## Migration Strategy

1. Add new columns with defaults (non-breaking)
2. Backfill existing tasks:
   - Copy `description` to `description_html`
   - Generate basic `acceptance_criteria` from description
3. Update frontend to use new fields
4. Mark old fields as deprecated
