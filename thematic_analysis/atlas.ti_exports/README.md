# ATLAS.ti Exports

This folder contains all **ATLAS.ti exports** used in our Edge AI architecture study. The goal of this document is to
help readers understand **what each export file contains**, **how it was generated**, and **how it can be reused or 
replicated**.

---

## 1. ATLAS.ti Project Context

- **Tool version:** ATLAS.ti (desktop/WEB)
- **Project scope:** qualitative/thematic coding of Edge AI-related architectural fragments,
  including codes, categories, memos, and relationships.  
- **Main tasks supported by these exports:**
  - Reconstructing the **coding scheme** (codes, categories, families).
  - Inspecting **quotations / fragments** and their assigned codes.
  - Validating and replicating the **thematic analysis process**.

---

## 2. File Overview


### 2.1 [20250914_codebook_full.csv](./20250914_codebook_full.csv)

- **Description**

    This file contains the **complete codebook** used during the thematic analysis. Exported directly from ATLAS.ti, it 
    documents the full hierarchical structure of the coding schema developed for the study. It documents every code 
    created during open, axial, and thematic coding. This codebook defines the complete analytic structure used in the 
    study, including:

    * the **18 high-level thematic families**,
    * all **codes** associated with each theme,
    * and classification groups indicating the origin of each code.


- **Columns Definitions**
    
    | Column            | Description                                                          |
    |-------------------|----------------------------------------------------------------------|
    | **Code**          | The name of the code, including theme-prefix hierarchy (e.g., “T1.”) |
    | **Comment**       | The code definition or explanatory note (if provided)                |
    | **Code Groups**   | The groups to which the code belongs                                 |


- **Usage**  
  
    This file is particularly important for reviewers who want to understand **exactly how codes were defined**, and for
    researchers who wish to replicate or extend the thematic analysis.


### 2.2 [20250914_code_list_frequencies.csv](./20250914_code_list_frequencies.csv)

- **Description**

    This file is an export of the **Code Manager** from ATLAS.ti. It contains the *complete hierarchical structure* of 
    all codes created during the thematic analysis, organized under their respective **themes (T1, T2, T3, ...)**. In 
    addition to listing each code, this export also includes the **quantitative metadata** associated with the coding 
    process. Because this file captures both the **taxonomy of themes → codes** and their **empirical frequencies**, 
    it provides the quantitative foundation used to support the analysis of architectural guidelines for EdgeAI systems. 
    It therefore complements the pure codebook export by presenting not only *what* the codes are, but also *how often*
    they occur and *how they cluster* across the dataset.

  
- **Columns**
    
    | Column                | Description                                                 |
    |-----------------------|-------------------------------------------------------------|
    | **Code**              | The family or individual code (hierarchical indentation)    |
    | **Magnitude Degree**  | Number of quotations coded with this code (frequency)       |
    | **Density**           | Number of relationships this code has with other codes      |
    | **Groups**            | The groups/categories this code belongs to (e.g., “Themes”) |
    | **Number of Groups**  | Count of groups associated with the code                    |
    | **Comment**           | Any memo associated with the code                           |
    | **Creation Date**     | When the code was created                                   |
    | **Modification Date** | When the code was last updated                              |


- **Usage**  
 
    This export is essential for replicating the **open coding stage** and for reconstructing the prevalence of each 
    architectural construct identified in the study.


### 2.3 [20250914_code_coocurrrence.xlsx](./20250914_code_coocurrrence.xlsx)

- **Description**
    This file contains the **complete code co-occurrence analysis** exported from ATLAS.ti. It provides a detailed view 
    of how often pairs of codes appeared together in the same quotation, enabling the identification of semantic 
    relationships and supporting the construction of higher-level categories and themes.
    
    ### The workbook contains **three sheets**:
     
    - **Code Co-occurrence Table (Visual Heatmap)**
    > _A matrix visualization where:_
    >   - rows and columns represent codes,
    >   - cell values indicate co-occurrence counts,
    >   - color intensity (red scale) reflects the frequency of occurrence.

    - **Code Co-occurrence:**
    > _Count_
    >> _A numeric matrix with raw co-occurrence frequencies that supports:_
    >>  - quantitative analyses, 
    >>  - chart generation, 
    >>  - and replication.
    >
    > _Coefficient_
    >> - A normalized co-occurrence matrix calculated by **ATLAS.ti** using similarity coefficients<sup>1</sup>. Values 
    range from 0 to 1 and represent the relative strength of association between code pairs 

    <sup>1</sup> c = n12 / (n1 + n2 - n12)



