'use client';

import { AlertTriangle, CheckCircle } from 'lucide-react';
import type { Conflict } from '@/types/graph';

interface ConflictPanelProps {
  conflicts: Conflict[];
  onResolve?: (conflictId: string, preferredClaimId: string) => void;
}

export function ConflictPanel({ conflicts, onResolve }: ConflictPanelProps) {
  if (conflicts.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center">
        <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-3" />
        <h3 className="text-lg font-medium text-gray-900">No Conflicts</h3>
        <p className="text-sm text-gray-500 mt-1">
          All your identity claims are consistent
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-amber-600">
        <AlertTriangle size={20} />
        <span className="font-medium">{conflicts.length} Conflict{conflicts.length > 1 ? 's' : ''} Detected</span>
      </div>

      {conflicts.map((conflict) => (
        <div
          key={conflict.conflictId}
          className="bg-white rounded-lg shadow p-4 border-l-4 border-amber-400"
        >
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-medium text-gray-900 capitalize">
                {conflict.attribute.replace(/\./g, ' › ')}
              </h4>
              <p className="text-xs text-gray-500 mt-1">
                Different values from multiple sources
              </p>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-4">
            <ConflictOption
              value={conflict.claimAValue}
              claimId={conflict.claimAId}
              onSelect={() => onResolve?.(conflict.conflictId, conflict.claimAId)}
            />
            <ConflictOption
              value={conflict.claimBValue}
              claimId={conflict.claimBId}
              onSelect={() => onResolve?.(conflict.conflictId, conflict.claimBId)}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

interface ConflictOptionProps {
  value: string;
  claimId: string;
  onSelect?: () => void;
}

function ConflictOption({ value, claimId, onSelect }: ConflictOptionProps) {
  return (
    <button
      onClick={onSelect}
      className="p-3 rounded-lg border-2 border-gray-200 hover:border-blue-500 hover:bg-blue-50 transition-colors text-left group"
    >
      <p className="font-medium text-gray-900 group-hover:text-blue-700">
        {value}
      </p>
      <p className="text-xs text-gray-400 mt-1 font-mono truncate">
        {claimId.slice(0, 8)}...
      </p>
      <p className="text-xs text-blue-600 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
        Click to prefer this value
      </p>
    </button>
  );
}
