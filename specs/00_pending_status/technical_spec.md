# Technical Specification: Task Pending Status & Filtering

## 1. Overview

### 1.1 Purpose

This document provides the technical implementation blueprint for adding "Pending" as a user-facing display name for draft tasks and enhancing the status filter dropdown in the Tasks UI.

### 1.2 Scope

| In Scope | Out of Scope |
|----------|--------------|
| Rename "Draft" to "Pending" in UI | Database schema changes |
| Expand status filter dropdown options | New status values |
| URL query parameter persistence | Multi-select filtering |
| Consistent badge styling | Status change from list view |

### 1.3 Architecture Summary

**Approach:** Frontend-only changes. The backend already supports filtering by any status value.

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Tasks.tsx                                               ││
│  │  - Update statusLabels['draft'] → 'Pending'             ││
│  │  - Expand dropdown options to all statuses              ││
│  │  - Add URL sync for status filter                       ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              │ GET /api/tasks?status=draft
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend (No Changes)                     │
│  - Already supports status_filter query param               │
│  - Already filters by exact status match                    │
│  - Status field is indexed for performance                  │
└─────────────────────────────────────────────────────────────┘
```

### 1.4 Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Display name approach | Frontend mapping | Zero backend changes, instant rollback possible |
| URL param format | `?status=draft` | Matches existing API contract |
| Filter options | All 8 statuses + "All" | Complete visibility, no hidden states |

---

## 2. System Architecture

### 2.1 Component Overview

```
frontend/
└── src/
    └── pages/
        └── Tasks.tsx          # Primary change location
            ├── statusLabels   # Change 'draft' → 'Pending'
            ├── statusColors   # Already correct
            └── <select>       # Expand options
```

### 2.2 Data Flow

```
User selects "Pending"
        │
        ▼
setStatusFilter('draft')  ─────►  URL updates to ?status=draft
        │
        ▼
React Query refetches with { status: 'draft' }
        │
        ▼
GET /api/tasks?status=draft
        │
        ▼
Backend returns tasks WHERE status = 'draft'
        │
        ▼
UI renders with "Pending" badge (via statusLabels mapping)
```

### 2.3 Existing Infrastructure Leveraged

| Component | Current State | Reuse |
|-----------|---------------|-------|
| `statusLabels` mapping | `draft: 'Draft'` | Change to `'Pending'` |
| `statusColors` mapping | `draft: 'badge-gray'` | No change needed |
| Status filter dropdown | Exists with 4 options | Expand to 9 options |
| Backend `status_filter` | Supports any string | No change needed |
| Task status index | Already indexed | No change needed |

---

## 3. Data Architecture

### 3.1 No Database Changes Required

The existing `Task.status` field with value `'draft'` serves as "Pending". This is a display-only change.

**Existing Schema (Unchanged):**

```sql
-- Task table (PostgreSQL)
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    -- ... other fields
);

CREATE INDEX ix_tasks_status ON tasks(status);
```

### 3.2 Frontend Type Definitions (Unchanged)

```typescript
// frontend/src/types/index.ts - NO CHANGES
export type TaskStatus =
  | 'draft'      // Displayed as "Pending"
  | 'funded'
  | 'decomposed'
  | 'in_progress'
  | 'in_review'
  | 'completed'
  | 'cancelled'
  | 'disputed'
