// Package main is the entry point for the ingestion service.
package main

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/uigs/ingestion/internal/config"
	"github.com/uigs/ingestion/internal/handlers"
	"github.com/uigs/ingestion/internal/middleware"
	"github.com/uigs/ingestion/internal/queue"
	"github.com/uigs/ingestion/internal/repository"
)

func main() {
	// Initialize logger
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}))
	slog.SetDefault(logger)

	logger.Info("Starting UIGS Ingestion Service")

	// Load configuration
	cfg := config.Load()
	logger.Info("Configuration loaded",
		"port", cfg.Port,
	)

	// Initialize database repository
	ctx := context.Background()
	repo, err := repository.NewPostgresRepository(ctx, cfg.PostgresURL)
	if err != nil {
		logger.Error("Failed to initialize database", "error", err)
		os.Exit(1)
	}
	defer repo.Close()
	logger.Info("Database connection established")

	// Initialize message queue publisher
	publisher, err := queue.NewRabbitMQPublisher(cfg.RabbitMQURL, logger)
	if err != nil {
		logger.Error("Failed to initialize message queue", "error", err)
		os.Exit(1)
	}
	defer publisher.Close()
	logger.Info("Message queue connection established")

	// Create handlers
	ingestHandler := handlers.NewIngestHandler(repo, publisher, logger)

	// Set up Gin router
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()

	// Apply middleware
	router.Use(middleware.Recovery(logger))
	router.Use(middleware.Logger(logger))
	router.Use(middleware.CORS())

	// Health check endpoints
	router.GET("/health", handlers.HandleHealth)
	router.GET("/ready", handlers.HandleReadiness)

	// API v1 routes
	v1 := router.Group("/api/v1")
	{
		// Ingestion endpoints
		v1.POST("/ingest", ingestHandler.HandleIngest)
		v1.GET("/events", ingestHandler.HandleGetUserEvents)
		v1.GET("/events/:id", ingestHandler.HandleGetEvent)
	}

	// Create HTTP server
	addr := fmt.Sprintf(":%d", cfg.Port)
	server := &http.Server{
		Addr:         addr,
		Handler:      router,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Start server in goroutine
	go func() {
		logger.Info("Server starting", "address", addr)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Error("Server failed", "error", err)
			os.Exit(1)
		}
	}()

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")

	// Graceful shutdown with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		logger.Error("Server forced to shutdown", "error", err)
	}

	logger.Info("Server exited")
}
