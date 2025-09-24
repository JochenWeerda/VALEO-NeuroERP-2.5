# Service Bus - Core Message Bus

## 🎯 Service Overview

The Service Bus is the core message broker for VALEO NeuroERP 3.0, providing reliable inter-service communication using AMQP protocol.

## 🏗️ Architecture

### Message Bus Components
```
src/
├── core/                   # Core Message Bus Logic
│   ├── exchanges/          # Exchange Definitions
│   ├── queues/             # Queue Definitions
│   ├── routing/            # Message Routing Logic
│   └── events/             # Event Definitions
├── infrastructure/          # Infrastructure Layer
│   ├── connections/        # AMQP Connections
│   ├── publishers/         # Message Publishers
│   ├── subscribers/        # Message Subscribers
│   └── monitoring/         # Message Monitoring
└── presentation/           # Management Interface
    ├── controllers/        # Management Controllers
    ├── middleware/         # Request Middleware
    └── views/              # Management Views
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- RabbitMQ 3.8+

### Installation
```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Start development server
npm run dev
```

### Environment Variables
```env
# Service Configuration
SERVICE_PORT=5672
MANAGEMENT_PORT=15672
SERVICE_NAME=service-bus

# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=admin123
RABBITMQ_VHOST=/

# Exchange Configuration
DEFAULT_EXCHANGE=valero.events
DEAD_LETTER_EXCHANGE=valero.dlx

# Queue Configuration
DEFAULT_QUEUE_TTL=3600000
MAX_RETRY_ATTEMPTS=3

# Logging Configuration
LOG_LEVEL=info
LOG_FORMAT=json
```

## 📊 Message Bus Features

### Exchanges
- **valero.events** - Main event exchange
- **valero.commands** - Command exchange
- **valero.queries** - Query exchange
- **valero.dlx** - Dead letter exchange

### Queues
- **crm.events** - CRM domain events
- **erp.events** - ERP domain events
- **analytics.events** - Analytics domain events
- **integration.events** - Integration domain events

### Routing
- **Topic Routing** - Event-based routing
- **Direct Routing** - Command-based routing
- **Fanout Routing** - Broadcast routing

## 🧪 Testing

### Unit Tests
```bash
npm run test:unit
```

### Integration Tests
```bash
npm run test:integration
```

## 🐳 Docker

### Build Image
```bash
npm run docker:build
```

### Run Container
```bash
npm run docker:run
```

## 📈 Monitoring

### Health Check
- **Endpoint:** `GET /health`
- **Response:** Service health status

### Metrics
- **Endpoint:** `GET /metrics`
- **Response:** Prometheus metrics

### Management UI
- **URL:** `http://localhost:15672`
- **Username:** admin
- **Password:** admin123

## 🔒 Security

### Authentication
- AMQP authentication
- Management UI authentication
- API key authentication

### Authorization
- Virtual host access control
- Exchange permissions
- Queue permissions

## 📚 Documentation

### API Documentation
- **OpenAPI Spec:** `/api/docs`
- **Swagger UI:** `/api/docs-ui`

### Message Bus Documentation
- **Exchange Guide:** `docs/exchanges.md`
- **Queue Guide:** `docs/queues.md`
- **Routing Guide:** `docs/routing.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details
