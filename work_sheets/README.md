# Dataset Filtering Worksheets

This directory contains the [SPREADSHEET](./architecting-edgeAI-based-systems.xlsx) documenting all stages of the 
repository search, filtering, and eligibility assessment performed in this study. Each sheet corresponds to 
**one stage** of the pipeline, ensuring full transparency and complete reproducibility of the dataset construction 
process.

*Note: As this is an Excel file, some browsers may not render the preview correctly. For reliable access, downloading 
the document is recommended.*


## Spreadsheet Structure

The spreadsheet includes five sheets, each representing a specific step of the filtering workflow:

---

### **1. Initial Search (Keywords²)**

Programmatic GitHub API search results.

* Combined keywords and orthographic/stylistic variants related to Edge AI and IoT systems.
* Queries inspected the repository *name*, *description*, and *topics*.
* Applied criteria:

  * recent activity (`pushed: > last_year_date`)
  * minimum relevance threshold (`stars: > 10`)
* **Output:** 872 candidate repositories.

---

### **2. Exclusion Terms Filtering**

Removal of non-engineering or non-research content (educational materials, demos, toy examples, etc.).

* Repositories were excluded if their name/description/topics contained any term from the exclusion list, including:
  *course(s), class(es), tutorial(s), book(s), demo(s), simulator(s), toy(s), guideline(s), tool(s), library,* etc.
* **Output:** 258 repositories remained.

---

### **3. Recent Activity Signal**

Activity-based filtering using GitHub API commit counts.

* Required **at least 50 commits in 2024**, retrieved via paginated commit inspection.
* **Output:** 166 repositories passed.

---

### **4. Manual Eligibility Screening**

Human assessment against the formal inclusion/exclusion criteria (Table I).

* Inspection of repository structure, technical relevance, and fit to the Edge AI scope.
* **Output:** 103 repositories considered eligible.

---

### **5. Architectural Documentation Check**

Final verification of architecture-related materials:

* Markdown documentation, `docs/` or `design/` folders, diagrams, ADRs, and other architectural artifacts.
* **Output:** 70 repositories contained any architectural documentation.

---

## Purpose of This Material

These worksheets provide:

* Full traceability of the filtering process
* Transparency of inclusion/exclusion decisions
* Reproducibility of the dataset construction pipeline
* Support for audit, replication, and review


