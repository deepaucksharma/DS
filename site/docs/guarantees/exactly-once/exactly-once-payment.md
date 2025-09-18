# Exactly-Once Payment Systems: Financial Transaction Patterns

## Overview

Payment systems demand the highest levels of exactly-once guarantees due to regulatory requirements and financial impact. This guide examines patterns used by Stripe, Square, PayPal, and traditional banking systems to ensure transactions are processed exactly once, with comprehensive audit trails and regulatory compliance.

## Payment Processing Architecture

```mermaid
graph TB
    subgraph PaymentArchitecture[Payment Processing Exactly-Once Architecture]
        subgraph ClientLayer[Client Layer - Blue]
            CL1[Merchant Application<br/>E-commerce checkout<br/>Mobile payment app]
            CL2[Payment Form<br/>Credit card details<br/>Payment amount]
            CL3[Idempotency Key<br/>Client-generated UUID<br/>Unique per payment attempt]
        end

        subgraph PaymentGateway[Payment Gateway - Green]
            PG1[Request Validation<br/>Amount, currency, card<br/>Fraud detection screening]
            PG2[Idempotency Check<br/>Duplicate detection<br/>Return cached result]
            PG3[Payment Intent<br/>Authorize payment<br/>Reserve funds]
        end

        subgraph ProcessingNetwork[Processing Network - Orange]
            PN1[Card Network<br/>Visa, Mastercard<br/>Authorization request]
            PN2[Issuing Bank<br/>Customer's bank<br/>Approve/decline]
            PN3[Settlement<br/>Money movement<br/>T+1 or T+2 settlement]
        end

        subgraph ComplianceLayer[Compliance Layer - Red]
            CompL1[Audit Trail<br/>Immutable transaction log<br/>Regulatory reporting]
            CompL2[Anti-Money Laundering<br/>AML screening<br/>Suspicious activity detection]
            CompL3[PCI Compliance<br/>Secure card data<br/>Encryption and tokenization]
        end
    end

    %% Flow connections
    CL1 --> PG1
    CL2 --> PG2
    CL3 --> PG3

    PG1 --> PN1
    PG2 --> PN2
    PG3 --> PN3

    PN1 --> CompL1
    PN2 --> CompL2
    PN3 --> CompL3

    %% Apply 4-plane colors
    classDef clientStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef gatewayStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef networkStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef complianceStyle fill:#CC0000,stroke:#990000,color:#fff

    class CL1,CL2,CL3 clientStyle
    class PG1,PG2,PG3 gatewayStyle
    class PN1,PN2,PN3 networkStyle
    class CompL1,CompL2,CompL3 complianceStyle
```

## Stripe Payment Intent Flow

```mermaid
sequenceDiagram
    participant Client as E-commerce Site
    participant Stripe as Stripe API
    participant Bank as Issuing Bank
    participant Webhook as Webhook Endpoint
    participant DB as Merchant Database

    Note over Client,DB: Stripe Payment Intent Exactly-Once Flow

    Client->>Stripe: POST /payment_intents<br/>Idempotency-Key: checkout_sess_abc123<br/>amount: 5000, currency: "usd"

    Stripe->>Stripe: Check idempotency key in cache
    Stripe->>Stripe: Key not found - first request

    Stripe->>Stripe: Create PaymentIntent: pi_1ABC123
    Stripe->>Stripe: Store idempotency mapping

    Stripe->>Client: 200 OK {id: "pi_1ABC123", status: "requires_payment_method"}

    Note over Client: Customer enters card details

    Client->>Stripe: POST /payment_intents/pi_1ABC123/confirm<br/>payment_method: {card: {...}}

    Stripe->>Bank: Authorization request: $50.00
    Bank->>Stripe: APPROVED: auth_code_xyz789

    Stripe->>Stripe: Update PaymentIntent: status="succeeded"

    Stripe->>Webhook: POST webhook: payment_intent.succeeded<br/>Idempotency-Key: pi_1ABC123_succeeded

    Webhook->>DB: Check if payment already processed
    DB->>Webhook: Payment not found - process it

    Webhook->>DB: Create order, update inventory
    DB->>Webhook: Order created successfully

    Webhook->>Stripe: 200 OK (webhook processed)

    Note over Client,DB: Network issue causes client retry

    Client->>Stripe: POST /payment_intents<br/>Idempotency-Key: checkout_sess_abc123<br/>(same key, same payload)

    Stripe->>Stripe: Check idempotency key in cache
    Stripe->>Stripe: Key found - return cached response

    Stripe->>Client: 200 OK {id: "pi_1ABC123", status: "succeeded"}

    Note over Client,DB: No duplicate payment created
    Note over Client,DB: Exactly-once guarantee maintained
```

