# Multi-Tenant Usage Metering API

A multi-tenant backend API that enforces **per-tenant monthly usage limits** using API-key authentication.

The system models a common SaaS backend problem: isolating tenants, tracking usage reliably, and enforcing quotas under concurrent access, without relying on background workers.

---

## Features

* **Multi-tenant architecture** with strict tenant isolation
* **API-key authentication** via `X-API-Key` header
* **Admin vs tenant authorization separation**
* **Per-tenant monthly usage limits**
* **Concurrency-safe usage metering** using transactional row-level locking
* **Lazy billing-period rollover** without any background jobs
* **Alembic migrations**

---

## High-Level Design

### Multi-Tenancy

- Each tenant is represented by a `Tenant` record containing plan configuration, billing period, and usage.
- Every request is scoped to exactly one tenant, resolved via an API key.
- Usage accounting and authorization decisions are isolated per tenant via `tenant_id`.

This design supports an arbitrary number of tenants while keeping usage tracking and quota enforcement strictly separated.

---

### Authentication & Authorization

#### Tenant Authentication

* Clients authenticate using an API key provided via the `X-API-Key` header.
* API keys are generated once during tenant creation.
* Only a **hashed version** of the API key is stored in the database.
* The plaintext key is **never retrievable** after creation.

#### Admin Authentication

- Admin-only endpoints are protected using a static admin token loaded from application configuration.
- The admin token is not hardcoded and can be replaced via environment configuration changes.


#### Authorization Model

* **Admin-only endpoints**: tenant lifecycle and usage control
* **Tenant-only endpoints**: usage consumption and usage inspection

---

## Usage Metering & Quota Enforcement

### Billing Period Model

Each tenant maintains:

* `monthly_usage_limit`
* `current_usage`
* `period_start` (inclusive)
* `period_end` (exclusive)

Billing periods align with calendar months and are stored explicitly per tenant.

---

### Lazy Billing-Period Rollover

The system does **not** rely on background workers or scheduled jobs to reset usage.

Instead, billing rollover is handled lazily:

* On each usage-increment request, the current time is compared against `period_end`.
* If the billing period has elapsed:

  * Usage is reset to zero.
  * New `period_start` and `period_end` values are calculated for the new month.

This approach ensures:

* No cron jobs or background workers are required
* Correct behavior even if a tenant is inactive for extended periods
* Deterministic state transitions driven by real traffic

---

### Concurrency-Safe Usage Incrementation

Usage increments are handled inside a single database transaction using **row-level locking**:

* The tenant row is selected using `SELECT ... FOR UPDATE`.
* Billing rollover (if required) and quota checks are performed while holding the lock.
* Usage is incremented atomically and committed.

This guarantees:

* No race conditions under concurrent requests
* No quota overruns due to parallel increments
* At-most-once usage increment per request

---

## API Overview

### Admin Endpoints

#### Create Tenant

* Creates a new tenant with a plan and monthly usage limit
* Initializes the billing period
* Generates and returns the tenant API key **once**

#### Update Tenant

* Updates tenant plan and monthly usage limit
* Does not rotate or reissue API keys

#### Reset Tenant Usage

* Resets `current_usage` to zero
* Recalculates the billing period based on the current month
* Intended for administrative or billing correction scenarios

---

### Tenant Endpoints

#### Increment Usage

* Increments tenant usage by one unit per request
* Applies lazy billing rollover if the billing period has elapsed
* Enforces monthly usage limits atomically

#### Retrieve Usage

* Returns current usage and billing-period information for the tenant

---

## Possible Extensions

* Automated billing-cycle resets via background workers
* API key rotation and revocation
* Rate limiting per tenant
* Integration with external billing providers (like Stripe)

---

## Purpose

This project was built to demonstrate:

* Multi-tenant backend design
* Correct quota enforcement under concurrency
* Clean separation of authentication and authorization concerns
* Practical backend tradeoffs for usage-metered APIs

It is intended as a learning and portfolio project rather than a production SaaS system.
