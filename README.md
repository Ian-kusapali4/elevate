---
title: Elevate: Your AI Career Defensive Engine
emoji: 🛡️
colorFrom: Green
colorTo: orange
sdk: docker
app_port: 8501
pinned: true
---

# 🛡️ Elevate: Reclaim Your Career in the Age of AI

**Elevate** is not a job board; it is a stateful, agentic career assistant designed to empower professionals in an AI-driven market. Built on an open-source ethos and powered by **AMD ROCm**, Elevate uses **Gemma 12B** to help users bridge the gap between their current skills and their ultimate career goals.

## 🚀 The Power of Elevate
While other tools automate job displacement, Elevate automates **career sovereignty**. It uses advanced Retrieval-Augmented Generation (RAG) and live market research to provide real-time strategic advice.

### 🧩 Core Modules
* **🎯 Job Matcher:** Intelligent extraction and alignment of your resume against live market opportunities.
* **🔄 Career Pivot:** Analyzes your transferable skills to identify high-ROI career shifts, providing step-by-step transition roadmaps and timelines.
* **⭕ The Circle:** Uses **Tavily** to scout the internet for blogs, communities, and networking groups specific to your niche, helping you build a human support system.
* **🏆 Goal Engine:** Define your "North Star" (e.g., "Earn $200k/year" or "Become CTO"). The agent performs a **Gap Analysis** on your resume and prescribes the exact skills and milestones needed to get there.

## 🛠️ Technical Manifesto
Elevate is engineered for high performance on lightweight, accessible hardware.

* **Compute:** Optimized for **AMD ROCm** (Radeon Open Compute) for high-speed local inference.
* **Model:** **Gemma 12B** — A lightweight yet powerful model capable of complex reasoning and market analysis.
* **Frameworks:** * **LangGraph & LangChain:** For complex, stateful multi-agent workflows.
    * **Pydantic:** Strict data validation for 0% failure extraction.
    * **JobSpy:** Real-time job scraping without the "AI-search" premium cost.
    * **Tavily:** Direct internet access for real-time market trends and networking research.
* **Interface:** **Streamlit** for a reactive, intuitive dashboard.
* **Deployment:** Fully **Dockerized** for seamless deployment on local machines or cloud environments like Hugging Face.

## 🏗️ The Agentic Workflow



Elevate doesn't rely on "internal knowledge." It treats the internet as its source of truth, checking current market trends and real-world networking opportunities before giving you advice.

## 📦 Getting Started

### Prerequisites
* AMD GPU with ROCm support (Recommended) or standard Docker environment.

### 1. Clone & Setup
```bash
git clone [https://github.com/Ian-kusapali4/elevate]
cd elevate