# Study Artifacts - Documentation

This directory contains all artifacts produced during the thematic analysis phase of the EdgeAI empirical study. Each 
file stores a specific intermediate output of the analysis pipeline, supporting traceability, transparency, and 
replicability of the study.

Below you will find an overview of each file and a detailed description of its structure and purpose.

---

## 1. File Overview

### 1.1 [projects_included_by_criteria.csv](./projects_included_by_criteria.csv)

- **Purpose**

This file contains the complete list of repositories that **passed the inclusion criteria** defined for the study's dataset.
It represents *all projects selected after applying systematic screening rules*, prior to deeper architectural analysis.

Unlike `software_architecture_documented_projects.csv`, which focuses only on repositories with architecture-related documentation, this file captures **all repositories** that were deemed relevant and eligible according to the methodological filters.

It is the formal output of the *repository selection and eligibility phase*.

- **Description**

During the mining phase, the initial set of collected repositories was filtered using explicit inclusion and exclusion rules, influenced by related studies (e.g., Malavolta et al., “Mining Guidelines for Architecting Robotics Software”) and adapted to EdgeAI contexts.

Typical criteria included:

* Relevance to EdgeAI or edge–cloud AI workflows
* Presence of runnable code (not just templates or quizzes)
* Exclusion of demos, student projects, sample-only repositories
* Exclusion of repos containing only datasets, models, or simulators
* Minimum activity or maturity level
* English-language documentation

`projects_included_by_criteria.csv` stores the repositories that satisfied *all inclusion criteria* and overcame all exclusion checks.

This file is a cornerstone for reproducibility, ensuring reviewers can confirm the project selection logic.

- **Column Definitions**
    
    | Column Name                  | Description                                          |
    |------------------------------|------------------------------------------------------|
    | **criteria**                 | inclusion criteria that the repository met.          |
    | **repo_id**                  | Unique identifier for the repository.                |
    | **repo_name**                | Name of the GitHub repository.                       |
    | **full_repo_name**           | Full name of the repository on GitHub.               |
    | **url**                      | URL to the repository.                               |
    | **sa_doc**                   | Repository documentation level.                      |
    | **sa_doc_link**              | Link to the repository documentation.                |
    | **domain**                   | Domain classification assigned during mining.        |
    | **architectural_layer**      | Architectural layer to which the repository belongs. |
    | **capabilities**             | 3 Capabilities for each repository.                  |
    | **iso_mapping_capabilities** | Mapping capabilities based on ISO/IEC 30141:2024     |
    | **layer_capabilities**       | Layer where functionalities are assigned.            |
    | **layer**                    | Layer where systems operate.                         |
    | **search_term**              | search term that included the repository.            |
    | **desc.**                    | Description of the repository.                       |
    | **commits_2024**             | Total of commits in 2024.                            |
    | **#_commits**                | Total commits on repository.                         |



- **How to Use This File**

This dataset is essential for:

* Verifying the repository selection methodology
* Reproducing the eligibility filtering pipeline
* Analyzing dataset characteristics (domains, activity level, relevance)
* Supporting fairness and transparency in the study’s sampling strategy
* Linking included projects to downstream files (fragments, codes, themes, guidelines)

It forms the baseline sample from which all further analyses were constructed.

---
### 1.2 [software_architecture_documented_projects.csv](./software_architecture_documented_projects.csv)

- **Purpose**

This file lists all repositories in the dataset that *contain explicit or implicit software architecture documentation*.
It represents the filtered subset of EdgeAI projects considered suitable for architectural analysis (RQ1.1–RQ1.5), based on criteria such as:

* Presence of architecture-relevant artifacts
* Existence of diagrams, design documents, ADRs, or conceptual explanations
* Evidence of architectural decisions, patterns, or structural descriptions

This file defines the **core dataset** for all architectural examinations performed in the study.

- **Description**

During the initial mining and filtering phases, repositories were screened to determine whether they included documentation relevant to software architecture.
Projects were included based on criteria derived from:

* Content analysis of Markdown files
* Search in documentation folders
* Examination of linked external resources
* Detection of architectural patterns and structural descriptions
* Presence of workflow, deployment, or capability explanations

Only repositories meeting these criteria were further analyzed for architectural characteristics, quality attributes, domains, and guideline extraction.

This file stores the *final list* of such repositories.

- **Column Definitions**
    
    | Column Name                    | Description                                            |
    |--------------------------------|--------------------------------------------------------|
    | **criteria**                   | inclusion criteria that the repository met.            |
    | **repo_id**                    | Unique identifier for the repository.                  |
    | **repo_name**                  | Name of the GitHub repository.                         |
    | **included**                   | If the repository was used as a source for fragments.  |
    | **full_repo_name**             | Full name of the repository on GitHub.                 |
    | **url**                        | URL to the repository.                                 |
    | **Architectural Completeness** | Set of columns for validating repository completeness. |
    | **sa_doc**                     | Repository documentation level.                        |
    | **sa_doc_link**                | Link to the repository documentation.                  |
    | **domain**                     | Domain classification assigned during mining.          |
    | **architectural_layer**        | Architectural layer to which the repository belongs.   |
    | **application_type**           | System type.                                           |
    | **capabilities**               | 3 Capabilities for each repository.                    |
    | **iso_mapping_capabilities**   | Mapping capabilities based on ISO/IEC 30141:2024       |
    | **layer_capabilities**         | Layer where functionalities are assigned.              |
    | **layer**                      | Layer where systems operate.                           |
    | **search_term**                | search term that included the repository.              |
    | **desc.**                      | Description of the repository.                         |
    | **commits_2024**               | Total of commits in 2024.                              |
    | **#_commits**                  | Total commits on repository.                           |