## Banking System Double-Entry Accounting

```mermaid
graph TB
    subgraph BankingSystem[Banking System Double-Entry Exactly-Once]
        subgraph TransactionInitiation[Transaction Initiation]
            TI1[Wire Transfer Request<br/>From: Account A<br/>To: Account B<br/>Amount: $10,000]
            TI2[Transaction ID<br/>Unique identifier<br/>TXID: wire_20231001_001]
            TI3[Pre-Authorization<br/>Check account balance<br/>Fraud screening]
        end

        subgraph DoubleEntryLedger[Double-Entry Ledger]
            DEL1[Debit Entry<br/>Account A: -$10,000<br/>Reference: wire_20231001_001]
            DEL2[Credit Entry<br/>Account B: +$10,000<br/>Reference: wire_20231001_001]
            DEL3[Balancing Constraint<br/>Total debits = Total credits<br/>Mathematical guarantee]
        end

        subgraph AtomicCommit[Atomic Commit Process]
            AC1[Begin Transaction<br/>Database transaction<br/>All-or-nothing execution]
            AC2[Journal Entries<br/>Write to transaction log<br/>Immutable audit trail]
            AC3[Commit/Rollback<br/>Either both entries succeed<br/>or both entries fail]
        end

        subgraph ComplianceReporting[Compliance & Reporting]
            CR1[Regulatory Reports<br/>Daily position reports<br/>Central bank submissions]
            CR2[Audit Trail<br/>Complete transaction history<br/>Immutable ledger]
            CR3[Reconciliation<br/>End-of-day balancing<br/>Exception handling]
        end
    end

    TI1 --> DEL1
    TI2 --> DEL2
    TI3 --> DEL3

    DEL1 --> AC1
    DEL2 --> AC2
    DEL3 --> AC3

    AC1 --> CR1
    AC2 --> CR2
    AC3 --> CR3

    classDef initiationStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef ledgerStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef commitStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef complianceStyle fill:#CC0000,stroke:#990000,color:#fff

    class TI1,TI2,TI3 initiationStyle
    class DEL1,DEL2,DEL3 ledgerStyle
    class AC1,AC2,AC3 commitStyle
    class CR1,CR2,CR3 complianceStyle
```

## PayPal Transaction Lifecycle

```mermaid
sequenceDiagram
    participant Buyer as Buyer
    participant Merchant as Merchant
    participant PayPal as PayPal System
    participant Bank as Buyer's Bank
    participant MerchantBank as Merchant Bank

    Note over Buyer,MerchantBank: PayPal Transaction with Exactly-Once Guarantees

    Buyer->>Merchant: Purchase items ($100)
    Merchant->>PayPal: Create payment: pp_txn_abc123<br/>amount: $100, currency: USD

    PayPal->>PayPal: Generate unique transaction ID
    PayPal->>PayPal: Check for duplicate transaction

    PayPal->>Buyer: Redirect to PayPal checkout
    Buyer->>PayPal: Approve payment

    PayPal->>Bank: Debit buyer account: $100
    Bank->>PayPal: Transaction approved

    PayPal->>PayPal: Record transaction in ledger<br/>Status: COMPLETED

    PayPal->>Merchant: Webhook: payment.completed<br/>Transaction: pp_txn_abc123

    Merchant->>Merchant: Check if transaction already processed
    Merchant->>Merchant: Process order fulfillment

    Note over PayPal,MerchantBank: Settlement process (T+1)

    PayPal->>MerchantBank: Credit merchant account: $97<br/>(after fees)

    Note over Buyer,MerchantBank: Dispute scenario - exactly-once reversal

    Buyer->>PayPal: Dispute transaction: pp_txn_abc123

    PayPal->>PayPal: Check dispute eligibility
    PayPal->>PayPal: Create reversal: pp_rev_abc123

    PayPal->>MerchantBank: Debit merchant: $97
    PayPal->>Bank: Credit buyer: $100

    PayPal->>Merchant: Webhook: payment.reversed<br/>Reversal: pp_rev_abc123

    Note over Buyer,MerchantBank: Each financial movement tracked exactly once
```

