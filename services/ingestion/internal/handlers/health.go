// Package handlers provides HTTP request handlers for the ingestion service.
package handlers

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// HealthResponse represents the health check response.
type HealthResponse struct {
	Status    string    `json:"status"`
	Timestamp time.Time `json:"timestamp"`
	Version   string    `json:"version"`
	Service   string    `json:"service"`
}

// HandleHealth returns the health status of the service.
// GET /health
func HandleHealth(c *gin.Context) {
	c.JSON(http.StatusOK, HealthResponse{
		Status:    "healthy",
		Timestamp: time.Now().UTC(),
		Version:   "1.0.0",
		Service:   "ingestion-service",
	})
}

// HandleReadiness returns the readiness status of the service.
// GET /ready
func HandleReadiness(c *gin.Context) {
	// TODO: Add checks for database and queue connectivity
	c.JSON(http.StatusOK, gin.H{
		"status": "ready",
	})
}
