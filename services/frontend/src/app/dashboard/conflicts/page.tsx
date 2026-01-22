'use client';

import { Header } from '@/components/layout/Header';
import { ConflictPanel } from '@/components/conflicts/ConflictPanel';
import { useGraph } from '@/hooks/useGraph';

export default function ConflictsPage() {
  const { conflicts, isLoading, refetch } = useGraph();

  return (
    <div className="h-screen flex flex-col">
      <Header
        title="Conflicts"
        onRefresh={refetch}
      />

      <div className="flex-1 p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
          </div>
        ) : (
          <ConflictPanel
            conflicts={conflicts}
            onResolve={(conflictId, preferredClaimId) => {
              console.log('Resolve conflict:', conflictId, preferredClaimId);
              // TODO: Call mutation
              refetch();
            }}
          />
        )}
      </div>
    </div>
  );
}
