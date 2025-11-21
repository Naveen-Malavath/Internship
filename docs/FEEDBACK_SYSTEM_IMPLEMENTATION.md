# Feedback and Regeneration System Implementation

## Overview

This document describes the comprehensive feedback and regeneration system implemented for the AutoAgents application. The system allows users to provide feedback on features, stories, and visualizations, and regenerate them based on that feedback.

## Architecture

### Frontend Components

1. **FeedbackChatbotComponent** (`autoagents-frontend/src/app/feedback/feedback-chatbot.component.ts`)
   - Standalone Angular component for collecting feedback
   - Manages state: feedback text, submission status, regeneration count, history
   - Handles error states, timeouts, and success notifications
   - Supports undo functionality for regenerations

2. **FeedbackService** (`autoagents-frontend/src/app/services/feedback.service.ts`)
   - Angular service for API communication
   - Handles async/await patterns
   - Implements retry logic and timeout handling
   - Provides error handling with user-friendly messages

### Backend Components

1. **Feedback Router** (`autoagents-backend/app/routers/feedback.py`)
   - `/api/feedback/submit` - Submit feedback
   - `/api/feedback/regenerate` - Regenerate content based on feedback
   - `/api/feedback/history/{item_id}` - Get feedback history
   - `/api/feedback/regeneration-count/{item_id}` - Get regeneration count

2. **Feedback Service** (`autoagents-backend/app/services/feedback_service.py`)
   - Orchestrates regeneration for features, stories, and visualizations
   - Calls appropriate agent services (Agent1, Agent2, Agent3)
   - Enhances prompts with feedback context

3. **Database Schema** (`autoagents-backend/app/schemas/feedback.py`)
   - Pydantic models for request/response validation
   - MongoDB collection: `feedback_history`

## Features Implemented

### State Management
- ✅ Track feedback submissions per item
- ✅ Update UI with regenerated content
- ✅ Maintain version history (optional - via previousVersions)
- ✅ Handle concurrent feedback submissions (disabled buttons during operations)

### Error Handling
- ✅ API timeout handling (60s for regeneration)
- ✅ LLM failure fallbacks
- ✅ User-friendly error messages
- ✅ Retry mechanism (2 retries with exponential backoff)

### Additional Features
- ✅ Rate limiting (max 3 regenerations per item)
- ✅ Feedback history/versioning
- ✅ Undo last regeneration
- ✅ Clear placeholder text: "Describe how you'd like this improved..."

## Implementation Details

### 1. FeedbackChatbot Component

**Location**: `autoagents-frontend/src/app/feedback/feedback-chatbot.component.ts`

**Key Features**:
- Signal-based state management
- Computed properties for rate limiting checks
- Timeout handling (60 seconds)
- Error and success message display
- Feedback history display
- Undo functionality

**Debug Logging**:
- Component initialization
- Feedback submission
- Content regeneration
- Error handling
- State updates

### 2. API Endpoint Implementation

**Location**: `autoagents-backend/app/routers/feedback.py`

**Endpoints**:

#### POST `/api/feedback/submit`
- Validates request
- Creates feedback history entry
- Returns feedback ID and regeneration count

#### POST `/api/feedback/regenerate`
- Checks rate limits (max 3 regenerations)
- Retrieves latest feedback
- Calls feedback service to regenerate
- Updates feedback history
- Returns regenerated content

#### GET `/api/feedback/history/{item_id}?itemType={type}`
- Returns feedback history for an item
- Limited to 50 most recent entries

#### GET `/api/feedback/regeneration-count/{item_id}?itemType={type}`
- Returns current regeneration count

**Debug Logging**:
- Request validation
- Rate limit checks
- Service calls
- Database operations
- Error handling

### 3. Database Schema

**Location**: `autoagents-backend/app/schemas/feedback.py`

**Collections**:
- `feedback_history`: Stores all feedback submissions and regenerations

**Schema**:
```python
{
    "_id": str (UUID),
    "item_id": str,
    "item_type": str,  # 'feature', 'story', or 'visualization'
    "project_id": str,
    "feedback": str,
    "original_content": dict,
    "project_context": str,
    "status": str,  # 'submitted', 'regenerated', 'failed'
    "created_at": datetime,
    "regenerated_at": datetime (optional),
    "version": int,
    "regenerated_content": dict (optional)
}
```

