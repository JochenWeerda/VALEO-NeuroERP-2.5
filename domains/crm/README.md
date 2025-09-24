# CRM Service - Customer Relationship Management

## 🎯 Service Overview

The CRM Service is responsible for managing customer relationships, sales pipelines, and customer analytics within the VALEO NeuroERP 3.0 ecosystem.

## 🏗️ Architecture

### Domain Structure
```
src/
├── core/                   # Domain Core Logic
│   ├── entities/          # Customer, Contact, Opportunity
│   ├── value-objects/     # Email, Phone, Address
│   ├── domain-events/     # CustomerCreated, OpportunityWon
│   └── domain-services/   # CustomerValidationService
├── application/           # Application Layer
│   ├── commands/          # CreateCustomer, UpdateOpportunity
│   ├── queries/           # GetCustomer, ListOpportunities
│   ├── dto/               # CustomerDTO, OpportunityDTO
│   └── events/            # Application Event Handlers
├── infrastructure/        # Infrastructure Layer
│   ├── repositories/      # CustomerRepository, OpportunityRepository
│   ├── external-services/ # EmailService, SMSService
│   ├── messaging/         # Event Publisher, Event Subscriber
│   └── persistence/       # Database Layer
└── presentation/          # Presentation Layer
    ├── controllers/       # CustomerController, OpportunityController
    ├── middleware/        # Authentication, Validation
    └── views/             # Response Views
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3.8+

### Installation
```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Run database migrations
npm run migrate

# Start development server
npm run dev
```

### Environment Variables
```env
# Service Configuration
SERVICE_PORT=8081
SERVICE_NAME=crm-service
SERVICE_REGISTRY_URL=http://service-registry:8761

# Database Configuration
DATABASE_URL=postgresql://crm_user:crm_pass@crm-db:5432/crm_db
DATABASE_POOL_MIN=2
DATABASE_POOL_MAX=10

# Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=

# Message Queue Configuration
RABBITMQ_URL=amqp://admin:admin123@service-bus:5672
RABBITMQ_EXCHANGE=crm.events

# Security Configuration
JWT_SECRET=your-jwt-secret
JWT_EXPIRES_IN=24h
BCRYPT_ROUNDS=12

# Logging Configuration
LOG_LEVEL=info
LOG_FORMAT=json
```

## 📊 API Endpoints

### Customer Management
- `GET /api/v1/customers` - List customers
- `POST /api/v1/customers` - Create customer
- `GET /api/v1/customers/:id` - Get customer
- `PUT /api/v1/customers/:id` - Update customer
- `DELETE /api/v1/customers/:id` - Delete customer

### Opportunity Management
- `GET /api/v1/opportunities` - List opportunities
- `POST /api/v1/opportunities` - Create opportunity
- `GET /api/v1/opportunities/:id` - Get opportunity
- `PUT /api/v1/opportunities/:id` - Update opportunity
- `DELETE /api/v1/opportunities/:id` - Delete opportunity

### Contact Management
- `GET /api/v1/contacts` - List contacts
- `POST /api/v1/contacts` - Create contact
- `GET /api/v1/contacts/:id` - Get contact
- `PUT /api/v1/contacts/:id` - Update contact
- `DELETE /api/v1/contacts/:id` - Delete contact

## 🧪 Testing

### Unit Tests
```bash
npm run test:unit
```

### Integration Tests
```bash
npm run test:integration
```

### End-to-End Tests
```bash
npm run test:e2e
```

### Performance Tests
```bash
npm run test:performance
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

### Docker Compose
```bash
docker-compose up crm-service
```

## 📈 Monitoring

### Health Check
- **Endpoint:** `GET /health`
- **Response:** Service health status

### Metrics
- **Endpoint:** `GET /metrics`
- **Response:** Prometheus metrics

### Logs
- **Format:** JSON structured logging
- **Levels:** error, warn, info, debug
- **Correlation ID:** Request tracing

## 🔒 Security

### Authentication
- JWT token-based authentication
- Role-based access control (RBAC)
- API key authentication for service-to-service

### Authorization
- Customer data access control
- Opportunity visibility rules
- Contact privacy controls

### Data Protection
- Encryption at rest
- Encryption in transit
- GDPR compliance features

## 📚 Documentation

### API Documentation
- **OpenAPI Spec:** `/api/docs`
- **Swagger UI:** `/api/docs-ui`

### Domain Documentation
- **Domain Model:** `docs/domain-model.md`
- **Business Rules:** `docs/business-rules.md`
- **Integration Guide:** `docs/integration.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details
