# Introduction
This repository contains the supplementary material and replication package for our empirical study on architectural 
practices and guidelines in Edge AI–based systems. It provides the complete research artifacts, including datasets, 
scripts, and analytical workflows used to collect, process, and analyze open-source Edge AI repositories. The goal of 
this material is to ensure transparency, reproducibility, and reusability of our findings. Researchers can use the 
included tools to replicate the study’s pipeline —from dataset acquisition to data treatment and thematic analysis— or 
adapt them for related investigations in software architecture, AI engineering, and edge computing. Together, these 
resources support the broader research community in advancing the understanding and engineering of distributed, 
intelligent systems operating across the cloud–edge continuum.

---

# Getting Started

## Installation Guide

Follow this step-by-step guide to set up your environment, install all required dependencies, and prepare the project 
for execution.

➡️ For a complete installation walkthrough, check **[INSTALL.md](./INSTALL.md)**.

Once your environment is ready, you can proceed with the data collection workflow.

➡️ The full guide for running the **data collection and processing scripts** is available in
**[data_collection/README.md](./data_collection/README.md)**.

---

## Study Artifacts

The `thematic_analysis/` directory contains all qualitative artifacts used in the thematic analysis stage of the study, 
including **ATLAS.ti exports** and the **curated study artifacts** derived from them. Together, these materials 
represent the complete dataset used to generate codes, categories, themes, and—ultimately—the architectural guidelines for EdgeAI systems.

This folder contains two subdirectories; each one includes its own README with a column-by-column explanation of the 
files, their purpose, and their role in the analysis workflow.


* **`atlas.ti_exports/`** — raw and processed exports from ATLAS.ti.

  ➡️ See the detailed description in **[README.md](./thematic_analysis/atlas.ti_exports/README.md)**.


* **`study_artifacts/`** — cleaned datasets, curated fragment collections, derived from the study.

  ➡️ See the detailed description in **[README.md](./thematic_analysis/study_artifacts/README.md)**.

---