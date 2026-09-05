# REVIVE — Autonomous AI Revenue Recovery Agent


> **“REVIVE isn't optimized to take the most actions. It's optimized to take the right actions.”**


---

## 🚀 Overview

REVIVE is an autonomous AI revenue recovery platform that detects revenue-loss events, evaluates risk using Machine Learning, retrieves relevant context using **RAG**, uses an LLM to diagnose and recommend recovery actions, executes approved actions through Razorpay, verifies outcomes, and maintains a complete audit trail.

REVIVE focuses on:

* Failed payments
* Checkout abandonment
* Subscription failures
* Overdue receivables
* Repeated payment failures

 **Detect Revenue at Risk → Diagnose → Decide → Act → Verify → Recover → Audit**


---

## 🎯 Problem Statement

Businesses lose revenue because of failed payments, abandoned checkouts, overdue invoices, and recurring payment failures.

Traditional recovery systems may:

* Miss recovery opportunities
* Retry unnecessarily
* Treat every customer the same
* Lack decision transparency
* Continue automated retries without sufficient safety controls

REVIVE provides an intelligent but **bounded recovery process**.

---

## ✨ Key Capabilities

* **AI-powered diagnosis and decision making**
* **ML-based revenue-risk scoring**
* **Retrieval-Augmented Generation (RAG)**
* Structured JSON AI responses
* Deterministic Revenue Risk Engine
* Policy and safety controls
* Razorpay Payments
* Razorpay Payment Links
* Subscription-related event handling
* Webhook processing
* Webhook signature verification
* Webhook event-id idempotency
* Payment verification
* Human-in-the-loop review
* Recovery analytics
* Complete audit trail

---

# 🔄 System Workflow

```text
Revenue Event
     ↓
Event Ingestion
     ↓
Revenue Risk Engine
     ↓
ML Risk Score
     ↓
RAG Context Retrieval
     ↓
AI Diagnosis
     ↓
AI Decision
     ↓
Policy Engine
     ├── APPROVE → Recovery → Verification → ₹ Recovered
     ├── BLOCK   → STOP
     └── HUMAN   → Human Review
                              ↓
                         Audit Trail
```

---

# 🏗️ Architecture

```text
                         ┌──────────────┐
                         │   RAZORPAY   │
                         └──────┬───────┘
                                ↓
                     ┌─────────────────────┐
                     │  EVENT INGESTION    │
                     └──────────┬──────────┘
                                ↓
                  ┌──────────────────────────┐
                  │ REVENUE RISK ENGINE      │
                  └────────────┬─────────────┘
                               ↓
                     ┌──────────────────┐
                     │  ML RISK SCORE   │
                     └────────┬─────────┘
                              ↓
                     ┌──────────────────┐
                     │   RAG RETRIEVAL  │
                     │ Relevant Context │
                     └────────┬─────────┘
                              ↓
                ┌──────────────────────────┐
                │       AI ENGINE          │
                │ Diagnosis + Decision     │
                └────────────┬─────────────┘
                             ↓
                  ┌────────────────────┐
                  │   POLICY ENGINE    │
                  └──────┬─────┬───────┘
                         │     │
                  APPROVE│     │BLOCK
                         ↓     ↓
                  ┌─────────┐ STOP
                  │RECOVERY │
                  └────┬────┘
                       ↓
                 ┌────────────┐
                 │ VERIFICATION│
                 └──────┬─────┘
                        ↓
              ┌──────────────────┐
              │ ₹ REVENUE        │
              │ RECOVERED        │
              └────────┬─────────┘
                       ↓
                ┌────────────┐
                │ AUDIT TRAIL│
                └────────────┘

                    HUMAN
                      ↑
                 ┌────┴─────┐
                 │  REVIEW  │
                 └──────────┘
```

### Component Responsibilities

| Component               | Responsibility                                          |
| ----------------------- | ------------------------------------------------------- |
| **Event Ingestion**     | Receives revenue events and Razorpay webhooks           |
| **Revenue Risk Engine** | Identifies revenue-risk signals                         |
| **ML Risk Scoring**     | Calculates revenue-risk score                           |
| **RAG Layer**           | Retrieves relevant knowledge and contextual information |
| **AI Engine**           | Provides diagnosis and recovery recommendation          |
| **Policy Engine**       | Validates actions and enforces safety rules             |
| **Recovery Engine**     | Executes approved recovery actions                      |
| **Verification**        | Confirms successful recovery                            |
| **Human Review**        | Handles escalated cases                                 |
| **Audit Trail**         | Records decisions, actions, and outcomes                |