## High-Frequency Trading Settlement

```mermaid
graph LR
    subgraph HFTSettlement[High-Frequency Trading Settlement System]
        subgraph TradeExecution[Trade Execution - Blue]
            TE1[Order Matching<br/>Microsecond latency<br/>FIFO price-time priority]
            TE2[Trade Confirmation<br/>Unique trade ID<br/>Immutable trade record]
            TE3[Risk Checks<br/>Position limits<br/>Margin requirements]
        end

        subgraph ClearingProcess[Clearing Process - Green]
            CP1[Trade Netting<br/>Multilateral netting<br/>Reduce settlement volume]
            CP2[Novation<br/>Central counterparty<br/>Becomes trade counterparty]
            CP3[Margin Calculation<br/>Initial + variation margin<br/>Daily mark-to-market]
        end

        subgraph SettlementProcess[Settlement Process - Orange]
            SP1[DVP Settlement<br/>Delivery vs Payment<br/>Atomic exchange]
            SP2[Cash Movement<br/>Central bank accounts<br/>Real-time gross settlement]
            SP3[Securities Transfer<br/>Dematerialized form<br/>Electronic book entries]
        end

        subgraph RiskManagement[Risk Management - Red]
            RM1[Position Monitoring<br/>Real-time exposure<br/>Limit enforcement]
            RM2[Collateral Management<br/>Margin calls<br/>Liquidity facilities]
            RM3[Default Procedures<br/>Member default<br/>Loss allocation]
        end
    end

    TE1 --> CP1
    TE2 --> CP2
    TE3 --> CP3

    CP1 --> SP1
    CP2 --> SP2
    CP3 --> SP3

    SP1 --> RM1
    SP2 --> RM2
    SP3 --> RM3

    classDef executionStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef clearingStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef settlementStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef riskStyle fill:#CC0000,stroke:#990000,color:#fff

    class TE1,TE2,TE3 executionStyle
    class CP1,CP2,CP3 clearingStyle
    class SP1,SP2,SP3 settlementStyle
    class RM1,RM2,RM3 riskStyle
```

## Cryptocurrency Payment Gateway

```mermaid
sequenceDiagram
    participant Customer as Customer
    participant Gateway as Crypto Gateway
    participant Blockchain as Blockchain Network
    participant Exchange as Exchange
    participant Merchant as Merchant

    Note over Customer,Merchant: Cryptocurrency Payment with Exactly-Once Settlement

    Customer->>Gateway: Pay 0.1 BTC for order #12345
    Gateway->>Gateway: Generate unique payment address<br/>Address: bc1q...abc123

    Gateway->>Customer: Pay to address: bc1q...abc123<br/>Amount: 0.1 BTC exactly

    Customer->>Blockchain: Broadcast transaction<br/>TxID: a1b2c3d4e5f6...

    Note over Blockchain: Transaction confirmed (6+ blocks)

    Blockchain->>Gateway: Transaction confirmed<br/>TxID: a1b2c3d4e5f6...<br/>Confirmations: 6

    Gateway->>Gateway: Verify exact amount received<br/>Check for double-spending

    Gateway->>Exchange: Convert 0.1 BTC to USD<br/>Rate: $30,000/BTC = $3,000

    Exchange->>Gateway: Conversion completed<br/>USD amount: $2,970 (after fees)

    Gateway->>Merchant: Credit merchant account<br/>Payment ID: crypto_pay_xyz789<br/>Amount: $2,970

    Merchant->>Merchant: Check payment not already processed
    Merchant->>Merchant: Fulfill order #12345

    Gateway->>Merchant: Webhook: payment.confirmed<br/>blockchain_tx: a1b2c3d4e5f6...

    Note over Customer,Merchant: Blockchain guarantees no double-spend
    Note over Customer,Merchant: Gateway ensures no duplicate processing
    Note over Customer,Merchant: Exactly-once conversion and settlement
```

