/**
 * VALEO NeuroERP 3.0 - Inventory Domain Entity
 *
 * Domain entity following Domain-Driven Design principles.
 * Includes validation, business rules, and domain events.
 */
import { InventoryId } from '@valero-neuroerp/data-models/branded-types';
import { DomainEvent } from '@valero-neuroerp/data-models/domain-events';
export interface Inventory {
    readonly id: InventoryId;
    name: string;
    status?: string;
    productId: string;
    quantity: number;
    reservedQuantity: number;
    availableQuantity: number;
    reorderLevel: number;
    reorderQuantity: number;
    lastUpdated: Date;
    readonly createdAt: Date;
    readonly updatedAt: Date;
}
export interface CreateInventoryCommand {
    name: string;
    status?: string;
    productId: string;
    quantity: number;
    reservedQuantity: number;
    availableQuantity: number;
    reorderLevel: number;
    reorderQuantity: number;
    lastUpdated: Date;
}
export interface UpdateInventoryCommand {
    name?: string;
    status?: string;
    productId?: string;
    quantity?: number;
    reservedQuantity?: number;
    availableQuantity?: number;
    reorderLevel?: number;
    reorderQuantity?: number;
    lastUpdated?: Date;
}
export declare class InventoryCreatedEvent implements DomainEvent {
    readonly inventory: Inventory;
    readonly type = "InventoryCreated";
    readonly aggregateId: InventoryId;
    readonly occurredAt: Date;
    constructor(inventory: Inventory);
}
export declare class InventoryUpdatedEvent implements DomainEvent {
    readonly inventory: Inventory;
    readonly changes: Record<string, any>;
    readonly type = "InventoryUpdated";
    readonly aggregateId: InventoryId;
    readonly occurredAt: Date;
    constructor(inventory: Inventory, changes: Record<string, any>);
}
export declare class InventoryEntity implements Inventory {
    readonly id: InventoryId;
    name: string;
    status?: string;
    productId: string;
    quantity: number;
    reservedQuantity: number;
    availableQuantity: number;
    reorderLevel: number;
    reorderQuantity: number;
    lastUpdated: Date;
    readonly createdAt: Date;
    readonly updatedAt: Date;
    private constructor();
    static create(command: CreateInventoryCommand): InventoryEntity;
    update(command: UpdateInventoryCommand): InventoryEntity;
    isActive(): boolean;
    private static validateCreateCommand;
    private static validateUpdateCommand;
}
//# sourceMappingURL=inventory.d.ts.map