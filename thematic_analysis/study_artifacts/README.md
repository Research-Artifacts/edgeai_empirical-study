# Study Artifacts

This directory contains all artifacts produced during the thematic analysis phase of the EdgeAI empirical study. Each 
file stores a specific intermediate output of the analysis pipeline, supporting traceability, transparency, and 
replicability of the study.

Below you will find an overview of each file and a detailed description of its structure and purpose.

---

## 1. File Overview

### 1.1 [projects_included_by_criteria.csv](./projects_included_by_criteria.csv)

- **Description**

    During the mining phase, the initial set of collected repositories was filtered using explicit inclusion and 
    exclusion rules, influenced by related studies and adapted to Edge AI contexts. It forms the baseline sample from
    which all further analyses were constructed.

  
- **Purpose**

    This file contains the complete list of repositories that **passed the inclusion criteria** defined for the study's 
    dataset. It represents *all projects selected after applying systematic screening rules*, prior to deeper 
    architectural analysis. Indeed is the formal output of the *repository selection and eligibility phase*.

    Unlike `software_architecture_documented_projects.csv`, which focuses only on repositories with architecture-related 
    documentation, this file captures **all repositories** that were deemed relevant and eligible according to the 
    methodological filters.


> Typical criteria included:
> 
> * Relevance to EdgeAI or edge–cloud AI workflows
> * Presence of runnable code (not just templates or quizzes)
> * Exclusion of demos, student projects, sample-only repositories
> * Exclusion of repos containing only datasets, models, or simulators
> * Minimum activity or maturity level
> * English-language documentation


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


- **How to Use This File**:

  * Verifying the repository selection methodology
  * Reproducing the eligibility filtering pipeline
  * Analyzing dataset characteristics (domains, activity level, relevance)
  * Supporting fairness and transparency in the study’s sampling strategy
  * Linking included projects to downstream files (fragments, codes, themes, guidelines)

---
### 1.2 [software_architecture_documented_projects.csv](./software_architecture_documented_projects.csv)

- **Description**

    During the initial mining and filtering phases, repositories were screened to determine whether they included 
    documentation relevant to software architecture. Projects were included based on criteria derived from:

    * Presence of architecture-relevant artifacts
    * Existence of diagrams, design documents, ADRs, or conceptual explanations
    * Evidence of architectural decisions, patterns, or structural descriptions


- **Purpose**

    This file lists all repositories in the dataset that *contain explicit or implicit software architecture 
    documentation*. It represents the filtered subset of Edge AI projects considered suitable for architectural 
    analysis.

    * Content analysis of Markdown files
    * Search in documentation folders
    * Examination of linked external resources
    * Detection of architectural patterns and structural descriptions   
    * Presence of workflow, deployment, or capability explanations
    
    
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
    | **search_term**                | Search term that included the repository.              |
    | **desc.**                      | Description of the repository.                         |
    | **commits_2024**               | Total of commits in 2024.                              |
    | **#_commits**                  | Total commits on repository.                           |


- **How to Use This File**:

  * Determining which projects contribute evidence to architectural RQs
  * Cross-matching domains, quality attributes, architectural patterns, and capabilities
  * Supporting descriptive statistics on the prevalence of architectural documentation in EdgeAI OSS
  * Linking repositories to extracted fragments

> This file defines the **core dataset** for all architectural examinations performed in the study.

---

### 1.3 [all_collected_fragments.csv](./all_collected_fragments.csv)

- **Description**

    Each row corresponds to a single architectural fragment identified during content analysis. Fragments originate from 
    README files, Markdown documents, design documents, configuration files, and external links referenced inside the 
    repository.


- **Purpose**

    This file contains *all raw architectural fragments* extracted from the analyzed Edge AI repositories. It serves as 
    the primary set of data for the open coding phase and represents the full textual corpus used in the thematic
    analysis process. It enables:
    
    * Transparency of the data extraction process
    * Auditing and re-coding by other researchers
    * Reproduction of the thematic analysis workflow


- **Column Definitions**

    | Column Name              | Description                                         |
    |--------------------------|-----------------------------------------------------|
    | **frag_ID**              | Sequential identifier for each fragment.            |
    | **repo_ID**              | Unique identifier for the repository.               |
    | **full_repo_name**       | Full name of the repository on GitHub.              |
    | **fragments**            | The raw text excerpt collected from the repository. |
    | **quality_requirements** | Quality attribute assigned to the fragment          |
    | **fragments_source**     | Path of the file where the fragment was found .     |


- **How to Use This File**:

  * Reproduce the thematic analysis
  * Derive new codes or categories
  * Validate mappings to ISO standards
  * Conduct cross-domain comparisons
  * Explore architectural patterns in Edge AI OSS

> This file is considered the **ground truth dataset** for all subsequent coding and synthesis steps.

---

### 1.4 [fragments_used.csv](./fragments_used.csv)

- **Description**

    From an initial set of 490 extracted fragments, only 400 were retained for analysis. To reduce the dataset without 
    introducing selection bias, we restricted the removal process to repositories that had produced more than 15 
    fragments, ensuring a more balanced contribution of fragments across repositories. Within this subset, fragments
    were randomly removed until the target sample size was reached. The decision to work specifically with 400 fragments 
    was grounded in the SurveyMonkey Sample Size Calculator, which indicated that this sample size provides a 99% 
    confidence level with a 3% margin of error for this population. This procedure ensured statistical 
    representativeness while maintaining methodological rigor for the subsequent open coding phase.


