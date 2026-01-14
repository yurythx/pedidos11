# ProjetoRavenna Backend - Task Breakdown

## Planning Phase
- [x] Analyze requirements and architecture
- [x] Create implementation plan
- [x] Define app structure and dependencies

## Implementation Phase

### Core Foundation
- [x] Create `core` app structure
- [x] Implement `TenantManager` in `core/managers.py`
- [x] Implement `TenantModel` (abstract base) in `core/models.py`

### Geographic/Locations Module
- [x] Create `locations` app structure
- [x] Implement `Endereco` model with GenericForeignKey

### Catalog Module
- [x] Create `catalog` app structure

- [x] Implement `Categoria` model with self-referencing parent
- [x] Implement `Produto` model (without stock fields)


### Stock/Inventory Module
- [x] Create `stock` app structure
- [x] Implement `Deposito` model
- [x] Implement `Saldo` model (pivot table)
- [x] Implement `Movimentacao` model with atomic save() logic
- [x] Add select_for_update() and race condition prevention

## Verification Phase
- [x] Review all models for SOLID principles
- [x] Verify multi-tenancy implementation
- [x] Check UUID primary keys
- [x] Validate DecimalField usage
- [x] Review business rules implementation
