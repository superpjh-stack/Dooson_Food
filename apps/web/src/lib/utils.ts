import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** LOT 코드에서 날짜·제품코드 파싱 */
export function parseLotCode(code: string) {
  const match = code.match(/^DS-(\d{8})-(\w+)-(\d{4})$/)
  if (!match) return null
  return { date: match[1], productCode: match[2], seq: match[3] }
}

/** AI 신뢰도 → 표시 등급 */
export function getConfidenceLevel(confidence: number): 'high' | 'medium' | 'low' | 'hidden' {
  if (confidence >= 0.8) return 'high'
  if (confidence >= 0.6) return 'medium'
  return 'hidden' // 0.6 미만은 표시하지 않음 (CONVENTIONS 규칙)
}

/** OEE 계산: 가동률 × 성능률 × 품질률 */
export function calculateOEE(availability: number, performance: number, quality: number) {
  return Number((availability * performance * quality).toFixed(4))
}

/** 숫자 포맷 (한국식 천 단위) */
export function formatNumber(value: number, decimals = 0) {
  return value.toLocaleString('ko-KR', { maximumFractionDigits: decimals })
}
