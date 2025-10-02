/**
 * VALEO NeuroERP 3.0 - Product Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */
import { ProductId } from '@valero-neuroerp/data-models/branded-types';
import { DomainEvent } from '@valero-neuroerp/data-models/domain-events';
export interface Product {
    readonly id: ProductId;
    name: string;
    status?: string;
    sku: string;
    price: number;
    category: string;
    description?: string;
    readonly createdAt: Date;
    readonly updatedAt: Date;
}
export interface CreateProductCommand {
    name: string;
    status?: string;
    sku: string;
    price: number;
    category: string;
    description?: string;
}
export interface UpdateProductCommand {
    name?: string;
    status?: string;
    sku?: string;
    price?: number;
    category?: string;
    description?: string;
}
export declare class ProductCreatedEvent implements DomainEvent {
    readonly product: Product;
    readonly type = "ProductCreated";
    readonly aggregateId: ProductId;
    readonly occurredAt: Date;
    constructor(product: Product);
}
export declare class ProductUpdatedEvent implements DomainEvent {
    readonly product: Product;
    readonly changes: Record<string, any>;
    readonly type = "ProductUpdated";
    readonly aggregateId: ProductId;
    readonly occurredAt: Date;
    constructor(product: Product, changes: Record<string, any>);
}
export declare class ProductEntity implements Product {
    readonly id: ProductId;
    name: string;
    status?: string;
    sku: string;
    price: number;
    category: string;
    description?: string;
    readonly createdAt: Date;
    readonly updatedAt: Date;
    private constructor();
    static create(command: CreateProductCommand): ProductEntity;
    update(command: UpdateProductCommand): ProductEntity;
    isActive(): boolean;
    isInStock(): boolean;
    calculateTotalPrice(quantity: number, taxRate?: number): number;
    private static validateCreateCommand;
    private static validateUpdateCommand;
}
export declare function createProduct(command: CreateProductCommand): ProductEntity;
export declare function isValidProductId(id: string): boolean;
export declare function formatPrice(price: number, currency?: string): string;
//# sourceMappingURL=product.d.ts.map