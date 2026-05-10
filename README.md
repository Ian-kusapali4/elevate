```markdown
---
title: Elevate: AI Career Optimization System
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: true
---

# 🤖 Elevate (Hire-ability Engine)

An agentic AI workflow designed to automate the bridge between talent and opportunity. Elevate extracts structured data from complex resumes, fetches live job listings, and uses a Human-in-the-Loop (HIP) approach to intelligently tailor resumes for specific roles—all while aggressively optimizing LLM token costs.

## 🌟 Key Features
* **High-Fidelity Extraction:** Leverages LLMs to parse unstructured PDFs into highly structured JSON candidate profiles.
* **Token-Optimized Workflow:** Bypasses expensive AI-driven job searching. Instead, it fetches relevant jobs and relies on human intelligence to select the best targets.
* **Human-in-the-Loop (HIP):** LangGraph execution automatically pauses (`interrupt_before`), passing control to the Streamlit UI where the user manually selects the job to pursue.
* **Precision Tailoring:** Once a job is selected by the user, the AI rewrites and tailors the resume specifically for that role.
* **Dockerized Deployment:** Fully containerized for consistent behavior across local and cloud environments (Hugging Face Spaces).

## 🛠️ Tech Stack
* **LLMs:** openai/gpt-oss-120b (via Groq API) & llama 3 local models 
* **Framework:** LangChain & LangGraph (Stateful Agentic Workflows),pydantic,jobspy
* **Interface:** Streamlit, jupiter notebook(flow visualization)
* **DevOps:** Docker (Python-slim base)
* **Platform:** Hugging Face Spaces
* **Evaluation:** langsmith 

## 🔍 Observability & Evaluation
Elevate uses **LangSmith** for full-lifecycle observability. This allows for:
* **Trace Analysis:** Every agent decision, from skill extraction to final rewrite, is logged and traceable.
* **Latency Monitoring:** Real-time tracking of LLM performance (e.g., monitoring the 170s+ rewrite cycles for optimization).
* **Token Management:** Granular visibility into token consumption per node to ensure cost-efficiency.


## 🏗️ System Architecture (Current Flow)

Elevate operates on a sequential, stateful graph using LangGraph. The pipeline is designed to extract data, fetch jobs, pause for human selection, and then execute a tailored rewrite.

### The Node Flow

```text
[ __start__ ]
      │
      ▼
[ pdf_reader ]
      │
      ▼
[ Resume_extaction ] ──────────────┐ (failed)
      │      ▲                     │
      │      └── (retry)           │
      ▼ (passed)                   │
[ suggested_Job_formating ] ───────┤ (failed)
      │      ▲                     │
      │      └── (retry)           │
      ▼ (passed)                   │
[ fetch_jobs ] <─────────────┐     │
      │                      │     │
      ▼                      │     │
[ start_career_optimization ]│     │
      │                      │     │
      ▼                      │     │
[ select_job_details ] ──────┘     │
  (INTERRUPT: Human UI)  (retry)   │
      │                            │
      ▼ (Procced)                  │
[ resume_rewrite ]                 │
      │                            │
      ▼                            │
[ human_rewritter_agent ]          │
      │                            │
      ▼                            │
[ __end__ ] <──────────────────────┘


1. **Ingestion & Extraction (`pdf_reader` -> `Resume_extaction`):** The user uploads a PDF. The system reads the document and extracts core skills and experiences.
2. **Search Strategy (`suggested_Job_formating`):** The AI formulates optimized keyword searches based on the candidate's profile.
3. **Job Sourcing (`fetch_jobs`):** The system queries external boards to pull live job openings. *(Note: AI ranking is intentionally disabled here to save on token costs).*
4. **Human-in-the-Loop / HIP (`select_job_details`):** **[GRAPH PAUSES]** The fetched jobs are displayed in the Streamlit UI. The user reviews the "Matching Job Openings" and manually clicks "Tailor Resume" on their preferred role.
5. **Resume Tailoring (`resume_rewrite`):** **[GRAPH RESUMES]** The AI drafts a customized version of the resume targeting the user-selected job description.
6. **Final Review (`human_rewritter_agent`):** The final polished draft is presented to the user for any last-minute manual edits.

## 🚀 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   gh repo clone Ian-kusapali4/AI-Career-Optimization-System
   cd career-app

```

2. **Configure Environment:**
Create a `.env` file in the root directory and add your API keys:
```env
GROQ_API_KEY=your_groq_key_here
# Add any other required scraping/LLM keys here

```


3. **Build and Run via Docker:**
```bash
docker build -t Elevate-engine .
docker run -p 7860:7860 --env-file .env Elevate-engine

```


4. **Access the Application:**
Open your browser and navigate to `http://localhost:7860`.

