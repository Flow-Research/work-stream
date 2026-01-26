# Product Specification: Task Pending Status & Filtering

## 1. Executive Summary

**Product Name:** Task Status Filtering Enhancement

**Vision:** Provide users with a clear, intuitive way to track task lifecycle stages and filter tasks by status, starting with a "Pending" state that clearly identifies tasks waiting to be started.

**Overview:** This feature enhances the existing task status system by introducing "Pending" as the user-friendly display name for draft tasks and adding a single-select status filter dropdown to the Tasks UI. Users will be able to quickly identify backlog items and focus their view on tasks in specific stages of completion.

**Key Value Proposition:** Improved task discoverability and workflow visibility, enabling users to efficiently manage their task pipeline from creation through completion.

---

## 2. Problem Statement

### Current Pain Points

1. **Unclear task states** — The current `draft` status is technical jargon that doesn't clearly communicate "waiting to be started" to end users
2. **No focused filtering** — Users cannot easily filter the task list to show only tasks in a specific state
3. **Pipeline visibility** — Administrators and task creators lack a quick way to see bottlenecks (e.g., how many tasks are stuck pending vs. in progress)

### User Impact

- **Task creators** waste time scrolling through all tasks to find pending ones
- **Workers** cannot easily discover available tasks to claim
- **Administrators** lack quick insights into task distribution across statuses

### Business Impact

- Reduced platform efficiency as users struggle to find relevant tasks
- Potential for tasks to be "lost" in pending state without visibility

---

## 3. Target Users & Personas

### Primary Persona: Task Worker (Contributor)

| Attribute | Description |
|-----------|-------------|
| **Role** | Freelancer or researcher looking for tasks to claim |
| **Goal** | Find available pending tasks that match their skills |
| **Pain Point** | Currently scrolls through all tasks; no way to see only unclaimed work |
| **Success** | Can filter to "Pending" and immediately see available tasks |

### Secondary Persona: Task Creator (Client)

| Attribute | Description |
|-----------|-------------|
| **Role** | User who creates and funds research tasks |
| **Goal** | Monitor which of their tasks are still pending vs. in progress |
| **Pain Point** | No quick overview of task pipeline status |
| **Success** | Can filter to see pending tasks and take action to promote them |

### Tertiary Persona: Administrator

| Attribute | Description |
|-----------|-------------|
| **Role** | Platform admin managing the overall task ecosystem |
| **Goal** | Understand task distribution and identify bottlenecks |
| **Pain Point** | No status-based filtering to analyze task pipeline |
| **Success** | Can filter by any status to generate insights |

---

## 4. Feature Requirements

### 4.1 Pending Status Display (P0 - Must Have)

**Requirement:** Display "Pending" as the user-facing label for tasks in `draft` status.

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| F1.1 | Status badge shows "Pending" for draft tasks | Badge displays "Pending" text with appropriate styling |
| F1.2 | Consistent across all views | Task list, task detail, and any status references use "Pending" |
| F1.3 | Color coding | Pending status uses a neutral/gray color to indicate "not started" |

**[ASSUMPTION]** "Pending" is a display-name alias for the existing `draft` status. No database schema changes required.

### 4.2 Status Filter Dropdown (P0 - Must Have)

**Requirement:** Add a single-select dropdown filter to the Tasks list page.

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| F2.1 | Dropdown placement | Filter appears in the existing filter bar area, near search |
| F2.2 | Filter options | All, Pending, Funded, In Progress, In Review, Completed, Cancelled, Disputed |
| F2.3 | Default selection | "All" is selected by default |
| F2.4 | Filter behavior | Selecting a status immediately filters the task list |
| F2.5 | URL persistence | Filter state reflected in URL query params for shareability |
| F2.6 | Combined with search | Filter works in conjunction with existing search functionality |

### 4.3 Status Badge Enhancement (P1 - Should Have)

