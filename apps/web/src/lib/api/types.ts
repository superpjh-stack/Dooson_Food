export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
}

export type LotStatus = 'ACTIVE' | 'ON_HOLD' | 'CONSUMED' | 'SHIPPED' | 'RECALLED'
export type LotType = 'RAW' | 'WIP' | 'FG'

export interface Lot {
  id: string
  code: string
  type: LotType
  status: LotStatus
  product_id: string | null
  work_order_id: string | null
  qty: number
  unit: string
  produced_at: string | null
  expiry_date: string | null
  storage_location: string | null
  created_at: string
}

export interface LotTraceNode {
  lot: Lot
  depth: number
  qty_used: number | null
  relation_type: string | null
}

export interface LotTraceResponse {
  target_lot: Lot
  ancestors: LotTraceNode[]
  query_ms: number
}

export interface LotForwardTraceResponse {
  source_lot: Lot
  affected_fg_lots: LotTraceNode[]
  query_ms: number
}

export type WorkOrderStatus = 'PLANNED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'

export interface WorkOrder {
  id: string
  code: string
  product_id: number | null
  production_line_id: number | null
  status: WorkOrderStatus
  planned_qty: number
  actual_qty: number
  unit: string
  planned_start: string
  planned_end: string
  actual_start: string | null
  actual_end: string | null
  bom_version: string | null
  notes: string | null
  created_at: string
  updated_at: string | null
}

export interface WorkOrderListResponse {
  items: WorkOrder[]
  total: number
}

export interface CcpRecord {
  id: string
  ccp_id: string
  work_order_id: string
  lot_id: string | null
  measured_at: string
  measured_value: number
  is_deviation: boolean
  corrective_action: string | null
  created_at: string
}

export interface XRayResult {
  id: string
  machine_id: string
  work_order_id: string
  lot_id: string | null
  inspected_at: string
  result: 'OK' | 'NG'
  contaminant_type: string | null
  contaminant_size: number | null
  confidence: number | null
  image_url: string | null
  grad_cam_url: string | null
  ai_classification: string | null
  created_at: string
}

export interface Equipment {
  id: string
  code: string
  name: string
  type: string
  line_id: number | null
  status: 'RUNNING' | 'IDLE' | 'FAULT' | 'MAINTENANCE'
  oee: number | null
  last_maintained_at: string | null
  notes: string | null
  created_at: string
  updated_at: string | null
}

export interface HaccpCheckRecord {
  id: string
  plan_id: string
  lot_id: string | null
  work_order_id: string | null
  checked_by: string
  checked_at: string
  result: 'PASS' | 'FAIL' | 'CONDITIONAL_PASS'
  measured_values: Record<string, unknown>
  corrective_action_taken: string | null
  notes: string | null
  deleted_at: string | null
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface Product {
  id: number
  code: string
  name: string
  category: string | null
  unit: string
  shelf_life_days: number | null
  is_active: boolean
}

export interface ProductionLine {
  id: number
  code: string
  name: string
  capacity_per_hour: number | null
  unit: string
  is_active: boolean
}

export interface IotSensorReading {
  id: number
  equipment_id: number
  sensor_type: string
  value: number
  unit: string
  recorded_at: string
  quality: string
}
