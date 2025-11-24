# About Me

My name is Ethan and I've been a hobby programmer since I was 15 years old. What started off as writing JApplets with my friends to "download more RAM" eventually inspired me to study Computer Science in college at Rensselaer Polytechnic Institute. Now, my full-time job is Software Engineering.

I love building things with code. The website you're on right now is a labor of love and the culmination of years of accumulated knowledge.

---

# Proficiencies

---

# Experience

## Major League Baseball (MLB)

_New York, NY_

_Senior Software Engineer, Streaming | March 2023 – Present_

* Architect and produce Enterprise middleware for MLB’s flagship product, “MLB.tv”. The distributed system is responsible for delivering live & on-demand baseball games, as well as other non- game video content. At peak, this system has delivered content to over 400,000 concurrent users with a p99 response time of 58 milliseconds.
* Technical Product Owner and Lead Engineer for a suite of tools which allows Tier-0 technical support to perform incident resolution on backend systems. Also provides a cross-cutting interface for event auditing, health monitoring, disaster recovery, and lower environment testing. Reduced direct on-call Engineer intervention by 75% within 1 month of adoption, and 97% within 6 months.
* Designed a server-driven client caching framework using GraphQL Subscriptions, allowing Frontend systems to display real-time data changes to users. Reduced programmatic polling to sensitive backend infrastructure by 99.99%, enabling system optimizations which allowed for 10% faster processing speed on business-critical operations.
* Extended an existing event-driven distributed system to handle new Product domains, representing 300% more traffic and video content for a given day. Proposed & implemented infrastructure extensions to persistence layers and event-driven autoscaling (KEDA) in anticipation of elevated load. The upgraded system handles 165 peak writes per second to Elasticsearch, with a p99 of 15 seconds end-to-end processing time for video availability.
* Led and executed on a business initiative to enable playback of 27,000 unique video and radio broadcasts for historical games on-demand. Wrangled legacy broadcast information and sanitized data to enable playback via the MLB.tv product, unlocking access to previously-unavailable video content for users.
* Piloted a CDN migration which serves nearly 20 million requests per-day with zero downtime. Moved cache rules from CDN to service layer for elevated control over Edge cache directives, enabling vendor-agnosticism for future migrations and increased testability.
* Championed software testing strategies which were applied across multiple backend teams. Logged Architecture Decision Records (ADRs) and developed new testing patterns which allowed for more expressive tests as documentation, improving code coverage by 20%. Correlated with reduced change failure rate of 5%.

## Capsule Pharmacy

_New York, NY (Remote)_

_Senior Software Engineer & Technical Lead, Platform Product | March 2022 – January 2023_

_Software Engineer, Platform Product | April 2020 – February 2022_

* Developed domain-driven microservices to enable the automation of processing insurance claims and orders for patients’ prescriptions. Performed foundational work with tools, frameworks, and architecture ideologies recommended by Business & Engineering leadership to assess their value for product vision.
* Facilitated ticket refinement and discovery sessions as Technical Lead of an Agile team with Product Managers, Product Owners, and Designers to advocate for technical product requirements and constraints.
* Designed, architected, and built a business-critical transaction processing (OLTP) system which supports over 30,000 transactions per-business day. Built dashboards and alerting for Engineering and Product Managers to monitor and observe the health of the system in Production.
* Led a multi-member project to refactor the top-of-funnel intake work stream for new users of the pharmacy. This workflow orchestrates the reception of new prescriptions and gathering information of new patients across all pharmacy locations nationwide. The new workflow follows an Event-driven Architecture and leverages the Local Read Model (LRM) pattern to deliver this data to distributed consumers. This workflow sees a peak throughput of over 500 messages per second.
* Rewrote a proprietary EDI transmission library from the ground-up to enable product evolvability, improve tests and documentation, and retain intellectual control for long-term maintainability. Data integrity improved from 5.9% to 99.9%, using a sample size of nearly 400,000 historical transactions.

## IBM

_New York, NY_

_Software Developer & Technology Consultant, Blockchain Innovation Unit | February 2018 – April 2020_

* Engineered client solutions leveraging Linux Hyperledger Fabric blockchain technology.
* Managed and deployed a production blockchain network using Helm, Tiller, Docker, and Istio in a first-of-its-kind automated deployment of enterprise blockchain using Hyperledger Fabric on Kubernetes for a major financial services client.
* Committed Change Request [FAB-15051](https://github.com/hyperledger/fabric-samples/commit/b64fd45) to the official Linux Hyperledger Fabric open source project to fix a bug in their example “smart contract” code. Extended the blockchain application’s use case to remove assets from a distributed ledger’s world state (database).
