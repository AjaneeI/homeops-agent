# Architecture

```mermaid
graph TD
    A["User selects Run Good Night Check"] --> B["HomeOps Agent / Strands Agent"]
    B --> C["Tool Registry"]
    C --> D["Device State Tool"]
    C --> E["Safe Action Tool"]
    C --> F["Human Approval Tool"]
    C --> G["Audit Log Tool"]
    D --> H["Device / Simulation Layer"]
    E --> H
    F --> I["Approval Gate"]
    G --> J["Audit Trail"]
    H --> K["Dashboard"]
    I --> K
    J --> K
```

## Flow

1. The user starts Good Night Check.
2. The agent reads device state through tool calls.
3. Low-risk actions run automatically.
4. Security-sensitive or uncertain actions are paused for human review.
5. The dashboard displays state, actions, approvals, and audit history.
