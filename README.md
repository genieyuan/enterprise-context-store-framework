# Enterprise Context Store Framework

The Enterprise Context Store (ECS) Framework is a technology-agnostic architecture for capturing
evidence, compiling atomic claims into a versioned Enterprise Context Graph, and serving
request-scoped context packages to AI agents.

> **Maturity:** Phase 1 framework and design documentation. This repository is not a production runtime.

## Start here

- [Framework cover page](docs/framework/cover-page.md)
- [Phase 1 framework](docs/framework/phase-1.md)
- [Lifecycle](docs/framework/lifecycle.md)
- [Capture](docs/framework/capture.md)
- [Compile](docs/framework/compile.md)
- [Reference architecture](docs/reference-architecture.md)
- [Accepted decisions](docs/decisions.md)
- [Roadmap](docs/roadmap.md)
- [Falsification criteria](docs/falsification-criteria.md)

## Non-goals

This project does not provide a production runtime, access-control enforcement, private-message ingestion, or a guarantee of correctness. Security enforcement and deployment concerns remain future work.

## License

Documentation and diagrams are [CC BY 4.0](LICENSE-DOCS). Schemas, tests, and tools are [Apache-2.0](LICENSE-CODE). See [licensing](docs/licensing.md).
