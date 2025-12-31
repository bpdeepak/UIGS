// Package repository provides database access for the ingestion service.
package repository

import (
	"context"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/uigs/ingestion/internal/models"
)

// EventRepository defines the interface for event storage operations.
type EventRepository interface {
	CreateEvent(ctx context.Context, event *models.IngestionEvent) error
	GetEventByID(ctx context.Context, eventID string) (*models.IngestionEvent, error)
	GetEventsByUser(ctx context.Context, userID string, limit int) ([]models.IngestionEvent, error)
	Close()
}

// PostgresRepository implements EventRepository using PostgreSQL.
type PostgresRepository struct {
	pool *pgxpool.Pool
}

// NewPostgresRepository creates a new PostgreSQL repository.
func NewPostgresRepository(ctx context.Context, connString string) (*PostgresRepository, error) {
	config, err := pgxpool.ParseConfig(connString)
	if err != nil {
		return nil, fmt.Errorf("failed to parse connection string: %w", err)
	}

	// Configure connection pool
	config.MaxConns = 10
	config.MinConns = 2
	config.MaxConnLifetime = time.Hour
	config.MaxConnIdleTime = 30 * time.Minute

	pool, err := pgxpool.NewWithConfig(ctx, config)
	if err != nil {
		return nil, fmt.Errorf("failed to create connection pool: %w", err)
	}

	// Test connection
	if err := pool.Ping(ctx); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return &PostgresRepository{pool: pool}, nil
}

// CreateEvent inserts a new ingestion event into the database.
func (r *PostgresRepository) CreateEvent(ctx context.Context, event *models.IngestionEvent) error {
	query := `
		INSERT INTO ingestion_events (event_id, user_id, source_type, raw_payload, checksum, created_at)
		VALUES ($1, $2, $3, $4, $5, $6)
	`

	_, err := r.pool.Exec(ctx, query,
		event.EventID,
		event.UserID,
		event.SourceType,
		event.RawPayload,
		event.Checksum,
		event.CreatedAt,
	)
	if err != nil {
		return fmt.Errorf("failed to insert event: %w", err)
	}

	return nil
}

// GetEventByID retrieves an event by its ID.
func (r *PostgresRepository) GetEventByID(ctx context.Context, eventID string) (*models.IngestionEvent, error) {
	query := `
		SELECT event_id, user_id, source_type, raw_payload, checksum, created_at
		FROM ingestion_events
		WHERE event_id = $1
	`

	var event models.IngestionEvent
	err := r.pool.QueryRow(ctx, query, eventID).Scan(
		&event.EventID,
		&event.UserID,
		&event.SourceType,
		&event.RawPayload,
		&event.Checksum,
		&event.CreatedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to get event: %w", err)
	}

	return &event, nil
}

// GetEventsByUser retrieves events for a specific user.
func (r *PostgresRepository) GetEventsByUser(ctx context.Context, userID string, limit int) ([]models.IngestionEvent, error) {
	query := `
		SELECT event_id, user_id, source_type, raw_payload, checksum, created_at
		FROM ingestion_events
		WHERE user_id = $1
		ORDER BY created_at DESC
		LIMIT $2
	`

	rows, err := r.pool.Query(ctx, query, userID, limit)
	if err != nil {
		return nil, fmt.Errorf("failed to query events: %w", err)
	}
	defer rows.Close()

	var events []models.IngestionEvent
	for rows.Next() {
		var event models.IngestionEvent
		if err := rows.Scan(
			&event.EventID,
			&event.UserID,
			&event.SourceType,
			&event.RawPayload,
			&event.Checksum,
			&event.CreatedAt,
		); err != nil {
			return nil, fmt.Errorf("failed to scan event: %w", err)
		}
		events = append(events, event)
	}

	return events, nil
}

// Close closes the database connection pool.
func (r *PostgresRepository) Close() {
	r.pool.Close()
}
