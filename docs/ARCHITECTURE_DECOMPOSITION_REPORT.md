# Architecture Decomposition and Refactoring Report

## 1. Executive Summary

This project has been physically decomposed from a single overloaded `stock` app into three domain-focused Django apps while preserving existing URL paths and route names:

- `inventory`: stock catalog, stock transactions, stock history, inventory forms, repositories, services, export strategies.
- `scrum_board`: scrum list and task domain.
- `core`: registration, dashboard/home composition, dependent location forms, contacts, and location/person entities.

The `stock` app now acts as a compatibility facade for URL behavior and legacy imports.

## 2. Architectural Changes (Physical Decomposition)

### 2.1 New App Boundaries

- `inventory` now owns:
  - Models: `Category`, `Stock`, `StockHistory`, `StockBaseModel`
  - Forms: stock create/search/update/issue/receive/reorder/history-search
  - Views: inventory CRUD + issue/receive/reorder + history view/export
  - Repositories and services for data access and business logic
  - CSV export strategy and service

- `scrum_board` now owns:
  - Models: `Scrums`, `ScrumTitles`
  - Forms: `AddScrumListForm`, `AddScrumTaskForm`
  - Views: `scrum_list`, `scrum_view`

- `core` now owns:
  - Models: `User`, `Country`, `State`, `City`, `Person`, `Contacts`
  - Forms: `DependentDropdownForm`, `ContactsForm`
  - Views: register, home/dashboard, dependent forms CRUD, AJAX location endpoints, contacts

### 2.2 URL Compatibility Strategy

Behavior remained unchanged by keeping the existing `stock/urls.py` endpoints and names. The path map still resolves exactly as before. Internally, `stock/views.py` now re-exports callables from `inventory.views`, `core.views`, and `scrum_board.views`.

Snippet:

```python
# stock/views.py (compatibility facade)
from core.views import get_client_ip, new_register, dependent_forms, contact
from inventory.views import view_stock, add_stock, issue_item, view_history
from scrum_board.views import scrum_list, scrum_view
```

### 2.3 Stock App Transitioned to Facade

The old `stock` app no longer carries business-heavy implementation. It now provides:

- Compatibility imports for views/forms/models
- Existing templates/static/URL file continuity
- Zero duplicate admin registrations

## 3. Foundational Changes Applied

### 3.1 Layered Structure Added

Within `inventory`, foundation layers are explicit:

- `repositories`: query/data access logic
- `services`: business rules and transaction boundaries
- `exporters`: strategy-based export format implementation

Snippet:

```python
# inventory/services/stock.py
class StockService(BaseService):
    @BaseService.atomic
    def issue_stock(self, stock: Stock, quantity: int, issued_by):
        if quantity <= 0:
            raise ValidationError('Issue quantity must be greater than 0.')
        if not stock.can_issue(quantity):
            raise ValidationError('Insufficient stock')
        stock.quantity = (stock.quantity or 0) - quantity
        stock.issue_quantity = quantity
        stock.issued_by = str(issued_by)
        stock.full_clean()
        stock.save()
        return stock
```

### 3.2 Shared Base Model for Inventory Entities

`StockBaseModel` deduplicates shared fields between `Stock` and `StockHistory`.

Snippet:

```python
class StockBaseModel(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null=True)
    item_name = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    receive_quantity = models.IntegerField(default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    issue_quantity = models.IntegerField(default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    re_order = models.IntegerField(default=0, blank=True, null=True, validators=[MinValueValidator(0)])

    class Meta:
        abstract = True
```

### 3.3 Strategy-Based Export

CSV generation was extracted from views into strategy classes and an export service.

Snippet:

```python
class CSVStockExportStrategy:
    def export(self, records):
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
        for stock in records:
            writer.writerow([stock.category, stock.item_name, stock.quantity])
        return output.getvalue()
```

### 3.4 DB Compatibility for Decomposition

Moved models are mapped to existing legacy tables and marked unmanaged to avoid schema churn during decomposition:

```python
class Stock(StockBaseModel):
    class Meta:
        db_table = 'stock_stock'
        managed = False
```

Equivalent mapping was applied for all moved entities (`stock_category`, `stock_stockhistory`, `stock_country`, `stock_state`, `stock_city`, `stock_person`, `stock_contacts`, `stock_scrums`, `stock_scrumtitles`, `stock_user`).

### 3.5 Installed Apps Updated

