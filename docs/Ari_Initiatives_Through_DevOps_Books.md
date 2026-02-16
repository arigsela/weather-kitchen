# How I Applied the Three Ways — My Work Through the Lens of DevOps Literature

> This document tells the story of five major initiatives I led at Artemis Health, framed through the principles of **The Phoenix Project**, **Accelerate**, and **The DevOps Handbook**. These aren't just books I've read — they're frameworks I've lived. Each initiative demonstrates how theory translates into real engineering decisions under real constraints.

---

## The Framework: Why These Three Books Matter Together

Before diving into the work, it's worth understanding how these three texts complement each other. The Phoenix Project gives you the **why** — through narrative, it shows what happens when an organization can't see its own value stream, when unplanned work devours capacity, and when the constraint goes unmanaged. Accelerate gives you the **what** — 23,000 survey respondents proving that speed and stability aren't at odds, that DORA metrics predict organizational performance, and that culture (Westrum's model) is as measurable as deployment frequency. The DevOps Handbook gives you the **how** — the step-by-step implementation of the Three Ways: Flow, Feedback, and Continuous Learning.

What I've found over four years of leading DevSecOps at Artemis is that you don't apply these books in sequence. You apply them in layers. Every initiative I've led has elements of all three, and the real skill is knowing which principle to lean on at which phase of the work.

---

## Initiative 1: ECS to EKS Migration — The Strangler Fig in Practice

**154 tickets | Feb 2022 → Jul 2024 | 97% completion rate**

This was the single largest initiative of my tenure — a complete platform migration from legacy ECS and EC2 infrastructure to a modern EKS platform with GitOps, policy enforcement, RBAC, and autoscaling. It touched every layer of the stack and spanned two and a half years.

### Seeing the Value Stream (The First Way: Flow)

The DevOps Handbook's opening principle is that you can't improve a system you haven't mapped. Before writing a single line of Terraform, I mapped Artemis's deployment value stream end-to-end: code commit through Jenkins, manual configuration in ECS task definitions, ad-hoc SSH sessions to troubleshoot, CloudWatch alarms that nobody watched. The lead time from commit to production was measured in days, sometimes weeks. The process time — actual hands-on-keyboard work — was maybe an hour. The gap between those two numbers was pure waste: waiting for approvals, waiting for manual steps, waiting because the single DevOps person was the bottleneck on every deployment.

This is the Theory of Constraints from The Phoenix Project in its purest form. The constraint wasn't compute. It wasn't budget. It was the fact that every deployment required the same person to touch the same fragile pipeline, and that person was also handling SOC2 audits, Jenkins maintenance, and every ad-hoc request that came through the door.

### Why Not Big-Bang: The Strangler Fig Pattern

The DevOps Handbook describes the Strangler Fig Pattern — modernize incrementally by wrapping the legacy system, extracting services into the new platform one at a time, and retiring the old infrastructure only after the new platform has proven itself. This is exactly the approach I took, and it was a deliberate, principled decision.

**Phase 1** was about building the foundation without touching any running workloads. We provisioned a new VPC dedicated to Kubernetes, set up public and internal ALB ingress classes, deployed AWS WAF, created an Internet Gateway, and — critically — designed the IAM-to-Kubernetes RBAC mapping before a single application pod existed. I spent significant time on spikes: how to restrict secrets access with permissions in EKS, how to implement pull-based deployments (evaluating FluxCD, ArgoCD, and others), and how to structure the IAM groups, roles, and Kubernetes roles we'd manage going forward. We also built a demo application that printed environment variables sourced from secrets, just to validate the entire secrets-in-Kubernetes flow end-to-end before we put any real workload on the platform.

This is what Accelerate would call investing in "Architecture" capabilities — specifically, loosely coupled architecture and empowered teams. We didn't just build a cluster. We built a platform that teams could deploy to independently, with guardrails that prevented them from doing damage.

**Phase 2** was the general migration — 24 tickets of moving Chronos, Hermes, and other front-end services into EKS using Kustomize and ArgoCD. But this phase was as much about governance as it was about migration. We implemented Datree for Kubernetes policy compliance, ran kubescape security assessments, created firewalls between the Transit Gateway and the new VPC's private subnets, and blocked services from creating their own load balancers (which would have bypassed our WAF). We built RBAC Operator into the clusters so that IAM group membership automatically translated into Kubernetes RBAC permissions — meaning developers got the access they needed without anyone having to manually edit configmaps.

