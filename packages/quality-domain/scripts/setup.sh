#!/bin/bash

# Quality Domain Setup Script
# Automatisiert die Einrichtung der Entwicklungsumgebung

set -e

echo "🚀 Quality Domain Setup"
echo "======================="
echo ""

# 1. Check Node.js version
echo "📋 Checking Node.js version..."
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo "❌ Error: Node.js 20 or higher is required"
    exit 1
fi
echo "✅ Node.js $(node --version)"
echo ""

# 2. Install dependencies
echo "📦 Installing dependencies..."
npm install
echo "✅ Dependencies installed"
echo ""

# 3. Create .env file if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Server
PORT=3007
NODE_ENV=development
API_BASE_URL=http://localhost:3007

# Database
DATABASE_URL=postgres://postgres:postgres@localhost:5432/quality_db
POSTGRES_URL=postgres://postgres:postgres@localhost:5432/quality_db

# JWT/Auth (Development - replace in production!)
JWT_SECRET=dev-secret-change-in-production
JWKS_URI=
JWT_ISSUER=
JWT_AUDIENCE=valeo-neuroerp

# NATS (Event Bus)
NATS_URL=nats://localhost:4222
NATS_CLUSTER_ID=valeo-cluster
NATS_CLIENT_ID=quality-domain

# Redis (Cache)
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=
REDIS_DB=0

# OpenTelemetry
OTEL_ENABLED=false
OTEL_SERVICE_NAME=quality-domain
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=1.0

# Logging
LOG_LEVEL=info
LOG_PRETTY=true

# Integration URLs
PRODUCTION_DOMAIN_URL=http://localhost:3004
CONTRACTS_DOMAIN_URL=http://localhost:3005
INVENTORY_DOMAIN_URL=http://localhost:3006
ANALYTICS_DOMAIN_URL=http://localhost:3008
EOF
    echo "✅ .env file created"
else
    echo "ℹ️  .env file already exists"
fi
echo ""

# 4. Check PostgreSQL
echo "🗄️  Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL is installed"
    
    # Try to connect to database
    if psql -h localhost -U postgres -lqt | cut -d \| -f 1 | grep -qw quality_db 2>/dev/null; then
        echo "✅ Database 'quality_db' exists"
    else
        echo "⚠️  Database 'quality_db' not found"
        echo "   Run: createdb -U postgres quality_db"
    fi
else
    echo "⚠️  PostgreSQL not found. Please install PostgreSQL 14+"
    echo "   Docker: docker run -d --name quality-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=quality_db -p 5432:5432 postgres:16-alpine"
fi
echo ""

# 5. Check NATS (optional)
echo "📡 Checking NATS..."
if nc -z localhost 4222 2>/dev/null; then
    echo "✅ NATS is running on port 4222"
else
    echo "⚠️  NATS not running (optional for development)"
    echo "   Docker: docker run -d --name nats -p 4222:4222 nats:latest"
fi
echo ""

# 6. Build
echo "🔨 Building project..."
npm run build
echo "✅ Build complete"
echo ""

# 7. Run migrations (if database is available)
echo "🗄️  Running database migrations..."
if npm run migrate:up 2>/dev/null; then
    echo "✅ Migrations applied"
else
    echo "⚠️  Could not run migrations (database might not be available)"
fi
echo ""

# 8. Run tests
echo "🧪 Running tests..."
npm test
echo "✅ Tests passed"
echo ""

echo "═══════════════════════════════════════════════"
echo "✨ Setup complete!"
echo "═══════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Start development server:  npm run dev"
echo "  2. Visit API docs:            http://localhost:3007/documentation"
echo "  3. Check health:              curl http://localhost:3007/health"
echo ""
echo "Happy coding! 🎉"