`INSTALLED_APPS` now includes:

- `inventory`
- `scrum_board`
- `core`
- `stock` (kept for compatibility)

## 4. Bad Smells Identified and Addressed

### Smell A: God App / Low Cohesion

Problem:
- Inventory, scrum, geo/person, and contacts were bundled in one app.

Refactoring:
- Extract Class / Extract Module at app level.
- Physical decomposition into `inventory`, `scrum_board`, `core`.

Reason:
- Increase cohesion and reduce blast radius of changes.

### Smell B: Fat Views

Problem:
- HTTP handlers performed validation, state mutation, export generation, and persistence.

Refactoring:
- Extract Method + Introduce Service Layer + Introduce Repository.

Reason:
- Improve testability and maintainability.

### Smell C: Duplicated Export Logic in Views

Problem:
- CSV logic duplicated and hardcoded in multiple handlers.

Refactoring:
- Introduce Strategy Pattern (`CSVStockExportStrategy`, `CSVHistoryExportStrategy`) and `ExportService`.

Reason:
- Open/Closed compliance; easy to add new export formats.

### Smell D: Model Field Duplication

Problem:
- `Stock` and `StockHistory` repeated many fields.

Refactoring:
- Extract Superclass (`StockBaseModel`).

Reason:
- DRY, consistency of validation defaults.

### Smell E: Unsafe/Weak Numeric Defaults

Problem:
- Numeric defaults were previously string values in legacy model lineage.

Refactoring:
- Normalize to integer defaults with validators.

Reason:
- Type correctness and cleaner data behavior.

### Smell F: Architecture Coupling via Imports

Problem:
- Legacy callers import from `stock.views`, `stock.form`, `stock.models`.

Refactoring:
- Introduce Compatibility Facade in `stock` package.

Reason:
- Zero route/name behavior break during migration.

## 5. Refactorings Applied (Catalog)

1. Extract App (Architectural)
- Split monolith app responsibilities into dedicated apps.

2. Extract Superclass
- Common stock fields moved to `StockBaseModel`.

3. Introduce Repository
- Query logic moved from views to repositories.

4. Introduce Service Layer
- Transactional business operations isolated in services.

5. Introduce Strategy
- Export format logic encapsulated and interchangeable.

6. Introduce Facade (Compatibility)
- `stock` module preserved as external API surface for routes/importers.

7. Replace Direct ORM in Controllers
- Critical endpoints use repositories/services, reducing controller complexity.

## 6. Before/After Architecture Snapshot

Before:

```text
stock app
  models.py (all domains)
  views.py (all domains + business logic + exports)
  form.py (all forms)
```

After:

```text
inventory app
  models.py, forms.py, views.py
  repositories/, services/, exporters/

core app
  models.py, forms.py, views.py

scrum_board app
  models.py, forms.py, views.py

stock app
  urls.py (unchanged endpoints)
  views.py/form.py/models/* (compatibility facade)
  templates/static retained
```

## 7. Code Snippets: Representative Changes

### Thin Controller in Inventory

```python
@login_required
def issue_item(request, pk):
    issue = get_object_or_404(Stock, id=pk)
    form = IssueForm(request.POST or None, instance=issue)
    if form.is_valid():
        quantity = form.cleaned_data.get('issue_quantity')
        try:
            value = stock_service.issue_stock(stock=issue, quantity=quantity, issued_by=request.user)
            messages.success(request, 'Issued Successfully, ' + str(value.quantity) + ' ' + str(value.item_name) + 's now left in Store')
        except ValidationError as exc:
            messages.error(request, str(exc))
        return redirect(reverse('stock_detail', args=[issue.id]))
    return render(request, 'stock/add_stock.html', {'form': form, 'issue': issue})
```

### Repository Query Isolation

```python
class StockRepository(BaseRepository[Stock]):
    def search(self, item_name: str = '', category_id: Optional[int] = None) -> List[Stock]:
        queryset = self.model.objects.all()
        if item_name:
            queryset = queryset.filter(item_name__icontains=item_name)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return list(queryset)
```

### Legacy Import Safety

```python
# stock/form.py
from core.forms import ContactsForm, DependentDropdownForm
from inventory.forms import StockCreateForm, StockSearchForm, IssueForm
from scrum_board.forms import AddScrumListForm, AddScrumTaskForm
```

## 8. Validation Performed

