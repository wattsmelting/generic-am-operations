# Generic AM Operations — Development Operating Manual

These are **uncontrolled demonstration instructions**, not approved SOPs.

1. Launch with START_WINDOWS.bat. Browser opens the local application.
2. Use the sidebar to select a module and **? Page Help** to view module instructions.
3. Create fictional Customers and RFQs, then Work Orders. Copy numeric record IDs for related fields.
4. Create a fictional powder lot in Powder Inventory; record source and destination links in Powder Transactions. For a build, enter the numeric powder lot ID and work order ID.
5. Create a Part linked to its Build ID. Add Inspections, NCRs and Shipping records using the Part ID. Open Traceability and enter the Part ID to view relationships.
6. Add fictional Personnel, controlled-document placeholders, Training Materials and Training Records. Qualifications are not enforced automatically.
7. Open NCR for nonconformances; create CAPA linked to the NCR when needed. Formal dispositions, approval and effectiveness controls are not enforced.
8. Use Documents, Procedures, Audits, Risk Register, Change Control, Calibration, Validation, Complaints and Management Review as generic record catalogs only.
9. Reports shows counts; Audit Events lists record creation events. Neither is a compliant audit report.
10. Stop the Windows launcher to stop the local service. Database files are stored in `local_data/` and must never be published.

## AS9100 / ISO 13485 implementation roadmap
Before production deployment implement and validate: access control, qualified-personnel gates, controlled revisions, approval workflows, secure electronic signatures where applicable, audit integrity, complete lot genealogy and mass balance, retention schedules, backup/restore, complaint and regulatory reporting logic, validation evidence, supplier evaluation, contract review, FAI where applicable, device files and risk management linkage. Compliance requires organization-specific implementation and independent assessment.
