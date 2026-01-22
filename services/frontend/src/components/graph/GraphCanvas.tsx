'use client';

import React, { useEffect, useRef } from 'react';
import cytoscape, { Core, NodeDefinition, EdgeDefinition } from 'cytoscape';
import type { IdentityGraph, GraphNode, GraphEdge } from '@/types/graph';

interface GraphCanvasProps {
  graph: IdentityGraph | undefined;
  onNodeSelect: (node: GraphNode) => void;
  selectedNodeId?: string;
}

// Color scheme for node types
const nodeColors: Record<string, string> = {
  User: '#6366F1',      // Indigo
  Fragment: '#3B82F6',  // Blue
  Credential: '#8B5CF6', // Purple
  Claim: '#10B981',     // Green
  Context: '#F59E0B',   // Amber
};

// Shape for node types
const nodeShapes: Record<string, string> = {
  User: 'star',
  Fragment: 'hexagon',
  Credential: 'diamond',
  Claim: 'ellipse',
  Context: 'rectangle',
};

export function GraphCanvas({ graph, onNodeSelect, selectedNodeId }: GraphCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!containerRef.current || !graph) return;

    // Convert graph data to Cytoscape format
    const nodes: NodeDefinition[] = graph.nodes.map((node) => ({
      data: {
        id: node.nodeId,
        label: getNodeLabel(node),
        type: node.nodeType,
        ...node.properties,
      },
    }));

    const edges: EdgeDefinition[] = graph.edges.map((edge) => ({
      data: {
        id: edge.edgeId,
        source: edge.sourceId,
        target: edge.targetId,
        type: edge.edgeType,
        confidence: edge.confidence,
      },
    }));

    // Initialize or update Cytoscape
    if (!cyRef.current) {
      cyRef.current = cytoscape({
        container: containerRef.current,
        elements: { nodes, edges },
        style: getCytoscapeStyles() as any,
        layout: {
          name: 'cose',
          animate: true,
          animationDuration: 500,
          nodeRepulsion: () => 8000,
          idealEdgeLength: () => 100,
        },
      });

      // Node click handler
      cyRef.current.on('tap', 'node', (event) => {
        const nodeId = event.target.id();
        const node = graph.nodes.find((n) => n.nodeId === nodeId);
        if (node) onNodeSelect(node);
      });
    } else {
      // Update elements
      cyRef.current.json({ elements: { nodes, edges } });
      cyRef.current.layout({ name: 'cose', animate: true }).run();
    }

    // Highlight selected node
    if (selectedNodeId) {
      cyRef.current.nodes().removeClass('selected');
      cyRef.current.$(`#${selectedNodeId}`).addClass('selected');
    }

    return () => {
      // Cleanup on unmount
    };
  }, [graph, onNodeSelect, selectedNodeId]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, []);

  if (!graph || graph.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50 rounded-lg">
        <div className="text-center text-gray-500">
          <p className="text-lg font-medium">No identity data yet</p>
          <p className="text-sm">Upload a Verifiable Credential to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="w-full h-full bg-gray-50 rounded-lg" />
  );
}

function getNodeLabel(node: GraphNode): string {
  const props = node.properties;
  
  switch (node.nodeType) {
    case 'Credential':
      return String(props.credential_type || 'Credential');
    case 'Claim':
      return `${props.attribute}: ${String(props.value).slice(0, 20)}`;
    case 'User':
      return 'You';
    default:
      return node.nodeType;
  }
}

function getCytoscapeStyles() {
  return [
    // Base node style
    {
      selector: 'node',
      style: {
        'background-color': '#6366F1',
        'label': 'data(label)',
        'text-valign': 'bottom',
        'text-halign': 'center',
        'font-size': 10,
        'text-margin-y': 5,
        'width': 40,
        'height': 40,
      },
    },
    // Node types
    {
      selector: 'node[type="User"]',
      style: {
        'background-color': nodeColors.User,
        'shape': nodeShapes.User as any,
        'width': 50,
        'height': 50,
      },
    },
    {
      selector: 'node[type="Credential"]',
      style: {
        'background-color': nodeColors.Credential,
        'shape': nodeShapes.Credential as any,
      },
    },
    {
      selector: 'node[type="Claim"]',
      style: {
        'background-color': nodeColors.Claim,
        'shape': nodeShapes.Claim as any,
        'width': 30,
        'height': 30,
      },
    },
    {
      selector: 'node[type="Fragment"]',
      style: {
        'background-color': nodeColors.Fragment,
        'shape': nodeShapes.Fragment as any,
      },
    },
    // Selected node
    {
      selector: 'node.selected',
      style: {
        'border-width': 3,
        'border-color': '#1F2937',
      },
    },
    // Base edge style
    {
      selector: 'edge',
      style: {
        'width': 2,
        'line-color': '#9CA3AF',
        'target-arrow-color': '#9CA3AF',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
      },
    },
    // Edge types
    {
      selector: 'edge[type="SUPPORTS"]',
      style: {
        'line-color': '#10B981',
        'target-arrow-color': '#10B981',
      },
    },
    {
      selector: 'edge[type="CONTRADICTS"]',
      style: {
        'line-color': '#EF4444',
        'target-arrow-color': '#EF4444',
        'line-style': 'dashed',
      },
    },
    {
      selector: 'edge[type="BELONGS_TO"]',
      style: {
        'line-color': '#6366F1',
        'target-arrow-color': '#6366F1',
      },
    },
  ];
}
