// Package handlers provides HTTP request handlers for the ingestion service.
package handlers

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"log/slog"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/uigs/ingestion/internal/models"
	"github.com/uigs/ingestion/internal/queue"
	"github.com/uigs/ingestion/internal/repository"
)

// IngestHandler handles credential ingestion requests.
type IngestHandler struct {
	repo   repository.EventRepository
	queue  queue.Publisher
	logger *slog.Logger
}

// NewIngestHandler creates a new ingest handler.
func NewIngestHandler(repo repository.EventRepository, q queue.Publisher, logger *slog.Logger) *IngestHandler {
	return &IngestHandler{
		repo:   repo,
		queue:  q,
		logger: logger,
	}
}

// HandleIngest processes incoming credential ingestion requests.
// POST /api/v1/ingest
func (h *IngestHandler) HandleIngest(c *gin.Context) {
	var req models.IngestionRequest

	// Parse request body
	if err := c.ShouldBindJSON(&req); err != nil {
		h.logger.Warn("Invalid request body", "error", err)
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "invalid_request",
			"message": "Invalid request body: " + err.Error(),
		})
		return
	}

	// Get user ID from context (set by auth middleware)
	// For now, use a default test user if not authenticated
	userID := c.GetString("user_id")
	if userID == "" {
		userID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11" // Default test user
	}

	// Generate event ID
	eventID := uuid.New().String()

	// Marshal payload for storage
	payloadBytes, err := json.Marshal(req.Payload)
	if err != nil {
		h.logger.Error("Failed to marshal payload", "error", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "internal_error",
			"message": "Failed to process payload",
		})
		return
	}

	// Calculate checksum for integrity
	checksum := calculateChecksum(payloadBytes)

	// Create event
	now := time.Now().UTC()
	event := &models.IngestionEvent{
		EventID:    eventID,
		UserID:     userID,
		SourceType: req.SourceType,
		RawPayload: payloadBytes,
		Checksum:   checksum,
		CreatedAt:  now,
	}

	// Store in PostgreSQL
	if err := h.repo.CreateEvent(c.Request.Context(), event); err != nil {
		h.logger.Error("Failed to store event", "error", err, "event_id", eventID)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "storage_error",
			"message": "Failed to store event",
		})
		return
	}

	// Publish to RabbitMQ
	queueMsg := &models.QueueMessage{
		EventID:    eventID,
		UserID:     userID,
		SourceType: req.SourceType,
		Payload:    req.Payload,
		Timestamp:  now,
	}

	if err := h.queue.Publish(c.Request.Context(), queueMsg); err != nil {
		h.logger.Error("Failed to publish event", "error", err, "event_id", eventID)
		// Event is stored, but not published - log for retry mechanism
		// For MVP, we'll continue and return success
	}

	h.logger.Info("Event ingested successfully",
		"event_id", eventID,
		"user_id", userID,
		"source_type", req.SourceType,
	)

	// Return success response
	c.JSON(http.StatusCreated, models.IngestionResponse{
		EventID:   eventID,
		Status:    "accepted",
		Message:   "Credential ingested successfully",
		CreatedAt: now,
	})
}

// HandleGetEvent retrieves an event by ID.
// GET /api/v1/events/:id
func (h *IngestHandler) HandleGetEvent(c *gin.Context) {
	eventID := c.Param("id")
	if eventID == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "invalid_request",
			"message": "Event ID is required",
		})
		return
	}

	event, err := h.repo.GetEventByID(c.Request.Context(), eventID)
	if err != nil {
		h.logger.Error("Failed to get event", "error", err, "event_id", eventID)
		c.JSON(http.StatusNotFound, gin.H{
			"error":   "not_found",
			"message": "Event not found",
		})
		return
	}

	c.JSON(http.StatusOK, event)
}

// HandleGetUserEvents retrieves events for the current user.
// GET /api/v1/events
func (h *IngestHandler) HandleGetUserEvents(c *gin.Context) {
	userID := c.GetString("user_id")
	if userID == "" {
		userID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11" // Default test user
	}

	events, err := h.repo.GetEventsByUser(c.Request.Context(), userID, 100)
	if err != nil {
		h.logger.Error("Failed to get events", "error", err, "user_id", userID)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "internal_error",
			"message": "Failed to retrieve events",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"events": events,
		"count":  len(events),
	})
}

// calculateChecksum calculates SHA-256 checksum of data.
func calculateChecksum(data []byte) string {
	hash := sha256.Sum256(data)
	return hex.EncodeToString(hash[:])
}
