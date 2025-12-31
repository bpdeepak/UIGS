// Package queue provides message queue functionality for the ingestion service.
package queue

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
	"github.com/uigs/ingestion/internal/models"
)

const (
	// ExchangeName is the name of the RabbitMQ exchange.
	ExchangeName = "identity.events"
	// QueueName is the name of the queue for the graph engine.
	QueueName = "graph.engine.queue"
	// RoutingKey is the routing key for identity events.
	RoutingKey = "identity.new"
)

// Publisher defines the interface for publishing messages.
type Publisher interface {
	Publish(ctx context.Context, msg *models.QueueMessage) error
	Close() error
}

// RabbitMQPublisher implements Publisher using RabbitMQ.
type RabbitMQPublisher struct {
	conn     *amqp.Connection
	channel  *amqp.Channel
	exchange string
	logger   *slog.Logger
}

// NewRabbitMQPublisher creates a new RabbitMQ publisher.
func NewRabbitMQPublisher(url string, logger *slog.Logger) (*RabbitMQPublisher, error) {
	// Connect to RabbitMQ
	conn, err := amqp.Dial(url)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to RabbitMQ: %w", err)
	}

	// Open channel
	channel, err := conn.Channel()
	if err != nil {
		conn.Close()
		return nil, fmt.Errorf("failed to open channel: %w", err)
	}

	// Declare exchange
	err = channel.ExchangeDeclare(
		ExchangeName, // name
		"fanout",     // type
		true,         // durable
		false,        // auto-deleted
		false,        // internal
		false,        // no-wait
		nil,          // arguments
	)
	if err != nil {
		channel.Close()
		conn.Close()
		return nil, fmt.Errorf("failed to declare exchange: %w", err)
	}

	// Declare queue
	queue, err := channel.QueueDeclare(
		QueueName, // name
		true,      // durable
		false,     // delete when unused
		false,     // exclusive
		false,     // no-wait
		nil,       // arguments
	)
	if err != nil {
		channel.Close()
		conn.Close()
		return nil, fmt.Errorf("failed to declare queue: %w", err)
	}

	// Bind queue to exchange
	err = channel.QueueBind(
		queue.Name,   // queue name
		RoutingKey,   // routing key
		ExchangeName, // exchange
		false,        // no-wait
		nil,          // arguments
	)
	if err != nil {
		channel.Close()
		conn.Close()
		return nil, fmt.Errorf("failed to bind queue: %w", err)
	}

	logger.Info("RabbitMQ publisher initialized",
		"exchange", ExchangeName,
		"queue", QueueName,
	)

	return &RabbitMQPublisher{
		conn:     conn,
		channel:  channel,
		exchange: ExchangeName,
		logger:   logger,
	}, nil
}

// Publish sends a message to the queue.
func (p *RabbitMQPublisher) Publish(ctx context.Context, msg *models.QueueMessage) error {
	body, err := json.Marshal(msg)
	if err != nil {
		return fmt.Errorf("failed to marshal message: %w", err)
	}

	err = p.channel.PublishWithContext(ctx,
		p.exchange, // exchange
		RoutingKey, // routing key
		false,      // mandatory
		false,      // immediate
		amqp.Publishing{
			ContentType:  "application/json",
			DeliveryMode: amqp.Persistent,
			Timestamp:    time.Now(),
			Body:         body,
		},
	)
	if err != nil {
		return fmt.Errorf("failed to publish message: %w", err)
	}

	p.logger.Debug("Message published",
		"event_id", msg.EventID,
		"source_type", msg.SourceType,
	)

	return nil
}

// Close closes the RabbitMQ connection.
func (p *RabbitMQPublisher) Close() error {
	if err := p.channel.Close(); err != nil {
		p.logger.Error("Failed to close channel", "error", err)
	}
	if err := p.conn.Close(); err != nil {
		return fmt.Errorf("failed to close connection: %w", err)
	}
	p.logger.Info("RabbitMQ connection closed")
	return nil
}
