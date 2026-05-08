# Stock Management System - Comprehensive Refactoring Roadmap

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Refactoring Strategy](#refactoring-strategy)
4. [Phase 1: Foundation (High Priority)](#phase-1-foundation-high-priority)
5. [Phase 2: Enhancement (Medium Priority)](#phase-2-enhancement-medium-priority)
6. [Phase 3: Polish (Lower Priority)](#phase-3-polish-lower-priority)
7. [Testing Strategy](#testing-strategy)
8. [Metrics & Success Criteria](#metrics--success-criteria)

---

## Executive Summary

This document provides a structured, step-by-step plan to refactor the Stock Management System from a tightly-coupled monolithic architecture to a layered, maintainable architecture following SOLID principles.

**Timeline:** 6-8 weeks  
**Effort:** ~80-100 development hours  
**Impact:** 40-50% improvement in maintainability, 60% code duplication reduction

---

## Current State Analysis

### Architecture Overview
```
Current Monolithic Structure:
┌──────────────────────────────────────────┐
│           Django Views (20 functions)     │
│  ├─ HTTP handling                         │
│  ├─ Database queries                      │
│  ├─ Business logic                        │
│  └─ Data formatting                       │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│         Django ORM Models (13 models)     │
│  ├─ Duplicated fields                     │
│  ├─ No validation                         │
│  └─ Weak relationships                    │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│          MySQL Database                   │
└──────────────────────────────────────────┘
```

### Key Issues Identified

| Category | Issue | Impact | Files |
|----------|-------|--------|-------|
| **Models** | Stock/StockHistory duplication | Data inconsistency | models.py |
| **Models** | Type errors (default='0') | Runtime errors | models.py |
| **Models** | String fields as ForeignKeys | Data integrity | models.py |
| **Models** | No validation | Invalid data | models.py |
| **Views** | God objects (20+ functions) | Hard to maintain | views.py |
| **Views** | Business logic in views | Untestable | views.py |
| **Views** | No error handling | Poor UX | views.py |
| **Forms** | Duplicate form definitions | DRY violation | forms.py |
| **Forms** | Inconsistent data access | Confusing patterns | forms.py |
| **Security** | String URL building | URL injection risk | views.py |
| **Security** | DEBUG=True in production | Information disclosure | settings.py |
| **Dependencies** | Outdated packages | Security vulnerabilities | requirements.txt |

---

## Refactoring Strategy

### Guiding Principles

1. **Incremental**: Make changes branch-by-branch, keeping the system functional
2. **Testable**: Each layer should be independently testable
3. **SOLID**: Follow Single Responsibility, Open/Closed, etc.
4. **Maintainable**: Code should be self-documenting with clear separation of concerns
5. **Reversible**: Each phase can be validated and reverted if needed

### Target Architecture

```
Proposed Layered Architecture:
┌──────────────────────────────────────────┐
│      Views/Controllers (HTTP Layer)      │
│  ├─ Request handling                      │
│  ├─ Response formatting                   │
│  └─ Redirect logic                        │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│     Services (Business Logic Layer)       │
│  ├─ StockService                          │
│  ├─ StockHistoryService                   │
│  ├─ ExportService                         │
│  └─ ValidationService                     │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│    Repository (Data Access Layer)         │
│  ├─ StockRepository                       │
│  ├─ CategoryRepository                    │
│  └─ PersonRepository                      │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│      Models (Domain/Data Layer)           │
│  ├─ Proper relationships                  │
│  ├─ Validation rules                      │
│  └─ Business constraints                  │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│         MySQL Database                    │
└──────────────────────────────────────────┘
```

---

# PHASE 1: FOUNDATION (High Priority)

## Week 1-2: Model Refactoring

### 1.1 Create Abstract Base Model

**File:** `stock/models/base.py` (NEW)

```python
from django.db import models
from django.core.validators import MinValueValidator

class StockBaseModel(models.Model):
    """Abstract base model for stock-related entities"""
    
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        help_text="Product category"
    )
    item_name = models.CharField(
        max_length=100,
        help_text="Name of the item"
    )
    quantity = models.IntegerField(
        default=0,  # FIX: Was '0' (string)
        validators=[MinValueValidator(0)],
        help_text="Current quantity in stock"
    )
    receive_quantity = models.IntegerField(
        default=0,  # FIX: Was '0' (string)
        validators=[MinValueValidator(0)],
        help_text="Quantity received in this transaction"
    )
    issue_quantity = models.IntegerField(
        default=0,  # FIX: Was '0' (string)
        validators=[MinValueValidator(0)],
        help_text="Quantity issued in this transaction"
    )
    re_order = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Reorder level for this item"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        help_text="User who created this record"
    )
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return f"{self.item_name} ({self.quantity})"
```

**Rationale:**
- Eliminates duplication between Stock and StockHistory
- Centralizes validation rules
- Type-correct defaults
- Self-documenting with help_text

**Changes:**
- [ ] Create new file `stock/models/base.py`
- [ ] Move common fields from Stock and StockHistory
- [ ] Fix default values from '0' to 0

---

### 1.2 Refactor Stock Model

**File:** `stock/models/stock.py` (NEW)

```python
from django.db import models
from django.utils import timezone
from .base import StockBaseModel

class Stock(StockBaseModel):
    """Current stock records"""
    
    # Operation tracking
    received_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_received'
    )
    issued_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_issued'
    )
    issued_to = models.ForeignKey(
        'Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_received'
    )
    
    # Media
    image = models.ImageField(
        upload_to='stock/images/',  # FIX: Was 'stock/static/images'
        null=True,
        blank=True,
        help_text="Product image"
    )
    
    # Status tracking
    export_to_csv = models.BooleanField(
        default=False,
        help_text="Flag to export this record to CSV"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp"
    )
    date = models.DateField(
        default=timezone.now,
        help_text="Date of transaction"
    )
    
    class Meta:
        ordering = ['-last_updated']
        indexes = [
            models.Index(fields=['item_name']),
            models.Index(fields=['category']),
            models.Index(fields=['last_updated']),
        ]
    
    def is_below_reorder_level(self) -> bool:
        """Check if stock is below reorder level"""
        return self.quantity < self.re_order
    
    def can_issue(self, quantity: int) -> bool:
        """Check if we can issue requested quantity"""
        return self.quantity >= quantity
    
    def clean(self):
        """Validate model data"""
        from django.core.exceptions import ValidationError
        
        if self.quantity < 0:
            raise ValidationError("Quantity cannot be negative")
        if self.receive_quantity < 0:
            raise ValidationError("Receive quantity cannot be negative")
        if self.issue_quantity < 0:
            raise ValidationError("Issue quantity cannot be negative")
```

**Key Changes:**
- [ ] Create `stock/models/stock.py`
- [ ] Convert received_by, issued_by, issued_to to ForeignKeys
- [ ] Fix image upload path from 'stock/static/images' to 'stock/images/'
- [ ] Add business logic methods (is_below_reorder_level, can_issue)
- [ ] Add database indexes for performance

---

### 1.3 Refactor StockHistory Model

**File:** `stock/models/history.py` (NEW)

```python
from django.db import models
from .base import StockBaseModel

class StockHistory(StockBaseModel):
    """Audit trail for stock transactions"""
    
    # Operation metadata
    received_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_history_received'
    )
    issued_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_history_issued'
    )
    issued_to = models.ForeignKey(
        'Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_history_received_to'
    )
    
    # Timestamps
    last_updated = models.DateTimeField(
        auto_now_add=False,
        null=True,
        help_text="Last update timestamp"
    )
    timestamp = models.DateTimeField(
        auto_now_add=False,
        null=True,
        help_text="Transaction timestamp"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Stock Histories'
        indexes = [
            models.Index(fields=['item_name']),
            models.Index(fields=['timestamp']),
        ]
```

**Key Changes:**
- [ ] Create `stock/models/history.py`
- [ ] Convert text fields to ForeignKeys
- [ ] Remove date field (use timestamp)
- [ ] Add proper ordering by timestamp

---

### 1.4 Update All Models to Use New Structure

**File:** `stock/models/__init__.py` (NEW)

```python
from .base import StockBaseModel
from .stock import Stock
from .history import StockHistory
from .category import Category
from .person import Country, State, City, Person
from .user import User
from .scrums import ScrumTitles, Scrums
from .contacts import Contacts

__all__ = [
    'StockBaseModel',
    'Stock',
    'StockHistory',
    'Category',
    'Country',
    'State',
    'City',
    'Person',
    'User',
    'ScrumTitles',
    'Scrums',
    'Contacts',
]
```

**Actions:**
- [ ] Convert models.py into models/ directory structure
- [ ] Create separate files for each model group
- [ ] Move existing models into appropriate files
- [ ] Update imports throughout project

---

### 1.5 Add Validation Methods

**Updates to all relevant models:**

```python
def clean(self):
    """Validate model constraints"""
    from django.core.exceptions import ValidationError
    
    # Add business rule validation
    # Examples:
    # - Item names must be unique within category
    # - Quantity cannot be negative
    # - Reorder level must be positive
```

**Actions:**
- [ ] Add clean() methods to Stock and StockHistory
- [ ] Add validators for CharField/IntegerField
- [ ] Override save() to call full_clean() if needed

---

## Week 2-3: Repository Pattern Implementation

### 2.1 Create Base Repository Class

**File:** `stock/repositories/base.py` (NEW)

```python
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from django.db import models

T = TypeVar('T', bound=models.Model)

class BaseRepository(ABC, Generic[T]):
    """Abstract repository for data access"""
    
    def __init__(self, model_class: type):
        self.model = model_class
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all records"""
        pass
    
    @abstractmethod
    def get_by_id(self, pk) -> Optional[T]:
        """Get record by primary key"""
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> T:
        """Create new record"""
        pass
    
    @abstractmethod
    def update(self, pk, **kwargs) -> T:
        """Update existing record"""
        pass
    
    @abstractmethod
    def delete(self, pk) -> bool:
        """Delete record"""
        pass
    
    def exists(self, pk) -> bool:
        """Check if record exists"""
        return self.model.objects.filter(pk=pk).exists()
```

**Rationale:**
- Provides consistent interface for all repositories
- Enables dependency injection for testing
- Centralizes query logic
- Makes it easy to switch database backends

---

### 2.2 Create StockRepository

**File:** `stock/repositories/stock.py` (NEW)

```python
from typing import List, Optional
from django.db.models import Q, F
from stock.models import Stock
from .base import BaseRepository

class StockRepository(BaseRepository):
    """Repository for Stock data access"""
    
    def __init__(self):
        super().__init__(Stock)
    
    def get_all(self) -> List[Stock]:
        """Get all stocks"""
        return list(Stock.objects.all())
    
    def get_by_id(self, pk: int) -> Optional[Stock]:
        """Get stock by ID, handles not found gracefully"""
        try:
            return Stock.objects.get(id=pk)
        except Stock.DoesNotExist:
            return None
    
    def get_by_name(self, name: str) -> List[Stock]:
        """Search stocks by item name"""
        return list(Stock.objects.filter(item_name__icontains=name))
    
    def get_by_category(self, category_id: int) -> List[Stock]:
        """Get all stocks in category"""
        return list(Stock.objects.filter(category_id=category_id))
    
    def get_below_reorder_level(self) -> List[Stock]:
        """Get items that need reordering"""
        return list(Stock.objects.filter(quantity__lt=F('re_order')))
    
    def search(self, name: str = '', category_id: int = None) -> List[Stock]:
        """Advanced search with filters"""
        queryset = Stock.objects.all()
        
        if name:
            queryset = queryset.filter(item_name__icontains=name)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return list(queryset)
    
    def create(self, **kwargs) -> Stock:
        """Create new stock record"""
        stock = Stock(**kwargs)
        stock.full_clean()
        stock.save()
        return stock
    
    def update(self, pk: int, **kwargs) -> Optional[Stock]:
        """Update stock record"""
        stock = self.get_by_id(pk)
        if not stock:
            return None
        
        for key, value in kwargs.items():
            setattr(stock, key, value)
        
        stock.full_clean()
        stock.save()
        return stock
    
    def delete(self, pk: int) -> bool:
        """Delete stock record"""
        stock = self.get_by_id(pk)
        if stock:
            stock.delete()
            return True
        return False
    
    def get_low_stock_summary(self) -> List[dict]:
        """Get summary of items below reorder level"""
        return [
            {
                'id': s.id,
                'name': s.item_name,
                'current': s.quantity,
                'reorder_level': s.re_order,
                'shortage': s.re_order - s.quantity,
            }
            for s in self.get_below_reorder_level()
        ]
```

**Actions:**
- [ ] Create `stock/repositories/` directory
- [ ] Create base.py with BaseRepository
- [ ] Create stock.py with StockRepository
- [ ] Create similar repositories for Category, Person, etc.

---

### 2.3 Create Other Repositories

**Files:** `stock/repositories/{category,person,history}.py` (NEW)

Create similar repositories for:
- CategoryRepository
- PersonRepository
- StockHistoryRepository

**Example structure:**

```python
class CategoryRepository(BaseRepository):
    def get_all(self) -> List[Category]:
        return list(Category.objects.all())
    
    def get_by_id(self, pk: int) -> Optional[Category]:
        try:
            return Category.objects.get(id=pk)
        except Category.DoesNotExist:
            return None
    
    # ... other methods
```

---

### 2.4 Create Repository Factory

**File:** `stock/repositories/__init__.py` (NEW)

```python
from .stock import StockRepository
from .category import CategoryRepository
from .person import PersonRepository
from .history import StockHistoryRepository

class RepositoryFactory:
    """Factory for creating repository instances"""
    
    _repositories = {
        'stock': StockRepository,
        'category': CategoryRepository,
        'person': PersonRepository,
        'history': StockHistoryRepository,
    }
    
    @classmethod
    def get_repository(cls, name: str):
        """Get repository instance by name"""
        repo_class = cls._repositories.get(name)
        if not repo_class:
            raise ValueError(f"Unknown repository: {name}")
        return repo_class()

# Make repositories easily accessible
stock_repo = StockRepository()
category_repo = CategoryRepository()
person_repo = PersonRepository()
history_repo = StockHistoryRepository()
```

**Benefits:**
- [ ] Centralized repository access
- [ ] Easy to mock for testing
- [ ] Single source of truth for data access

---

## Week 3-4: Service Layer Implementation

### 3.1 Create Base Service Class

**File:** `stock/services/base.py` (NEW)

```python
from abc import ABC
from django.db import transaction

class BaseService(ABC):
    """Base service class with common functionality"""
    
    @staticmethod
    def atomic(func):
        """Decorator for atomic database transactions"""
        def wrapper(*args, **kwargs):
            with transaction.atomic():
                return func(*args, **kwargs)
        return wrapper
```

---

### 3.2 Create StockService

**File:** `stock/services/stock.py` (NEW)

```python
from typing import List, Optional
from django.core.exceptions import ValidationError
from stock.models import Stock
from stock.repositories import StockRepository
from .base import BaseService

class StockService(BaseService):
    """Business logic for stock operations"""
    
    def __init__(self, repo: StockRepository = None):
        self.repo = repo or StockRepository()
    
    @BaseService.atomic
    def issue_stock(self, stock_id: int, quantity: int, 
                   issued_by_id: int, issued_to_id: int) -> Stock:
        """
        Issue stock to someone
        
        Args:
            stock_id: ID of stock to issue
            quantity: Quantity to issue
            issued_by_id: User ID of person issuing
            issued_to_id: Person ID receiving
        
        Returns:
            Updated Stock object
        
        Raises:
            ValidationError: If stock doesn't exist or insufficient quantity
        """
        stock = self.repo.get_by_id(stock_id)
        if not stock:
            raise ValidationError(f"Stock {stock_id} not found")
        
        if not stock.can_issue(quantity):
            raise ValidationError(
                f"Insufficient stock. Available: {stock.quantity}, "
                f"Requested: {quantity}"
            )
        
        # Update stock
        stock.quantity -= quantity
        stock.issue_quantity = quantity
        stock.issued_by_id = issued_by_id
        stock.issued_to_id = issued_to_id
        stock.receive_quantity = 0
        
        stock.full_clean()
        stock.save()
        
        return stock
    
    @BaseService.atomic
    def receive_stock(self, stock_id: int, quantity: int, 
                     received_by_id: int) -> Stock:
        """
        Receive stock into inventory
        
        Args:
            stock_id: ID of stock to receive
            quantity: Quantity received
            received_by_id: User ID of person receiving
        
        Returns:
            Updated Stock object
        """
        stock = self.repo.get_by_id(stock_id)
        if not stock:
            raise ValidationError(f"Stock {stock_id} not found")
        
        stock.quantity += quantity
        stock.receive_quantity = quantity
        stock.received_by_id = received_by_id
        stock.issue_quantity = 0
        
        stock.full_clean()
        stock.save()
        
        return stock
    
    @BaseService.atomic
    def set_reorder_level(self, stock_id: int, reorder_level: int) -> Stock:
        """Update reorder level for stock"""
        stock = self.repo.get_by_id(stock_id)
        if not stock:
            raise ValidationError(f"Stock {stock_id} not found")
        
        stock.re_order = reorder_level
        stock.full_clean()
        stock.save()
        
        return stock
    
    def get_low_stock_items(self) -> List[Stock]:
        """Get all items below reorder level"""
        return self.repo.get_below_reorder_level()
    
    def search_stocks(self, name: str = '', category_id: int = None) -> List[Stock]:
        """Search stocks with filters"""
        return self.repo.search(name=name, category_id=category_id)
```

**Key Features:**
- [ ] Encapsulates business logic separate from views
- [ ] Uses repository for data access
- [ ] Includes validation and error handling
- [ ] Atomic transactions for data consistency
- [ ] Single responsibility for stock operations

---

### 3.3 Create ExportService

**File:** `stock/services/export.py` (NEW)

```python
import csv
from io import StringIO
from typing import List
from stock.models import Stock, StockHistory

class ExportService:
    """Service for exporting stock data"""
    
    @staticmethod
    def export_stocks_to_csv(stocks: List[Stock]) -> str:
        """
        Export stocks to CSV format
        
        Args:
            stocks: List of Stock objects to export
        
        Returns:
            CSV content as string
        """
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY', 
                        'REORDER LEVEL', 'LAST UPDATED'])
        
        for stock in stocks:
            writer.writerow([
                stock.category.group,
                stock.item_name,
                stock.quantity,
                stock.re_order,
                stock.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_history_to_csv(history: List[StockHistory]) -> str:
        """
        Export stock history to CSV format
        
        Args:
            history: List of StockHistory objects
        
        Returns:
            CSV content as string
        """
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY',
                        'ISSUE QUANTITY', 'RECEIVE QUANTITY',
                        'RECEIVED BY', 'ISSUED BY', 'TIMESTAMP'])
        
        for record in history:
            writer.writerow([
                record.category.group,
                record.item_name,
                record.quantity,
                record.issue_quantity,
                record.receive_quantity,
                record.received_by.username if record.received_by else '',
                record.issued_by.username if record.issued_by else '',
                record.timestamp.strftime('%Y-%m-%d %H:%M:%S') if record.timestamp else '',
            ])
        
        return output.getvalue()
```

**Benefits:**
- [ ] CSV logic separated from views
- [ ] Reusable across multiple views
- [ ] Easy to extend for other formats (JSON, Excel, etc.)
- [ ] Testable independently

---

### 3.4 Create Service Factory

**File:** `stock/services/__init__.py` (NEW)

```python
from .stock import StockService
from .export import ExportService

class ServiceFactory:
    """Factory for creating service instances"""
    
    _stock_service = None
    
    @classmethod
    def get_stock_service(cls) -> StockService:
        if cls._stock_service is None:
            cls._stock_service = StockService()
        return cls._stock_service
    
    @classmethod
    def get_export_service(cls) -> ExportService:
        return ExportService()

# Convenience exports
stock_service = ServiceFactory.get_stock_service()
export_service = ServiceFactory.get_export_service()
```

---

## Week 4-5: Refactor Views

### 4.1 Update Views to Use Services

**File:** `stock/views.py` (REFACTORED)

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from stock.models import Stock
from stock.forms import StockCreateForm, IssueForm, ReceiveForm
from stock.services import stock_service, export_service
from stock.repositories import stock_repo

@login_required
def view_stock(request):
    """View all stocks with search/filter"""
    title = "VIEW STOCKS"
    
    name_filter = request.POST.get('item_name', '')
    category_id = request.POST.get('category', '')
    
    # Use repository for data access
    stocks = stock_repo.search(
        name=name_filter,
        category_id=category_id if category_id else None
    )
    
    # Handle CSV export
    if request.POST.get('export_to_CSV'):
        csv_content = export_service.export_stocks_to_csv(stocks)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="stocks.csv"'
        response.write(csv_content)
        return response
    
    context = {
        'title': title,
        'stocks': stocks,
    }
    return render(request, 'stock/view_stock.html', context)


@login_required
def issue_item(request, pk):
    """Issue stock to customer"""
    stock = get_object_or_404(Stock, id=pk)
    
    if request.method == 'POST':
        form = IssueForm(request.POST, instance=stock)
        if form.is_valid():
            try:
                quantity = form.cleaned_data['issue_quantity']
                issued_to_id = form.cleaned_data['issued_to'].id
                
                # Use service for business logic
                stock_service.issue_stock(
                    stock_id=stock.id,
                    quantity=quantity,
                    issued_by_id=request.user.id,
                    issued_to_id=issued_to_id
                )
                
                messages.success(
                    request,
                    f"Issued {quantity} {stock.item_name}(s) successfully. "
                    f"{stock.quantity} now in store."
                )
                return redirect(reverse('stock_detail', args=[stock.id]))
                
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = IssueForm(instance=stock)
    
    context = {
        'title': f'Issue {stock.item_name}',
        'stock': stock,
        'form': form,
    }
    return render(request, 'stock/add_stock.html', context)


@login_required
def receive_item(request, pk):
    """Receive stock into inventory"""
    stock = get_object_or_404(Stock, id=pk)
    
    if request.method == 'POST':
        form = ReceiveForm(request.POST, instance=stock)
        if form.is_valid():
            try:
                quantity = form.cleaned_data['receive_quantity']
                
                # Use service for business logic
                stock_service.receive_stock(
                    stock_id=stock.id,
                    quantity=quantity,
                    received_by_id=request.user.id
                )
                
                messages.success(
                    request,
                    f"Received {quantity} {stock.item_name}(s) successfully. "
                    f"{stock.quantity} now in store."
                )
                return redirect(reverse('stock_detail', args=[stock.id]))
                
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = ReceiveForm(instance=stock)
    
    context = {
        'title': f'Receive {stock.item_name}',
        'stock': stock,
        'form': form,
    }
    return render(request, 'stock/add_stock.html', context)
```

**Key Improvements:**
- [ ] No raw database queries in views
- [ ] Business logic delegated to services
- [ ] Proper error handling with ValidationError
- [ ] Use of Django's get_object_or_404() instead of bare get()
- [ ] Use of reverse() for URL generation instead of string building
- [ ] Clean separation of concerns

---

## Week 5: Form Refactoring

### 5.1 Create Base Forms

**File:** `stock/forms.py` (REFACTORED)

```python
from django import forms
from stock.models import Stock, StockHistory, Category, Person

class BaseStockForm(forms.ModelForm):
    """Base form with common stock fields"""
    
    class Meta:
        model = Stock
        fields = ['category', 'item_name', 'quantity']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'item_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter item name'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }


class StockCreateForm(BaseStockForm):
    """Form for creating new stock"""
    
    class Meta(BaseStockForm.Meta):
        fields = BaseStockForm.Meta.fields + ['image', 'date']
        widgets = {
            **BaseStockForm.Meta.widgets,
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class StockUpdateForm(BaseStockForm):
    """Form for updating stock"""
    
    class Meta(BaseStockForm.Meta):
        fields = BaseStockForm.Meta.fields + ['image']


class IssueForm(forms.ModelForm):
    """Form for issuing stock"""
    
    class Meta:
        model = Stock
        fields = ['issue_quantity', 'issued_to']
        widgets = {
            'issue_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'issued_to': forms.Select(attrs={'class': 'form-control'}),
        }


class ReceiveForm(forms.ModelForm):
    """Form for receiving stock"""
    
    class Meta:
        model = Stock
        fields = ['receive_quantity']
        widgets = {
            'receive_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
        }


class StockSearchForm(forms.Form):
    """Form for searching stocks"""
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    item_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by item name'
        })
    )
    export_to_csv = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
```

**Improvements:**
- [ ] Inheritance reduces duplication
- [ ] Consistent CSS classes
- [ ] Proper widget configuration
- [ ] Better field organization

---

# PHASE 2: ENHANCEMENT (Medium Priority)

## Week 6: Error Handling & Middleware

### Create Custom Exception Classes

**File:** `stock/exceptions.py` (NEW)

```python
class StockException(Exception):
    """Base exception for stock operations"""
    pass

class InsufficientStockError(StockException):
    """Raised when stock quantity is insufficient"""
    pass

class StockNotFoundError(StockException):
    """Raised when stock record not found"""
    pass

class InvalidQuantityError(StockException):
    """Raised when quantity is invalid"""
    pass
```

### Create Error Handling Middleware

**File:** `stock/middleware.py` (NEW)

```python
import logging
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from .exceptions import StockException

logger = logging.getLogger(__name__)

class StockExceptionMiddleware:
    """Handle stock-specific exceptions"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
        except StockException as e:
            logger.error(f"Stock error: {str(e)}")
            # Return JSON or HTML response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': str(e)}, status=400)
            # Handle appropriately
        
        return response
```

---

## Week 7: Logging & Monitoring

### Implement Logging

**File:** `stock/logging_config.py` (NEW)

```python
import logging
from django.conf import settings

def configure_logging():
    """Configure application logging"""
    
    logger = logging.getLogger('stock')
    handler = logging.FileHandler('stock.log')
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    return logger
```

---

# PHASE 3: POLISH (Lower Priority)

## Week 8: Testing & Optimization

### Create Unit Tests

**File:** `stock/tests/test_services.py` (NEW)

```python
from django.test import TestCase
from stock.services import StockService
from stock.models import Stock, Category
from django.core.exceptions import ValidationError

class StockServiceTestCase(TestCase):
    
    def setUp(self):
        self.category = Category.objects.create(group='Electronics')
        self.stock = Stock.objects.create(
            category=self.category,
            item_name='Laptop',
            quantity=10,
            re_order=5
        )
        self.service = StockService()
    
    def test_issue_stock_success(self):
        """Test issuing stock successfully"""
        updated_stock = self.service.issue_stock(
            stock_id=self.stock.id,
            quantity=5,
            issued_by_id=1,
            issued_to_id=1
        )
        
        self.assertEqual(updated_stock.quantity, 5)
    
    def test_issue_stock_insufficient(self):
        """Test issuing more than available"""
        with self.assertRaises(ValidationError):
            self.service.issue_stock(
                stock_id=self.stock.id,
                quantity=20,
                issued_by_id=1,
                issued_to_id=1
            )
```

---

## Success Metrics

### Code Quality Metrics

| Metric | Before | Target | After |
|--------|--------|--------|-------|
| Lines per function | 50-80 | 20-30 | 15-25 |
| Cyclomatic complexity | 8-12 | 3-5 | 2-4 |
| Code duplication | 40% | <20% | 15% |
| Test coverage | 0% | >70% | 80%+ |
| SOLID compliance | 0/5 | 4/5 | 5/5 |

### Maintainability Metrics

| Metric | Before | After |
|--------|--------|-------|
| Time to add feature | 4-8 hrs | 1-2 hrs |
| Time to fix bug | 3-6 hrs | 1-2 hrs |
| Code review time | 45 min | 15 min |
| Onboarding time | 2 weeks | 3 days |

### Technical Debt

| Item | Priority | Effort |
|------|----------|--------|
| Remove wildcard imports | High | 30 min |
| Add type hints | Medium | 4 hrs |
| Update dependencies | High | 2 hrs |
| Add API documentation | Low | 8 hrs |

---

## Migration Strategy

### Step 1: Prepare (1-2 hours)
- Create feature branch: `git checkout -b refactor/phase-1`
- Set up new directory structure
- Document migration plan

### Step 2: Model Refactoring (4 hours)
- Create models/ directory structure
- Create new base models
- Create migrations: `python manage.py makemigrations`
- Update imports

### Step 3: Test & Verify (2 hours)
- Run full test suite
- Check admin interface works
- Verify templates still render

### Step 4: Repository Implementation (6 hours)
- Create repositories directory
- Implement all repositories
- Update views to use repositories

### Step 5: Service Layer (8 hours)
- Create services directory
- Implement all services
- Refactor critical views

### Step 6: Final Testing (4 hours)
- Integration testing
- Manual testing of key workflows
- Performance testing

### Step 7: Documentation (3 hours)
- Update code documentation
- Create migration guide
- Document new architecture

---

## Risk Mitigation

### Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Database migration fails | Low | Critical | Test on copy, backup, rollback plan |
| Performance degradation | Medium | High | Profile before/after, optimize queries |
| Breaking changes | Medium | High | Comprehensive testing, gradual rollout |
| Lost functionality | Low | Critical | Feature parity tests, user testing |

---

## Branch Strategy

```
main
├── refactor/phase-1-models (Models + Tests)
├── refactor/phase-2-repositories (Repositories)
├── refactor/phase-3-services (Services)
├── refactor/phase-4-views (Views)
└── refactor/phase-5-forms (Forms)

Each branch:
- Focused on single concern
- Fully tested before PR
- Documented changes
- Reviewable in scope
```

---

## Checklist

### Phase 1: Models
- [ ] Create models/ directory structure
- [ ] Create base models
- [ ] Create specific models
- [ ] Fix type errors
- [ ] Add relationships
- [ ] Create migrations
- [ ] Test admin interface
- [ ] Update imports

### Phase 2: Repositories
- [ ] Create repositories/ directory
- [ ] Create base repository
- [ ] Create specific repositories
- [ ] Add repository factory
- [ ] Update documentation
- [ ] Create repository tests

### Phase 3: Services
- [ ] Create services/ directory
- [ ] Create base service
- [ ] Create specific services
- [ ] Add transaction handling
- [ ] Add logging
- [ ] Create service tests

### Phase 4: Views
- [ ] Update imports
- [ ] Inject dependencies
- [ ] Replace direct ORM calls
- [ ] Use services for logic
- [ ] Add error handling
- [ ] Test all views

### Phase 5: Forms
- [ ] Remove duplication
- [ ] Create base forms
- [ ] Add widgets
- [ ] Add validation
- [ ] Test forms

---

## Resources & References

- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Django Service Layer Pattern](https://docs.djangoproject.com/en/stable/topics/db/transactions/)

---

## Conclusion

This refactoring roadmap provides a structured, incremental approach to improving the Stock Management System. By following this plan, you will:

1. **Improve Code Quality**: Reduce complexity, duplication, and violations
2. **Enhance Maintainability**: Easier to understand, modify, and extend
3. **Enable Testing**: Better testability through separation of concerns
4. **Follow Best Practices**: Implement SOLID principles and design patterns
5. **Create Portfolio Work**: Demonstrate professional software engineering skills

Expected timeline: **6-8 weeks**  
Expected effort: **80-100 hours**  
Expected improvement: **40-50% better maintainability**