## Payment Implementation Code

```python
import uuid
import time
import hashlib
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

class PaymentStatus(Enum):
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

@dataclass
class PaymentIntent:
    id: str
    merchant_id: str
    amount_cents: int
    currency: str
    status: PaymentStatus
    idempotency_key: str
    created_at: float
    metadata: Dict[str, Any]

class PaymentProcessor:
    """Production payment processor with exactly-once guarantees"""

    def __init__(self, database, audit_logger):
        self.db = database
        self.audit = audit_logger
        self.logger = logging.getLogger(__name__)

    async def create_payment_intent(self, merchant_id: str, amount_cents: int,
                                  currency: str, idempotency_key: str,
                                  metadata: Dict = None) -> PaymentIntent:
        """Create payment intent with exactly-once guarantee"""

        # Check for existing payment with same idempotency key
        existing = await self.get_payment_by_idempotency_key(
            merchant_id, idempotency_key
        )
        if existing:
            self.logger.info(f"Returning existing payment for key {idempotency_key}")
            return existing

        # Validate payment parameters
        await self.validate_payment_request(merchant_id, amount_cents, currency)

        # Generate unique payment ID
        payment_id = f"pi_{uuid.uuid4().hex}"

        # Create payment intent
        payment = PaymentIntent(
            id=payment_id,
            merchant_id=merchant_id,
            amount_cents=amount_cents,
            currency=currency,
            status=PaymentStatus.PENDING,
            idempotency_key=idempotency_key,
            created_at=time.time(),
            metadata=metadata or {}
        )

        # Atomic database insertion with unique constraint on idempotency key
        try:
            await self.db.insert_payment_intent(payment)
            await self.audit.log_payment_created(payment)
            return payment

        except UniqueConstraintViolation:
            # Another request created payment first - return that one
            existing = await self.get_payment_by_idempotency_key(
                merchant_id, idempotency_key
            )
            return existing

    async def capture_payment(self, payment_id: str,
                            amount_cents: Optional[int] = None) -> Dict[str, Any]:
        """Capture authorized payment with exactly-once guarantee"""

        # Get payment with pessimistic lock
        payment = await self.db.get_payment_for_update(payment_id)
        if not payment:
            raise PaymentNotFoundError(f"Payment {payment_id} not found")

        # Check if already captured
        if payment.status == PaymentStatus.CAPTURED:
            self.logger.info(f"Payment {payment_id} already captured")
            return self.format_payment_response(payment)

        # Validate capture request
        if payment.status != PaymentStatus.AUTHORIZED:
            raise InvalidPaymentStateError(
                f"Cannot capture payment in status {payment.status}"
            )

        capture_amount = amount_cents or payment.amount_cents
        if capture_amount > payment.amount_cents:
            raise InvalidAmountError("Capture amount exceeds authorized amount")

        try:
            # Process capture with payment network
            capture_result = await self.process_network_capture(
                payment, capture_amount
            )

            # Update payment status atomically
            await self.db.update_payment_status(
                payment_id, PaymentStatus.CAPTURED
            )

            # Create immutable audit record
            await self.audit.log_payment_captured(
                payment_id, capture_amount, capture_result
            )

            # Send webhooks asynchronously (with own idempotency)
            await self.send_payment_webhook(payment, "payment.captured")

            return self.format_payment_response(payment)

        except NetworkError as e:
            self.logger.error(f"Network error capturing payment {payment_id}: {e}")
            await self.db.update_payment_status(payment_id, PaymentStatus.FAILED)
            raise PaymentProcessingError("Payment capture failed")

    async def refund_payment(self, payment_id: str, amount_cents: int,
                           reason: str, idempotency_key: str) -> Dict[str, Any]:
        """Refund payment with exactly-once guarantee"""

        # Check for existing refund with same idempotency key
        existing_refund = await self.get_refund_by_idempotency_key(
            payment_id, idempotency_key
        )
        if existing_refund:
            return self.format_refund_response(existing_refund)

        # Get payment with lock
        payment = await self.db.get_payment_for_update(payment_id)
        if not payment:
            raise PaymentNotFoundError(f"Payment {payment_id} not found")

        # Validate refund request
        if payment.status != PaymentStatus.CAPTURED:
            raise InvalidPaymentStateError(
                f"Cannot refund payment in status {payment.status}"
            )

        # Check refund amount limits
        total_refunded = await self.get_total_refunded_amount(payment_id)
        if total_refunded + amount_cents > payment.amount_cents:
            raise InvalidAmountError("Refund amount exceeds captured amount")

        # Generate unique refund ID
        refund_id = f"re_{uuid.uuid4().hex}"

        try:
            # Begin database transaction
            async with self.db.transaction():
                # Process refund with payment network
                refund_result = await self.process_network_refund(
                    payment, amount_cents, reason
                )

                # Create refund record
                refund = await self.db.create_refund(
                    id=refund_id,
                    payment_id=payment_id,
                    amount_cents=amount_cents,
                    reason=reason,
                    idempotency_key=idempotency_key,
                    network_result=refund_result
                )

                # Update payment status if fully refunded
                if total_refunded + amount_cents == payment.amount_cents:
                    await self.db.update_payment_status(
                        payment_id, PaymentStatus.REFUNDED
                    )

                # Create audit trail
                await self.audit.log_refund_processed(refund)

            # Send webhooks
            await self.send_refund_webhook(refund)

            return self.format_refund_response(refund)

        except NetworkError as e:
            self.logger.error(f"Network error refunding payment {payment_id}: {e}")
            raise RefundProcessingError("Refund processing failed")

    async def validate_payment_request(self, merchant_id: str, amount_cents: int,
                                     currency: str):
        """Validate payment request parameters"""
        if amount_cents <= 0:
            raise InvalidAmountError("Amount must be positive")

        if currency not in ["USD", "EUR", "GBP"]:  # Supported currencies
            raise UnsupportedCurrencyError(f"Currency {currency} not supported")

        # Check merchant limits
        merchant_limits = await self.get_merchant_limits(merchant_id)
        if amount_cents > merchant_limits.max_transaction_amount:
            raise MerchantLimitExceededError("Transaction exceeds merchant limits")

    async def process_network_capture(self, payment: PaymentIntent,
                                    amount_cents: int) -> Dict[str, Any]:
        """Process capture with payment network"""
        # Implementation depends on specific payment processor
        # (Stripe, Square, traditional bank, etc.)
        pass

# Database schema for exactly-once guarantees
CREATE_TABLES_SQL = """
-- Payment intents table with idempotency key constraint
CREATE TABLE payment_intents (
    id VARCHAR(255) PRIMARY KEY,
    merchant_id VARCHAR(255) NOT NULL,
    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status VARCHAR(50) NOT NULL,
    idempotency_key VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    metadata JSONB,

    -- Ensure exactly-once per merchant + idempotency key
    UNIQUE(merchant_id, idempotency_key)
);

-- Refunds table with idempotency key constraint
CREATE TABLE refunds (
    id VARCHAR(255) PRIMARY KEY,
    payment_id VARCHAR(255) NOT NULL REFERENCES payment_intents(id),
    amount_cents INTEGER NOT NULL,
    reason TEXT,
    idempotency_key VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    network_transaction_id VARCHAR(255),

    -- Ensure exactly-once refund per payment + idempotency key
    UNIQUE(payment_id, idempotency_key)
);

-- Immutable audit log
CREATE TABLE payment_audit_log (
    id SERIAL PRIMARY KEY,
    payment_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Immutable - no updates or deletes allowed
    -- Only inserts for complete audit trail
);

-- Indexes for performance
CREATE INDEX idx_payment_intents_merchant_created ON payment_intents(merchant_id, created_at);
CREATE INDEX idx_refunds_payment_id ON refunds(payment_id);
CREATE INDEX idx_audit_log_payment_timestamp ON payment_audit_log(payment_id, timestamp);
"""
```