---

# 🤖 AI, ML & RAG Intelligence

AI and Machine Learning form the core intelligence layer of REVIVE.

## 🧠 Machine Learning — Risk Scoring

REVIVE uses **scikit-learn** to calculate a revenue-risk score for each revenue event.

The risk analysis can consider:

* Payment failure history
* Customer payment behavior
* Transaction amount
* Previous purchases
* Retry count
* Days overdue
* Time since checkout abandonment
* Failure reason

The ML model produces a **risk score** that helps prioritize revenue-loss cases.

### ML Flow

```text
Customer + Transaction Data
             ↓
      Feature Extraction
             ↓
       ML Risk Model
             ↓
        Risk Score
             ↓
       AI Decision
```

---

## 📚 RAG — Context-Aware Intelligence

REVIVE uses **Retrieval-Augmented Generation (RAG)** to provide relevant context to the AI before making a recovery recommendation.

RAG can retrieve relevant information such as:

* Recovery policies
* Retry rules
* Business-specific guidelines
* Customer context
* Previous recovery outcomes
* Scenario-specific information

Instead of relying only on the LLM's internal knowledge, the system retrieves relevant context and provides it to the AI.

### RAG Flow

```text
Revenue Event
      ↓
Query / Context Creation
      ↓
Knowledge Retrieval
      ↓
Relevant Context
      ↓
LLM
      ↓
Diagnosis + Recommendation
```

---

## 🧠 AI — Diagnosis & Decision

REVIVE uses an **LLM API** for intelligent reasoning.

### AI Diagnosis

The AI analyzes:

* Revenue event
* Customer information
* ML risk score
* Retrieved RAG context

to determine:

* Why revenue is at risk
* Likely failure cause
* Relevant context
* Recovery situation

### AI Decision

The AI recommends the most appropriate recovery action.

Possible actions include:

* `retry_payment`
* `payment_link`
* `reminder`
* `human_escalation`
* `no_action`

### Structured Output

AI responses are returned as **structured JSON**, allowing the backend to reliably consume the diagnosis and recommendation.

---

## 🔄 Combined AI + ML + RAG Pipeline

```text
                    REVENUE EVENT
                          ↓
                ┌──────────────────┐
                │   ML RISK MODEL  │
                └────────┬─────────┘
                         ↓
                    RISK SCORE
                         ↓
              ┌─────────────────────┐
              │   RAG RETRIEVAL     │
              │   Relevant Context  │
              └──────────┬──────────┘
                         ↓
              ┌─────────────────────┐
              │        LLM          │
              │ Diagnosis + Decision│
              └──────────┬──────────┘
                         ↓
                 STRUCTURED JSON
                         ↓
                ┌──────────────────┐
                │  POLICY ENGINE   │
                └────────┬─────────┘
                         ↓
              APPROVE / BLOCK / HUMAN
```

---

## 🛡️ Bounded AI Autonomy

**AI does not directly control payments.**

```text
ML
 ↓
Risk Score
 ↓
RAG
 ↓
Relevant Context
 ↓
LLM
 ↓
Diagnosis + Recommendation
 ↓
Policy Engine
 ↓
Validation
 ↓
Recovery Engine
 ↓
Razorpay
 ↓
Verification
 ↓
Recovered Revenue
```

> **REVIVE uses ML to understand risk, RAG to provide relevant context, and AI to reason about the right action — while deterministic policies remain responsible for controlling execution.**

---

# 💰 Revenue-Loss Scenarios

## 1. Failed Payment

**Example: ₹2,499**

```text
Payment Failed
      ↓
Risk Analysis
      ↓
AI Diagnosis
      ↓
Retry Payment
      ↓
Payment Successful
      ↓
₹2,499 Recovered
```

---

## 2. Checkout Abandonment

**Example: ₹5,999**

REVIVE evaluates:

* Customer history
* Cart value
* Previous purchases
* Payment history
* Time since abandonment

```text
Checkout Abandoned
        ↓
Customer + Cart Analysis
        ↓
Recovery Eligible
        ↓
Payment Link
        ↓
Payment
        ↓
Verification
```

---

## 3. Subscription Failure

**Example: ₹7,999**

