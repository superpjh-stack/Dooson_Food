'use client'

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Legend,
} from 'recharts'

interface FValueDataPoint {
  time: string
  actual?: number
  predicted?: number
}

interface FValueChartProps {
  data: FValueDataPoint[]
  threshold?: number
  targetFValue?: number
  height?: number
}

export function FValueChart({ data, threshold = 121, targetFValue = 10, height = 200 }: FValueChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: -16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
        <XAxis
          dataKey="time"
          tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip
          contentStyle={{
            background: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '6px',
            fontSize: 12,
          }}
        />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <ReferenceLine
          y={threshold}
          stroke="hsl(var(--color-critical))"
          strokeDasharray="4 2"
          label={{ value: `${threshold}°C`, fontSize: 10, fill: 'hsl(var(--color-critical))' }}
        />
        <ReferenceLine
          y={targetFValue}
          stroke="hsl(var(--color-success))"
          strokeDasharray="4 2"
          label={{ value: `F=${targetFValue}`, fontSize: 10, fill: 'hsl(var(--color-success))' }}
        />
        <Line
          type="monotone"
          dataKey="actual"
          name="실측 온도"
          stroke="hsl(var(--primary))"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4 }}
        />
        <Line
          type="monotone"
          dataKey="predicted"
          name="AI 예측"
          stroke="hsl(var(--accent))"
          strokeWidth={1.5}
          strokeDasharray="5 3"
          dot={false}
          activeDot={{ r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