We also wrote extensive documentation: how to add new applications through GitOps, how to update existing applications, how to troubleshoot. This is the Third Way — Continuous Learning — in practice. Documentation isn't overhead; it's how you reduce the bus factor and enable others to participate in the system.

**Phase 3** — the Zeus migration — was the hardest. Zeus was a stateful data processing platform with HCG and MARA workers that had strict performance requirements. We couldn't just containerize it and hope for the best. We validated the migration paradigm with the Zeus team, verified environment configurations, created custom node groups sized for HCG workers (4 CPU / 8 GB requests, 8 CPU / 16 GB limits, 2 pods per node), increased ALB timeouts to 300 seconds to accommodate long-running data processing, and migrated environment by environment — DEV first, then PREPROD, then PROD — with validation at each stage.

This is exactly what Accelerate describes when it talks about small batch sizes and fast feedback loops. We didn't migrate Zeus all at once. We migrated one environment, let it soak, caught issues (missing env_vars, timeout problems, memory limits), fixed them, and then moved to the next environment. Each migration was its own small batch with its own feedback cycle.

**Phase 4** was platform enhancement — implementing ArgoCD's App of Apps paradigm, upgrading Kubernetes versions, adding External DNS for automatic Route53 record creation, deploying infrastructure-dedicated node groups, and continuing to extract ECS services (hermes-filterset, kafka brokers) into their own Kubernetes deployments. This is what happens when you've built a solid platform: the work shifts from "how do we make this work" to "how do we make this better."

**Phase 5** — the DNS cutover — was the point of no return. This is where the Strangler Fig pattern reaches its climax: you've been running the new system alongside the old one, and now you redirect traffic. But we didn't just flip a switch. We ran performance tests that validated scaling needs. We did load testing that revealed deploying 3 applications simultaneously could overwhelm the cluster — which taught us we needed to increase nginx controller replicas to 3 and isolate infrastructure applications onto their own node group. We trained developers on the new deployment model. We communicated the cutover plan to end users. And when we cut over production DNS for app.artemishealth.com, we had a triage team ready — we even granted temporary DevOps-level access to a senior engineer specifically for cutover triage.

**Phase 6** was the cleanup — announcing the deprecation of EKS-CLUSTER0, migrating the last remaining services (Unleash, Pallas), scaling down old workers, removing ECS clusters and configurations, downsizing EC2 instances, and cleaning up CloudWatch alarms. This is the part that most organizations skip and that The Phoenix Project warns about: if you don't retire the old system, you end up maintaining two systems forever, and the unplanned work doubles.

### What the DORA Metrics Looked Like

Before the migration, deployment frequency for most services was weekly at best, lead time was days, and the change failure rate was high because configurations were manual and inconsistent across environments. After migration, with ArgoCD syncing from a GitOps repository, deployments became self-service — developers merged a PR to the deployments repo and ArgoCD handled the rest. Lead time dropped to minutes. And because every deployment was declarative and version-controlled, rollbacks were just "revert the PR." The change failure rate dropped because the same manifest that worked in dev worked in preprod worked in prod.

This is Accelerate's central thesis in action: speed and stability aren't at odds. By investing in the deployment pipeline (First Way), we got both.

---

## Initiative 2: The LastPass Incident — From Firefighting to Future-Proofing

**30 tickets | Dec 2022 → Feb 2026 | 97% completion rate**

This initiative is the clearest example of how The Phoenix Project's Four Types of Work play out in real life — and how a reactive incident can become a strategic capability when you approach it with the right principles.

### Unplanned Work Becomes Planned Work

When the LastPass security breach became public knowledge, it hit us the way unplanned work always hits: with urgency and zero advance notice. We had credentials in shared LastPass folders — VPN admin passwords, Docker Hub credentials, Snowflake service accounts, Jenkins AWS credentials, GitHub PATs, and more. Every one of those credentials was potentially compromised, and every one needed to be rotated immediately.