- **How to Use This File**

This dataset is essential for:

* Determining which projects contribute evidence to architectural RQs
* Reproducing the filtering and inclusion decisions
* Cross-matching domains, quality attributes, and architectural patterns
* Supporting descriptive statistics on the prevalence of architectural documentation in EdgeAI OSS
* Linking repositories to extracted fragments (`all_collected_fragments.csv` & `fragments_used.csv`)

It serves as the *reference list of architectural evidence sources* for the entire thematic analysis pipeline.

---


### 1.3 [all_collected_fragments.csv](./all_collected_fragments.csv)

- **Purpose**

    This file contains *all raw architectural fragments* extracted from the analyzed EdgeAI repositories. It serves as 
    the primary data source for the open coding phase and represents the full textual corpus used to generate codes, 
    categories, and final thematic guidelines.


- **Description**

    Each row corresponds to a single architectural fragment identified during content analysis. Fragments originate from 
    README files, Markdown documents, design documents, configuration files, and external links referenced inside the 
    repository.

> The file enables:
> * Transparency of the data extraction process
> * Auditing and re-coding by other researchers
> * Alignment with standards (e.g., ISO/IEC 25010 mappings)
> * Reproduction of the thematic analysis workflow


- **Column Definitions**

    | Column Name              | Description                                         |
    |--------------------------|-----------------------------------------------------|
    | **frag_ID**              | Sequential identifier for each fragment.            |
    | **repo_ID**              | Unique identifier for the repository.               |
    | **full_repo_name**       | Full name of the repository on GitHub.              |
    | **fragments**            | The raw text excerpt collected from the repository. |
    | **quality_requirements** | Quality attribute assigned to the fragment          |
    | **fragments_source**     | Path of the file where the fragment was found .     |


- **How to Use This File** (_researchers may use this dataset to_):

  * Reproduce the thematic analysis
  * Derive new codes or categories
  * Validate mappings to ISO standards
  * Conduct cross-domain comparisons
  * Explore architectural patterns in EdgeAI OSS

#### This file is considered the **ground truth dataset** for all subsequent coding and synthesis steps.

---

### 1.4 [fragments_used.csv](./fragments_used.csv)

- **Purpose**

    This file contains the *final subset of fragments* that were selected for thematic analysis after applying all inclusion 
    criteria, quality checks, and de-duplication steps.
    While `all_collected_fragments.csv` stores every raw fragment extracted from all repositories, **this file contains only 
    the fragments that were actually used** in the thematic coding process.

    It therefore represents the *cleaned, curated, and validated dataset* used to derive codes, categories, and architectural 
    guidelines for EdgeAI systems.

- **Description**

  During the extraction phase, some fragments may have been discarded because they were duplicated, irrelevant, too 
  generic, outside the architectural scope, or misaligned with the research questions. `fragments_used.csv` Stores 
  only the *qualified* fragments that passed methodological screening and were used by the 
  researchers during open coding.


- **Column Definitions**

    | Column Name              | Description                                               |
    |--------------------------|-----------------------------------------------------------|
    | **frag_ID**              | Sequential identifier for each fragment.                  |
    | **repo_ID**              | Unique identifier for the repository.                     |
    | **full_repo_name**       | Full name of the repository on GitHub.                    |
    | **fragments**            | The raw text excerpt collected from the repository.       |
    | **quality_attributes**   | Mapping to quality attributes based on the ISO/IEC 25010. |
    | **fragments_source**     | Path of the file where the fragment was found .           |

- **How to Use This File** (_this dataset supports_):

  * Reproducibility of the fragment selection process
  * Verification of inclusion/exclusion decisions
  * Cross-checking with coding files and guideline categories
  * Independent replication of the thematic analysis
  * Maintaining traceability between raw data → curated data → coded data → themes

#### This file represents the **starting point of the coding process**, guaranteeing methodological rigor and transparency.

---


### 1.5 [codes.csv](./codes.csv)

- **Purpose**

    This file contains the *complete set of codes* generated during the open coding phase of the thematic analysis.
    Each code represents a meaningful conceptual label assigned to one or more architectural fragments, capturing 
    patterns, concerns, strategies, constraints, or design decisions observed across EdgeAI repositories.

      `codes.csv` is a fundamental artifact because it documents the **intermediate analytical layer** between raw fragments and higher-level categories/themes.

  - **Description**

  After selecting the relevant fragments (`fragments_used.csv`), researchers performed *inductive open coding* —reading 
  each fragment, identifying significant ideas, and assigning codes that describe the underlying architectural concepts.

