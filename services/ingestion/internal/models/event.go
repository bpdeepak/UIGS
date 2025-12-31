// Package models defines data structures for the ingestion service.
package models

import (
	"time"
)

// SourceType represents the type of identity signal source.
type SourceType string

const (
	SourceTypeVC     SourceType = "VC"
	SourceTypeOIDC   SourceType = "OIDC"
	SourceTypeManual SourceType = "MANUAL"
)

// IngestionEvent represents an ingested identity signal.
type IngestionEvent struct {
	EventID    string     `json:"event_id" db:"event_id"`
	UserID     string     `json:"user_id" db:"user_id"`
	SourceType SourceType `json:"source_type" db:"source_type"`
	RawPayload []byte     `json:"raw_payload" db:"raw_payload"`
	Checksum   string     `json:"checksum" db:"checksum"`
	CreatedAt  time.Time  `json:"created_at" db:"created_at"`
}

// IngestionRequest represents the incoming request for credential ingestion.
type IngestionRequest struct {
	// SourceType indicates the type of credential (VC, OIDC, MANUAL)
	SourceType SourceType `json:"source_type" binding:"required,oneof=VC OIDC MANUAL"`
	
	// Payload contains the credential data
	Payload map[string]interface{} `json:"payload" binding:"required"`
}

// IngestionResponse represents the response after successful ingestion.
type IngestionResponse struct {
	EventID   string    `json:"event_id"`
	Status    string    `json:"status"`
	Message   string    `json:"message,omitempty"`
	CreatedAt time.Time `json:"created_at"`
}

// QueueMessage represents the message published to RabbitMQ.
type QueueMessage struct {
	EventID    string                 `json:"event_id"`
	UserID     string                 `json:"user_id"`
	SourceType SourceType             `json:"source_type"`
	Payload    map[string]interface{} `json:"payload"`
	Timestamp  time.Time              `json:"timestamp"`
}