In The Phoenix Project, Erik Reid teaches Bill Palmer that unplanned work is the silent killer of IT capacity. It crowds out planned work, disrupts flow, and creates cascading downstream effects. The LastPass incident was exactly this — a massive injection of unplanned work that demanded immediate attention.

But here's where the learning from the books changed how I responded. Instead of treating this as pure firefighting (rotate everything as fast as possible and move on), I treated it as an opportunity to address a systemic problem. The vulnerability wasn't LastPass itself — it was that we were storing production credentials in a shared password manager with no RBAC, no rotation policy, no audit trail, and no programmatic access.

### Theory of Constraints Applied to Secrets Management

The first thing I did was identify the blast radius — a full audit of every credential that lived in our shared LastPass folders. This is value stream mapping applied to security: before you fix anything, you need to understand the current state end-to-end.

Then, rather than just rotating credentials and putting them back in a different vault, I designed a completely new secrets architecture. I wrote a one-pager on an RBAC design for AWS Secrets Manager, proposing a structure where secrets were organized by service (services/pingdom, services/olympus, services/github) and access was controlled through IAM policies attached to team-specific groups. Lower environment secrets had broader access; production secrets required elevated permissions through a separate IAM group.

This is the DevOps Handbook's principle of building quality in at the source. We weren't just fixing a security incident; we were redesigning the entire secrets management capability so that future rotations would be routine, auditable, and self-service.

### The Migration as a Deployment Pipeline Problem

Each credential rotation followed a pattern that mirrors the DevOps Handbook's deployment pipeline: identify all consumers of the credential, update configurations (Ansible playbooks, Jenkins configs, Kubernetes secrets), rotate the credential in the source system, validate that all services still functioned, and then update the new credential in AWS Secrets Manager. This is the First Way — left-to-right flow with built-in validation at each stage.

We rotated OpenVPN admin credentials, Docker Hub accounts (updating playbooks and rerunning them for prod environments), Snowflake service account passwords, Jenkins AWS credentials, GitHub PATs for our automation accounts, and Pingdom monitoring credentials. Each one had its own dependency chain, its own set of consumers, and its own risk profile.

### From Incident Response to Operational Practice

The most important part of this story — and the part that connects directly to the Third Way (Continuous Learning) — is what happened years later. In January 2026, we executed a systematic production credential rotation initiative. Not because of an incident. Not because of an audit finding. Because we had established credential rotation as an operational practice.

We rotated PostgreSQL database passwords across 14 database users. We rotated AWS IAM access keys for content export services and the Hermes ecosystem. We rotated the artemis-auth RSA keypair using a blue/green approach for JWT signing keys — meaning we could roll the new key into production without invalidating existing sessions. We rotated RabbitMQ credentials across preprod and production, and we created service-specific credentials for Proteus where previously it had been sharing another service's credentials.

This is the evolution that The Phoenix Project describes: unplanned work (LastPass breach) gets converted into planned internal IT projects (secrets architecture redesign) which eventually become routine changes (scheduled credential rotation). The fire became a system, and the system became a capability.

### The SOC2 Connection

The DevOps Handbook makes a powerful point about compliance: the deployment pipeline IS the change management evidence. The same principle applies to secrets management. Because every credential now lived in AWS Secrets Manager with IAM-based access control, every access was logged in CloudTrail. When SOC2 auditors asked for evidence of access controls, credential management, and separation of duties, we didn't have to produce screenshots or manually compiled spreadsheets — we pointed them at the IAM policies, the CloudTrail logs, and the Secrets Manager audit trail. The security architecture we built in response to an incident became the compliance evidence we needed for audits.

---

## Initiative 3: Ballista — Building the Deployment Pipeline

**55 tickets | Feb 2022 → Jan 2026 | 96% completion rate**

If the EKS migration was about building the platform, Ballista was about building the pipeline that delivers value through that platform. This initiative is the most direct implementation of the First Way (Flow) across all my work — and it's also the best example of the Strangler Fig Pattern applied to CI/CD.

### Understanding the Constraint

When I arrived, the CI/CD landscape at Artemis was what The Phoenix Project would call a "Brent problem" — everything flowed through a single Jenkins instance maintained by a single person, and that person was also the only one who understood the deployment process. Jenkins workers couldn't reach MySQL databases. PR builds were routing to the wrong server. Deployment Jenkinsfiles had cryptographic key issues. DB copy scripts consumed so much disk space they'd fail mid-execution. Utility jobs used by the Zeus team had been broken since the last infrastructure change.

