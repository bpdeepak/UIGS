/**
 * Graph Types for Identity Graph
 */

export type NodeType = 'Fragment' | 'Claim' | 'Credential' | 'Context' | 'User';
export type EdgeType = 'SUPPORTS' | 'CONTRADICTS' | 'LIKELY_SAME' | 'CONFIRMED_SAME' | 'BELONGS_TO';

export interface GraphNode {
  nodeId: string;
  nodeType: NodeType;
  properties: Record<string, unknown>;
  createdAt?: string;
  expiresAt?: string;
}

export interface GraphEdge {
  edgeId: string;
  edgeType: EdgeType;
  sourceId: string;
  targetId: string;
  confidence: number;
}

export interface IdentityGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  nodeCount: number;
  edgeCount: number;
}

export interface Conflict {
  conflictId: string;
  attribute: string;
  claimAId: string;
  claimAValue: string;
  claimBId: string;
  claimBValue: string;
}

export interface LinkSuggestion {
  sourceId: string;
  targetId: string;
  confidence: number;
  sharedAttributes: string[];
}

export interface ProcessingResult {
  success: boolean;
  messagesProcessed: number;
  errors: string[];
}
