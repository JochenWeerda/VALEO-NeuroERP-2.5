import { Brand } from '@packages/data-models';
export type MetricId = Brand<string, 'MetricId'>;
export type MetricType = 'counter' | 'gauge' | 'histogram';
export interface Metric {
    readonly id: MetricId;
    readonly tenantId: string;
    name: string;
    value: number;
    type: MetricType;
    unit?: string;
    dimensions: Record<string, string>;
    recordedAt: Date;
}
export interface RecordMetricInput {
    tenantId: string;
    name: string;
    value: number;
    type?: MetricType;
    unit?: string;
    dimensions?: Record<string, string>;
    recordedAt?: Date;
}
export declare function recordMetric(input: RecordMetricInput): Metric;
//# sourceMappingURL=metric.d.ts.map