This is the Four Types of Work in microcosm: every one of these Jenkins issues was unplanned work that disrupted the flow of business projects (features) and internal IT projects (platform improvements). The first seven tickets I worked on in this initiative were all firefighting — stabilizing a broken Jenkins infrastructure so that the rest of the organization could ship code.

### Mapping the Value Stream Before Redesigning It

The DevOps Handbook's first prescription is to map the value stream. At Artemis, the deployment value stream looked roughly like this: developer pushes code to GitHub → Jenkins polls for changes (sometimes missing them) → Jenkins builds a Docker image → Jenkins pushes the image to a registry → someone manually updates a configuration → ECS picks up the new task definition → service restarts. The lead time was long, the process was fragile, and there was no audit trail beyond Jenkins build logs.

The waste in this value stream was enormous: wait time for Jenkins to pick up changes, manual configuration steps, debugging when builds routed to the wrong server, and — critically — no connection between the deployment process and the GitOps model we'd built for Kubernetes.

### Designing Ballista: The First Way in Action

Ballista was our custom GitHub Action designed to replace Jenkins-driven deployments with a GitOps workflow. The key insight — drawn directly from the DevOps Handbook's deployment pipeline design — was that the deployment artifact shouldn't be a Docker image that gets pushed somewhere. It should be a pull request.

Here's how Ballista works: when a developer merges code into their service's main branch, the Ballista GHA triggers. It builds the Docker image, pushes it to ECR, and then generates a PR to our deployments repository with the updated image tag and any configuration changes defined in the service's `ballista.yml` file. ArgoCD watches the deployments repository and syncs the changes to the target Kubernetes cluster.

This design embodies multiple principles simultaneously. From Accelerate's capabilities framework: version control for all artifacts (the deployments repo is the source of truth), trunk-based development (services deploy from main), and deployment automation (no human clicks required). From the DevOps Handbook: the deployment pipeline is automated end-to-end, environments are repeatable (same manifests, different overlays), and every deployment is auditable (it's a Git commit with a PR review trail).

The `ballista.yml` file in each service repository is particularly important. It declares the service's dependencies, resource requirements, environment variables, and deployment targets. This is what Accelerate calls "loosely coupled architecture" — each service owns its own deployment configuration, and Ballista standardizes the process without centralizing the knowledge.

### The Migration: Small Batches, Fast Feedback

We didn't migrate everything to Ballista at once. Following the Strangler Fig Pattern, we migrated service by service: unleash-proxy first (low risk, simple), then export-manager, delivery, artemis-app, chronos, Powerpoint-Writer, Excel-Writer, and content-export services. Each migration was its own small batch: configure the ballista.yml, verify the GHA workflow, deploy to lower environments, validate, then cut over production.

The Hermes migration was the most complex — it required an environment variable compatibility layer because Hermes's Django settings expected environment variables in a format that differed between Jenkins (legacy) and Ballista. We had to implement backward-compatible environment variable handling so the same codebase could be deployed through either pipeline during the transition period. This is pragmatic engineering that acknowledges what the DevOps Handbook calls the reality of brownfield environments: you can't always cut over cleanly, and you need to design for coexistence.

### Modernizing What Remains

Not everything could move to Ballista. MySQL database copy jobs, Atlas team builds, and certain utility jobs still needed Jenkins. But instead of leaving them on the legacy infrastructure, we modernized Jenkins itself: deployed it to Kubernetes (eating our own dog food), configured SSO through Microsoft EntraID, implemented automated backup and restore, migrated jobs to the new instance, and decommissioned the old servers.

This is the Third Way applied to tooling: even for the components you can't fully replace, you improve them. You don't leave legacy infrastructure rotting — you either migrate it or modernize it in place.

### The Impact on DORA Metrics

Before Ballista, deployments were Jenkins-dependent, manual-configuration-dependent, and single-person-dependent. Deployment frequency was limited by how many manual steps one person could execute in a day. Lead time included waiting for that person to be available.

