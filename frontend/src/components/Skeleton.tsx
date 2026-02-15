'use client';

export function SkeletonCard() {
  return (
    <div className="animate-pulse bg-gray-100 rounded-lg p-4 space-y-3">
      <div className="h-4 bg-gray-200 rounded w-3/4" />
      <div className="h-3 bg-gray-200 rounded w-1/2" />
      <div className="h-3 bg-gray-200 rounded w-2/3" />
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="animate-pulse space-y-3">
      <div className="h-8 bg-gray-200 rounded" />
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-10 bg-gray-100 rounded" />
      ))}
    </div>
  );
}

export function SkeletonKPI() {
  return (
    <div className="animate-pulse bg-gray-100 rounded-lg p-4 text-center space-y-2">
      <div className="h-8 bg-gray-200 rounded w-1/2 mx-auto" />
      <div className="h-3 bg-gray-200 rounded w-3/4 mx-auto" />
    </div>
  );
}