```text
Subscription Charge Failed
          ↓
Failure Classification
          ↓
AI Decision
          ↓
Recovery Action
          ↓
Payment Verification
```

---

## 4. Overdue Receivable

**Example: ₹48,000**

REVIVE evaluates:

* Invoice amount
* Days overdue
* Customer history
* Previous purchases
* Payment behavior

Possible actions:

* Friendly reminder
* Payment Link
* Human escalation

---

## 5. Repeated Payment Failure

```text
Payment Failed
      ↓
Retry #1
      ↓
Failed
      ↓
Retry #2
      ↓
Failed
      ↓
RETRY LIMIT REACHED
      ↓
STOP AUTOMATION
      ↓
HUMAN REVIEW
```

**REVIVE never retries indefinitely.**

---

# 🛡️ Safety & Policy Controls

* **Retry Limits** — prevents unlimited automatic retries
* **Policy Gate** — AI recommendations require deterministic approval
* **Human Escalation** — cases beyond safe automation are sent for review
* **Webhook Idempotency** — prevents duplicate event processing
* **Signature Verification** — validates Razorpay webhook authenticity
* **Payment Verification** — recovered revenue is recorded only after confirmation

---

# 🧰 Technology Stack

| Layer                      | Technologies                                              |
| -------------------------- | --------------------------------------------------------- |
| **Backend**                | Python, FastAPI, SQLAlchemy, PostgreSQL                   |
| **AI**                     | LLM API, OpenAI API, Structured JSON                      |
| **RAG**                    | Retrieval-Augmented Generation, Knowledge Retrieval       |
| **ML**                     | scikit-learn, pandas, NumPy                               |
| **Payments**               | Razorpay Payments, Payment Links, Subscriptions, Webhooks |
| **Async / Infrastructure** | Celery, Redis, Docker, Docker Compose                     |
| **Frontend**               | React, Vite, Axios, React Router                          |
| **Visualization**          | Recharts                                                  |
| **UI**                     | Lucide React                                              |
| **Development**            | Git, GitHub                                               |

---

# 📁 Project Structure

```text
REVIVE/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── api/
│   │   ├── policy/
│   │   ├── services/
│   │   ├── webhooks/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   └── models.py
│   │
│   └── tests/
│
├── frontend/
│   └── src/
│       ├── pages/
│       └── services/
│
├── data/
├── evaluation/
├── demo/
├── architecture/
├── docker-compose.yml
├── .env.example
└── README.md
```

---

# 📊 Dashboard

REVIVE provides six major dashboard screens:

1. **Dashboard**
2. **Recovery Feed**
3. **Case Detail**
4. **Analytics**
5. **Audit Trail**
6. **Human Review**

The dashboard provides visibility into:

* Revenue at risk
* Revenue recovered
* Recovery rate
* Case status
* Risk scores
* AI decisions
* Recovery actions
* Scenario performance
* Human review
* Audit events

---

# 📸 Screenshots

Store screenshots in:

```text
docs/screenshots/
├── dashboard.png
├── recovery-feed.png
├── case-detail.png
├── analytics.png
├── audit-trail.png
└── human-review.png
```

Add them to the README:

```markdown
![Dashboard](docs/screenshots/dashboard.png)

![Recovery Feed](docs/screenshots/recovery-feed.png)

![Case Detail](docs/screenshots/case-detail.png)

![Analytics](docs/screenshots/analytics.png)

![Audit Trail](docs/screenshots/audit-trail.png)

![Human Review](docs/screenshots/human-review.png)
```

---

# 🔌 API Overview

| Method   | Endpoint                   | Purpose          |
| -------- | -------------------------- | ---------------- |
| **GET**  | `/`                        | Backend status   |
| **GET**  | `/health`                  | Health check     |
| **POST** | `/webhooks/razorpay`       | Razorpay webhook |
| **GET**  | `/api/dashboard`           | Dashboard data   |
| **GET**  | `/api/dashboard/analytics` | Analytics        |
| **GET**  | `/api/cases`               | Revenue cases    |
| **GET**  | `/api/recovery`            | Recovery actions |
| **GET**  | `/api/audit`               | Audit events     |
| **GET**  | `/api/review`              | Human review     |

---

# 💳 Razorpay Integration

REVIVE uses **Razorpay Test Mode** for payment recovery demonstrations.

Integration includes:

* Payments
* Payment Links
* Subscription-related events
* Webhooks
* Payment verification
* Webhook signature verification