After Ballista, any developer can deploy their service by merging to main. ArgoCD syncs within minutes. Rollback is reverting a PR. The deployment frequency ceiling was removed entirely — it's now limited only by how fast teams can write and review code, which is exactly where you want the constraint to be.

This is what Accelerate means when it says elite performers have removed deployment as a bottleneck. The constraint shifted from "can we deploy?" to "should we deploy?" — which is a fundamentally healthier question.

---

## Initiative 4: Disaster Recovery — The Second Way Applied to Resilience

**46 tickets | Jun 2024 → Jan 2026 | 89% completion rate**

Disaster Recovery is often treated as a checkbox exercise — write a plan, file it somewhere, hope you never need it. This initiative was different. It was the Second Way (Feedback) applied at the infrastructure level: building the capability to detect failure and recover fast, while simultaneously proving that our IaC was truly repeatable.

### The First Way: Flow Through Infrastructure as Code

The entire DR environment was built through Terraform and automated pipelines. Every resource — VPC, EKS cluster, RDS instances, ElastiCache Redis, SQS queues, Lambda functions, S3 buckets, Snowflake accounts, AWS Secrets — was provisioned through IaC. We evaluated Terraform Cloud for automated plan/apply workflows, set up Terraform Cloud agents on EC2 instances within the DR VPC's private subnets, and created a new Terraform root based on our existing dev_kubernetes_vpc root.

This is the DevOps Handbook's principle of environments on demand: if your infrastructure is truly codified, you should be able to stand up a complete environment in a new region by running terraform apply. And that's essentially what we did — but the process of doing it revealed every place where we'd been relying on manual steps, hardcoded values, or undocumented assumptions.

We provisioned the full stack in US-WEST-2: the VPC and networking, a DR-EKS cluster with all infrastructure resources (ArgoCD, nginx ingress, External DNS, cluster autoscaler), RDS PostgreSQL instances with databases/grants/users, Redis clusters, SQS queues, Lambda functions, and AWS Secrets. We configured ZScaler for private access, set up VPN endpoints, created hosted zones and certificates for artemishealthdr.com, and deployed the complete Artemis front-end application suite — proteus, proteus-ui, refresh-artifacts, metric-usage-service, and more.

The data layer required special attention. We set up a new Snowflake account in US-WEST-2 with database replication from the primary region, and we stood up a new Confluent Kafka cluster to support event-driven services in the DR environment.

### The Second Way: Feedback Loops at the Infrastructure Level

Building a DR environment isn't just about provisioning resources — it's about proving that those resources work. The Second Way demands fast feedback at every stage.

We deployed existing production application images from US-EAST-1 to the DR account and validated them. We configured Okta SSO for ArgoCD in the new account. We tested Route53 cross-region failover strategies. We set up Grafana with custom MySQL queries against the DR database to validate data integrity.

Phase II pushed further into automation: we built GitHub Actions workflows to automatically sync the production overlay with the DR overlay, ensuring that any deployment to prod was reflected in DR. This is the deployment pipeline concept extended to infrastructure — the DR environment shouldn't be a snapshot in time; it should be a continuously synchronized replica.

The bugs we found during validation were themselves valuable feedback: Snowflake databases in US-WEST-2 couldn't refresh due to permission issues, SMTP required an AMI-based deployment approach rather than containerization, and some S3 replication rules needed Terraform-level configuration that hadn't been anticipated. Each of these issues, found in DR validation rather than during an actual disaster, is the Second Way working as designed — problems surfaced early, fixed cheaply, lessons captured.

### The Third Way: Learning from the DR Build

The most valuable output of the DR initiative wasn't the DR environment itself — it was the documentation and the validated IaC patterns. We created wiki documentation with step-by-step procedures for provisioning a new VPC/EKS/Environment from scratch. This documentation was tested against reality because it was written during the actual build, not after the fact.

The DevOps Handbook calls this "creating and maintaining documentation through practice." The DR build was, in effect, a full-scale test of our infrastructure automation. Every gap we discovered and filled made our primary environment more resilient too, because the same Terraform modules and patterns underpin both regions.

### Accelerate's Architecture Capability

Accelerate identifies loosely coupled architecture as a key predictor of high performance. The DR initiative proved that our architecture was loosely coupled enough to run in a completely different region with different endpoints, different Snowflake accounts, and different Kafka clusters — without changing any application code. The application configuration was environment-driven (through Kubernetes configmaps and secrets), not hardcoded, which meant the same container images ran in both regions with different configurations.

