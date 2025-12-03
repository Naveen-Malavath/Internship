# AutoAgents Workspace

A full-stack AI-powered project management application with Angular frontend and FastAPI backend.

## Architecture

- **Frontend**: Angular 19 + Angular Material (Port 4201)
- **Backend**: FastAPI + Claude Haiku 3.5 (Port 8000)
- **AI Model**: Claude Haiku 3.5 (claude-3-5-haiku-20241022)

## Features

✅ Project creation wizard with 6 steps
✅ AI-powered content generation:
  - Executive summaries
  - Epic ideas (max 2, 200 words each)
  - Acceptance criteria
  - Risk highlights (max 2, 200 words each)
✅ Real-time word counting with validation
✅ Beautiful loading animations during AI generation
✅ Dark theme UI with responsive design

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
```powershell
cd backend
```

2. Activate virtual environment:
```powershell
.\env\Scripts\Activate.ps1
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

4. Ensure `.env` file exists with your API key:
```env
ANTHROPIC_API_KEY=your_api_key_here
```

5. Start the backend server:
```powershell
python main.py
```

Backend will run on: http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```powershell
cd frontend/autoagents-app
```

2. Install dependencies (if not already done):
```powershell
npm install
```

3. Start the development server:
```powershell
ng serve --port 4201 --open
```

Frontend will run on: http://localhost:4201

## API Endpoints

### Health Check
```
GET http://localhost:8000/health
```

### Generate AI Content
```
POST http://localhost:8000/api/generate
Content-Type: application/json

{
  "type": "summary" | "epics" | "acceptance" | "risks",
  "projectName": "string",
  "industry": "string",
  "methodology": "string",
  "promptSummary": "string",
  "focusAreas": "string (optional)"
}
```

## Usage

1. **Start Both Servers**:
   - Backend on port 8000
   - Frontend on port 4201

2. **Create New Project**:
   - Click "New Project" button
   - Select a template (Step 1)
   - Fill in project details (Step 2)
   - Generate AI content (Step 3):
     - Click "Generate" on any AI prompt card
     - Watch the loading animation
     - View generated content

3. **AI Generation Types**:
   - **Project Summary**: Executive summary in 120 words
   - **Epic-level Roadmap**: 4-6 epic ideas
   - **Acceptance Criteria**: MVP acceptance criteria
   - **Delivery Risk Register**: Top delivery risks

## Project Structure

```
AutoGen/
├── backend/
│   ├── env/                 # Python virtual environment
│   ├── main.py             # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
│
└── frontend/
    └── autoagents-app/
        ├── src/
        │   ├── app/
        │   │   ├── components/
        │   │   │   ├── create-project-modal/
        │   │   │   └── loading-dialog/
        │   │   └── services/
        │   │       └── api.service.ts
        │   └── styles.scss
        └── package.json
```

## Technologies Used

### Backend
- FastAPI 0.122.0
- Anthropic Claude API 0.42.0
- Uvicorn (ASGI server)
- Python-dotenv
- Pydantic

### Frontend
- Angular 19
- Angular Material 21
- RxJS
- TypeScript
- SCSS

## Current Status

✅ Backend API running successfully
✅ Frontend compiling without errors
✅ API connectivity established
✅ Loading dialog implemented
✅ AI generation integrated with Claude Haiku 3.5
✅ Word counting and validation
✅ Responsive UI with dark theme

## Next Steps

- [ ] Implement Steps 4-6 (Features, Stories, Review)
- [ ] Add form validation
- [ ] Save projects to MongoDB
- [ ] Implement authentication
- [ ] Add error handling and retry logic
- [ ] Deploy to production
