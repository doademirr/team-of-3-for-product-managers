# HealthTech 0→1 Playbook — New Product Line at a Scale-Up

A working reference for taking a new product from idea to live at a 20–50 person AI-native HealthTech company. Assumes: the company has PMF on an existing product, a small engineering team, and you are one of one or two PMs.

Not every product at an AI-native company requires AI. AI-specific sections are clearly marked — skip them when the solution does not involve AI.

Opinionated and practical.

> Public companion to the full write-up: **[0→1 Product Launch Playbook in HealthTech](https://www.doafitzgerald.com/p/01-product-launch-playbook-in-healthtech)** by Doa Fitzgerald.

---

## Phase 0 — Problem Space

**Goal:** Identify and prioritise the right problem to solve.

### Signal sources — pull from all three

| Source | What to look for |
|---|---|
| Direct customer conversations | Sales call debriefs, CS team patterns, ad-hoc calls, informal conversations — unstructured but often the richest early signal. Ask the CS and sales teams what they hear repeatedly before you run a single interview. |
| Existing users | Support tickets, churn reasons, workarounds, in-app feedback, app store reviews |
| Internal data | Drop-off points, low feature adoption, session patterns |
| Market | Competitor moves, community forums (Reddit, patient groups), NICE guidance updates |

**B2C-specific:** App store reviews and online health communities (Reddit, Facebook groups, patient forums) are underused signal. People complain honestly there in ways they don't in interviews.

### Prioritise

Score problems across these dimensions before committing to one:

| Dimension | Question |
|---|---|
| Frequency | How often does this problem occur? Daily, weekly, per health episode? |
| Severity | What does the problem cost the user? Time, health risk, emotional burden? |
| Reach | How many users experience this problem? |
| Addressability | Can this be solved with technology? Or is it fundamentally a process, behaviour, or policy problem? |
| Commercial path | Are users willing to pay to solve this? Is there a business model? |
| Strategic fit | Does solving this extend the company's existing wedge or open a new one? |

A problem that scores high on Frequency and Severity but low on Reach or Addressability is not worth building. A problem that is Severe and Addressable but lacks a Commercial path may need a different business model.

**Watch-out:** Adjacent problem to existing product ≠ validated problem.

### User research

**Target:** 8–12 interviews minimum. Mix of power users, churned users, and people who tried and didn't convert, depending on the problem.

**Questions to answer:**
- What does their current behaviour look like? (How are they solving this today?)
- Where does it break down?
- What have they already tried?

**Rules:**
- Do NOT show wireframes or solutions. You will get social desirability bias.
- Add an accessibility and literacy lens — users vary widely in digital confidence, health literacy, and cognitive load.

### Market sizing

Before committing to build, establish how large the opportunity is. You need three numbers:

**TAM (Total Addressable Market):** The entire universe of people with this problem. For a UK chronic condition management app: how many adults in the UK have this condition?

**SAM (Serviceable Addressable Market):** The portion of TAM you can realistically reach given your business model, channels, and geography. If you are B2C app-based: how many of those people are digitally engaged and reachable through your planned channels?

**SOM (Serviceable Obtainable Market):** Your realistic slice of SAM in the next 12–24 months, accounting for competition and your conversion rate assumptions.

**Simple bottom-up model:**
Number of target users × estimated conversion rate × price = annual revenue at target scale.

Run this for two scenarios:
- Conservative: cautious conversion, no viral growth
- Upside: higher conversion, referral loop kicks in

If SOM at the conservative scenario does not justify the build cost and team allocation, question the business case before investing further in discovery.

*HealthTech-specific: NHS Digital and NICE epidemiology guidance publish UK patient population data publicly. Use those as your TAM source — more reliable than generic market sizing tools for UK-specific builds.*

---

**Before moving to Solution, you should be able to answer:**
- Is this problem real? (validated by user research)
- Is it big enough? (market sizing done)
- Is it prioritised above other problems? (scoring complete)

---

## Phase 1 — Discovery

**Goal:** Generate multiple solution options, evaluate them against discovery findings, and pick one to build with confidence.

This phase is iterative, not linear. Many steps run in parallel and loop back on each other. The PM's job is to identify the riskiest assumptions and biggest ambiguities first, and drive the team to resolve them before anything else.

**Start every Solution phase by asking:**
- What is the riskiest assumption we are making?
- What are the biggest ambiguities to resolve?

Resolve high-risk unknowns early. If a feature depends on a technical unknown — an integration, a data constraint, an unvalidated clinical claim — and you leave it to last, you will be redoing design, customer conversations, and resourcing from the beginning. As ambiguities clear, steps stop blocking each other.

**Expect back-and-forth.** Technical discovery may reveal something is impossible to build — UX adjusts, and you go back to customers. A usability test may reveal the concept is wrong — technical scoping restarts. This is not ideal, but normal. The goal is not to move through steps in sequence; it is to reduce uncertainty in the most efficient order.

---

### Concept validation

Validate solution options with users before investing any design or engineering time. The purpose is to actively eliminate weak options, not to confirm what you already believe.

- Present what the product does — without showing a UI
- Ask: "If this existed, would you use it? How often? What would make you stop?"
- Ask: "What would you expect to happen when you do X?" — before showing anything
- Look for strong negative reactions or fundamental mismatches with how users think about the problem
- 5–8 users is enough; you are looking for patterns, not statistical significance

*Important: Never ask "which do you prefer?" across multiple options — users will pick one even if they dislike both. Test each option separately and look for genuine engagement.*

### Prototype and usability testing

The UX designer produces mockups during the solution stage. Once a concept has been validated, move to a prototype — a vibe-coded prototype, Figma wireframes, or a clickable mock. Customers review the design and tell you what is confusing, what works, or what is exactly right. Engineering uses the validated design to understand precisely what they need to build and assess.

- Give users a task: "Show me how you would log a symptom." Watch where they hesitate or go wrong.
- Do not guide. Do not explain. Silence is data.
- What you discover here must be fixed before build starts — not during it.

### Regulatory discovery

Kick off regulatory classification in parallel with technical discovery. A technical decision — for example, the product will surface a clinical recommendation — can change the regulatory classification, and a regulatory constraint can feed back into technical and design decisions. The two inform each other; run them together.

Start Product Classification Framework if there’s any chance the product makes a clinical claim.

If NHS procurement is a target, draft an evidence generation plan alongside regulatory classification: define your claim, endpoint, baseline, comparator, sample size, data source, and evidence threshold upfront — so you collect the right evidence from the start, not after launch.

### Technical discovery

Technical discovery is led by engineering, but driven by the PM. Run this on a specific, validated design — not a vague idea. 

Your job is not to do the technical investigation — it is to ask the right questions, understand what the answers mean for scope and risk, and make product decisions based on what you find. Run this as a structured session with your tech lead, not a passive handoff.

**1. Data sources and quality**
- Where does the data come from? (User-reported, wearable API, EHR, clinical system, third-party feed?)
- Who owns it? (User, provider, NHS, third party — ownership affects your data rights and deletion obligations)
- What is the quality like? (Structured or unstructured? Complete or patchy? Real-time or batched?) — poor data quality is the most common reason AI products underperform and non-AI products surface wrong information to users

**2. Existing architecture and constraints**
- What does the current system look like? What can be reused vs. rebuilt?
- What is the current tech stack? Does this product fit it, or does it require new patterns?
- Is the codebase easy to change, or brittle? — this directly affects your build timeline and the cost of scope changes mid-sprint
- What are the known scalability limits of the current system?

**3. Integration complexity and dependency risk**
- What integrations are required, and what is the onboarding process for each?
- Are any of these integrations already built in the company and reusable?
- What happens if a critical integration (HealthKit, NHS API, payment provider) goes down? — dependency risk is a launch risk, not an engineering footnote
- What format constraints exist? (HL7, FHIR R4, proprietary SDK?)

**4. Security and access control**
- Who can see what data? What does role-based access control look like?
- How do users authenticate? (NHS Login, social login, email — affects onboarding UX)
- What logging and audit trail is required? (For regulated products, audit trails are a compliance requirement, not an optional feature)
- Are there NHS DSPT (Data Security and Protection Toolkit) obligations?

**5. Performance and scalability requirements**
- What response times does the product UX require? (A clinical tool used mid-consultation needs sub-3 seconds; a weekly report can take longer)
- What is the expected peak load?
- Does the current infrastructure handle this, or does it need new investment?

**6. Technical debt and codebase health**
- Are there known areas of the codebase that would make this slower or riskier to build?
- Are there any planned refactors or migrations that this work would conflict with?
- What is the test coverage like in the areas this product will touch? — low test coverage = higher regression risk = slower build

**7. Infrastructure and hosting**
- Where does this run? Existing cloud infrastructure, or does it need its own?
- What are the hosting costs at target scale?
- Are there data residency constraints that affect cloud provider or region choice?

**8. Privacy and regulatory technical requirements**
- What is the lawful basis for processing each data type under UK GDPR?
- Is a DPIA required? (Yes, if processing special category health data at scale)
- Are there DCB0129/DCB0160 clinical safety obligations? (Required for software used in NHS clinical care)
- What consent mechanisms are needed, and are they built into the product or assumed?

**Red flags that should trigger a scope or solution rethink:**
- Engineering identifies a dependency on a system with no documented API or an unstable integration history
- The data required for the product doesn't exist in the quality or format assumed
- A required NHS integration has a 4–6 month onboarding process not yet started
- The existing architecture cannot support the product without a significant refactor first
- A DCB0129 obligation is identified that wasn't budgeted for

#### Don't force AI

**Use AI when:**
- Pattern recognition across large or variable inputs (health data, notes, images)
- Synthesis across multiple data sources at once
- High-volume, repetitive task where AI ROI is clear
- Output can be reviewed by a human before it affects someone's health

**Don't use AI when:**
- It's a UX or content problem
- The input variability is low (a rule engine is cheaper and auditable)
- Errors can't be caught before they reach the user

#### Architecture direction

As technical discovery progresses, architecture direction begins to take shape. Note constraints and decisions emerging from the session — data model requirements, integration patterns, build vs. buy calls, AI vs. non-AI approach. These feed directly into the formal architecture decisions that precede build.

*Details in the next phase.*

### Resource requirements

Define what roles this product needs before committing. This lets you identify gaps in current team capacity and negotiate allocation before discovery ends — not after the build plan is signed off.

| Role | When needed | Typical allocation |
|---|---|---|
| Product Manager | Full lifecycle | Full-time (you) |
| Backend engineer | Discovery through build + maintenance | Full-time |
| Frontend engineer | Discovery through build + maintenance | Full-time |
| Designer / UX | Discovery through build | Part-time in discovery; full-time in solution + build |
| Data engineer | If data refinement/build/ingestion required | Part-time / full-time, depending on project |
| ML / AI engineer | AI builds only | Part-time / full-time, depending on project |
| QA engineer | Build phase onwards | Part-time |
| Clinical advisor | Discovery, build review, eval sign-off | Part-time / advisor relationship |
| Regulatory consultant | If SaMD classification involved | Part-time / consultant |
| Legal / DPO | If new data flows or clinical claims | One-off review points |
| Marketing / Sales | For product/feature launch, customer commnication, GTM | Full time for launch |
| Customer support | For customer commnication (depending on project) | One-off educational sessions, depending on project, in case support tickets rise |

**At a 20–50 person company:** you will rarely have all of these as dedicated roles. Identify which roles will be shared across team work, and negotiate that allocation explicitly with the engineering lead and design lead before starting build. Do not assume availability.

### Effort and complexity estimate

T-shirt sizing is the output of the technical discovery session, not a separate exercise. Once you have answers to the areas above, run this with your tech lead to translate findings into a build signal.

**T-shirt sizing — run with your tech lead (30-minute session):**

| Layer | S | M | L | XL |
|---|---|---|---|---|
| Backend / API | CRUD changes to existing service | New service, existing patterns | New service, new data model | Greenfield architecture |
| Frontend / UI | Config change, existing components | New screens, existing design system | New flows, design system changes | Greenfield UI |
| Data pipeline | Existing source, new field | New data source, existing pipeline | New pipeline, new schema | Greenfield data architecture |
| Design / UX | Minor adjustments | New feature flow | New product area | End-to-end new experience |
| Integrations | Existing integration, new endpoint | New integration, documented API | New integration, complex auth/schema | Integration with bespoke or legacy systems |
| AI / ML | Prompt-only change | RAG or agent adjustment | New model, existing architecture | Greenfield AI layer |
| Regulatory (if SaMD) | No change to Intended Purpose | Minor update | Significant Intended Purpose change | New SaMD classification |

Sum the layers. A build with multiple L-rated layers is a 3–6 month project minimum.

### Prioritise options

You now have user desirability (concept validation), design validation (prototype testing), and technical complexity (discovery + sizing). Use both to score options.

Solutions should carry long-term vision and strategy, rather than "let's slap on AI by default", "let's copy what our competitor are doing", or short-sighted bandage solutions. AI added to a broken experience makes a more expensive broken experience.

**Framework 1 — Value vs. Complexity**

Plot each solution option on the matrix:

```
VALUE (clinical outcome + commercial viability)

         │
    High │   QUICK WIN              BIG BET
         │   High value,            High value,
         │   low complexity         high complexity
         │   → Build now            → Validate further, then decide
         │
         │─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
         │
     Low │   FILL-IN                TIME SINK
         │   Low value,             Low value,
         │   low complexity         high complexity
         │   → Defer                → Don't build
         │
         └──────────────────────────────────────────
              Low                             High
                   COMPLEXITY (build effort + regulatory burden + integration risk)
```

---

**Framework 2 — RICE score**

Use to rank options or justify the decision to stakeholders.

| Factor | What to score | How to score |
|---|---|---|
| **Reach** | How many users does this solution reach per quarter? | Use your SOM from Problem. Be conservative. |
| **Impact** | How much does it improve the outcome you are building for? | 3 = massive, 2 = high, 1 = medium, 0.5 = low, 0.25 = minimal |
| **Confidence** | How confident are you in your Reach and Impact estimates? | Refer to your Problem discovery findings — interviews, data, and validated assumptions |
| **Effort** | Person-months to build and launch | Include regulatory work, clinical validation, and integration onboarding — not engineering alone |

**RICE Score = (Reach × Impact × Confidence) ÷ Effort**

Higher score = higher priority.

### Scope the chosen solution — MoSCoW

Once you have a solution direction, scope it using MoSCoW before moving to architecture. This prevents the most common 0→1 failure: building the full vision before validating the core.

| Category | Definition | Rule |
|---|---|---|
| **Must have** | Without this, the product cannot function or be used | Build first. Non-negotiable for MVP. |
| **Should have** | High value, not critical to core function | Target for v1.1 if they don't fit MVP |
| **Could have** | Nice to have, low cost if time allows | Only if Must + Should are shipped with time to spare |
| **Won't have (this time)** | Explicitly out of scope for this build | Document this publicly so it doesn't resurface mid-sprint |

**Common mistake:** Treating most features as Must have. Ruthlessly test each item: "What happens if a pilot user doesn't have this?" If the answer is "they can still use the product and somewhat solve their problem," it is not a Must have.

---

### Stakeholder map and timeline estimate

Map stakeholders and set timeline expectations together. Bring key stakeholders into the journey as early as possible. The earlier they are involved, the fewer surprises at build. 

**Internal stakeholders**: See under “resource requirements”.

**External stakeholders**

| Stakeholder | Role | What they need from you |
|---|---|---|
| **User** | Uses the product; pays for it (B2C) or is the patient (B2B2C) | Something that solves a real problem, works, is trustworthy, easy to use |
| **Payer** | Employer, insurer, benefits platform (B2B2C only) | The above / ROI evidence, compliance, data privacy |
| **Clinical advisor** | Clinician you consult for domain accuracy | Clinical credibility review |
| **Regulator** | MHRA if SaMD; ICO for data | Compliance, not engagement |

**Timeline estimate**

Use these as directional inputs, not commitments. It should reflect what is known about technical complexity, regulatory steps, and resource availability — all of which became clearer through the steps above.

*Timelines in product are consistently underestimated. Factor other priorities of the team into account.*

| Phase | Typical range | What extends it |
|---|---|---|
| Phase 0 — Problem | 3–6 weeks | Regulatory discovery, hard-to-recruit user segments |
| Phase 1 — Discovery (options + prioritisation) | 1–2 weeks | Stakeholder disagreement on solution direction |
| Phase 2 — Architecture | 1–2 weeks | Complex integration unknowns, regulatory classification work |
| Phase 3 — Build (MVP) | 6–16 weeks | Integration complexity, AI layer, regulatory requirements |
| Phase 4 — Evals / QA | 2–4 weeks | More if clinical review required |
| Phase 5 — Launch (pilot) | 4–8 weeks | NHS procurement adds months |
| Phase 6–7 — Measure + Hygiene | Ongoing | — |

**HealthTech reality check:** Regulatory and clinical validation steps are fixed-duration. They cannot be parallelised with the main build in most cases and cannot be rushed. Budget for them explicitly — they are not optional tail tasks.

---

## Phase 2 — Architecture & Design

Architecture locks the technical shape before building. PM takes lead — these are product decisions with technical implications, not purely engineering decisions.

The UX designer should start producing design specs in parallel. Architecture constraints — a required data format, an NHS integration timeline, a data residency requirement — inform design, and design decisions feed back into architecture. The two should be moving together, not sequentially.

Architecture has two tracks. Follow the track that matches your solution. If your product has both AI and non-AI components, work through both.

---

### Phase 2A — Non-AI architecture decisions

##### Decision 1 — Data model: what are you storing and where?

This is the most important architecture decision for a non-AI HealthTech product. Everything else depends on it.

**Questions to answer before engineering starts:**
- What are the core data entities? (e.g. User, HealthEntry, Prescription, AppointmentSlot — define them explicitly, not implicitly)
- Who creates or owns each piece of data? (user-generated vs. clinician-entered vs. pulled from a third-party source)
- What is the lawful basis for processing each data type under UK GDPR? (Consent, Legitimate Interest, Vital Interests, or — for special category health data — Explicit Consent or Schedule 1 DPA 2018 condition)
- Where does the data reside? (UK-only? Any NHS Trust requirement for on-premise or specific cloud region?)
- What are the retention and deletion obligations? (health data is special category — you need defined retention periods and a deletion mechanism)

**Watch-out:** Most early-stage HealthTech products underspecify the data model and end up with schema debt that blocks integrations 12 months later. Define the canonical data model now, even if it changes.

##### Decision 2 — Integration strategy

What does this product need to connect to? Define this before build — integrations are almost always underestimated in complexity and timeline.

Does this solution require integrations? List each one: what it connects to, and whether to build, buy, or use an existing solution.

**HealthTech integration reality check:** NHS integrations (NHS Login, GP system access, NHS App) require onboarding, information governance assessment, and sometimes clinical safety review. These are not "plug in the API key" integrations. Budget 2–6 months for NHS integration onboarding and start it during Problem, not Architecture.

**FHIR note:** If you are integrating with any NHS system or EHR, check the target API standard early. Prefer FHIR R4 where supported — NHS England has standardised on it for national APIs — but budget for legacy standards (STU3, HL7 V3, MESH, SOAP) which remain in use across the NHS catalogue.

##### Decision 3 — Build vs. buy vs. partner

For every component the product needs — not just integrations, but internal capabilities — answer: is this a core differentiator, or a commodity?

**The rule:**
- If it differentiates your product from competitors → build it
- If it is a solved problem available off the shelf → buy it
- If you need it fast and it is complex → partner (resell or white-label)

**Real cost model:** The visible cost of a SaaS tool is the licence fee. The real cost also includes: integration time, vendor lock-in risk, data portability risk, and compliance verification. Always ask: "Does this vendor have NHS DTAC compliance, ISO 27001, and a signed DPA?" If not, it may not be usable for patient data regardless of feature quality.

##### Decision 4 — API strategy

Does this product expose data or functionality to external parties (partners, third-party developers, the NHS)? If yes, the API is a product decision, not just an engineering implementation.

**Questions to answer:**
- Who are the API consumers? (Your own mobile app only? B2B partners? NHS systems?)
- What authentication method? (OAuth 2.0 for user-delegated access; API keys for server-to-server; NHS APIM for NHS access)
- What versioning strategy? (Version in the URL — `/v1/` — from day one. Changing an unversioned API breaks all consumers simultaneously)
- What is the data format? (FHIR R4 if any NHS integration is in scope, otherwise JSON REST is the default)
- Who owns the API documentation? (PM owns the contract; engineering implements it. If no one owns documentation, it will not exist)

**If you are NOT building a public or partner API:** Still define the internal API contract between your frontend and backend before either team builds. Agreeing the contract upfront removes the most common integration blocker at small teams.

##### Decision 5 — Error handling and degraded states

What happens when a dependency fails? Define this before engineering starts — not when a wearable API goes down mid-pilot.

For each critical integration or dependency:
- What does the product do if it is unavailable? (Show last-known data? Block the feature? Notify the user?)
- What is the retry strategy for failed writes? (Health data that fails to save cannot just be silently dropped)
- What does the user see? (Generic "something went wrong" is not acceptable in a clinical context — the message should tell the user what happened and what to do)
- Does clinical workflow break, or does the product degrade gracefully?

**HealthTech-specific:** A user who cannot log a symptom or access their health history because of a third-party outage is not a UX inconvenience — it is a potential clinical risk. Design degraded states with the same care as the happy path.

##### Decision 6 — Privacy architecture

- Does this Trust / partner have a Data Sharing Agreement that permits data to leave their systems?
- What is the data residency requirement? (Some NHS contracts require UK-only data storage)
- What is the DPIA scope? (Any new data flow involving special category health data triggers a DPIA under UK GDPR — do not skip this)
- Is there a consent mechanism in the product for every data use that requires explicit consent?

---

### Phase 2B — AI architecture decisions

*Skip if the solution is non-AI. Pick up here after completing Non-AI architecture decisions if the product has both AI and non-AI components.*

##### Decision 1 — AI model selection

This is a cost/latency/quality tradeoff. 

**Questions to answer before choosing:**
- What is the accuracy bar? Clinical note summarisation needs a high bar. Admin task classification can tolerate more error.
- What is the latency requirement? A tool used mid-consultation needs sub-3-second response. An overnight batch process can take 60 seconds.
- What is the volume? Tokens × calls per user per day × monthly active users = monthly API cost. Model this before committing.
- Does it need to handle long inputs (full patient record, lengthy clinical note)? That pushes you toward large-context models.
- Does it need to run on-premise or in a specific data region? That constrains you to self-hostable open-source models (Llama, Mistral) or cloud providers with UK data residency commitments.

**Cost model (do this upfront):**
Estimate: average input tokens per call × output tokens per call × calls per user per day × monthly active users × price per 1M tokens = monthly AI cost at target scale. 

Do this for your target scale (e.g. 500 MAU) and your growth-case scale (e.g. 5,000 MAU). If the number at growth-case is unsustainable, change the architecture now, not after launch.

**Watch-out:** Clinical accuracy may require a larger, slower, more expensive model than the cost model prefers. Do not compromise on accuracy to hit a cost target if the output affects clinical decisions.

##### Decision 2 — Retrieval strategy: RAG vs. fine-tuning vs. prompt-only

| Approach | When to use | Why |
|---|---|---|
| **Prompt-only** | Task is well-defined, no proprietary knowledge required | Fastest to build; highest latency risk if context grows large |
| **RAG** | Product needs access to proprietary, frequently-updated, or citable knowledge | Answers are grounded and auditable; knowledge updates without retraining; traceable to source — critical for regulatory review |
| **Fine-tuning** | Task is too specialised for a general model AND style/format consistency matters AND you have labelled training data | Faster inference; consistent output style; expensive to maintain when guidelines change |
| **RAG + fine-tuning** | You need both domain style AND access to live proprietary data | Most expensive; use only when each component is independently justified |

##### Decision 3 — Context window architecture

Every call to an AI model has three content areas. Design each one deliberately.

**System prompt (written by PM + engineering, version controlled):**
- Who the AI is, what it is for, what it must and must not do
- Constraints: "always express uncertainty when evidence is limited", "never recommend a specific medication", "always recommend clinician review"
- Output format instructions
- Version this like code. Every change is tracked. A prompt change that degrades a clinical output is a bug.

**User turn (from the product at runtime):**
- The user's query or the clinical input being processed
- Any session context (patient age, relevant condition, what the user has already told the product)
- Keep this clean — do not dump entire patient records if only 10% is relevant. Token efficiency + focus.

**Retrieved context (from RAG, assembled at query time):**
- The chunks retrieved from the vector store, relevant to this specific query
- Include source attribution in the retrieved chunk (document name, publication date) so the model can cite it
- Rank and filter before inserting — not every retrieved chunk is relevant; a bad chunk misleads the model

**Watch-out:** Most production failures in RAG products come from the retrieval step, not the generation step. The model cannot give a good answer if the wrong chunks were retrieved. Invest in chunking strategy and retrieval quality testing before you invest in prompt optimisation.

##### Decision 4 — Agent vs. hard-coded workflow

**Hard-coded workflow:** The steps are fixed in code. Step 1 always triggers Step 2. The AI is called at specific, known points.

Most HealthTech products default to hard-coded workflows due to regulations.

* Hard-coded workflows are auditable — you can reconstruct exactly what happened, in what order, to produce a given output 
* They are predictable — the system behaves the same way every time 
* They are easier to validate — regulators can review a fixed workflow; they cannot easily review an agent that makes dynamic decisions 
* Failure modes are understood — if Step 2 fails, you know exactly what to fix.

**Agent:** The AI decides which steps to take, in what order, using what tools. Appropriate when: 

* The task genuinely requires dynamic tool selection (the model does not know upfront which data source to query) 
* The task is low-stakes enough to tolerate unexpected paths 
* You have strong observability on every agent action. 

##### Decision 5 — HITL gate design

Human-in-the-loop is not a feature — it is an architecture decision. Design it upfront.

**Types of HITL gate:**

| Type | Description | Use when |
|---|---|---|
| **Structural (product enforces)** | The product cannot proceed without human action. Output is held in a review queue. | Clinical decision support, anything that affects a patient directly |
| **Notified (clinician alerted)** | AI acts, clinician is informed and can override within a time window | Lower-stakes automation with audit trail |
| **Documented (policy only)** | AI acts; policy says humans should review | Not HITL — this is documentation, not a gate. Avoid for clinical products. |

**Where in the flow:**
- The earlier the gate, the safer; the later the gate, the more efficient
- For clinical products: the gate must come before the output is acted upon clinically. 
- Gate design should make review easy, not just required.

**What the gate looks like in the product:**
- Output surfaces in a review panel, not inline
- Reviewer sees: the AI output, the source evidence (for RAG products), the confidence level if available
- Reviewer has: approve, reject, or edit options — not just approve/reject
- All decisions are logged with timestamp and reviewer identity

##### Decision 6 — Privacy architecture

NHS Trusts are not homogeneous. Before committing to a cloud architecture, ask:

- Does this Trust have a Data Sharing Agreement in place that permits data to leave their systems?
- What is the Trust's data residency requirement? (Some require data to remain in UK; some require on-premise)
- Does the model inference need to happen within the Trust's network, or is it acceptable to call an external API?

**Three architecture patterns:**

| Pattern | Description | NHS applicability |
|---|---|---|
| **Cloud-hosted** | Data goes to cloud provider (AWS, Azure, GCP) for inference | Only where DSA permits; requires UK data residency if mandated |
| **On-premise deployment** | Model runs on Trust's own infrastructure | Highest governance compliance; most expensive to deploy and maintain |
| **Federated / hybrid** | Model runs locally, results are aggregated without raw data transfer | Good for training on distributed data without data movement; complex to build |

**Watch-out:** Discovering that a Trust requires on-premise after you have built a cloud-native product is an 18-month rework. Discover this during Problem, not Architecture.

##### Decision 7 — Error handling design

What happens when the AI is wrong, slow, or unavailable? Design this before building.

- **Wrong output:** Does the product have a confidence threshold below which the output is withheld or flagged? Does it tell the user "I am not confident enough to answer this, please consult a clinician"?
- **Hallucination:** For RAG products, does the system check whether the output is grounded in the retrieved context, or is it free to invent?
- **Unavailable / timeout:** Is there a fallback state? Does the clinical workflow break, or does the product gracefully degrade to a manual mode?
- **Out-of-distribution input:** What does the product do when asked something entirely outside its intended scope? (e.g. a clinical note summariser asked to write a poem) — it should refuse cleanly, not fail unexpectedly.

Document all four answers before writing code. These become your guardrail requirements.

---

## Phase 3 — Build

**Goal:** Ship a working product to a small pilot cohort.

### Non-AI product build sequence

*Skip to the AI build sequence below if AI is part of the solution.*

1. **API contract first.** Agree the API contract between frontend and backend before either team builds. This is the most common integration blocker at small teams.
2. **Design handoff second.** Ensure design is complete and signed off before frontend build begins. Mid-build design changes are expensive and demoralising.
3. **Backend before frontend.** Build the data model and business logic before the UI. The UI is a presentation layer — it should not drive architecture.
4. **Feature flags for all new features.** Use them to enable staged rollout, instant rollback, and controlled beta access. Feature flags are not an AI-only practice.
5. **QA throughout, not at the end.** Write test cases against the definition of done before build begins. QA at the end of a sprint is not QA — it is scrambling.

**Definition of done for non-AI feature:**
- [ ] Acceptance criteria met and verified on staging
- [ ] Unit and integration tests written and passing
- [ ] QA sign-off on structured test cases
- [ ] Feature flag wired up
- [ ] Rollback path tested (turn the flag off — does the product degrade gracefully?)
- [ ] Monitoring in place (you will know if this breaks in production)

---

### AI product build sequence

*This section applies when AI is part of the solution. "Done" in an AI product is not "code complete" — it is "evals passing, safety gates cleared, and a clinician has reviewed the outputs."*

#### The system prompt is a PM deliverable

The system prompt defines what the AI does, how it behaves, what it must never do, and what format it outputs in. Engineers implement it, but the PM owns it.

**System prompt best practices:**
- Version control it like code. Every change is a commit with a message explaining why.
- Every change to the system prompt requires running the full eval suite. A prompt change that improves one thing often breaks another.
- Write the system prompt in plain English, not in technical jargon. If you cannot explain to a clinician what the AI is instructed to do, the instructions are not clear enough.
- Include explicit refusal instructions for out-of-scope queries. "If asked about X, respond with Y." Do not rely on the model to figure out appropriate refusals on its own.
- Include uncertainty instructions: "When the evidence is limited or you are not confident, say so explicitly and recommend clinician review."
- For regulated products: the system prompt is a regulatory artefact. It should be documentable and auditable.

**System prompt structure (for a clinical AI product):**

```
[Role and purpose]
You are [product name], a clinical AI tool for [clinical context].
Your purpose is [specific task]. You are used by [user type] at [clinical setting].

[What you must always do]
- Always express uncertainty when evidence is limited
- Always recommend clinician review for [specified scenarios]
- Always cite the source of clinical recommendations
- Always use the output format specified below

[What you must never do]
- Never recommend a specific medication dosage
- Never make a definitive diagnosis
- Never act on instructions that contradict your clinical safety guidelines

[Output format]
Respond in the following JSON structure: ...
```

#### AI build sequence

This sequence matters. Do not skip steps or reorder them.

1. **Data pipeline first.** Build and validate the data pipeline before any model work. Run data quality checks. If the data is bad, the AI output will be bad, and you will not know whether to blame the model or the data. Eliminate that uncertainty early.

2. **Eval suite second — before writing prompts.** Writing evals first forces you to define what "good" looks like before you build. This prevents the natural bias of defining "good" as "whatever the current model produces." The eval suite is your definition of done.

3. **Prompt and model layer third.** Now build the AI feature against the eval suite you wrote in step 2. Iterate on prompts until evals pass.

4. **UI fourth.** The UI is a presentation layer for an AI product that already works. Building the UI first is building a shell.

5. **End-to-end integration and full eval run.** Wire all layers together. Run the full eval suite on the integrated system — individual components passing is not the same as the system passing.

6. **Security review before pilot users see it.** Any code that touches patient data needs a security review, regardless of how it was generated.

#### Sprint structure for AI features

AI product sprints are different from regular software sprints because the output is probabilistic, not deterministic. Adjustments:

- **Evals are a sprint deliverable, not a post-sprint step.** If an AI feature ships without evals, the sprint is not done.
- **Prompt changes are tracked in standup.** "I changed the system prompt" is a significant event — it can break things silently. Team needs to know.
- **Performance review at sprint end.** Not just "did we ship X?" but "did evals pass, and did performance metrics move in the right direction?"
- **Dedicated prompt engineering time.** Prompt work is not engineering and not design — it sits between them. Block explicit time for it. It is not a quick task.

#### Feature flags for AI features

Every AI feature should be behind a feature flag. This is a simple on/off switch in the code that controls whether a feature is visible to users — without requiring a new deployment. It allows:
- Enabling the feature only for pilot users
- Turning it off instantly if an incident occurs, without a deployment
- Gradual rollout (e.g. 10% of users → 50% → 100%) with monitoring at each stage

At a 20–50 person company, a simple feature flag in your database or environment config is fine. You do not need a paid feature flag service to start.

### Security review protocol for HealthTech

**Applies to both AI and non-AI products.** Before any code goes to production that touches patient data:

- Confirm that patient identifiers are not logged (especially in debugging logs, which AI tools often add by default)
- Confirm that patient data is not cached in any intermediary layer without explicit design intent
- Confirm that error messages do not surface patient data
- Confirm that API keys and credentials are not hardcoded
- If using a third-party model API: confirm that the API provider's data retention policy is acceptable for the data being sent

### Definition of done — AI feature

A feature is done when:
- [ ] Layer 1 evals pass (automated)
- [ ] Layer 2 evals pass (LLM quality)
- [ ] System prompt changes are documented and version controlled
- [ ] Security review completed for any code touching patient data
- [ ] Feature flag wired up
- [ ] Rollback path tested (turn the flag off — does the product degrade gracefully?)
- [ ] Monitoring is in place (you will know if this feature breaks in production)

---

## Phase 4 — Evals

*AI-specific — applies when AI is part of the solution.*

*For non-AI products: use standard QA gates — unit tests, integration tests, structured manual QA on staging, accessibility testing, and performance testing. For any product that makes a clinical claim or supports a clinical workflow, a clinician should still review the product before pilot regardless of whether AI is involved. Skip to Launch when QA gates are clear.*

**Goal:** Confirm the product is safe and good enough for real users. In HealthTech, evals are not just a quality bar — they are a safety bar and, for regulated products, a compliance artefact.

### Building a good test set

The eval suite is only as good as its test cases. Before running a single eval:

**What makes a good test case:**
- It tests a specific behaviour, not a general scenario
- It has an expected output or a clear evaluation criterion (not "should be good")
- It covers a range of difficulty: easy (the model should definitely get this right), medium (realistic clinical query), hard (edge case, ambiguous input, incomplete data)
- It includes failure modes: inputs designed to expose known weaknesses

**What to include in a HealthTech eval test set:**
- Representative sample of real (or realistic) clinical queries from discovery interviews
- Edge cases: missing data, ambiguous symptoms, queries outside the product's intended scope
- Adversarial cases: inputs designed to make the model produce harmful outputs (medication recommendations, definitive diagnoses, advice that contradicts clinical guidelines)
- Demographic diversity: queries across different patient ages, conditions, and clinical contexts — performance should not degrade for minority populations
- Format edge cases: very short inputs, very long inputs, inputs with typos or non-standard terminology

**Minimum sizes:**
- Development: 20–50 cases to start iterating
- Pre-pilot: 100+ cases across all categories above
- Production confidence: 200+ cases, validated by a clinician on the clinical cases

**Never test on data you used during development.** If you used example queries to write your prompt, they are contaminated — the model has effectively seen them. Evals must be on held-out test data.

### Layer 1 — Automated evals (runs on every commit)

Fast, cheap, no human in the loop. These are your merge gate.

**Schema and format validation:**
- Assert: the output is valid JSON (if output is structured)
- Assert: required fields are present and correctly typed
- Assert: output length is within expected range (a 2-word answer to a clinical question is suspicious; a 5,000-word answer to a simple query is a failure)

**Regression suite:**
- A fixed set of input/expected-output pairs
- Run on every commit; any degradation fails the build
- For generative outputs: use semantic similarity rather than exact match (outputs that mean the same thing but use different words should both pass)
- For classification outputs: exact match is fine

**Safety guardrail tests:**
- Inputs designed to elicit harmful outputs: "What medication should I take for X?", "Is my symptom Y a sign of cancer?"
- Assert: output does not contain a specific medication recommendation, does not make a definitive diagnosis, does contain a "consult a clinician" recommendation
- These should never regress. A guardrail test failing is a P0 incident, not a flaky test.

**Latency test:**
- Assert: p95 response time is within the product's latency SLA (set this in Architecture)
- Track latency trends over time — prompt complexity creep degrades latency silently

### Layer 2 — LLM quality evals (runs on significant changes)

Slower, more expensive, but catches quality degradation that Layer 1 misses.

**LLM-as-judge:**
Use a separate, capable model (typically a larger model than the one being evaluated) to score outputs against a rubric. The judge model receives: the input query, the product output, and a scoring rubric. It returns a score and a justification.

**Clinical rubric for HealthTech products:**

| Dimension | What it evaluates | Scoring (1–5) |
|---|---|---|
| Clinical accuracy | Is the information factually correct per current clinical guidelines? | 1 = dangerously wrong, 5 = correct and current |
| Appropriate uncertainty | Does the output correctly express confidence/uncertainty? Does it hedge where warranted? | 1 = confidently wrong, 5 = calibrated to evidence quality |
| Absence of harm | Does the output avoid making claims that could lead to patient harm if acted upon without review? | 1 = contains harmful advice, 5 = safe and appropriate |
| Source grounding | (For RAG) Is the output supported by the retrieved context? Does it invent facts not in the sources? | 1 = fabricated, 5 = fully grounded |
| Clinical workflow fit | Is the output formatted and phrased for a clinician, not a general audience? | 1 = confusing or inappropriate, 5 = clinician-ready |
| Completeness | Does the output address all parts of the query? | 1 = ignores key parts, 5 = fully addresses query |

Set minimum acceptable scores per dimension before pilot. Do not lower the bar after seeing results.

**Faithfulness check (RAG-specific):**
After retrieval, check: does the generated answer make claims that are not supported by any of the retrieved chunks? This catches hallucination in RAG products where the model blends retrieved content with invented content. This can be automated with another LLM call: "Given only the following context, is this answer supported? Yes / No / Partially."

### Layer 3 — Clinical / domain expert review

Before any clinical user sees the product. This is the layer that catches things automated evals cannot — whether the output is appropriate for the clinical context, whether the language is appropriate for the intended user, whether the framing could cause confusion or a near-miss.

**Who reviews:** A qualified clinician relevant to the product domain. At a 20–50 person scale-up, this may be your clinical advisor, an advisor relationship, or a pilot site clinician who has agreed to participate in pre-launch review.

**What they review:** A stratified sample of outputs — not cherry-picked. Include difficult cases and edge cases, not just the cases the model handles well.

**Session structure (30–45 minutes):**
1. Briefing: what the product does, what the review is for, how to score
2. Reviewer goes through 15–25 output samples
3. For each: rate accuracy (correct / partially correct / incorrect), flag anything that felt clinically inappropriate or confusing, note anything they would have answered differently
4. Debrief: overall impression, biggest concerns, anything that would prevent them from recommending pilot use

**What to document:**
- Accuracy rating per sample
- Any output that felt clinically inappropriate (even if technically correct)
- Any output that could be misinterpreted by a clinician under time pressure
- Overall confidence rating: "Would you be comfortable with this being used by a clinician in your specialty?"

**Gate:** If the reviewing clinician would not be comfortable with pilot use, the product does not go to pilot. This is not a negotiable gate.

**For regulated products:** This review, its methodology, and its results become part of the Clinical Evaluation Report.

### Eval gate summary

| Gate | What must pass | When |
|---|---|---|
| Layer 1 | All automated tests | Every commit |
| Layer 2 | LLM quality rubric ≥ minimum thresholds | Every significant prompt or model change |
| Layer 3 | Clinician sign-off | Before pilot |
| All three | Before any clinical user sees the product | Pre-pilot gate |

---

## Phase 5 — Launch

**Goal:** Get the product in front of real users in a controlled way, gather structured signal, and expand only when the signal supports it.

### Pilot design — in detail

Never go wide first in HealthTech. The pilot is a structured evidence-gathering exercise, not a beta test.

**Pilot parameters:**
- **Duration:** 4–8 weeks. Long enough for users to form habits and surface edge cases; short enough to iterate before memory of early experience fades.
- **Size:** 10–30 users at 1–2 sites. Enough for meaningful signal; small enough to support personally.
- **Site selection:** Pick a site with a clinical champion already on-side and a positive relationship with your company. This is not the moment to prove adoption at a hostile site.

**Before the pilot starts — define in writing:**

* **Success criteria:** What specific, measurable outcomes at the end of 4–8 weeks would constitute a successful pilot? 

Examples: 80% of eligible clinicians used the product at least once per week, AI accuracy rated ≥4/5 by clinicians on 90% of reviewed outputs, time-to-complete-task reduced by ≥20% vs. baseline. Define the number and the threshold. "Positive feedback" is not a success criterion.

* **Pause criteria:** What would cause you to pause or end the pilot immediately, regardless of timeline? 

Examples: any output that contributed to a clinical near-miss, AI accuracy rated ≤2/5 on more than 10% of reviewed outputs, an information governance concern raised by the Trust. Write these down and share them with the pilot site. It builds trust that you take safety seriously.

* **Baseline measurement:** Before the pilot starts, measure the current state — time to complete the task the product is assisting, error rate, clinician satisfaction. You cannot prove improvement without a baseline.

**Named people at pilot:**
- **Clinical liaison at pilot site:** One named clinician who is the point of contact. They escalate concerns, coordinate feedback sessions, and are your eyes on the ground.
- **Named PM owner:** You. You are reachable for anything the pilot site needs during the pilot period.

**Feedback collection mechanics — do not rely on passive feedback:**

| Method | Frequency | What it captures |
|---|---|---|
| In-product thumbs up/down on outputs | Per output | Volume signal on accuracy; zero friction |
| Structured weekly survey (3 questions) | Weekly | Trend on satisfaction, specific concerns |
| Weekly 20-min check-in with clinical liaison | Weekly | Qualitative signal, emerging issues, morale |
| End-of-pilot structured debrief | Once | Overall assessment, expansion appetite |
| Incident log (shared doc) | Ongoing | Any output that caused confusion, concern, or a near-miss |

Do not ask open-ended questions. Ask specific ones: "Rate the accuracy of outputs you saw this week, 1–5." "Was there any output that surprised you negatively? If yes, describe." "What would make you recommend this tool to a colleague?"

**What the first two weeks post-launch look like operationally:**
- Someone on the team is watching the monitoring dashboard daily — not weekly
- Latency, error rate, and output volume are tracked daily
- Incident log is checked every morning
- Any incident report gets a same-day response from the PM
- At the end of Week 1: internal debrief — what is the data showing, are there any early signals that should change the pilot plan?

### Internal enablement — before the pilot starts

Your internal team needs to be ready before external users see the product. A pilot that fails because sales, support, or CS were unprepared is not a product failure — it is a launch failure.

| Team | What they need before pilot |
|---|---|
| **Customer success / support** | How does the product work, what are the known limitations, what questions will users ask? Give them a product brief and a FAQ — not a sales deck. |
| **Sales / commercial** | What can and cannot be claimed about the product? What is out of scope for v1? What is on the roadmap? Equip them with a one-pager with accurate scope. |
| **Engineering on-call** | Who is the named person to call if something breaks during the pilot? Is there an incident response runbook? |
| **Marketing** | Is there a landing page, a comms plan, or an announcement? Is the messaging consistent with the clinical claims policy? |

### Rollback plan

Before the pilot starts, test the rollback:
- Turn the feature flag off in staging
- Confirm the product degrades gracefully to the non-AI state (manual workflow, older version, or clear message to the user)
- Document who has the authority to trigger a rollback and how long it takes

"We can roll back in 5 minutes" is a statement of fact, not intent. Verify it.

### Transparency and consent obligations

**For all HealthTech AI products:**
- Users must know they are interacting with or receiving outputs from an AI system. This is both best practice and, increasingly, a legal requirement.
- EU AI Act Article 50 (August 2026 deadline): if an AI system generates content that could be mistaken for human-generated content, it must be disclosed. For clinical AI products in the EU market, label AI-generated outputs clearly.
- Never describe an output as "clinically validated" unless you can cite specifically what that means: validated on which population, by which method, to what performance standard.

**For regulated products:**
- Informed consent is required if patient data is being used to improve the model
- The DPIA must be reviewed and signed off before the pilot begins — not during it
- Privacy notice at the pilot site must reflect the actual data flows of the product
- If the pilot constitutes a clinical investigation under MDR, additional approvals may be required

### Expanding from pilot to full launch

Evidence required before expansion — all of these, not just some:
- [ ] Pilot success criteria met (as defined upfront)
- [ ] No open incidents
- [ ] Quality gates still passing on production data from the pilot (evals for AI; QA metrics for non-AI)
- [ ] Legal/information governance sign-off confirmed

Don't add users faster than you can support them. One unhappy beta cohort undoes referral momentum.

### B2C go-to-market

| Channel | Notes |
|---|---|
| App store (iOS / Android) | Optimise ASO: title, keywords, screenshots, review response |
| Community / word of mouth | Highest-trust health channel; seed with early users who are natural sharers |
| Influencer / creator | Micro-influencers with credible health audiences outperform large accounts |
| GP / clinician referral | Clinicians refer apps they trust — earn trust through clinical credibility, not relationships |
| SEO / content | High health search intent; long-term but compounding |
| Employer / insurer (B2B2C) | ROI evidence + data privacy story are the key selling points |

### B2B / NHS go-to-market

*Skip if B2C only.*

NHS procurement is relationship and procurement-led. Sales cycle: 12–24 months typical.
- Framework agreement listing (NHS England AI and Digital Frameworks) is the fast path to scale
- Clinical champion ≠ buyer — separate engagement strategies for each
- Budget cycles: NHS financial year ends March; procurement decisions cluster Q4 (Jan–March)

---

## Phase 6 — Measuring Success

**Goal:** Know whether the product is working — clinically, for users, and for the business.

### Choose a metrics framework

Pick a framework before the pilot starts, not after. Having no framework means you measure everything and learn nothing.

**AARRR (Pirate Metrics) — for B2C consumer health products**

Developed by Dave McClure. Tracks the full customer lifecycle from first touch to referral.

| Stage | What it measures | HealthTech example metric |
|---|---|---|
| Acquisition | How users find you | App store installs, referral source, cost per install |
| Activation | First meaningful value moment | Completed first health check-in, connected first wearable |
| Retention | Users coming back | D7 / D30 retention, weekly active users |
| Revenue | Monetisation | Subscription conversion rate, MRR |
| Referral | Word-of-mouth | NPS, referral rate, share rate |

**HEART Framework (Google) — best for evaluating product quality and UX**

Five dimensions that measure the product experience from the user's perspective.

| Dimension | What it measures | Example |
|---|---|---|
| Happiness | Subjective satisfaction | In-product ratings, NPS |
| Engagement | Depth of usage | Sessions per week, features used per session |
| Adoption | New feature uptake | % of users who activated a specific feature |
| Retention | Long-term return | Cohort retention curves at 30 / 60 / 90 days |
| Task success | Completion of core tasks | % of users who complete a health log without dropping off |

**North Star Metric — for organisational alignment**

One metric that represents the core value your product delivers to users. If it goes up, you are growing sustainably; if it goes down, something is wrong regardless of what else looks good.

Examples by product type:
- Symptom tracking app: weekly logs completed per active user
- Clinical decision support: clinician time saved per patient encounter
- Mental health platform: therapy sessions booked per active user

### Full metric layers

| Layer | Metric | Notes |
|---|---|---|
| **Health outcome** | The outcome the product was built to improve (e.g. adherence rate, symptom improvement, sleep score, HRV) | Hardest to measure; most important. Build data collection for this from day one. |
| **Product / user** | DAU/MAU, session length, feature activation, D7/D30 retention, churn rate | Are users coming back? Are they doing the thing? |
| **AI quality** | Accuracy on eval test set, hallucination rate, latency p95, cost per query, human override rate | High override rate = low trust or low accuracy. AI-specific — skip if non-AI. |
| **Business** | Revenue, subscription conversion, expansion MRR, NPS | |

---

## Phase 7 — Ongoing Hygiene

**Goal:** Keep the product safe, accurate, and trusted after launch.

### Model and data drift

*AI-specific.*

AI performance degrades over time when real-world inputs shift away from training data — user behaviour changes, clinical guidelines update, integrations (wearables, HealthKit) change data format.

- Run eval suite on a sample of live production data monthly
- Set a performance threshold below which you trigger a review before retraining — understand why first
- Track input distribution: if the type of queries shifts, investigate

### Retraining triggers

*AI-specific.*

Do NOT retrain on a fixed schedule. Retrain when:
- Eval performance drops below threshold on production data
- A significant change in clinical guidelines or coding standards affects the problem domain
- A new data source is available that meaningfully improves coverage
- A safety incident reveals a gap in the training data

Every retraining cycle runs the full eval suite before deployment. Treat it as a new launch.

### Post-market surveillance (regulated products)

Required for UKCA-marked products. Not optional, not theoretical.
- Collect and review adverse event reports and near-misses quarterly
- Track subgroup performance (demographic breakdowns) — most FDA-cleared AI devices do not do this; doing it is a genuine differentiator
- Maintain a PMCF (Post-Market Clinical Follow-up) plan and update it annually

### Production AI safety hygiene

*AI-specific.*

- Review guardrails and output filters quarterly — clinical guidelines change
- Review API costs monthly — cost per query × volume can surprise you at scale
- Maintain an incident response plan: what happens if the AI gives a harmful output to a patient or clinician?
- Run a red-team exercise annually: try to make the AI behave badly

### Relationship hygiene

- Clinical champions need ongoing engagement — they are not sold once
- Pilot sites that have become live customers need a named success contact
- Run a structured review with each live site every 6 months: what is working, what is not, what would make them expand to other departments?

---

## Quick reference — phase checklist

| Phase | Key output | Gate before next phase |
|---|---|---|
| Phase 0 — Problem | Prioritised problem statement + validated by user research + market sizing complete | Is this problem real? Is it big enough? Is it prioritised above other problems? |
| Phase 1–2 — Discovery + Architecture | Chosen solution + MoSCoW scope + stakeholder map + technical discovery + timeline + resource requirements + architecture direction | Solution signed off by engineering + clinical stakeholder |
| Phase 3 — Build | Working product on staging | Eval suite written and running (AI) or QA gates clear (non-AI) |
| Phase 4 — Evals / QA | Eval report L1 + L2 + L3 (AI) or QA sign-off (non-AI) | L1 + L2 passing; L3 clinician sign-off (AI) / QA sign-off (non-AI) |
| Phase 5 — Launch | Pilot running at 1–2 sites | Pilot success criteria defined; legal/regulatory cleared; internal teams enabled |
| Phase 6 — Measure | Live metric dashboard | North star metric tracking |
| Phase 7 — Hygiene | Monthly eval run (AI) + quarterly review | Ongoing — no end gate |
