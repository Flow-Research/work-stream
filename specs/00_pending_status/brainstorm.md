# Brainstorm: Task Pending Status

## Core Idea

Add a "Pending" status to Tasks that serves as the default state for newly created tasks that haven't been started or assigned yet. This enables users to distinguish between tasks in the backlog versus tasks actively being worked on.

## Problem Statement

Currently, tasks lack a clear "waiting to start" state. Users need a way to:
- Identify tasks that exist but haven't been picked up
- Filter the Tasks UI to focus on pending/backlog items
- Track the full lifecycle of a task from creation to completion

## Proposed Status Flow

```
Pending → Assigned → In Progress → Review → Completed
```

| Status | Description |
|--------|-------------|
| **Pending** | Task created but not yet started or assigned (default) |
| **Assigned** | Task has been assigned to someone |
| **In Progress** | Active work is happening |
| **Review** | Work submitted, awaiting review |
| **Completed** | Task finished and approved |

## Key Features

### 1. Pending as Default Status
- When a task is created, it automatically starts in "Pending" status
- No manual intervention required to set initial state

### 2. Status Filtering in Tasks UI
- Single-select dropdown filter in the Tasks list page
- Options: All, Pending, Assigned, In Progress, Review, Completed
- "All" selected by default to show everything
- Filter persists during the session

### 3. Visual Status Indicators
- Status badge displayed on task cards in the list view
- Consistent color coding across the UI
- Status visible in task detail view

## Target Users

- **Task creators** — Want to see which tasks are still waiting to be picked up
- **Task workers** — Want to filter to find available (pending) tasks to claim
- **Administrators** — Want overview of task pipeline and bottlenecks

## Success Criteria

- [ ] Tasks created with "Pending" as default status
- [ ] Status dropdown filter functional in Tasks UI
- [ ] Filter correctly shows only tasks matching selected status
- [ ] Status badge visible on task cards
- [ ] Smooth transitions between status states

## Existing System Context

**Note:** The current codebase has an existing status system:
- **Task statuses:** `draft`, `funded`, `decomposed`, `in_progress`, `in_review`, `completed`, `cancelled`, `disputed`
- **Subtask statuses:** `open`, `claimed`, `in_progress`, `submitted`, `approved`, `rejected`, `disputed`

The implementation will need to determine whether to:
1. Add "Pending" alongside existing statuses
2. Replace/consolidate the existing status flow
3. Map "Pending" to an existing status (e.g., `draft` or `open`)

This decision should be addressed in the PRD phase.

## Open Questions

- Should "Pending" replace the existing `draft` status or coexist with it?
- How does "Assigned" map to the existing `claimed` concept for subtasks?
- Should cancelled/disputed statuses be included in the filter dropdown?

## References

- Tasks UI: `frontend/src/pages/Tasks.tsx`
- Task types: `frontend/src/types/index.ts`
- Task model: `backend/app/models/task.py`
- Task API: `backend/app/api/routes/tasks.py`

---

*Generated from brainstorming session*
