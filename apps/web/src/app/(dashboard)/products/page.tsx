'use client'

import { useQuery } from '@tanstack/react-query'
import { TopBar } from '@/components/layout/TopBar'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api/client'
import type { Product } from '@/lib/api/types'

async function fetchProducts(): Promise<Product[]> {
  const { data } = await apiClient.get<Product[]>('/api/v1/products')
  return data
}

export default function ProductsPage() {
  const { data: products, isLoading, error } = useQuery({
    queryKey: ['products'],
    queryFn: fetchProducts,
  })

  return (
    <div className="flex flex-col h-full">
      <TopBar title="제품 / BOM 관리" />
      <div className="flex-1 p-6 overflow-auto">
        {isLoading && (
          <p className="text-muted-foreground text-sm">로딩 중...</p>
        )}
        {error && (
          <p className="text-destructive text-sm">데이터를 불러오지 못했습니다.</p>
        )}
        {products && (
          <div className="rounded-md border border-border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted text-muted-foreground">
                <tr>
                  <th className="px-4 py-2 text-left font-medium">제품코드</th>
                  <th className="px-4 py-2 text-left font-medium">제품명</th>
                  <th className="px-4 py-2 text-left font-medium">카테고리</th>
                  <th className="px-4 py-2 text-left font-medium">단위</th>
                  <th className="px-4 py-2 text-left font-medium">유효기간(일)</th>
                  <th className="px-4 py-2 text-left font-medium">활성여부</th>
                </tr>
              </thead>
              <tbody>
                {products.map((product) => (
                  <tr
                    key={product.id}
                    className="border-t border-border hover:bg-muted/50 cursor-pointer transition-colors"
                    onClick={() => console.log('product selected:', product)}
                  >
                    <td className="px-4 py-2 font-mono text-xs">{product.code}</td>
                    <td className="px-4 py-2">{product.name}</td>
                    <td className="px-4 py-2 text-muted-foreground">
                      {product.category ?? '-'}
                    </td>
                    <td className="px-4 py-2">{product.unit}</td>
                    <td className="px-4 py-2">
                      {product.shelf_life_days != null ? product.shelf_life_days : '-'}
                    </td>
                    <td className="px-4 py-2">
                      <Badge variant={product.is_active ? 'default' : 'secondary'}>
                        {product.is_active ? '활성' : '비활성'}
                      </Badge>
                    </td>
                  </tr>
                ))}
                {products.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-4 py-6 text-center text-muted-foreground">
                      등록된 제품이 없습니다.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
