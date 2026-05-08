# Software Re-engineering Project Plan: Django Stock Management System

**Author:** Fayyez Farrukh
**Course:** Software Reengineering
**Target Repository:** `DonGuillotine/stock-management-system`

---

## Phase 1: System Understanding and Design Identification

### 1.1 Architectural Style
The target system is built using the Django web framework, which inherently follows the **Model-View-Template (MVT)** architectural pattern (a variation of Model-View-Controller). 
* **Model:** Database schema defined in `models.py` (e.g., `Stock`, `Category`, `StockHistory`).
* **View:** Request/response routing and business logic heavily concentrated in `views.py`.
* **Template:** HTML rendering with Django Template Language.

### 1.2 System Organization
The current system operates as a **Monolithic Application**. All functionalities—inventory management, user registration, agile scrum boards, and geographic dropdown data—are tightly coupled within a single Django app named `stock`. 

### 1.3 Module Interactions & Current Design Patterns
* The system largely lacks formal design patterns beyond the framework's default MVT structure.
* **Module Interaction:** The UI layer (templates/Ajax) interacts directly with the View layer (`views.py`), which in turn directly manipulates the Database (ORM) and handles external file generation (CSV writing). There is no intermediary Service or Repository layer.

---

## Phase 2: Design Evaluation and Defect Identification

Based on an initial code review, several critical architectural defects and anti-patterns have been identified:

### 2.1 "Fat View" Anti-Pattern (Violation of Single Responsibility Principle)
* **Defect:** Functions in `views.py` (e.g., `issue_item`, `receive_item`, `view_stock`) are overloaded. They handle HTTP request parsing, form validation, mathematical calculations for stock levels, and database saving simultaneously.
* **Evidence:** In `issue_item`, the view directly subtracts `issue_quantity` from `quantity` and checks for negative values before calling `value.save()`.

### 2.2 Lack of High Cohesion & Poor Modularization
* **Defect:** The `stock` app contains highly unrelated domain entities.
* **Evidence:** `models.py` contains inventory models (`Stock`, `Category`) alongside human resource models (`Person`, `Contacts`) and project management models (`Scrums`, `ScrumTitles`).

### 2.3 Hardcoded File Generation (Violation of Open-Closed Principle)
* **Defect:** The CSV export logic is hardcoded directly into the views.
* **Evidence:** In `view_stock` and `view_history`, the `csv.writer` logic is explicitly written line-by-line within the `if request.method == 'POST':` block. Adding a new export format (like PDF) would require modifying the core view logic.

### 2.4 Code Duplication (Violation of DRY Principle)
* **Defect:** Redundant data structures.
* **Evidence:** `Stock` and `StockHistory` in `models.py` contain almost identical fields. Changes to the inventory schema require modifying multiple models manually.

---

## Phase 3: Re-engineering and Refactoring Strategy

To resolve the identified defects without altering the system's external behavior (UI/UX), the following re-engineering techniques will be applied:

### 3.1 Modular Restructuring (App Decomposition)
* **Action:** Break the monolith into distinct, highly cohesive Django applications:
    * `inventory` (Stock, Category, StockHistory)
    * `scrum_board` (Scrums, ScrumTitles)
    * `core` or `locations` (Country, State, City, Person)
* **Goal:** Improve maintainability and system modularity.

### 3.2 Abstraction Improvement: The Service Layer Pattern
* **Action:** Extract business logic from `views.py` into a newly created `services.py` module.
* **Implementation:** Create functions like `StockService.issue_stock(item_id, quantity)` that handle the mathematical logic and database transactions. The view will solely handle HTTP routing and passing data to the service.
* **Goal:** Resolve SRP violations and improve testability.

### 3.3 Design Pattern Injection: The Strategy Pattern
* **Action:** Refactor the export logic.
* **Implementation:** Create an abstract base class `ExportStrategy` with a concrete `CSVExportStrategy` class. The view will delegate the export task to this strategy, making the system open for extension (e.g., adding an `ExcelExportStrategy`) but closed for modification.
* **Goal:** Resolve OCP violations and improve extensibility.

### 3.4 Model Refactoring (Inheritance)
* **Action:** Use Django's abstract base classes to deduplicate `Stock` and `StockHistory` models.

---

## Phase 4: Documentation and Evaluation Deliverables

The final project submission will document the re-engineering process comprehensively:

### 4.1 Original vs. Updated Design
* **Before:** Original UML Class Diagram showing the monolithic structure, and an ERD showing the tangled database tables.
* **After:** Updated UML Diagrams illustrating the newly introduced Service Layer, Strategy Pattern classes, and modular app boundaries.

### 4.2 Code Snippet Comparisons
* Side-by-side comparisons of the "Fat View" (`views.py`) vs. the refactored "Thin View + Service Layer".

### 4.3 Quality Attribute Justification (ISO/IEC 25010)
* **Maintainability (Analysability & Modularity):** Justified by the decomposition of the `stock` app into distinct domain apps.
* **Extensibility:** Justified by the implementation of the Strategy Pattern for file exports.
* **Testability:** Justified by the extraction of pure Python business logic into `services.py`, allowing unit tests to bypass the Django HTTP request cycle.

---
*End of Document*