- Static diagnostics: no current editor errors across decomposed apps.
- Bytecode compile check passed for `inventory`, `core`, `scrum_board`, and `stock`.

## 9. Residual Risks and Next Refactoring Opportunities

1. Route composition can be further cleaned by mounting app-specific `urls.py` directly in project URL config and reducing stock facade responsibilities.
2. Current decomposition uses `managed = False` table mapping for safe transition. A future phase can introduce explicit data migrations and full ownership transfer by app labels.
3. `get_client_ip` dashboard logic still includes mixed concerns and can be extracted into a reporting/query service.
4. Dedicated tests should be added per app (`inventory/tests`, `core/tests`, `scrum_board/tests`) for regression safety.

## 10. Final Change Inventory

### New apps and modules
- `inventory/*`
- `core/*`
- `scrum_board/*`

### Compatibility layer updates
- `stock/views.py`
- `stock/form.py`
- `stock/models/__init__.py`
- `stock/models/base.py`
- `stock/models/inventory.py`
- `stock/models/people.py`
- `stock/models/misc.py`
- `stock/models/scrum.py`
- `stock/admin.py`

### Settings update
- `stockmgtr/settings.py` (`INSTALLED_APPS`)

## 11. Phase 2 Implementation Update (Completed in This Iteration)

This iteration implemented the next roadmap steps focused on hardening, operational safety, and further controller cleanup.

### 11.1 Security and Config Hardening

Changes applied:
- `DEBUG` is now environment-driven instead of hardcoded.
- `ALLOWED_HOSTS` is now environment-driven with safe local defaults.
- `MEDIA_URL` changed to `/media/` to match uploaded media serving semantics.

Files changed:
- `stockmgtr/settings.py`

Refactoring applied:
- Replace Constant with Configuration (environment-based runtime config).

Bad smell addressed:
- Security Misconfiguration (`DEBUG=True` in production path).

### 11.2 Global Error Handling Layer

Changes applied:
- Added domain exception hierarchy.
- Added request middleware to catch domain exceptions and return:
  - JSON 400 for AJAX requests
  - message + safe redirect for browser requests

Files added:
- `stock/exceptions.py`
- `stock/middleware.py`

Files changed:
- `stockmgtr/settings.py` (middleware registration)

Refactoring applied:
- Introduce Exception Hierarchy.
- Introduce Middleware for cross-cutting error policy.

Bad smell addressed:
- Inconsistent error handling spread across views.

### 11.3 Logging and Operational Visibility

Changes applied:
- Added centralized Django logging dictionary factory.
- Logging now writes to both console and file (`stock.log`).

Files added:
- `stock/logging_config.py`

Files changed:
- `stockmgtr/settings.py` (LOGGING wiring)

Refactoring applied:
- Extract Configuration Object (logging config factory).

Bad smell addressed:
- Missing observability and ad hoc runtime diagnostics.

### 11.4 Remaining URL Hardcoding Cleanup

Changes applied:
- Replaced hardcoded redirect strings in inventory/core views with named route resolution via `reverse(...)`.

Files changed:
- `inventory/views.py`
- `core/views.py`

Refactoring applied:
- Replace Literal Redirect Paths with Named URL Resolution.

Bad smell addressed:
- Stringly-typed navigation and brittle redirect paths.

### 11.5 Further Fat-View Reduction

Changes applied:
- Extracted dashboard aggregation logic from `core.views.get_client_ip` into service function.

Files added:
- `core/services/__init__.py`
- `core/services/dashboard.py`

Files changed:
- `core/views.py`

Refactoring applied:
- Extract Function / Introduce Service for composition logic.

Bad smell addressed:
- Multi-responsibility controller method (IP tracking + analytics aggregation + rendering).

### 11.6 Service-Level Tests Introduced

Changes applied:
- Added baseline tests for stock issue/receive logic and insufficient stock case.

Files added:
- `inventory/tests/__init__.py`
- `inventory/tests/test_services.py`

Refactoring applied:
- Characterization tests for business rules.

Bad smell addressed:
- No automated validation of business invariants.

### 11.7 Additional Domain-Exception Integration

Changes applied:
- Stock service now raises domain-specific exceptions (`InsufficientStockError`, `InvalidQuantityError`).
- Inventory views handle both validation and domain exceptions consistently.

Files changed:
- `inventory/services/stock.py`
- `inventory/views.py`

Refactoring applied:
- Replace Generic Exception Usage with Domain-Specific Exceptions.