This isn't something you can achieve retroactively. It's the result of years of investment in the First Way: building the deployment pipeline so that environments are repeatable, configurations are externalized, and infrastructure is codified.

---

## Initiative 5: AI Platform — The Third Way as Strategy

**31 tickets | Mar 2025 → Feb 2026 | 100% completion rate**

The Third Way is about continuous learning and experimentation — creating a culture where trying new things, failing safely, and sharing knowledge are built into the operating rhythm. The AI Platform initiative is the purest expression of this principle in my portfolio, and it's also where the work I've done connects most directly to where the industry is heading.

### Experimentation Through Proof of Concept

The DevOps Handbook advocates for dedicated improvement time and safe-to-fail experiments. The AI platform work started exactly this way: a series of spikes and POCs designed to evaluate what was possible before committing to any specific architecture.

We started by deploying Open WebUI against an existing Kubernetes-hosted Ollama/DeepSeek environment — giving engineers a self-service interface for interacting with local LLMs. Then we containerized our MCP (Model Context Protocol) server, deployed it to ECR, wrote comprehensive documentation, and fixed stability issues. This gave us the building block for connecting AI agents to our actual infrastructure.

The Kagent spike was a pivotal moment: we deployed an open-source Kubernetes-native AI agent framework to TEST-EKS, evaluated its capabilities for infrastructure automation, and within weeks moved to deploying the Kagent Enterprise trial with the full stack — AgentGateway, CRDs, and operator. We integrated it with Microsoft Entra ID for SSO, connected the Snowflake MCP server so AI agents could query our data warehouse, tested n8n workflow automation with Teams integration, and created comprehensive architecture diagrams documenting the entire AI platform.

Each of these was a small batch experiment: deploy, test, learn, decide whether to invest further or pivot. This is Accelerate's "experimentation" capability in action — the ability to try new approaches without requiring months of planning and approval.

### Building the Internal Developer Platform: Conway's Law in Action

Conway's Law says that systems mirror organizational communication structures. When we deployed Backstage as our IDP, we were deliberately reshaping how developers interacted with infrastructure — and therefore how the organization communicated about deployment and operations.

Backstage became the single pane of glass: it integrated with our ballista.yml service definitions to automatically populate the software catalog, added Kubernetes and Crossplane plugins for infrastructure visibility, and eventually incorporated n8n workflow templates for promoting changes from DEV to PROD. We migrated authentication from GitHub OAuth to Microsoft Entra SSO so that it plugged into the same identity system as everything else.

This is what Accelerate calls a "loosely coupled architecture with empowered teams": developers can see their services, understand their dependencies, deploy changes, and provision infrastructure — all through a self-service portal that enforces the right guardrails without requiring a DevOps ticket for every action.

### Intelligent Operations: The Second Way Amplified by AI

The most forward-looking work in this initiative was building AI-powered operational tooling. We deployed an OnCall Agent API to prod-eks with read-only Kubernetes access, implemented periodic cluster health monitoring every 15 minutes through the OnCall API, and added image tag retrieval capabilities so the agent could tell you exactly what's deployed where.

We built an AWS Cost Explorer automation tool through n8n that monitors daily costs and alerts on anomalies. We deployed an EKS CVE Monitor with an exclusion feature for false positives, so the team gets actionable security alerts instead of noise. And we created Claude Skills for Jira documentation and implementation plan creation — automating the overhead of ticket writing so engineers could spend more time on engineering.

This is the Second Way — telemetry and feedback — amplified by intelligence. Instead of dashboards that humans have to watch, we built systems that watch themselves and surface only what matters. The DevOps Handbook talks about creating telemetry at infrastructure, application, and business levels. The AI platform extends that idea: not just telemetry that reports, but telemetry that reasons.

### What This Means for an Organization Like Golden

This initiative matters in the context of Golden because it shows a progression that maps to their likely trajectory. Golden is starting from VMs with a single DevOps person. They need to build the platform (EKS migration), fix the pipeline (Ballista equivalent), and establish operational maturity (DR, secrets management, compliance). But beyond that, the organizations that win long-term are the ones that invest in developer experience and intelligent automation — reducing the operational burden so that a small team can operate at the scale of a much larger one.

