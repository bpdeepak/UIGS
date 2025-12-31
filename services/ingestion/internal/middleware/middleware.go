// Package middleware provides HTTP middleware for the ingestion service.
package middleware

import (
	"log/slog"
	"time"

	"github.com/gin-gonic/gin"
)

// Logger returns a middleware that logs HTTP requests.
func Logger(logger *slog.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		query := c.Request.URL.RawQuery

		// Process request
		c.Next()

		// Log after request
		latency := time.Since(start)
		status := c.Writer.Status()

		attrs := []any{
			"status", status,
			"method", c.Request.Method,
			"path", path,
			"latency", latency.String(),
			"ip", c.ClientIP(),
		}

		if query != "" {
			attrs = append(attrs, "query", query)
		}

		if len(c.Errors) > 0 {
			attrs = append(attrs, "errors", c.Errors.String())
		}

		switch {
		case status >= 500:
			logger.Error("Server error", attrs...)
		case status >= 400:
			logger.Warn("Client error", attrs...)
		default:
			logger.Info("Request completed", attrs...)
		}
	}
}

// CORS returns a middleware that adds CORS headers.
func CORS() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Authorization")
		c.Header("Access-Control-Max-Age", "86400")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

// Recovery returns a middleware that recovers from panics.
func Recovery(logger *slog.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				logger.Error("Panic recovered",
					"error", err,
					"path", c.Request.URL.Path,
					"method", c.Request.Method,
				)
				c.AbortWithStatusJSON(500, gin.H{
					"error":   "internal_error",
					"message": "Internal server error",
				})
			}
		}()
		c.Next()
	}
}