**Requirement:** Ensure all status badges have consistent, distinct styling.

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| F3.1 | Color scheme | Each status has a unique, accessible color |
| F3.2 | Badge visibility | Badges are clearly visible on task cards |
| F3.3 | Hover state | Optional: tooltip showing status description on hover |

**Proposed Color Mapping:**

| Status | Color | Rationale |
|--------|-------|-----------|
| Pending | Gray (`badge-gray`) | Neutral, not yet active |
| Funded | Blue (`badge-info`) | Ready, positive state |
| In Progress | Amber (`badge-warning`) | Active, attention |
| In Review | Purple (`badge-secondary`) | Different stage, review |
| Completed | Green (`badge-success`) | Positive completion |
| Cancelled | Red (`badge-error`) | Negative terminal state |
| Disputed | Red (`badge-error`) | Requires attention |

---

## 5. User Experience & Design

### 5.1 Tasks List Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Tasks                                          [+ Create]  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌─────────────────────────────────────┐  │
│  │ Status: All ▼│  │ 🔍 Search tasks...                  │  │
│  └──────────────┘  └─────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐│
│  │ [Pending] Research quantum computing applications      ││
│  │ Budget: 500 CNGN • 3 subtasks • Created 2 days ago     ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │ [In Progress] Analyze market trends for AI startups    ││
│  │ Budget: 1,200 CNGN • 5 subtasks • 60% complete         ││
│  └─────────────────────────────────────────────────────────┘│
│  ...                                                        │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Filter Dropdown States

**Closed State:**
```
┌──────────────────┐
│ Status: All    ▼ │
└──────────────────┘
```

**Open State:**
```
┌──────────────────┐
│ Status: All    ▲ │
├──────────────────┤
│ ● All            │
│ ○ Pending        │
│ ○ Funded         │
│ ○ In Progress    │
│ ○ In Review      │
│ ○ Completed      │
│ ○ Cancelled      │
│ ○ Disputed       │
└──────────────────┘
```

### 5.3 Interaction Flow

1. User lands on Tasks page → sees all tasks (default)
2. User clicks Status dropdown → options appear
3. User selects "Pending" → dropdown closes, list updates to show only pending tasks
4. URL updates to `?status=draft` for bookmarking/sharing
5. User can combine with search: `?status=draft&search=quantum`

---

## 6. Technical Requirements

### 6.1 Frontend Changes

| Component | Change Required |
|-----------|-----------------|
| `frontend/src/types/index.ts` | Add status display name mapping |
| `frontend/src/pages/Tasks.tsx` | Add status dropdown filter, update query params |
| `frontend/src/components/StatusBadge.tsx` | [ASSUMPTION] Create or update badge component for consistency |

### 6.2 Backend Changes

| Component | Change Required |
|-----------|-----------------|
| `backend/app/api/routes/tasks.py` | Verify existing `status_filter` param handles all statuses |
| No schema changes | [ASSUMPTION] Reusing existing `draft` status as "Pending" |

### 6.3 API Contract

**Existing Endpoint (no changes expected):**
```
GET /api/tasks?status_filter=draft&search=&page=1&limit=20
```

**Response includes tasks where `status == 'draft'`**

---

## 7. Data Requirements

### 7.1 No New Data Models

This feature reuses existing data structures:
- `Task.status` field already exists with `draft` as a valid value
- No migration required

### 7.2 Display Name Mapping (Frontend Only)

```typescript
const STATUS_DISPLAY_NAMES: Record<TaskStatus, string> = {
  draft: 'Pending',
  funded: 'Funded',
  decomposed: 'Decomposed',
  in_progress: 'In Progress',
  in_review: 'In Review',
  completed: 'Completed',
  cancelled: 'Cancelled',
  disputed: 'Disputed',
};
```

---

## 8. Integration Requirements

### 8.1 Existing Integrations (No Changes)

- React Query caching will automatically handle filtered queries
- Existing pagination works with status filter