Bad smell addressed:
- Generic validation errors that obscure domain intent.

## 12. Updated Smell-to-Refactoring Matrix

1. Security misconfiguration
- Smell: hardcoded debug mode.
- Refactoring: environment-based configuration.
- Files: `stockmgtr/settings.py`.

2. Cross-cutting error duplication
- Smell: scattered exception behavior across views.
- Refactoring: exception hierarchy + middleware boundary.
- Files: `stock/exceptions.py`, `stock/middleware.py`, `stockmgtr/settings.py`.

3. Opaque runtime failures
- Smell: no centralized logging policy.
- Refactoring: extracted logging config and global registration.
- Files: `stock/logging_config.py`, `stockmgtr/settings.py`.

4. Stringly-typed redirects
- Smell: hardcoded URL paths in controllers.
- Refactoring: reverse by route names.
- Files: `inventory/views.py`, `core/views.py`.

5. Controller overloading
- Smell: `get_client_ip` mixed persistence, aggregation, and rendering.
- Refactoring: service extraction for dashboard context.
- Files: `core/services/dashboard.py`, `core/views.py`.

6. Missing business-rule regression checks
- Smell: no tests for stock operations.
- Refactoring: add service-level tests.
- Files: `inventory/tests/test_services.py`.

## 13. Validation Status for This Iteration

- Editor/static diagnostics: no issues detected in touched files.
- Bytecode compile check: passed for `inventory`, `core`, `stock`, and `stockmgtr`.

Note:
- Full integration test execution via Django management commands may still depend on local MySQL client runtime setup.

## 14. Foreign-Key Conversion Update

This iteration addressed the remaining string-backed stock relation fields by introducing canonical foreign-key columns while preserving the legacy string fields as transitional compatibility data.

### 14.1 What Changed

- `received_by_user` now points to `auth.User`.
- `issued_by_user` now points to `auth.User`.
- `issued_to_person` now points to `core.Person`.
- The legacy string fields (`received_by`, `issued_by`, `issued_to`) remain temporarily for safe backfill and backward compatibility.

### 14.2 Safe Migration Strategy

The conversion uses a staged path rather than a destructive in-place swap:

1. Add new nullable FK columns.
2. Backfill them from existing string values when a matching user/person exists.
3. Update services and forms to use the FK-backed fields.
4. Keep the legacy string fields during the transition window.
5. Remove legacy string fields in a later cleanup migration once data is fully verified.

Migration file added:
- `inventory/migrations/0002_add_relation_foreign_keys.py`

### 14.3 Refactorings Applied

- Replace String Relation Fields with Canonical Foreign Keys.
- Add Transitional Backfill Migration.
- Update Service Layer to Populate Both Canonical and Legacy Fields During Transition.

### 14.4 Why This Was High Priority

This was not a low-priority cleanup because the roadmap explicitly identified string-backed relations as a data integrity problem. Converting them improves:

- Referential integrity
- Query reliability
- Form/model semantics
- Export correctness
- Long-term maintainability

## 15. Category and Person Data Access Layers

Repository and service layers were added for the remaining domain boundaries that still relied on direct ORM access.

### 15.1 Category

Files added:
- `inventory/repositories/category.py`
- `inventory/services/category.py`

Purpose:
- Centralize category lookups and keep stock-facing query logic out of forms/views.

### 15.2 Person

Files added:
- `core/repositories/base.py`
- `core/repositories/person.py`
- `core/services/person.py`

Purpose:
- Provide a reusable access layer for dependent-location/person workflows.
- Remove direct ORM lookup dependency from the dependent views path where practical.

### 15.3 Additional Refactorings Applied

- Introduce Category Repository/Service.
- Introduce Person Repository/Service.
- Extract person listing access from the dependent forms view.

## 16. Updated Smell-to-Refactoring Notes

7. String-backed domain relations
- Smell: fields storing user/person names as plain strings instead of normalized relations.
- Refactoring: add canonical FK fields plus staged backfill migration.
- Files: `inventory/models.py`, `inventory/migrations/0002_add_relation_foreign_keys.py`, `inventory/services/stock.py`.

8. Direct ORM dependency in domain-adjacent flows
- Smell: category/person lookups were still spread across view/form code.
- Refactoring: add category/person repositories and services.
- Files: `inventory/repositories/category.py`, `inventory/services/category.py`, `core/repositories/person.py`, `core/services/person.py`.