### 4. Agent Prompt Modifications

**Location**: `autoagents-backend/app/services/feedback_service.py`

The feedback service enhances prompts with feedback context:

```python
enhanced_prompt = f"{original_prompt}\n\n=== USER FEEDBACK ===\n{feedback}\n=== END FEEDBACK ===\n\nPlease regenerate this [item] incorporating the user's feedback while maintaining alignment with the original project requirements."
```

**Agent Integration**:
- **Agent1** (Features): Receives enhanced prompt with feedback
- **Agent2** (Stories): Receives enhanced prompt with feedback
- **Agent3** (Visualizations): Receives enhanced prompt with feedback

### 5. Integration Points

**Location**: `autoagents-frontend/src/app/workspace/workspace-view.component.ts`

**Integration**:
- Stories: FeedbackChatbot added to each story card
- Visualizations: FeedbackChatbot added to visualization panel
- Features: Can be added similarly (not shown in current implementation)

**Event Handlers**:
- `onStoryRegenerated()`: Updates story content
- `onVisualizationRegenerated()`: Updates mermaid diagram
- `onFeedbackError()`: Handles errors

## Debug Statements

All components include comprehensive debug logging:

### Frontend
- `[FeedbackChatbot]` - Component lifecycle, state changes, API calls
- `[FeedbackService]` - API requests, responses, errors
- `[WorkspaceView]` - Content regeneration events

### Backend
- `[feedback]` - Request processing, validation, rate limiting
- `[FeedbackService]` - Agent calls, prompt enhancement, content generation

## Usage Example

1. User views a story in the workspace
2. User clicks on FeedbackChatbot component
3. User enters feedback: "Make the acceptance criteria more specific"
4. User clicks "Submit Feedback"
5. System stores feedback and shows success message
6. User clicks "Regenerate"
7. System calls Agent2 with enhanced prompt including feedback
8. New story content is generated and displayed
9. User can click "Undo" to restore previous version

## Rate Limiting

- Maximum 3 regenerations per item
- Enforced at backend level
- Frontend disables regenerate button when limit reached
- Clear error messages when limit exceeded

## Error Handling

### Timeout Handling
- 60-second timeout for regeneration requests
- User-friendly timeout messages
- Automatic cleanup of timeout handlers

### LLM Failures
- Graceful error messages
- Retry mechanism (2 retries)
- Fallback error codes: `LLM_FAILURE`, `RATE_LIMIT_EXCEEDED`, `TIMEOUT`

### Network Errors
- Retry logic with exponential backoff
- User-friendly error messages
- Logging for debugging

## Testing Recommendations

1. **Test with all three item types**:
   - Features (if integrated)
   - Stories
   - Visualizations

2. **Test rate limiting**:
   - Submit 4 regenerations (should fail on 4th)

3. **Test error scenarios**:
   - Network timeout
   - LLM API failure
   - Invalid feedback submission

4. **Test undo functionality**:
   - Regenerate content
   - Click undo
   - Verify previous version restored

5. **Test concurrent submissions**:
   - Try submitting while another request is in progress
   - Verify buttons are disabled

## Files Created/Modified

### Created Files
1. `autoagents-frontend/src/app/feedback/feedback-chatbot.component.ts`
2. `autoagents-frontend/src/app/feedback/feedback-chatbot.component.html`
3. `autoagents-frontend/src/app/feedback/feedback-chatbot.component.scss`
4. `autoagents-frontend/src/app/services/feedback.service.ts`
5. `autoagents-backend/app/routers/feedback.py`
6. `autoagents-backend/app/services/feedback_service.py`
7. `autoagents-backend/app/schemas/feedback.py`

### Modified Files
1. `autoagents-frontend/src/app/types.ts` - Added feedback types
2. `autoagents-frontend/src/app/workspace/workspace-view.component.ts` - Added integration
3. `autoagents-frontend/src/app/workspace/workspace-view.component.html` - Added FeedbackChatbot components
4. `autoagents-backend/app/main.py` - Registered feedback router

## Next Steps (Optional Enhancements)

1. Add authentication middleware to feedback endpoints
2. Add feature-level feedback integration
3. Add email notifications for regenerations
4. Add analytics tracking for feedback usage
5. Add A/B testing for prompt variations
6. Add feedback templates/suggestions
7. Add collaborative feedback (multiple users)