### 8.2 URL State Management

- Filter state must sync with URL query parameters
- Browser back/forward should respect filter state

---

## 9. Non-Functional Requirements

### 9.1 Performance

| Requirement | Target |
|-------------|--------|
| Filter response time | < 200ms (existing indexed query) |
| UI update | Immediate (optimistic, no loading state for dropdown) |

### 9.2 Accessibility

| Requirement | Implementation |
|-------------|----------------|
| Keyboard navigation | Dropdown navigable with arrow keys, Enter to select |
| Screen reader | Dropdown announces selected status, options list |
| Color contrast | All status badge colors meet WCAG AA (4.5:1 ratio) |

### 9.3 Browser Support

- Chrome, Firefox, Safari, Edge (latest 2 versions)
- Mobile responsive

---

## 10. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Filter usage rate | 30% of task page visits use filter | Analytics event on filter change |
| Task discovery time | 50% reduction | User testing comparison |
| Pending task visibility | 100% of pending tasks show correct badge | QA verification |

---

## 11. MVP Scope

### In Scope (MVP)

- [x] "Pending" display name for `draft` status
- [x] Single-select status dropdown filter
- [x] URL query param persistence
- [x] Status badge color consistency
- [x] Combined search + filter functionality

### Out of Scope (Future)

- [ ] Multi-select status filter
- [ ] Status change from task list (bulk actions)
- [ ] Status-based notifications
- [ ] Saved filter presets
- [ ] Status history/audit trail

---

## 12. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Existing code uses `draft` terminology | Medium | Low | Use display mapping; keep `draft` in code/API |
| Users confused by status names | Low | Medium | Add tooltips with descriptions |
| Filter performance on large datasets | Low | Medium | Existing status index handles this |

---

## 13. Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Existing task status field | Technical | Available |
| Existing filter infrastructure | Technical | Partially available (search exists) |
| Design system badge component | Design | [ASSUMPTION] Exists or will be created |

---

## 14. Release Strategy

### Phase 1: MVP Release

1. Deploy "Pending" display name
2. Deploy status dropdown filter
3. Monitor usage and gather feedback

### Phase 2: Iteration (if needed)

1. Address user feedback
2. Consider multi-select filter if requested
3. Add status descriptions/tooltips

---

## 15. Open Questions & Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Should "Pending" replace `draft` in database? | No | Minimize risk; display-only change |
| Include `decomposed` in filter? | Yes | Part of existing status system |
| Show task count per status in dropdown? | Future | Nice-to-have, not MVP |

---

## Appendix A: Status State Machine

```
                    ┌─────────────┐
                    │   Pending   │ (draft)
                    │   (start)   │
                    └──────┬──────┘
                           │ fund
                           ▼
                    ┌─────────────┐
                    │   Funded    │
                    └──────┬──────┘
                           │ decompose
                           ▼
                    ┌─────────────┐
                    │ Decomposed  │
                    └──────┬──────┘
                           │ start work
                           ▼
                    ┌─────────────┐
          ┌────────│ In Progress │────────┐
          │        └──────┬──────┘        │
          │ dispute       │ submit        │ cancel
          ▼               ▼               ▼
    ┌──────────┐   ┌─────────────┐  ┌───────────┐
    │ Disputed │   │  In Review  │  │ Cancelled │
    └──────────┘   └──────┬──────┘  └───────────┘
                          │ approve
                          ▼
                   ┌─────────────┐
                   │  Completed  │
                   │    (end)    │
                   └─────────────┘
```

---

## Appendix B: References

- Brainstorm: `specs/00-pending/brainstorm.md`
- Tasks UI: `frontend/src/pages/Tasks.tsx`
- Task Types: `frontend/src/types/index.ts`
- Task Model: `backend/app/models/task.py`
- Task API: `backend/app/api/routes/tasks.py`

---

*Generated from brainstorm.md • PRD v1.0*
