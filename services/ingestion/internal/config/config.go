// Package config provides configuration management for the ingestion service.
package config

import (
	"os"
	"strconv"
)

// Config holds all configuration for the ingestion service.
type Config struct {
	// Server settings
	Port int

	// Database settings
	PostgresURL string

	// Message queue settings
	RabbitMQURL string

	// Security settings
	JWTSecret string

	// OIDC settings (for future use)
	GoogleClientID     string
	GoogleClientSecret string
	GitHubClientID     string
	GitHubClientSecret string
}

// Load reads configuration from environment variables.
func Load() *Config {
	return &Config{
		Port:               getEnvAsInt("PORT", 8081),
		PostgresURL:        getEnv("POSTGRES_URL", "postgres://uigs_user:uigs_password_2024@localhost:5432/uigs_audit?sslmode=disable"),
		RabbitMQURL:        getEnv("RABBITMQ_URL", "amqp://uigs_rabbit:rabbit_password_2024@localhost:5672/"),
		JWTSecret:          getEnv("JWT_SECRET", "default_jwt_secret_change_me"),
		GoogleClientID:     getEnv("GOOGLE_CLIENT_ID", ""),
		GoogleClientSecret: getEnv("GOOGLE_CLIENT_SECRET", ""),
		GitHubClientID:     getEnv("GITHUB_CLIENT_ID", ""),
		GitHubClientSecret: getEnv("GITHUB_CLIENT_SECRET", ""),
	}
}

// getEnv retrieves an environment variable or returns a default value.
func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

// getEnvAsInt retrieves an environment variable as an integer.
func getEnvAsInt(key string, defaultValue int) int {
	if value, exists := os.LookupEnv(key); exists {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}
