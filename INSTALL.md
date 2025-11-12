# Prepare you Environment


### 1) Prerequisites

- **Git**
- **Python 3.13** (recommended)
- **Poetry 1.8+**

> 💡 Tip: if Poetry is not installed yet, use:
> ```bash
>  pipx install poetry
> ```

---

### 2) Clone the repository

```bash
  git clone https://github.com/<org>/<edgeai.empirical-study.replication-package>.git
```

### 3) Set up environment variables

Create your .env file (used by the data collection scripts):

```shell
  cp .env.example .env
```
Edit .env and set at least the following variables:

```dotenv
GITHUB_API_TOKEN=ghp_xxx...# token with 'repo' and 'read:org' scopes recommended
```

⚠️ Use a Personal Access Token (classic) with repo and read:org permissions to avoid rate-limit issues during data 
collection.


#### 4) Install dependencies with Poetry

```shell
  poetry lock --no-update
  poetry install
  poetry env activate 
```
