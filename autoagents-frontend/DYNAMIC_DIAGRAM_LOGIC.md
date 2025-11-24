# Dynamic Diagram Generation Logic

## Overview
The LLD and DBD builders now **intelligently parse** user input to generate context-aware diagrams instead of using hardcoded templates.

---

## LLD (Low Level Design) - Dynamic Service Generation

### How It Works:
1. **Extract Entities (Nouns)** from features and context
   - Identifies main domain objects (User, Product, Order, etc.)
   - Capitalizes and normalizes names

2. **Extract Actions (Verbs)** from features
   - Finds CRUD operations (create, update, delete, get)
   - Identifies domain-specific actions (authenticate, process, send)

3. **Generate Services** dynamically
   - Creates `{Entity}Service` classes (e.g., `UserService`, `ProductService`)
   - Adds methods like `createUser()`, `getProduct()`, `updateOrder()`
   - Includes repository fields for data access

4. **Create Relationships**
   - Connects primary service to related services

### Example Input:
```
Features:
- "User Authentication"
- "Product Catalog Management"
- "Order Processing"
```

### Generated Output:
```
UserService
  - userRepository: Repository
  + authenticateUser(): User
  + createUser(): User
  + getUser(): User

ProductService
  - productRepository: Repository
  + manageProduct(): Product
  + getProduct(): Product
  + createProduct(): Product

OrderService
  - orderRepository: Repository
  + processOrder(): Order
  + createOrder(): Order
  + getOrder(): Order
```

---

## DBD (Database Design) - Dynamic Entity Generation

### How It Works:
1. **Extract Entities** from all text (context + features + stories)
   - Identifies nouns that represent database tables
   - Normalizes to UPPERCASE (USER, PRODUCT, ORDER)

2. **Infer Fields** based on entity type
   - **Users/Customers**: name, email, phone, status
   - **Orders/Transactions**: amount, status, date
   - **Products**: name, description, price, quantity
   - **Generic**: id, name, description, status, created_at, updated_at

3. **Detect Relationships** using pattern matching
   - USER → ORDER (users have orders)
   - ACCOUNT → TRANSACTION (accounts have transactions)
   - PRODUCT → REVIEW (products have reviews)
   - CATEGORY → PRODUCT (categories have products)

4. **Infer Field Types** intelligently
   - `id`, `*_id` → uuid
   - `amount`, `price`, `balance` → float
   - `email`, `name`, `status` → varchar
   - `description`, `notes` → text
   - `created_at`, `date` → datetime
   - `active`, `enabled` → bool

### Example Input:
```
Context: "E-commerce platform for online shopping"
Features:
- "Customer Registration"
- "Product Browsing"
- "Shopping Cart"
- "Order Checkout"
```

### Generated Output:
```
CUSTOMER {
  uuid id
  varchar name
  varchar email
  varchar phone
  varchar status
  datetime created_at
  datetime updated_at
}

PRODUCT {
  uuid id
  varchar name
  text description
  float price
  int quantity
  datetime created_at
  datetime updated_at
}

ORDER {
  uuid id
  float amount
  varchar status
  datetime date
  datetime created_at
  datetime updated_at
}

CART {
  uuid id
  varchar status
  datetime created_at
  datetime updated_at
}

CUSTOMER ||--o{ ORDER : "has"
CUSTOMER ||--o{ CART : "has"
```

---

## Key Improvements

### Before (Hardcoded):
- ✗ Always generated USER, ACCOUNT, TRANSACTION, STATEMENT
- ✗ Same entities regardless of user input
- ✗ Generic AuthService, PaymentService regardless of domain
- ✗ Ignored user's actual needs

### After (Dynamic):
- ✓ Generates entities from user's prompt
- ✓ Creates services based on actual features
- ✓ Adapts to ANY domain (healthcare, education, retail, finance)
- ✓ Infers relationships intelligently
- ✓ Field types match the context

---

## Examples of Different Domains

### Healthcare System:
```
Input: "Patient management, appointment scheduling, medical records"
LLD Output: PatientService, AppointmentService, RecordService
DBD Output: PATIENT, APPOINTMENT, RECORD tables with medical fields
```

### School Management:
```
Input: "Student enrollment, course registration, grade tracking"
LLD Output: StudentService, CourseService, GradeService
DBD Output: STUDENT, COURSE, GRADE tables with academic fields
```

### Restaurant App:
```
Input: "Menu browsing, table booking, order placement"
LLD Output: MenuService, BookingService, OrderService
DBD Output: MENU, BOOKING, ORDER tables with restaurant fields
```

---

## Fallback Behavior

If no features are provided or text is too generic:

**LLD Fallback:**
```
ApplicationService
  + initialize(): void
  + execute(): void
```

**DBD Fallback:**
```
APPLICATION_DATA {
  uuid id
  varchar name
  text value
  datetime created_at
}
```

---

## Technical Details

### Entity Extraction Algorithm:
1. Split text into words
2. Filter out common words (the, and, or, etc.)
3. Identify capitalized words (proper nouns)
4. Rank by frequency
5. Take top 6 unique entities

### Action Extraction:
- Scans for 40+ common action verbs
- Matches verbs to entities
- Deduplicates per service
- Limits to 6 methods per class

### Relationship Detection:
- Pattern matching against common parent-child relationships
- Cardinality: one-to-many (||--o{) by default
- Smart label generation ("has", "owns", "contains")

---

## No More Hardcoded Diagrams! 🎉

The system now works with **any domain, any features, any stories** - making it truly universal and developer-friendly.

