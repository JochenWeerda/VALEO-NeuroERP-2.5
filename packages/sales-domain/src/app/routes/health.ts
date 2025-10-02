import { FastifyInstance } from 'fastify';
import { getEventPublisher } from '../../infra/messaging/publisher';

export async function healthRoutes(fastify: FastifyInstance) {
  // Health check endpoint
  fastify.get('/health', {
    schema: {
      description: 'Health check endpoint',
      tags: ['Health'],
      response: {
        200: {
          type: 'object',
          properties: {
            status: { type: 'string', enum: ['ok'] },
            timestamp: { type: 'string', format: 'date-time' },
            uptime: { type: 'number' },
          },
        },
      },
    },
  }, async (request, reply) => {
    return {
      status: 'ok',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
    };
  });

  // Readiness check endpoint
  fastify.get('/ready', {
    schema: {
      description: 'Readiness check endpoint',
      tags: ['Health'],
      response: {
        200: {
          type: 'object',
          properties: {
            status: { type: 'string', enum: ['ready'] },
            checks: {
              type: 'object',
              properties: {
                database: { type: 'boolean' },
                messaging: { type: 'boolean' },
              },
            },
          },
        },
        503: {
          type: 'object',
          properties: {
            status: { type: 'string', enum: ['not ready'] },
            checks: {
              type: 'object',
              properties: {
                database: { type: 'boolean' },
                messaging: { type: 'boolean' },
              },
            },
          },
        },
      },
    },
  }, async (request, reply) => {
    const checks = {
      database: true, // TODO: Implement actual database health check
      messaging: getEventPublisher().isHealthy(),
    };

    const allHealthy = Object.values(checks).every(Boolean);

    if (!allHealthy) {
      return reply.code(503).send({
        status: 'not ready',
        checks,
      });
    }

    return {
      status: 'ready',
      checks,
    };
  });

  // Liveness check endpoint
  fastify.get('/live', {
    schema: {
      description: 'Liveness check endpoint',
      tags: ['Health'],
      response: {
        200: {
          type: 'object',
          properties: {
            status: { type: 'string', enum: ['alive'] },
            timestamp: { type: 'string', format: 'date-time' },
          },
        },
      },
    },
  }, async (request, reply) => {
    return {
      status: 'alive',
      timestamp: new Date().toISOString(),
    };
  });
}