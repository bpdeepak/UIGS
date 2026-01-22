/**
 * GraphQL Client Configuration
 */
import { GraphQLClient } from 'graphql-request';

const GRAPHQL_URL = process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:8082/graphql';

export const graphqlClient = new GraphQLClient(GRAPHQL_URL);

// GraphQL Queries
export const GET_IDENTITY_GRAPH = `
  query GetIdentityGraph($userId: String) {
    identityGraph(userId: $userId) {
      nodeCount
      edgeCount
      nodes {
        nodeId
        nodeType
        properties
      }
      edges {
        edgeId
        edgeType
        sourceId
        targetId
        confidence
      }
    }
  }
`;

export const GET_CONFLICTS = `
  query GetConflicts($userId: String) {
    conflicts(userId: $userId) {
      conflictId
      attribute
      claimAId
      claimAValue
      claimBId
      claimBValue
    }
  }
`;

export const GET_HEALTH = `
  query GetHealth {
    health {
      status
      neo4j
      rabbitmq
      timestamp
    }
  }
`;

// GraphQL Mutations
export const PROCESS_EVENTS = `
  mutation ProcessPendingEvents($maxMessages: Int!) {
    processPendingEvents(maxMessages: $maxMessages) {
      success
      messagesProcessed
      errors
    }
  }
`;

export const RESOLVE_CONFLICT = `
  mutation ResolveConflict($conflictId: String!, $preferredClaimId: String!) {
    resolveConflict(conflictId: $conflictId, preferredClaimId: $preferredClaimId)
  }
`;
