'use client';

import { useState } from 'react';
import { Header } from '@/components/layout/Header';
import { GraphCanvas } from '@/components/graph/GraphCanvas';
import { NodeDetails } from '@/components/graph/NodeDetails';
import { useGraph } from '@/hooks/useGraph';
import type { GraphNode } from '@/types/graph';

export default function GraphPage() {
  const { graph, isLoading, refetch, processEvents, isProcessing } = useGraph();
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  const handleRefresh = () => {
    processEvents(100);
    refetch();
  };

  return (
    <div className="h-screen flex flex-col">
      <Header
        title="Identity Graph"
        onRefresh={handleRefresh}
        isRefreshing={isProcessing}
      />

      <div className="flex-1 p-6">
        {/* Legend */}
        <div className="flex gap-4 mb-4">
          <LegendItem color="bg-indigo-500" label="User" />
          <LegendItem color="bg-purple-500" label="Credential" />
          <LegendItem color="bg-green-500" label="Claim" />
          <LegendItem color="bg-blue-500" label="Fragment" />
        </div>

        {/* Graph */}
        <div className="bg-white rounded-lg shadow h-[calc(100vh-200px)] relative">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
            </div>
          ) : (
            <GraphCanvas
              graph={graph}
              onNodeSelect={setSelectedNode}
              selectedNodeId={selectedNode?.nodeId}
            />
          )}

          {selectedNode && (
            <div className="absolute top-4 right-4 z-10">
              <NodeDetails
                node={selectedNode}
                onClose={() => setSelectedNode(null)}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className={`w-4 h-4 rounded-full ${color}`} />
      <span className="text-sm text-gray-600">{label}</span>
    </div>
  );
}