> This file stores:
> * All codes created during the analysis
> * Their relationship to individual fragments
> * Preliminary grouping hints
> * Notes supporting interpretation


- **Column Definitions**
    
    | Column Name           | Description                                                                    |
    |-----------------------|--------------------------------------------------------------------------------|
    | **code_ID**           | Unique identifier for each code.                                               |
    | **code**              | The name of the code, representing a conceptual idea extracted from fragments. |
    | **#_of_occurrences**  | Number of occurrences of the code.                                             |
    | **theme**             | Associated theme with the code.                                                |
    | **theme_ID**          | Unique identifier for each theme.                                              |
    | **high-order_themes** | Higher-order themes that underpin the sets of guidelines.                      |

- **How to Use This File** (_`codes.csv` allows researchers to_):

  * Reconstruct the coding process
  * Validate consistency across coders
  * Inspect how concepts emerged from raw data
  * Conduct further analyses (e.g., frequency counts, co-occurrence analysis)
  * Support transparency for replication packages submitted to conferences such as ICSA/ICSE

It is the main dataset feeding the subsequent **category formation** and **theme/guideline synthesis** phases.
This dataset is essential for transparency and enables external researchers to review or reproduce the coding logic.

---


### 1.6 [themes.csv](./themes.csv)

- **Purpose**

This file contains the *higher-level themes* produced after grouping and synthesizing the open codes (`codes.csv`).
Themes represent the **architectural guidelines**, concerns, or recurring patterns discovered across EdgeAI repositories, and they serve as the conceptual backbone of the study’s findings.

`themes.csv` therefore captures the final abstraction step before producing guideline families and architectural recommendations.

- **Description**

During the thematic analysis, codes were grouped into meaningful clusters based on conceptual similarity, co-occurrence patterns, and relevance to EdgeAI architectural practices.
Each cluster was then synthesized into a *theme*, which captures:

* A broader architectural insight
* The underlying design concern addressed by several codes
* The shared intent behind different implementations across repositories
* A generalizable pattern or principle

This file contains the finalized set of themes that emerged from this synthesis.

- **Column Definitions**

| Column Name                     | Description                                                                    |
|---------------------------------|--------------------------------------------------------------------------------|
| **theme_ID**                    | Unique identifier for each theme.                                              |
| **theme (m2m/edge_literature)** | Concise name for theme based on M2M - _Machine-to-Machine_ and IoT literature. |
| **high-order_themes**           | Higher-order themes that underpin the sets of guidelines.                      |
| **capabilities (ISO 30141)**    | Mapping to capabilities based on the ISO/IEC 30141:2024.                       |

- **How to Use This File**

Researchers can use this dataset to:

* Understand how codes were abstracted into higher-level architectural concepts
* Validate the thematic synthesis process
* Trace each guideline back to the raw evidence (fragments)
* Compare themes across repositories, domains, or quality attributes
* Support guideline creation, survey design, and cross-analysis

This file is critical for ensuring transparency and reproducibility in the final guideline derivation.

---

### 1.7 [fragments→codes.csv](./fragments→codes.csv)

- **Purpose**

This file provides the *explicit mapping* between architectural fragments (`fragments_used.csv`) and the codes generated during open coding (`codes.csv`).
Because thematic analysis involves a many-to-many relationship — where:

* One fragment may receive multiple codes, and
* One code may apply to multiple fragments

— this mapping file ensures full **bidirectional traceability** across all analytical layers.

It is essential for validating the coding process and for enabling independent reproduction of the analysis.

- **Description**

The file lists every instance where a fragment was associated with one or more codes.
Each row corresponds to a **single coding action**: one fragment linked to one assigned code.
This fine-grained representation makes it possible to:

* Track the coding density of fragments
* Inspect the overlap and distribution of conceptual patterns
* Analyze consistency across coders
* Support quantitative analyses (e.g., code frequency, co-occurrence networks)

It is the relational backbone connecting raw data → codes → themes.

- **Column Definitions**

| Column Name            | Description                                                 |
|------------------------|-------------------------------------------------------------|
| **fragment_id**        | Sequential identifier for each fragment.                    |
| **repo_id**            | Unique identifier for the repository.                       |
| **repo_name**          | Name of the GitHub repository.                              |
| **quality_attributes** | Mapping to quality attributes based on the ISO/IEC 25010.   |
| **fragments**          | The raw text excerpt collected from the repository.         |
| **codes**              | The code and its respective theme, extracted from ATLAS.ti. |
| **#_codes**            | Number of codes associated with each fragment.              |

- **How to Use This File**

This mapping enables researchers to:

* Reconstruct the coding process with precision
* Audit the allocation of codes across fragments
* Perform co-occurrence or cluster analyses
* Validate consistency across coders
* Build network graphs of conceptual relationships
* Trace every theme back to its empirical origins

This file ensures that every guideline in the study ultimately connects to explicit, documented evidence.


---