- **Purpose**

    This file contains the *final curated subset of fragments* selected for the thematic analysis after all
    methodological filters and sampling procedures were applied. While `all_collected_fragments.csv` includes every raw 
    fragment extracted from the repositories, **this file contains only the fragments that were actually analyzed** and 
    used to generate the final codes, categories, and themes. It therefore represents the *cleaned, validated, and 
    methodologically balanced dataset* that informed the derivation of architectural guidelines for EdgeAI systems.


- **Column Definitions**

    | Column Name              | Description                                               |
    |--------------------------|-----------------------------------------------------------|
    | **frag_ID**              | Sequential identifier for each fragment.                  |
    | **repo_ID**              | Unique identifier for the repository.                     |
    | **full_repo_name**       | Full name of the repository on GitHub.                    |
    | **fragments**            | The raw text excerpt collected from the repository.       |
    | **quality_attributes**   | Mapping to quality attributes based on the ISO/IEC 25010. |
    | **fragments_source**     | Path of the file where the fragment was found .           |


- **How to Use This File**:

  * Cross-checking with coding files
  * Independent replication of this study
  * Maintaining traceability between raw data → curated data → coded data → themes

> It's representing the **starting point of the coding process**, guaranteeing methodological rigor and transparency.

---


### 1.5 [codes.csv](./codes.csv)

- **Description**

    After selecting the relevant fragments (`fragments_used.csv`), researchers performed *inductive open coding* —reading 
    each fragment, identifying significant ideas, and assigning codes that describe the underlying architectural concepts.


- **Purpose**

    This file contains the *complete set of codes* generated during the open coding phase of the thematic analysis.
    Each code represents a meaningful conceptual label assigned to one or more architectural fragments, capturing 
    patterns, concerns, strategies, constraints, or design decisions observed across Edge AI repositories.

  
- **Column Definitions**
    
    | Column Name           | Description                                                                    |
    |-----------------------|--------------------------------------------------------------------------------|
    | **code_ID**           | Unique identifier for each code.                                               |
    | **code**              | The name of the code, representing a conceptual idea extracted from fragments. |
    | **#_occur**           | Number of occurrences of the code.                                             |
    | **theme**             | Associated theme with the code.                                                |
    | **theme_ID**          | Unique identifier for each theme.                                              |
    | **high-order_themes** | Higher-order themes that underpin the sets of guidelines.                      |


- **How to Use This File**:

  * Inspect how concepts emerged from raw data
  * Conduct further analyses
  * Support transparency for replication packages

> It is the main dataset feeding the subsequent **category formation** and **theme/guideline synthesis** phases.

---


### 1.6 [themes.csv](./themes.csv)

- **Description**

    During the thematic analysis, codes were grouped into meaningful clusters based on conceptual similarity, 
    co-occurrence patterns, and relevance to Edge AI architectural practices. Each cluster was then synthesized into a 
    *theme*, which captures:

    * A broader architectural insight
    * The underlying design concern addressed by several codes
    * The shared intent behind different implementations across repositories
    * A generalizable pattern or principle


- **Purpose**

    This file contains the *higher-level themes* produced after grouping and synthesizing the open codes (`codes.csv`).
    Themes represent the **architectural guidelines**, concerns, or recurring patterns discovered across Edge AI 
    repositories, and they serve as the conceptual backbone of the study’s findings.

  
- **Column Definitions**
    
    | Column Name                     | Description                                                        |
    |---------------------------------|--------------------------------------------------------------------|
    | **theme_ID**                    | Unique identifier for each theme                                   |
    | **theme (m2m/edge_literature)** | Concise name for theme based on M2M<sup>1</sup> and IoT literature |
    | **high-order_themes**           | Higher-order themes that underpin the sets of guidelines           |
    | **capabilities (ISO 30141)**    | Mapping to capabilities based on the ISO/IEC 30141:2024            |

<sup>1</sup> Machine-to-Machine


- **How to Use This File**:

  * Understand how codes were abstracted into higher-level architectural concepts
  * Validate the thematic synthesis process
  * Trace each guideline back to the raw evidence (fragments)
  * Support guideline creation, survey design, and cross-analysis


> This file is critical for ensuring transparency and reproducibility in the final guideline derivation.

---

### 1.7 [fragments→codes.csv](./fragments→codes.csv)

- **Description**
    
    The file lists every instance where a fragment was associated with one or more codes. 
    Each row corresponds to a **single encoding action**: a fragment linked to at least one assigned code. This detailed
    representation allows:

    * Track the coding density of fragments
    * Inspect the overlap and distribution of conceptual patterns
    * Support quantitative analyses

    ` It is the relational backbone connecting fragments → codes → themes.`


- **Purpose**

    This file provides the *explicit mapping* between architectural fragments (`fragments_used.csv`) and the codes 
    generated during open coding (`codes.csv`). Because thematic analysis involves a many-to-many relationship — where:

    * One fragment may receive multiple codes, and
    * One code may apply to multiple fragments

    This mapping file ensures full **bidirectional traceability** across all analytical layers. It is essential for 
    validating the coding process and for enabling independent reproduction of the analysis.


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


- **How to Use This File**:

  * Perform co-occurrence or cluster analyses
  * Build network graphs of conceptual relationships
  * Trace every theme back to its empirical origins

> This file ensures that every guideline in the study ultimately connects to explicit, documented evidence.


