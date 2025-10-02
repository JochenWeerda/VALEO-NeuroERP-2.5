/**
 * Request Validation Middleware
 */
import { ZodError } from 'zod';
import { createValidationError } from '../errors/api-errors.js';
export class RequestValidatorMiddleware {
    validate(options) {
        return async (req, res, next) => {
            try {
                // Validate request body
                if (options.body && req.body) {
                    req.body = await options.body.parseAsync(req.body);
                }
                // Validate query parameters
                if (options.query && req.query) {
                    req.query = await options.query.parseAsync(req.query);
                }
                // Validate route parameters
                if (options.params && req.params) {
                    req.params = await options.params.parseAsync(req.params);
                }
                // Validate headers
                if (options.headers && req.headers) {
                    req.headers = await options.headers.parseAsync(req.headers);
                }
                next();
            }
            catch (error) {
                if (error instanceof ZodError) {
                    const validationError = createValidationError('Request validation failed', error.errors.map(err => ({
                        field: err.path.join('.'),
                        message: err.message,
                        value: 'received' in err ? err.received : undefined
                    })));
                    return res.status(validationError.statusCode).json(validationError.toJSON());
                }
                next(error);
            }
        };
    }
}
//# sourceMappingURL=request-validator.js.map