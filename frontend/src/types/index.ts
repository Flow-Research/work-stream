export interface User {
  id: string
  wallet_address: string
  name: string
  country: string
  bio?: string
  skills?: string[]
  id_verified: boolean
  id_verified_at?: string
  reputation_score: number
  reputation_tier: string
  tasks_completed: number
  tasks_approved: number
  is_admin: boolean
  is_banned: boolean
  created_at: string
  updated_at: string
}

export interface ReferenceItem {
  id: string
  type: string
  title: string
  url: string
  description?: string
  required: boolean
}

export interface AttachmentItem {
  id: string
  filename: string
  mime_type: string
  size_bytes: number
  ipfs_hash: string
  description?: string
  uploaded_at?: string
  uploaded_by?: string
}

export interface DeliverableItem {
  id: string
  title: string
  description: string
  type: string
  required: boolean
  format_hint?: string
}

export interface Task {
  id: string
  title: string
  description: string
  description_html?: string
  research_question: string
  background_context?: string
  methodology_notes?: string
  expected_outcomes?: string[]
  references?: ReferenceItem[]
  attachments?: AttachmentItem[]
  client_id: string
  status: TaskStatus
  total_budget_cngn: string
  escrow_tx_hash?: string
  escrow_contract_task_id?: number
  skills_required?: string[]
  deadline?: string
  created_at: string
  updated_at: string
  funded_at?: string
  completed_at?: string
  subtasks?: SubtaskBrief[]
}

export type TaskStatus = 
  | 'draft'
  | 'funded'
  | 'decomposed'
  | 'in_progress'
  | 'in_review'
  | 'completed'
  | 'cancelled'
  | 'disputed'

export interface SubtaskBrief {
  id: string
  title: string
  subtask_type: SubtaskType
  status: SubtaskStatus
  budget_cngn: string
  claimed_by?: string
}

export interface Subtask {
  id: string
  task_id: string
  title: string
  description: string
  description_html?: string
  deliverables?: DeliverableItem[]
  acceptance_criteria?: string[]
  references?: ReferenceItem[]
  attachments?: AttachmentItem[]
  example_output?: string
  tools_required?: string[]
  estimated_hours?: string
  subtask_type: SubtaskType
  sequence_order: number
  budget_allocation_percent: string
  budget_cngn: string
  status: SubtaskStatus
  claimed_by?: string
  claimed_at?: string
  collaborators?: string[]
  collaborator_splits?: string[]
  submitted_at?: string
  approved_at?: string
  approved_by?: string
  auto_approved: boolean
  deadline?: string
  created_at: string
  updated_at: string
}

export type SubtaskType = 
  | 'discovery'
  | 'extraction'
  | 'mapping'
  | 'assembly'
  | 'narrative'

export type SubtaskStatus = 
  | 'open'
  | 'claimed'
  | 'in_progress'
  | 'submitted'
  | 'approved'
  | 'rejected'
  | 'disputed'

export interface Submission {
  id: string
  subtask_id: string
  submitted_by: string
  content_summary?: string
  artifact_ipfs_hash?: string
  artifact_type?: string
  artifact_on_chain_hash?: string
  artifact_on_chain_tx?: string
  status: 'pending' | 'approved' | 'rejected'
  review_notes?: string
  reviewed_by?: string
  reviewed_at?: string
  payment_tx_hash?: string
  payment_amount_cngn?: string
  created_at: string
}

export interface Dispute {
  id: string
  subtask_id: string
  raised_by: string
  reason: string
  status: 'open' | 'resolved' | 'dismissed'
  resolution?: string
  resolved_by?: string
  resolved_at?: string
  winner_id?: string
  created_at: string
}

export interface Artifact {
  id: string
  task_id: string
  title: string
  description?: string
  artifact_type: 'dataset' | 'knowledge_graph'
  ipfs_hash: string
  on_chain_hash?: string
  on_chain_tx?: string
  schema_version?: string
  contributors: string[]
  contributor_shares: string[]
  total_earnings_cngn: string
  is_listed: boolean
  listed_price_cngn?: string
  royalty_cap_multiplier: string
  royalty_expiry_years: number
  created_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
}
