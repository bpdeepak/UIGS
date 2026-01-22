'use client';

import { X } from 'lucide-react';
import type { GraphNode } from '@/types/graph';

interface NodeDetailsProps {
  node: GraphNode;
  onClose: () => void;
}

export function NodeDetails({ node, onClose }: NodeDetailsProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-4 min-w-80">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {node.nodeType}
        </h3>
        <button
          onClick={onClose}
          className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X size={20} />
        </button>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Node ID</p>
          <p className="text-sm font-mono text-gray-700 break-all">{node.nodeId}</p>
        </div>

        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Type</p>
          <span className={`inline-block px-2 py-1 text-xs font-medium rounded ${getTypeBadgeColor(node.nodeType)}`}>
            {node.nodeType}
          </span>
        </div>

        {Object.entries(node.properties).map(([key, value]) => (
          <div key={key}>
            <p className="text-xs text-gray-500 uppercase tracking-wide">{formatKey(key)}</p>
            <p className="text-sm text-gray-700 break-words">
              {formatValue(value)}
            </p>
          </div>
        ))}

        {node.createdAt && (
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Created At</p>
            <p className="text-sm text-gray-700">
              {new Date(node.createdAt).toLocaleString()}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function getTypeBadgeColor(type: string): string {
  const colors: Record<string, string> = {
    User: 'bg-indigo-100 text-indigo-800',
    Fragment: 'bg-blue-100 text-blue-800',
    Credential: 'bg-purple-100 text-purple-800',
    Claim: 'bg-green-100 text-green-800',
    Context: 'bg-amber-100 text-amber-800',
  };
  return colors[type] || 'bg-gray-100 text-gray-800';
}

function formatKey(key: string): string {
  return key.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '-';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}
