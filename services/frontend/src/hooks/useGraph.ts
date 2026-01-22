'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { graphqlClient, GET_IDENTITY_GRAPH, GET_CONFLICTS, PROCESS_EVENTS } from '@/lib/graphql-client';
import type { IdentityGraph, Conflict, ProcessingResult } from '@/types/graph';

interface GraphQueryResponse {
  identityGraph: IdentityGraph;
}

interface ConflictsQueryResponse {
  conflicts: Conflict[];
}

interface ProcessEventsResponse {
  processPendingEvents: ProcessingResult;
}

export function useGraph(userId?: string) {
  const queryClient = useQueryClient();

  const graphQuery = useQuery<GraphQueryResponse>({
    queryKey: ['identity-graph', userId],
    queryFn: () => graphqlClient.request(GET_IDENTITY_GRAPH, { userId }),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const conflictsQuery = useQuery<ConflictsQueryResponse>({
    queryKey: ['conflicts', userId],
    queryFn: () => graphqlClient.request(GET_CONFLICTS, { userId }),
  });

  const processEventsMutation = useMutation<ProcessEventsResponse, Error, number>({
    mutationFn: (maxMessages: number) =>
      graphqlClient.request(PROCESS_EVENTS, { maxMessages }),
    onSuccess: () => {
      // Invalidate and refetch graph data
      queryClient.invalidateQueries({ queryKey: ['identity-graph'] });
      queryClient.invalidateQueries({ queryKey: ['conflicts'] });
    },
  });

  return {
    graph: graphQuery.data?.identityGraph,
    conflicts: conflictsQuery.data?.conflicts ?? [],
    isLoading: graphQuery.isLoading,
    isError: graphQuery.isError,
    error: graphQuery.error,
    refetch: () => {
      graphQuery.refetch();
      conflictsQuery.refetch();
    },
    processEvents: processEventsMutation.mutate,
    isProcessing: processEventsMutation.isPending,
  };
}
