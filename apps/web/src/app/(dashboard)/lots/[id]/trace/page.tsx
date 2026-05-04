'use client'

import { use } from 'react'
import { TopBar } from '@/components/layout/TopBar'
import { LotTree } from '@/components/lot/LotTree'
import { useLotTraceBackward, useLotTraceForward } from '@/hooks/use-lot-trace'
import type { LotTraceNode, LotType, LotStatus } from '@/lib/api/types'

interface Props {
  params: Promise<{ id: string }>
}

function TraceSkeletonCard() {
  return (
    <div className="rounded-lg border bg-card p-4 animate-pulse space-y-2">
      <div className="h-4 bg-muted rounded w-1/3" />
      <div className="h-3 bg-muted rounded w-2/3" />
      <div className="h-3 bg-muted rounded w-1/2" />
    </div>
  )
}

function buildTreeFromNodes(
  rootId: string,
  rootCode: string,
  rootType: LotType,
  rootStatus: LotStatus,
  rootQty: number,
  rootUnit: string,
  nodes: LotTraceNode[]
) {
  return {
    lotId: rootId,
    lotCode: rootCode,
    productName: rootId,
    type: rootType,
    status: rootStatus,
    qty: rootQty,
    unit: rootUnit,
    depth: 0,
    children: nodes.map((node) => ({
      lotId: node.lot.id,
      lotCode: node.lot.code,
      productName: node.lot.product_id ?? node.lot.id,
      type: node.lot.type,
      status: node.lot.status,
      qty: Number(node.lot.qty),
      unit: node.lot.unit,
      depth: node.depth,
    })),
  }
}

export default function LotTracePage({ params }: Props) {
  const { id } = use(params)

  const {
    data: backwardData,
    isLoading: backwardLoading,
    error: backwardError,
  } = useLotTraceBackward(id)

  const {
    data: forwardData,
    isLoading: forwardLoading,
    error: forwardError,
  } = useLotTraceForward(id)

  return (
    <div className="flex flex-col min-h-full">
      <TopBar
        title="LOT 계보 추적"
        subtitle={`LOT ID: ${id}`}
      />

      <div className="flex-1 p-6 space-y-6">
        {/* Backward Trace */}
        <section>
          <h2 className="text-sm font-semibold text-muted-foreground mb-3">
            역추적 (완제품 → 원자재)
          </h2>
          {backwardLoading ? (
            <TraceSkeletonCard />
          ) : backwardError ? (
            <div className="rounded-lg border border-critical/30 bg-critical-bg p-4 text-sm text-critical">
              역추적 조회 실패: {backwardError.message}
            </div>
          ) : backwardData ? (
            <>
              <p className="text-xs text-muted-foreground mb-2">
                조회 시간: {backwardData.query_ms}ms · 조상 LOT {backwardData.ancestors.length}개
              </p>
              <LotTree
                root={buildTreeFromNodes(
                  backwardData.target_lot.id,
                  backwardData.target_lot.code,
                  backwardData.target_lot.type,
                  backwardData.target_lot.status,
                  Number(backwardData.target_lot.qty),
                  backwardData.target_lot.unit,
                  backwardData.ancestors
                )}
              />
            </>
          ) : null}
        </section>

        {/* Forward Trace */}
        <section>
          <h2 className="text-sm font-semibold text-muted-foreground mb-3">
            전방추적 (원자재 → 완제품)
          </h2>
          {forwardLoading ? (
            <TraceSkeletonCard />
          ) : forwardError ? (
            <div className="rounded-lg border border-critical/30 bg-critical-bg p-4 text-sm text-critical">
              전방추적 조회 실패: {forwardError.message}
            </div>
          ) : forwardData ? (
            <>
              <p className="text-xs text-muted-foreground mb-2">
                조회 시간: {forwardData.query_ms}ms · 영향 FG LOT {forwardData.affected_fg_lots.length}개
              </p>
              <LotTree
                root={buildTreeFromNodes(
                  forwardData.source_lot.id,
                  forwardData.source_lot.code,
                  forwardData.source_lot.type,
                  forwardData.source_lot.status,
                  Number(forwardData.source_lot.qty),
                  forwardData.source_lot.unit,
                  forwardData.affected_fg_lots
                )}
              />
            </>
          ) : null}
        </section>
      </div>
    </div>
  )
}