- **Purpose**

    This file contains the **Code Co-Occurrence Table** generated by ATLAS.ti, a matrix-based analytical output that 
    quantifies how often pairs of codes appear together within the same quotation or within overlapping coded segments.

    Its goal is to support:

    * identifying **semantic relationships** between architectural concerns,
    * detecting topics that tend to co-occur in practitioners’ documentation,
    * validating the **internal structure** of the theme hierarchy (T1–T18),
    * producing **quantitative evidence** to complement qualitative interpretation, and
    * ensuring transparency during the thematic analysis process.

    This artifact therefore serves as a bridge between qualitative coding and structural pattern discovery.


- **Usage:**  
 
  This export is particularly valuable for **data-driven theme formation** and validating the cohesion of guideline 
  families.


### 2.4 [20250914_quotation_export.csv](./20250914_quotation_export.csv)

- **Description:** 

    This file is the **full export of all quotations (fragments)** that were coded during the thematic analysis. Each 
    row represents a distinct **fragment extracted from the GitHub repositories** and coded according to the Edge AI 
    guideline taxonomy. The file integrates:

    * the **raw text of each fragment**,
    * the **document of origin**,
    * all **codes applied**,
    * **positional metadata** (start/end), and
    * timestamps for creation and modification.


- **Purpose:**

    This export contains all **quotation-level citation references** generated inside ATLAS.ti. It links each coded 
    fragment to its **original source repository**, commit, file, or documentation segment. This file ensures 
    **traceability**, allowing any researcher to verify the origin of each fragment.

  
- **Columns**

| Column                | Description                                                               |
|-----------------------|---------------------------------------------------------------------------|
| **Number**            | Unique quotation identifier (e.g., 1:1)                                   |
| **Reference**         | Paragraph marker in the source document                                   |
| **Name**              | Optional label (usually empty for raw fragments)                          |
| **Text Content**      | The full text of the extracted fragment                                   |
| **Document**          | Source document name (e.g., “[ATLAS] – Codifying Fragments”)              |
| **Codes**             | List of all codes applied to the fragment                                 |
| **Number of Codes**   | Total number of codes associated with the fragment                        |
| **Comment**           | Researcher notes or analytic memos                                        |
| **Initial Position**  | Start coordinate of the quotation in the source document                  |
| **Final Position**    | End coordinate                                                            |
| **Extensão**          | Length of the quotation (characters or lines depending on configuration)  |
| **Creation Date**     | When the fragment was created during coding                               |
| **Modification Date** | When it was last updated                                                  |


- **Usage:**  
  
    It is especially important for reviewers and replicators who need to verify **“Where did this fragment come from?”** 
    for any guideline, category, or theme.


### 2.5 [20250914_theme_frequencies.csv](./20250914_theme_frequencies.csv)

- **Description:**
    
    This file contains the **frequency distribution of the 18 top-level themes** (T1–T18) that form the Edge AI 
    guideline taxonomy. It is generated from the ATLAS.ti Code Manager by exporting **only the top-level codes**, each 
    of which represents a major architectural concern in EdgeAI systems.

    Each row corresponds to one thematic family and reports the number of quotations coded with that theme.


- **Purpose**

    This file summarizes the **overall thematic landscape** of the analyzed repositories, showing which architectural 
    concerns are more or less represented in real-world Edge AI projects. 


- **Columns**
    
    | Column                           | Description                                                               |
    |----------------------------------|---------------------------------------------------------------------------|
    | **Code**                         | The theme name (e.g., “T1. Edge Connectivity & Communication Protocols”)  |
    | **Magnitude Degree**             | Total number of quotations associated with that theme                     |
    | **Density**                      | Number of relationships with other codes (0 for themes, unless linked)    |
    | **Groups**                       | Code group classification (“Themes”)                                      |
    | **Number of Groups**             | Count of groups the theme belongs to                                      |
    | **Comment**                      | Any memo associated with the theme (empty here)                           |
    | **Creation/Modification Dates**  | Metadata recorded during coding                                           |