```

### 3.3 Display Name Mapping (Updated)

```typescript
// frontend/src/pages/Tasks.tsx
const statusLabels: Record<TaskStatus, string> = {
  draft: 'Pending',        // CHANGED from 'Draft'
  funded: 'Funded',
  decomposed: 'Decomposed',
  in_progress: 'In Progress',
  in_review: 'In Review',
  completed: 'Completed',
  cancelled: 'Cancelled',
  disputed: 'Disputed',
}
```

---

## 4. API Specification

### 4.1 Existing Endpoint (No Changes)

**GET /api/tasks**

The backend already supports the required filtering. No API changes needed.

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by task status (e.g., `draft`, `funded`) |
| `search` | string | Search in title, description, research_question |
| `page` | int | Page number (default: 1) |
| `limit` | int | Items per page (default: 20, max: 100) |
| `include_drafts` | bool | Include draft tasks in results |

**Example Request:**
```
GET /api/tasks?status=draft&page=1&limit=20&include_drafts=true
```

**Response:** Unchanged `TaskListResponse` schema.

---

## 5. Infrastructure & Deployment

### 5.1 Deployment Strategy

| Phase | Action | Risk |
|-------|--------|------|
| 1 | Deploy frontend changes | Zero risk - display only |
| 2 | Monitor for issues | N/A |
| 3 | Rollback if needed | Instant via revert |

### 5.2 No Infrastructure Changes

- No new services
- No database migrations
- No environment variables
- No configuration changes

### 5.3 Build & Bundle

Standard frontend build process:
```bash
cd frontend
npm run build
```

Bundle size impact: ~50 bytes (string changes only).

---

## 6. Security Architecture

### 6.1 No Security Changes Required

This feature:
- Does not introduce new API endpoints
- Does not change authentication/authorization
- Does not expose new data
- Does not modify data persistence

### 6.2 Existing Security Maintained

- Draft tasks remain hidden from non-admin users by default
- `include_drafts` parameter controlled by admin check in UI
- Backend authorization unchanged

---

## 7. Integration Architecture

### 7.1 URL State Synchronization

**New Requirement:** Sync filter state with URL query parameters.

```typescript
// Read from URL on mount
const searchParams = new URLSearchParams(window.location.search)
const initialStatus = searchParams.get('status') || ''

// Update URL on filter change
const handleStatusChange = (status: string) => {
  setStatusFilter(status)
  const url = new URL(window.location.href)
  if (status) {
    url.searchParams.set('status', status)
  } else {
    url.searchParams.delete('status')
  }
  window.history.replaceState({}, '', url.toString())
}
```

### 7.2 React Query Integration

Existing query key already includes `statusFilter`:

```typescript
queryKey: ['tasks', statusFilter, debouncedSearch, page, user?.is_admin]
```

No changes needed—React Query will automatically refetch when `statusFilter` changes.

---

## 8. Performance & Scalability

### 8.1 Performance Impact

| Metric | Impact | Reason |
|--------|--------|--------|
| API response time | None | Same query, indexed field |
| UI render time | None | Same component structure |
| Bundle size | +50 bytes | String changes only |
| Memory usage | None | Same data structures |

### 8.2 Existing Optimizations Leveraged

- `Task.status` column is indexed
- React Query caching handles repeated requests
- Debounced search (300ms) prevents excessive API calls

---

## 9. Reliability & Operations

### 9.1 Error Handling

Existing error handling in Tasks.tsx is sufficient:

```typescript
if (error) {
  return (
    <div className="text-center text-red-600">
      Error loading tasks. Please try again.
    </div>
  )
}
```

### 9.2 Monitoring

No new monitoring required. Existing metrics apply:
- API response times
- Error rates
- Page load performance

### 9.3 Rollback Procedure

1. Revert frontend commit
2. Redeploy frontend
3. Estimated time: < 5 minutes

---

## 10. Development Standards

### 10.1 Code Style

Follow existing patterns in `Tasks.tsx`:
- TypeScript strict mode
- React functional components
- Tailwind CSS classes
- React Query for data fetching

### 10.2 Testing Requirements

| Test Type | Scope | Priority |
|-----------|-------|----------|
| Unit test | `statusLabels` mapping | P1 |
| Integration test | Filter dropdown interaction | P1 |
| E2E test | Filter + search combination | P2 |

**Example Test Cases:**

```typescript
// Unit test
describe('statusLabels', () => {
  it('displays "Pending" for draft status', () => {
    expect(statusLabels.draft).toBe('Pending')
  })
})

// Integration test
describe('Tasks filter', () => {
  it('filters to pending tasks when Pending selected', async () => {
    render(<Tasks />)
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'draft' } })
    await waitFor(() => {
      expect(mockTaskService.list).toHaveBeenCalledWith(
        expect.objectContaining({ status: 'draft' })
      )
    })
  })
})
```

### 10.3 Accessibility Requirements

| Requirement | Implementation |
|-------------|----------------|
| Keyboard navigation | Native `<select>` element (already accessible) |
| Screen reader | Label association via adjacent text |
| Color contrast | Badge colors meet WCAG AA |

---

## 11. Implementation Roadmap

### 11.1 Work Items

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| T1 | Update `statusLabels['draft']` to `'Pending'` | 5 min | None |
| T2 | Expand dropdown options to all 8 statuses | 15 min | None |
| T3 | Add URL sync for status filter | 30 min | T2 |
| T4 | Write unit tests | 20 min | T1, T2 |
| T5 | Write integration tests | 30 min | T3 |
| T6 | Manual QA verification | 15 min | T1-T5 |

**Total estimated effort:** ~2 hours

### 11.2 Implementation Order

```
T1 (statusLabels) ──┐
                    ├──► T4 (unit tests)
