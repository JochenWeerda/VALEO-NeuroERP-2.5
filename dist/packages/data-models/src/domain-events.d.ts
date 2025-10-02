export interface DomainEvent {
    type: string;
    occurredAt: Date;
    payload?: unknown;
    metadata?: Record<string, unknown>;
}
//# sourceMappingURL=domain-events.d.ts.map