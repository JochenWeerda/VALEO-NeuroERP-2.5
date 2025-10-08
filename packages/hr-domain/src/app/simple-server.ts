/**
 * Simple HR Domain Server for VALEO NeuroERP 3.0
 * Simplified version without complex Fastify types
 */

import Fastify, { type FastifyReply, type FastifyRequest } from 'fastify';
import pino from 'pino';

import { type CreateEmployeeCommand, EmployeeService, type EmployeeStatistics } from '../domain/services/employee-service';
import type { HREvent } from '../domain/events';
import { PostgresEmployeeRepository } from '../infra/repo/postgres-employee-repository';

const DEFAULT_PORT = 3030;
const DEFAULT_HOST = '0.0.0.0';
const DEFAULT_LOG_LEVEL = 'info';
const DEFAULT_TENANT_ID = 'default-tenant';
const SYSTEM_USER_ID = 'system';

const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500
} as const;

const logger = pino({
  level: process.env.LOG_LEVEL ?? DEFAULT_LOG_LEVEL,
  transport: process.env.NODE_ENV === 'development'
    ? {
        target: 'pino-pretty',
        options: {
          colorize: true
        }
      }
    : undefined
});

const PORT = Number(process.env.PORT ?? DEFAULT_PORT);
const HOST = process.env.HOST ?? DEFAULT_HOST;
const BASE_URL = ['http://', HOST, ':', String(PORT)].join('');

const employeeRepository = new PostgresEmployeeRepository();

type DomainEventPublisher = (event: HREvent) => Promise<void>;

const eventPublisher: DomainEventPublisher = async (event) => {
  logger.info({ eventType: event.eventType, eventId: event.eventId }, 'Publishing domain event (simple server stub)');
};

const employeeService = new EmployeeService(employeeRepository, eventPublisher);

const fastify = Fastify({
  logger
});

type CreateEmployeePayload = Omit<CreateEmployeeCommand, 'tenantId' | 'createdBy'>;

type EmployeeParams = { id: string };

type TenantContext = { tenantId: string; userId: string };

function defaultTenantContext(): TenantContext {
  return {
    tenantId: DEFAULT_TENANT_ID,
    userId: SYSTEM_USER_ID
  };
}

fastify.get('/health', async () => ({
  ok: true,
  service: 'hr-domain-simple',
  timestamp: new Date().toISOString(),
  uptime: process.uptime()
}));

fastify.get('/ready', async () => ({
  ok: true,
  database: true,
  timestamp: new Date().toISOString()
}));

fastify.get('/live', async () => ({
  ok: true,
  timestamp: new Date().toISOString()
}));

fastify.post('/hr/api/v1/employees', async (
  request: FastifyRequest<{ Body: CreateEmployeePayload }>,
  reply: FastifyReply
) => {
  const { tenantId, userId } = defaultTenantContext();

  try {
    const employee = await employeeService.createEmployee({
      tenantId,
      createdBy: userId,
      ...request.body
    });

    await reply.code(HTTP_STATUS.CREATED).send(employee);
  } catch (error) {
    logger.error({ err: error }, 'Error creating employee (simple server)');
    await reply.code(HTTP_STATUS.BAD_REQUEST).send({
      error: error instanceof Error ? error.message : 'Failed to create employee'
    });
  }
});

fastify.get('/hr/api/v1/employees/:id', async (
  request: FastifyRequest<{ Params: EmployeeParams }>,
  reply: FastifyReply
) => {
  const { tenantId } = defaultTenantContext();

  try {
    const employee = await employeeService.getEmployee(tenantId, request.params.id);
    await reply.code(HTTP_STATUS.OK).send(employee);
  } catch (error) {
    logger.error({ err: error, employeeId: request.params.id }, 'Error getting employee (simple server)');
    await reply.code(HTTP_STATUS.NOT_FOUND).send({
      error: error instanceof Error ? error.message : 'Employee not found'
    });
  }
});

fastify.get('/hr/api/v1/employees', async (_request, reply: FastifyReply) => {
  const { tenantId } = defaultTenantContext();

  try {
    const employees = await employeeService.listEmployees(tenantId);
    await reply.code(HTTP_STATUS.OK).send(employees);
  } catch (error) {
    logger.error({ err: error }, 'Error listing employees (simple server)');
    await reply.code(HTTP_STATUS.INTERNAL_SERVER_ERROR).send({
      error: 'Failed to list employees'
    });
  }
});

fastify.get('/hr/api/v1/employees/statistics', async (_request, reply: FastifyReply) => {
  const { tenantId } = defaultTenantContext();

  try {
    const statistics: EmployeeStatistics = await employeeService.getEmployeeStatistics(tenantId);
    await reply.code(HTTP_STATUS.OK).send(statistics);
  } catch (error) {
    logger.error({ err: error }, 'Error getting employee statistics (simple server)');
    await reply.code(HTTP_STATUS.INTERNAL_SERVER_ERROR).send({
      error: 'Failed to get employee statistics'
    });
  }
});

fastify.setErrorHandler(async (error, request, reply) => {
  fastify.log.error({ err: error, url: request.url }, 'Unhandled error (simple server)');
  await reply.code(HTTP_STATUS.INTERNAL_SERVER_ERROR).send({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? error.message : 'An unexpected error occurred'
  });
});

async function start(): Promise<void> {
  try {
    const address = await fastify.listen({ port: PORT, host: HOST });
    logger.info({ address }, 'Simple HR Domain server running');
    logger.info({ health: `${BASE_URL}/health` }, 'Health endpoint available');
  } catch (error) {
    logger.error({ err: error }, 'Failed to start simple server');
    process.exit(1);
  }
}

async function gracefulShutdown(): Promise<void> {
  logger.info('Gracefully shutting down simple server...');
  try {
    await fastify.close();
    logger.info('Simple server shut down successfully');
    process.exit(0);
  } catch (error) {
    logger.error({ err: error }, 'Error during simple server shutdown');
    process.exit(1);
  }
}

process.on('SIGTERM', () => {
  void gracefulShutdown();
});

process.on('SIGINT', () => {
  void gracefulShutdown();
});

if (require.main === module) {
  void start();
}

export default fastify;