## Regulatory Compliance Requirements

```mermaid
graph TB
    subgraph ComplianceRequirements[Financial Regulatory Compliance for Exactly-Once]
        subgraph AuditRequirements[Audit Requirements]
            AR1[Immutable Audit Trail<br/>Complete transaction history<br/>No deletion or modification]
            AR2[Transaction Traceability<br/>End-to-end tracking<br/>Cross-system correlation]
            AR3[Timestamp Precision<br/>Synchronized clocks<br/>Sequence ordering]
        end

        subgraph ReportingRequirements[Reporting Requirements]
            RR1[Daily Position Reports<br/>Reconcile all transactions<br/>Submit to regulators]
            RR2[Exception Reporting<br/>Failed transactions<br/>System anomalies]
            RR3[Anti-Money Laundering<br/>Suspicious activity<br/>Large transaction reporting]
        end

        subgraph DataRetention[Data Retention]
            DR1[Transaction Records<br/>7+ years retention<br/>Immediate retrieval]
            DR2[Communication Records<br/>All customer interactions<br/>Dispute resolution]
            DR3[System Logs<br/>Technical audit trail<br/>Security event logging]
        end

        subgraph AccessControls[Access Controls]
            AC1[Role-Based Access<br/>Segregation of duties<br/>Maker-checker approval]
            AC2[Audit Logging<br/>All system access<br/>User activity tracking]
            AC3[Data Encryption<br/>At rest and in transit<br/>Key management]
        end
    end

    classDef auditStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef reportingStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef retentionStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef accessStyle fill:#CC0000,stroke:#990000,color:#fff

    class AR1,AR2,AR3 auditStyle
    class RR1,RR2,RR3 reportingStyle
    class DR1,DR2,DR3 retentionStyle
    class AC1,AC2,AC3 accessStyle
```

