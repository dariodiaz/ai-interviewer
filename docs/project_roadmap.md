# Project Roadmap: AI Interviewer Chatbot

## Phase 1: Environment & Infrastructure
- [ ] Initialize Git repository with `main` and `dev` branches.
- [ ] Set up Backend: Python (FastAPI) with Poetry.
- [ ] Set up Frontend: React (Vite) + TypeScript.
- [ ] Set up Database: PostgreSQL (local Docker container).
- [ ] Configure `alembic` for database migrations.
- [ ] Configure `pytest` and `httpx` for backend testing.

## [cite_start]Phase 2: Data Layer & State Machine [cite: 301]
- [ ] Implement SQLAlchemy models (Interview, Message) based on `database.md`.
- [ ] Implement Pydantic schemas for API request/response.
- [ ] Implement the Interview State Machine (DRAFT -> READY -> IN_PROGRESS -> COMPLETED).
- [ ] **Test**: Unit tests for state transitions and database CRUD operations.

## [cite_start]Phase 3: Admin Workflow (Document Ingestion) [cite: 265]
- [ ] Create API endpoint for uploading Resume + Role Description (PDF/Text).
- [ ] Implement simple text extraction (using `pypdf` or similar).
- [ ] Create `DocumentAnalysisChain` (LangChain) to generate Match Score & Focus Areas.
- [ ] **Test**: Integration test uploading a dummy PDF and verifying JSON output.

## [cite_start]Phase 4: Candidate Workflow (The Interview Loop) [cite: 276]
- [ ] Create "Start Interview" endpoint (generates session/token).
- [ ] Implement `QuestionGenerationChain` (Uses focus areas + history).
- [ ] Implement `AnswerEvaluationChain` (Scoring 1-10 + feedback).
- [ ] Implement the Chat Loop Logic:
    - User sends message -> Persist -> Evaluate Answer -> Adjust Difficulty -> Generate Next Q -> Persist -> Return.
- [ ] **Test**: Mock LLM responses to test the full loop logic without burning tokens.

## [cite_start]Phase 5: Reporting & Integrity [cite: 289, 363]
- [ ] Implement `ReportGenerationChain` to summarize the interview.
- [ ] Add integrity signals (response time tracking, paste_detected flag).
- [ ] Build the Final Report JSON structure.
- [ ] **Test**: Verify report generation logic on a completed dummy interview.

## Phase 6: Frontend & Polish
- [ ] Build Admin Dashboard (Create Interview, View Report).
- [ ] Build Candidate Chat Interface (Chat UI, Paste Event Listener).
- [ ] Connect Frontend to Backend APIs.
- [ ] specific: Add diagram of flow if possible.