> **Never commit API keys, webhook secrets, or other credentials to GitHub.**

---

# 📈 Data & Evaluation

REVIVE includes synthetic data for testing and evaluation.

```text
data/
├── customers.csv
├── transactions.csv
└── README.md
```

Evaluation:

```text
evaluation/
├── evaluate.py
└── results.json
```

The evaluation covers the revenue-recovery scenarios and system performance.

---

# ⚙️ Local Setup

## Prerequisites

* Python 3.x
* Node.js + npm
* Docker Desktop
* Git
* Razorpay Test Mode account
* LLM API key

## 1. Start Infrastructure

```powershell
docker compose up -d
```

## 2. Start Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8010
```

## 3. Start Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Application URLs

**Frontend:** `http://localhost:5173/`

**Backend:** `http://127.0.0.1:8010/`

---

# 🧪 Demo Flow

1. Open the Dashboard
2. Show revenue-at-risk metrics
3. Open Recovery Feed
4. Select a revenue case
5. Show ML Risk Score
6. Show RAG-retrieved context
7. Show AI Diagnosis
8. Show AI Decision
9. Show Policy Engine decision
10. Execute/inspect recovery
11. Show payment verification
12. Open Analytics
13. Demonstrate repeated failure
14. Show Human Review
15. Show Audit Trail

---

# 🔒 Security

* Razorpay Test Mode for development
* Secrets stored in `.env`
* `.env` excluded from Git
* Webhook signature verification
* Webhook event-id idempotency
* Bounded automatic retries
* Human escalation
* Policy-controlled AI execution

---

# 🚧 Limitations

* Test/synthetic events are used for demonstrations
* Evaluation data is synthetic
* Production deployment requires production credentials and operational controls
* AI functionality depends on LLM API availability

---

# 🔮 Future Enhancements

* Real-time event streaming
* Advanced ML models
* Customer lifetime-value scoring
* Email/SMS/WhatsApp recovery
* A/B testing
* Multi-payment-provider support
* Advanced fraud detection
* Production monitoring
* CI/CD automation

---

# 🧠 Design Principles

* **Intelligence** — combine ML risk scoring, RAG context, and LLM reasoning
* **Bounded Autonomy** — AI cannot bypass deterministic policies
* **Verification** — confirm recovery before recording revenue
* **Human Oversight** — escalate cases beyond safe automation
* **Auditability** — maintain a traceable decision history

---

# 🏁 Final Architecture Summary

```text
                         ┌────────────────┐
                         │    RAZORPAY    │
                         └───────┬────────┘
                                 ↓
                       ┌──────────────────┐
                       │ EVENT INGESTION   │
                       └────────┬─────────┘
                                ↓
                    ┌────────────────────────┐
                    │ REVENUE RISK ENGINE   │
                    └───────────┬────────────┘
                                ↓
                       ┌────────────────┐
                       │  ML RISK SCORE │
                       └───────┬────────┘
                               ↓
                       ┌────────────────┐
                       │ RAG RETRIEVAL  │
                       └───────┬────────┘
                               ↓
                  ┌──────────────────────────┐
                  │    AI DIAGNOSIS          │
                  │          +               │
                  │    AI DECISION           │
                  └────────────┬─────────────┘
                               ↓
                    ┌────────────────────┐
                    │   POLICY ENGINE    │
                    └──────┬────┬───────┘
                           │    │
              APPROVE ─────┘    └──── BLOCK
                  ↓                    ↓
           ┌─────────────┐           STOP
           │  RECOVERY   │
           └──────┬──────┘
                  ↓
           ┌─────────────┐
           │ VERIFICATION│
           └──────┬──────┘
                  ↓
          ┌──────────────────┐
          │ ₹ REVENUE        │
          │ RECOVERED         │
          └────────┬─────────┘
                   ↓
             ┌────────────┐
             │ AUDIT TRAIL│
             └────────────┘

             HUMAN ESCALATION
                    ↓
             ┌────────────┐
             │HUMAN REVIEW│
             └────────────┘
```

### Core Principle

> **REVIVE combines Machine Learning for risk scoring, RAG for relevant context, AI for diagnosis and decision-making, deterministic policies for safety, Razorpay for recovery execution, verification for correctness, and human review for bounded autonomy.**

---

# 📄 License

This project is intended as a software engineering and AI revenue-recovery demonstration project.

---

# 👤 Author

**Dhedeepya123**