## Disaster Recovery and Business Continuity

```mermaid
sequenceDiagram
    participant Primary as Primary Data Center
    participant Secondary as Secondary Data Center
    participant Client as Payment Client
    participant Network as Card Network

    Note over Primary,Network: Normal Operation

    Client->>Primary: Payment request: $500
    Primary->>Secondary: Replicate transaction log
    Primary->>Network: Authorization request
    Network->>Primary: APPROVED
    Primary->>Client: Payment successful
    Primary->>Secondary: Replicate success status

    Note over Primary,Network: Primary data center failure

    Primary--xClient: Primary unavailable
    Client->>Secondary: Failover - same payment request

    Secondary->>Secondary: Check replicated transaction log
    Secondary->>Secondary: Transaction already processed and approved

    Secondary->>Client: Return cached success response

    Note over Primary,Network: Exactly-once guarantee maintained during failover
    Note over Primary,Network: No duplicate authorization or charging
```

## Performance Monitoring and SLAs

```mermaid
graph LR
    subgraph PaymentSLAs[Payment System SLAs and Monitoring]
        subgraph LatencySLAs[Latency SLAs]
            LS1[Authorization: <500ms<br/>p99 response time<br/>Critical for checkout]
            LS2[Capture: <2 seconds<br/>p99 processing time<br/>Batch processing acceptable]
            LS3[Refund: <5 seconds<br/>p99 completion time<br/>Customer service priority]
        end

        subgraph AvailabilitySLAs[Availability SLAs]
            AS1[Payment Processing<br/>99.99% uptime<br/>5.3 minutes/month downtime]
            AS2[Exactly-Once Guarantee<br/>99.999% accuracy<br/>1 duplicate per 100K]
            AS3[Disaster Recovery<br/>RTO: 15 minutes<br/>RPO: 1 minute]
        end

        subgraph MonitoringMetrics[Monitoring Metrics]
            MM1[Duplicate Detection Rate<br/>Idempotency key hits<br/>Should be 5-10%]
            MM2[Failed Transaction Rate<br/>Authorization declines<br/>Target <15%]
            MM3[Reconciliation Gaps<br/>Unmatched transactions<br/>Target <0.01%]
        end

        subgraph AlertingThresholds[Alerting Thresholds]
            AT1[High Latency Alert<br/>p99 > 1 second<br/>Immediate investigation]
            AT2[Duplicate Spike Alert<br/>Duplicate rate > 20%<br/>Potential client issues]
            AT3[Reconciliation Alert<br/>Unmatched > 0.1%<br/>Financial risk]
        end
    end

    LS1 --> MM1
    AS2 --> MM2
    MM3 --> AT3

    classDef latencyStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef availabilityStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef monitoringStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef alertingStyle fill:#CC0000,stroke:#990000,color:#fff

    class LS1,LS2,LS3 latencyStyle
    class AS1,AS2,AS3 availabilityStyle
    class MM1,MM2,MM3 monitoringStyle
    class AT1,AT2,AT3 alertingStyle
```