T2 (dropdown)    ──┤
                    └──► T3 (URL sync) ──► T5 (integration tests)
                                                    │
                                                    ▼
                                              T6 (QA)
```

### 11.3 File Changes Summary

| File | Changes |
|------|---------|
| `frontend/src/pages/Tasks.tsx` | Update statusLabels, expand dropdown, add URL sync |

**Single file change.** No other files affected.

---

## 12. Appendices

### Appendix A: Complete Code Changes

#### A.1 Tasks.tsx Updates

**Change 1: Update statusLabels (line 20)**

```typescript
// BEFORE
const statusLabels: Record<TaskStatus, string> = {
  draft: 'Draft',
  // ...
}

// AFTER
const statusLabels: Record<TaskStatus, string> = {
  draft: 'Pending',
  // ...
}
```

**Change 2: Expand dropdown options (lines 115-125)**

```typescript
// BEFORE
<select
  value={statusFilter}
  onChange={(e) => setStatusFilter(e.target.value)}
  className="input w-48"
>
  <option value="">All Status</option>
  <option value="draft">Draft</option>
  <option value="funded">Funded</option>
  <option value="in_progress">In Progress</option>
  <option value="completed">Completed</option>
</select>

// AFTER
<select
  value={statusFilter}
  onChange={(e) => handleStatusChange(e.target.value)}
  className="input w-48"
>
  <option value="">All Status</option>
  <option value="draft">Pending</option>
  <option value="funded">Funded</option>
  <option value="decomposed">Decomposed</option>
  <option value="in_progress">In Progress</option>
  <option value="in_review">In Review</option>
  <option value="completed">Completed</option>
  <option value="cancelled">Cancelled</option>
  <option value="disputed">Disputed</option>
</select>
```

**Change 3: Add URL synchronization**

```typescript
// Add near top of component, after useState declarations
const searchParams = new URLSearchParams(window.location.search)
const [statusFilter, setStatusFilter] = useState<string>(
  searchParams.get('status') || ''
)

// Add handler function
const handleStatusChange = (status: string) => {
  setStatusFilter(status)
  setPage(1) // Reset to first page

  const url = new URL(window.location.href)
  if (status) {
    url.searchParams.set('status', status)
  } else {
    url.searchParams.delete('status')
  }
  window.history.replaceState({}, '', url.toString())
}
```

### Appendix B: Status Reference

| Internal Value | Display Name | Badge Class | Description |
|----------------|--------------|-------------|-------------|
| `draft` | Pending | `badge-gray` | Task created, not funded |
| `funded` | Funded | `badge-info` | Budget deposited in escrow |
| `decomposed` | Decomposed | `badge-info` | Broken into subtasks |
| `in_progress` | In Progress | `badge-warning` | Work actively happening |
| `in_review` | In Review | `badge-warning` | Submitted for review |
| `completed` | Completed | `badge-success` | All work approved |
| `cancelled` | Cancelled | `badge-error` | Task cancelled |
| `disputed` | Disputed | `badge-error` | Under dispute |

### Appendix C: Testing Checklist

- [ ] "Pending" displays for draft tasks in list view
- [ ] "Pending" displays for draft tasks in detail view
- [ ] Filter dropdown shows all 8 status options + "All"
- [ ] Selecting "Pending" filters to draft tasks only
- [ ] URL updates when filter changes
- [ ] Page loads with correct filter from URL params
- [ ] Filter combines correctly with search
- [ ] Pagination resets when filter changes
- [ ] Badge colors are visually distinct
- [ ] Keyboard navigation works for dropdown

---

*Technical Specification v1.0 • Generated from product_spec.md*
