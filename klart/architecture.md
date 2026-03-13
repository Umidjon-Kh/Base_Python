# 🗂️ File Organizer — Architecture

> Hexagonal Architecture (Ports & Adapters) with DDD principles.
> Dependencies always point **inward** — outer layers know about inner layers, never the reverse.

---

## Architecture Diagram

```mermaid
graph TB
    subgraph INFRA["🔴  INFRASTRUCTURE LAYER"]
        direction TB
        CLI["🖥️ CLI Adapter\n─────────────\nargparse\nConfigOverrides mapper"]
        BOOT["⚙️ bootstrap.py\n─────────────\nMerges default + file\n+ CLI configs"]
        JSON["📄 JsonConfigRepository\n─────────────\nimplements ConfigRepository\nParses nested JSON blocks"]
        FSA["📁 FileSystemAdapter\n─────────────\nimplements FileRepository\npathlib · os"]
        LOG["📋 Logger\n─────────────\nlogging module"]
    end

    subgraph APP["🟢  APPLICATION LAYER"]
        direction TB
        UC(["🎯 OrganizeFilesUseCase\n─────────────\nOrchestrates the entire\nfile organization flow"])
        DTO["📦 DTOs\n─────────────\nConfigOverrides\nOrganizeResult"]
    end

    subgraph DOMAIN["🟣  DOMAIN LAYER"]
        direction TB
        CFG["🗂️ AppConfig\n─────────────\nRoot entity\nHolds all settings"]
        DIR["📂 Directory\n─────────────\nValue object\nwalk_files · structure"]
        subgraph PORTS["  ⚡ Ports — Interfaces  "]
            P1(["ConfigRepository\n─────\nload · save"])
            P2(["FileRepository\n─────\nread · write · move"])
        end
    end

    CLI      -->|"triggers"| UC
    BOOT     -->|"assembles & injects"| UC
    UC       -->|"depends on"| P1
    UC       -->|"depends on"| P2
    UC       -->|"reads"| CFG
    UC       -->|"walks"| DIR
    JSON    -.->|"implements ✓"| P1
    FSA     -.->|"implements ✓"| P2

    classDef infra   fill:#2a0a0a,stroke:#e05a5a,color:#ff9090
    classDef app     fill:#0a2a14,stroke:#4ec994,color:#86efbd
    classDef domain  fill:#12023d,stroke:#a78bfa,color:#c4b5fd
    classDef port    fill:#1e0a4a,stroke:#c4a8ff,color:#e0d0ff
    classDef usecase fill:#0d3d20,stroke:#34d399,color:#6ee7b7

    class CLI,BOOT,JSON,FSA,LOG infra
    class UC usecase
    class DTO app
    class CFG,DIR domain
    class P1,P2 port

    style INFRA  fill:#1a0505,stroke:#e05a5a,color:#e05a5a
    style APP    fill:#051a0d,stroke:#4ec994,color:#4ec994
    style DOMAIN fill:#080212,stroke:#a78bfa,color:#a78bfa
    style PORTS  fill:#0f0525,stroke:#7c3aed,color:#c4b5fd
```

---

## Layer Responsibilities

### 🔴 Infrastructure Layer

Handles all external concerns — file system, CLI input, JSON config files, logging.
This is the only layer that knows about the outside world.

| Component              | Responsibility                                            |
| ---------------------- | --------------------------------------------------------- |
| `CLI Adapter`          | Parses `argparse` arguments → maps to `ConfigOverrides`   |
| `bootstrap.py`         | Merges default config + JSON file + CLI overrides         |
| `JsonConfigRepository` | Implements `ConfigRepository` port, reads/writes JSON     |
| `FileSystemAdapter`    | Implements `FileRepository` port using `pathlib` and `os` |
| `Logger`               | Application-wide logging via Python `logging` module      |

### 🟢 Application Layer

Orchestrates the use cases. Knows about Domain, but not about Infrastructure.

| Component              | Responsibility                                              |
| ---------------------- | ----------------------------------------------------------- |
| `OrganizeFilesUseCase` | Main use case — runs the full file organization flow        |
| `DTOs`                 | `ConfigOverrides`, `OrganizeResult` — data transfer objects |

### 🟣 Domain Layer

Pure business logic. No dependencies on any other layer.

| Component          | Responsibility                                        |
| ------------------ | ----------------------------------------------------- |
| `AppConfig`        | Root entity — holds all configuration settings        |
| `Directory`        | Value object — `walk_files()`, directory structure    |
| `ConfigRepository` | **Port** — interface for loading/saving config        |
| `FileRepository`   | **Port** — interface for reading/writing/moving files |

---

## Key Rule — Dependency Direction

```
Infrastructure  →  Application  →  Domain
     (knows about)    (knows about)   (knows nothing)
```

> Solid arrows `→` = **depends on**
> Dashed arrows `-.->` = **implements** (adapter fulfills a port contract)
