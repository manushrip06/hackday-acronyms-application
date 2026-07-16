# Platform Engineering Team Wiki (v2 — re-upload demo)

Same content as v1, plus a new acronym for the re-upload demo.

## Onboarding

New hires should complete the **OKR** alignment session in their first week. Ask your manager about the current **GTM** plan for the developer portal.

## Incidents

After any Sev-1, we schedule a **PIR** within 48 hours. The on-call uses **PagerDuty** and updates the **SLO** dashboard. If customer impact is unclear, open a **WAR** (Written Assessment of Risk) before escalating to the **CISO** office.

During a live incident we prefer **BAU** operations only for non-critical changes. Never ship a **hotfix** without a linked **RFC**.

## Delivery

We track work in **Jira**. Large changes need an **RFC** and a **DesignDoc**. Feature flags go through **LaunchDarkly**. The release train is owned by the **ReleaseCaptain**.

Our **CI** pipeline runs on **GitHub Actions**. Artifacts land in the **ACR** (Azure Container Registry). Production deploys use **ArgoCD**.

## New this quarter

We introduced **NFR** reviews (Non-Functional Requirements) before every **GA**. The **ChaosMonkey** drill runs monthly against staging.

## Meetings

- Weekly **SyncUp** with product
- Monthly **QBR** with leadership
- Ad-hoc **WhiteboardSession** for architecture spikes

## Glossary hints

The **API Gateway** fronts all public traffic. **ServiceMesh** handles east-west auth. **FeatureToggle** defaults are owned by the **ProductOwner**.

If you see **TBD** in a doc, replace it before the **GA** date. **MVP** scope is locked at kickoff; stretch goals go in the **Backlog**.
