# Study Artifacts - Documentation

This directory contains all artifacts produced during the thematic analysis phase of the EdgeAI empirical study. Each 
file stores a specific intermediate output of the analysis pipeline, supporting traceability, transparency, and 
replicability of the study.

Below you will find an overview of each file and a detailed description of its structure and purpose.

---

## 1. File Overview

### 1.1 all_collected_fragments.csv

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

    | Column Name              | Description                                                                |
    |--------------------------|----------------------------------------------------------------------------|
    | **repo_ID**              | Unique identifier of the repository from which the fragment was extracted. |
    | **repo_name**            | Name of the GitHub repository.                                             |
    | **frag_ID**              | Sequential identifier for each fragment within the same repository.        |
    | **fragments**            | The raw text excerpt collected from the repository.                        |
    | **fragments_source**     | Path of the file where the fragment was found .                            |
    | **quality_requirements** | Mapping of the fragment to categories or capabilities from ISO/IEC 25010.  |


- **How to Use This File** (_researchers may use this dataset to_):

  * Reproduce the thematic analysis
  * Derive new codes or categories
  * Validate mappings to ISO standards
  * Conduct cross-domain comparisons
  * Explore architectural patterns in EdgeAI OSS

#### This file is considered the **ground truth dataset** for all subsequent coding and synthesis steps.

### 1.2 fragments_used.csv

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

    | Column Name              | Description                                                                |
    |--------------------------|----------------------------------------------------------------------------|
    | **repo_ID**              | Unique identifier of the repository from which the fragment was extracted. |
    | **repo_name**            | Name of the GitHub repository.                                             |
    | **frag_ID**              | Sequential identifier for each fragment within the same repository.        |
    | **fragments**            | The raw text excerpt collected from the repository.                        |
    | **fragments_source**     | Path of the file where the fragment was found .                            |
    | **quality_requirements** | Mapping of the fragment to categories or capabilities from ISO/IEC 25010.  |                                                                   |

- **How to Use This File** (_this dataset supports_):

  * Reproducibility of the fragment selection process
  * Verification of inclusion/exclusion decisions
  * Cross-checking with coding files and guideline categories
  * Independent replication of the thematic analysis
  * Maintaining traceability between raw data → curated data → coded data → themes

#### This file represents the **starting point of the coding process**, guaranteeing methodological rigor and transparency.

---
