# DaVi - Wiki

**Goal:** Considering a collection of public datasets, build a modular Web tool – such as SPA (Single Page Application) or a Web browser extension – able to provide useful visualizations for better understanding of large data/information/knowledge collections. The core functionalities – based on a knowledge model expressed in SKOS and/or OWL including various vocabularies – will be accessed via a SPARQL endpoint. Different extensions (at least 3) will be provided in order to demonstrate specific operations – e.g., "intelligent" filtering, layered visualizations, trend computations, comparing tasks, etc. Bonus: exposing 3D visualizations by using WebGL and/or WebXR.

## Deliverables

All official deliverables are referenced from the wiki. Main deliverables include:

- **Technical Report (PDF)**  
  https://github.com/SamuelLazurca/CrawlWebbers-WADE-Project/blob/main/technical-report.pdf

- **C4 Diagram**
  https://github.com/SamuelLazurca/CrawlWebbers-WADE-Project/blob/main/architecture.jpg

- **User Guide (PDF)**
  https://github.com/SamuelLazurca/CrawlWebbers-WADE-Project/blob/main/user-guide.pdf

- **Demo Video**  
  https://youtu.be/IhP83nLOD2g

- **Live Application / Site**  
  https://davi-ui.vercel.app/

- **Source Code & Releases**  
  https://github.com/SamuelLazurca/CrawlWebbers-WADE-Project

- **Open API Specification**
  https://github.com/SamuelLazurca/CrawlWebbers-WADE-Project/blob/main/open-api.json

## Getting started

### Clone the repository

```bash
git clone https://github.com/SamuelLazurca/CrawlWebbers-WADE-Project.git
```

### Run rest-api

```bash
python.exe -m venv .venv
.\.venv\Scripts\activate

pip install -r requirements.txt

uvicorn uvicorn main:app --reload
```

### Run spa

```bash
npm install
npm run dev
```