## Testing and Validation Strategies

### Load Testing with Exactly-Once Validation
```python
import asyncio
import random
from concurrent.futures import ThreadPoolExecutor

async def test_payment_idempotency_under_load():
    """Test payment system under high load with duplicate detection"""

    payment_processor = PaymentProcessor()
    results = []

    # Generate test scenarios
    test_scenarios = []
    for i in range(1000):
        # 10% of requests are intentional duplicates
        if random.random() < 0.1 and i > 0:
            # Reuse previous idempotency key (simulate retry)
            idempotency_key = test_scenarios[i-1]["idempotency_key"]
        else:
            idempotency_key = f"test_payment_{i}_{uuid.uuid4().hex}"

        test_scenarios.append({
            "merchant_id": f"merchant_{random.randint(1, 10)}",
            "amount_cents": random.randint(100, 10000),
            "currency": "USD",
            "idempotency_key": idempotency_key
        })

    # Execute concurrent requests
    with ThreadPoolExecutor(max_workers=50) as executor:
        tasks = [
            executor.submit(payment_processor.create_payment_intent, **scenario)
            for scenario in test_scenarios
        ]

        for task in tasks:
            try:
                result = task.result(timeout=10)
                results.append(result)
            except Exception as e:
                print(f"Payment failed: {e}")

    # Validate exactly-once guarantees
    payment_ids = [r.id for r in results]
    unique_payments = set(payment_ids)

    assert len(payment_ids) == len(unique_payments), "Duplicate payments created!"

    # Check idempotency key effectiveness
    idempotency_keys = [r.idempotency_key for r in results]
    unique_keys = set(idempotency_keys)

    duplicate_count = len(idempotency_keys) - len(unique_keys)
    print(f"Detected and handled {duplicate_count} duplicate requests")

    assert duplicate_count >= 90, "Should detect ~100 duplicates (10% of 1000)"
```

## Key Takeaways

1. **Financial regulations demand exactly-once** - No room for "eventually consistent" in money movement
2. **Idempotency keys are essential** - Client-generated keys enable safe retries
3. **Audit trails must be immutable** - Complete transaction history for compliance
4. **Double-entry accounting provides natural exactness** - Mathematical constraints prevent errors
5. **Performance requirements are strict** - Sub-second authorization times expected
6. **Disaster recovery must maintain exactness** - Failover cannot create duplicates
7. **Testing must cover all failure scenarios** - Network issues, database failures, concurrent access
8. **Monitoring and alerting are critical** - Early detection of duplicate transactions prevents financial loss

Payment systems represent the most demanding use case for exactly-once delivery, where the consequences of failure include financial loss, regulatory violations, and loss of customer trust. The patterns and practices developed for payment systems often serve as templates for other critical exactly-once scenarios.