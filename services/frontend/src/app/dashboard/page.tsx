'use client';

import { useState } from 'react';
import { Header } from '@/components/layout/Header';
import { GraphCanvas } from '@/components/graph/GraphCanvas';
import { NodeDetails } from '@/components/graph/NodeDetails';
import { UploadModal } from '@/components/upload/UploadModal';
import { useGraph } from '@/hooks/useGraph';
import type { GraphNode } from '@/types/graph';
import { Upload, Network, AlertTriangle, FileJson } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const { graph, conflicts, isLoading, refetch, processEvents, isProcessing } = useGraph();
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [showUpload, setShowUpload] = useState(false);

  const handleRefresh = async () => {
    processEvents(100);
    refetch();
  };

  return (
    <div className="h-screen flex flex-col">
      <Header
        title="Dashboard"
        onRefresh={handleRefresh}
        isRefreshing={isProcessing}
      />

      <div className="flex-1 p-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <StatCard
            icon={<Network className="text-blue-500" />}
            label="Nodes"
            value={graph?.nodeCount ?? 0}
          />
          <StatCard
            icon={<FileJson className="text-purple-500" />}
            label="Credentials"
            value={graph?.nodes.filter((n) => n.nodeType === 'Credential').length ?? 0}
          />
          <StatCard
            icon={<AlertTriangle className="text-amber-500" />}
            label="Conflicts"
            value={conflicts.length}
            href="/dashboard/conflicts"
          />
          <button
            onClick={() => setShowUpload(true)}
            className="bg-white rounded-lg shadow p-4 flex items-center gap-3 hover:bg-gray-50 transition-colors border-2 border-dashed border-gray-300 hover:border-blue-500"
          >
            <Upload className="text-gray-400" />
            <span className="font-medium text-gray-600">Upload VC</span>
          </button>
        </div>

        {/* Main Graph Area */}
        <div className="bg-white rounded-lg shadow h-[calc(100vh-280px)] relative">
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

          {/* Node Details Panel */}
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

      {/* Upload Modal */}
      <UploadModal
        isOpen={showUpload}
        onClose={() => setShowUpload(false)}
        onSuccess={handleRefresh}
      />
    </div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  href?: string;
}

function StatCard({ icon, label, value, href }: StatCardProps) {
  const content = (
    <>
      <div className="flex items-center gap-3">
        {icon}
        <span className="text-sm text-gray-500">{label}</span>
      </div>
      <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
    </>
  );

  if (href) {
    return (
      <Link href={href} className="bg-white rounded-lg shadow p-4 hover:bg-gray-50 transition-colors">
        {content}
      </Link>
    );
  }

  return <div className="bg-white rounded-lg shadow p-4">{content}</div>;
}