The fact that I've already walked this path — from firefighting Jenkins issues to building an AI-powered operations platform — means I can help Golden skip the years of trial and error and focus on the highest-leverage improvements from day one.

---

## The Connecting Thread: How All Five Initiatives Embody the Three Ways

### The First Way — Flow

Every initiative started with mapping the current state and identifying where work got stuck. In the EKS migration, the bottleneck was manual ECS deployments through a single person. In Ballista, it was Jenkins-dependent, manual-configuration-dependent delivery. In DR, it was the absence of any automated environment provisioning. In secrets management, it was a shared password manager with no programmatic access. In the AI platform, it was engineers spending time on toil that machines could handle.

The solution in every case was the same: automate the value stream left-to-right, reduce handoffs, eliminate manual steps, and make the flow of work visible. Terraform for infrastructure. ArgoCD for deployment. Ballista for the pipeline. AWS Secrets Manager for credentials. Backstage for developer self-service.

### The Second Way — Feedback

Every initiative built in faster feedback loops. The EKS migration added Datree policy enforcement and kubescape security scanning — catching misconfigurations before they reached production. Ballista made every deployment a PR that could be reviewed, approved, and audited. DR validation surfaced infrastructure assumptions that had never been tested. Credential rotation established monitoring for access patterns through CloudTrail. The AI platform built automated health checks, CVE monitoring, and cost anomaly detection.

The DevOps Handbook says: "if the team finds out about outages from users, feedback loops are broken." By the end of these five initiatives, Artemis was detecting issues before they became outages — through policy enforcement, automated testing, infrastructure monitoring, and AI-powered alerting.

### The Third Way — Continuous Learning

Every initiative produced documentation, patterns, and reusable capabilities that made the next initiative easier. The EKS migration created Terraform modules that the DR build reused. The secrets management architecture designed for the LastPass incident became the credential rotation practice used years later. Ballista's ballista.yml convention became the service catalog entries in Backstage. The MCP servers built for AI experimentation became the integration layer for Kagent Enterprise.

This is the compounding effect that Accelerate's research identifies: organizations that invest in capabilities see accelerating returns over time. Each initiative didn't just solve its immediate problem — it added a building block that future initiatives could stand on.

---

## The Four Types of Work Across My Tenure

Looking at the full 1,444 ticket portfolio through The Phoenix Project's lens:

**Business Projects** — the features and products that executives care about. My work enabled these by building the platform and pipeline that delivered them: EKS gave services scalability, Ballista gave teams self-service deployments, Backstage gave developers visibility.

**Internal IT Projects** — the infrastructure improvements that are invisible to the business but essential. The EKS migration, Terraform modularization, DR environment, and AI platform were all internal IT projects that created lasting capability.

**Changes** — routine operational work. Kubernetes version upgrades, ArgoCD updates, certificate rotations, and Jenkins plugin management. These are the tickets that keep the lights on.

**Unplanned Work** — the firefighting. 25% of my tickets were ad-hoc/interrupt work. The LastPass breach was unplanned work that became planned work. Jenkins failures were unplanned work that Ballista eventually eliminated. The goal across four years was to systematically reduce the ratio of unplanned to planned work — and the data shows it: my later quarters had proportionally fewer ad-hoc tickets than my earlier quarters, because the platform, pipeline, and automation investments were reducing the surface area for surprises.

---

## Closing: What This Means for My Next Role

These five initiatives demonstrate something that goes beyond technical skill. They demonstrate a way of thinking about infrastructure and operations that is grounded in the research (Accelerate), informed by narrative understanding of organizational dynamics (The Phoenix Project), and executed through proven implementation patterns (The DevOps Handbook).

I don't just build infrastructure. I map value streams. I identify constraints. I design systems that produce feedback. I create documentation and patterns that enable others. And I continuously look for the next leverage point — whether that's containerizing a monolith, automating a pipeline, building a DR environment, or deploying AI agents that make a small team operate like a large one.

The Three Ways aren't just principles I can recite. They're principles I've lived across 316 tickets, 5 major initiatives, and 4 years of building and operating a production platform. And I'm ready to apply them again.
