<div align="center">

# AI Test Case Generator

**Automatically generate intelligent, comprehensive test cases from natural language requirements — powered by NLP and vector search.**

[![Java](https://img.shields.io/badge/Java-Spring%20Boot-brightgreen?style=flat-square&logo=spring)](https://spring.io/projects/spring-boot)
[![Python](https://img.shields.io/badge/Python-NLP%20Service-blue?style=flat-square&logo=python)](https://www.python.org/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange?style=flat-square)](https://www.trychroma.com/)
[![Allure](https://img.shields.io/badge/Testing-Allure%20Reports-yellow?style=flat-square)](https://docs.qameta.io/allure/)

</div>

---

## What Is This?

Zenius AI Test Case Generator eliminates the manual, time-consuming work of writing test cases. You describe your feature in plain English — the system uses NLP and semantic vector search to understand your requirements and generate structured, ready-to-use test cases in seconds.

Built as a full-stack intern project at **Zenius**, this tool integrates a Python NLP engine, a Java Spring Boot API, and a React UI into a cohesive, production-oriented platform.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                           │
│          (Test Case Form · File Manager · Results View)         │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST API
┌───────────────────────────▼─────────────────────────────────────┐
│              Spring Boot API  (Java)                            │
│   /api/generate · /api/upload-and-view · /api/list-uploaded-    │
│   files · /api/view-file · /api/delete-file                    │
└──────────┬────────────────────────────────────────┬─────────────┘
           │ NLP Processing                          │ File Storage
┌──────────▼────────────────┐           ┌────────────▼────────────┐
│   Python NLP Service      │           │   ChromaDB              │
│  (Text Extraction ·       │           │   Vector Store          │
│   Embeddings · Inference) │           │   (Semantic Search)     │
└───────────────────────────┘           └─────────────────────────┘
```

**Stack at a glance:**

| Layer | Technology |
|---|---|
| Frontend | React, CSS Modules |
| Backend API | Java 17, Spring Boot, Gradle |
| NLP Engine | Python, sentence-transformers |
| Vector Store | ChromaDB |
| Testing & Reports | JUnit 5, Allure Framework |
| Containerization | Docker |

---

## Key Features

### AI-Powered Test Generation
Upload a requirements document (PDF, Word, Excel, or plain text) or paste your requirements directly. The NLP pipeline extracts intent, identifies test scenarios, and generates structured test cases covering happy paths, edge cases, and failure modes.

### Semantic Vector Search
Requirements are embedded and stored in ChromaDB. When generating new test cases, the system retrieves semantically similar past requirements — so your generated tests stay consistent with your existing test suite and domain conventions.

### In-Browser File Viewing
Upload any supported file and view it directly in your browser — no external tools required. Full MIME-type detection ensures PDFs render as PDFs, documents render correctly, and so on.

### Allure Test Reporting
Every test run produces an interactive Allure HTML report — categorized by Epic, Feature, and Story — with step-by-step execution traces, severity levels, and trend analysis over time.

---

## Project Structure

```
TestCase_Generator/
├── zenius_testcase_generator_ui-main/     # React frontend
├── zenius-ai-testcase-generator-api-main/ # Spring Boot backend
├── zenius_testcase_generator_nlp-main/    # Python NLP service
├── src/                                   # Shared source utilities
├── embedding_service.py                   # Sentence embedding logic
├── chroma_vector_store_improved.py        # ChromaDB integration
├── text_extraction_service.py             # Multi-format text extraction
├── vector_store_chroma.py                 # Vector store interface
└── setup_and_run.py                       # One-command setup script
```

---

## Getting Started

### Prerequisites

- Java 17+
- Python 3.9+
- Node.js 18+
- Docker (optional, for ChromaDB)

### 1. Clone the Repository

```bash
git clone https://github.com/Bhavd33p/TestCase_Generator.git
cd TestCase_Generator
```

### 2. Start the NLP Service (Python)

```bash
cd zenius_testcase_generator_nlp-main
pip install -r requirements.txt
python app.py
```

The NLP service runs on `http://localhost:5000`.

### 3. Start the Backend API (Java)

```bash
cd zenius-ai-testcase-generator-api-main
./gradlew bootRun
```

The API runs on `http://localhost:8081`.

### 4. Start the Frontend (React)

```bash
cd zenius_testcase_generator_ui-main
npm install
npm start
```

The UI opens at `http://localhost:3000`.

> **One-command setup:** Run `python setup_and_run.py` from the root to start all services automatically.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/generate` | Generate test cases from requirements |
| `POST` | `/api/upload-and-view` | Upload a file and get a browser-viewable URL |
| `GET` | `/api/view-file/{fileName}` | Serve a file for in-browser viewing |
| `GET` | `/api/list-uploaded-files` | List all uploaded files with metadata |
| `DELETE` | `/api/delete-file/{fileName}` | Delete an uploaded file |

### Example: Generate Test Cases

```bash
curl -X POST http://localhost:8081/api/generate \
  -H "Content-Type: application/json" \
  -d '{"requirements": "Users must be able to log in with email and password. Login should fail after 5 incorrect attempts."}'
```

---

## Testing & Reports

### Run Tests

```bash
cd zenius-ai-testcase-generator-api-main
./gradlew test
```

### Generate Allure Report

```bash
./gradlew allureReport
./gradlew serveAllureReport   # opens interactive report in browser
```

The Allure report includes:

- Test results grouped by **Epic → Feature → Story**
- **Severity levels** (critical, major, minor, trivial)
- **Step-by-step execution traces** for every test
- **Failure categorization** with root cause hints
- **Trend charts** across multiple test runs

---

## Configuration

Key settings in `application.properties`:

```properties
# File upload
file.upload.directory=uploads
file.view.base.url=http://localhost:8081
spring.servlet.multipart.max-file-size=10MB
spring.servlet.multipart.max-request-size=10MB

# NLP service
nlp.service.url=http://localhost:5000
```

---

## Security

- File type validation on every upload (allowlist-based)
- Path traversal protection on all file endpoints
- Configurable CORS policy
- 10 MB file size limit (configurable)
- No credentials stored in code — all config via `application.properties`

See [`SECURITY_SETUP.md`](./SECURITY_SETUP.md) for full details.

---

## Roadmap

- [ ] CI/CD pipeline with GitHub Actions
- [ ] Screenshot capture on test failure (Allure attachment)
- [ ] Bulk test case export (Excel / JIRA CSV)
- [ ] File versioning and preview thumbnails
- [ ] Slack / Teams notifications on report completion
- [ ] Multi-project workspace support

---

## Contributing

1. Fork the repo and create a feature branch
2. Add tests with Allure annotations for any new functionality
3. Run `./gradlew test` — all tests must pass
4. Open a pull request with a clear description

Please follow the existing code conventions and update relevant documentation.

---

## Intern Project — Zenius

This project was built as part of an internship at **Zenius**. It represents a full end-to-end implementation: from NLP research and vector embedding design to REST API development, React UI, and automated test reporting.

---

<div align="center">
Built with care by <a href="https://github.com/Bhavd33p">Bhavdeep Singh</a> · Zenius Internship 2024
</div>
