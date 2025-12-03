from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import json
import traceback
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

app = FastAPI(title="AutoAgents API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4201", "http://localhost:4200"],  # Added port 4200
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Model configurations
HAIKU_MODEL = "claude-haiku-4-5-20251001"
SONNET_MODEL = "claude-sonnet-4-20250514"

# Self-healing retry mechanism
async def call_claude_with_retry(model: str, system_prompt: str, user_prompt: str, max_tokens: int = 1024, max_retries: int = 5, fallback_model: str = None):
    """
    Call Claude API with self-healing retry mechanism.
    Uses primary model for first 2 attempts, falls back to stronger model on 3rd attempt.
    """
    last_error = None
    last_response = None
    
    for attempt in range(max_retries):
        try:
            # Use fallback model (Sonnet) on 3rd attempt if specified
            current_model = model
            if attempt == 2 and fallback_model:
                current_model = fallback_model
                print(f"[RETRY] Attempt {attempt + 1}/{max_retries} - Falling back to {fallback_model}")
            else:
                print(f"[RETRY] Attempt {attempt + 1}/{max_retries} - Using {current_model}")
            
            # If this is a retry, modify the prompt to include the error
            if attempt > 0 and last_error:
                retry_prompt = f"""{user_prompt}

IMPORTANT: Your previous response had an error. Please fix it.

Previous Error: {last_error}

Previous Response:
{last_response}

Please generate a corrected response in valid JSON format."""
                current_prompt = retry_prompt
            else:
                current_prompt = user_prompt
            
            # Call Claude
            message = anthropic_client.messages.create(
                model=current_model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": current_prompt}]
            )
            
            response_text = message.content[0].text
            
            # Ensure response is a string
            if not isinstance(response_text, str):
                print(f"[WARNING] Claude returned non-string response: {type(response_text)}")
                response_text = str(response_text)
            
            print(f"[DEBUG] Response length: {len(response_text)}")
            
            return response_text
            
        except Exception as e:
            last_error = str(e)
            last_response = response_text if 'response_text' in locals() else None
            print(f"[ERROR] Attempt {attempt + 1} failed: {last_error}")
            
            if attempt == max_retries - 1:
                raise
    
    raise Exception(f"Failed after {max_retries} attempts. Last error: {last_error}")


async def generate_mermaid_with_validation(
    model: str, 
    system_prompt: str, 
    user_prompt: str, 
    diagram_type: str,
    max_tokens: int = 4096, 
    max_retries: int = 5, 
    fallback_model: str = None
):
    """
    Generate Mermaid diagram with syntax validation and auto-retry with error feedback.
    - Attempt 1-2: Use primary model (Haiku)
    - Attempt 3-5: Use fallback model (Sonnet) with error feedback
    """
    last_error = None
    last_diagram = None
    
    for attempt in range(max_retries):
        try:
            # Use fallback model (Sonnet) starting from 3rd attempt
            current_model = model
            if attempt >= 2 and fallback_model:
                current_model = fallback_model
                print(f"[MERMAID RETRY] Attempt {attempt + 1}/{max_retries} - Using fallback {fallback_model}")
            else:
                print(f"[MERMAID RETRY] Attempt {attempt + 1}/{max_retries} - Using {current_model}")
            
            # If this is a retry due to syntax error, include the error in prompt
            if attempt > 0 and last_error and last_diagram:
                retry_prompt = f"""{user_prompt}

CRITICAL: Your previous response had a Mermaid syntax error. You MUST fix it.

SYNTAX ERROR:
{last_error}

YOUR PREVIOUS INVALID DIAGRAM:
{last_diagram[:2000]}

Fix the syntax error and return ONLY valid Mermaid code. Do NOT include markdown fences."""
                current_prompt = retry_prompt
            else:
                current_prompt = user_prompt
            
            # Call Claude
            message = anthropic_client.messages.create(
                model=current_model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": current_prompt}]
            )
            
            diagram = message.content[0].text.strip()
            
            # Clean up diagram
            if diagram.startswith("```"):
                lines = diagram.split("\n")
                diagram = "\n".join(lines[1:])
            if diagram.endswith("```"):
                diagram = diagram.rsplit("```", 1)[0]
            diagram = diagram.strip()
            
            # Basic syntax validation
            validation_error = validate_mermaid_syntax(diagram, diagram_type)
            
            if validation_error:
                print(f"[MERMAID VALIDATION] Syntax error detected: {validation_error[:200]}")
                last_error = validation_error
                last_diagram = diagram
                
                if attempt < max_retries - 1:
                    continue  # Retry with error feedback
                else:
                    # Last attempt failed
                    # For critical diagram type mismatches (LLD must be classDiagram), raise error
                    if diagram_type == 'lld' and ('flowchart' in validation_error.lower() or 'classDiagram' in validation_error):
                        print(f"[MERMAID VALIDATION] CRITICAL: LLD must be classDiagram, not flowchart. Raising error.")
                        raise Exception(f"LLD generation failed: Model keeps generating flowchart instead of classDiagram. {validation_error}")
                    
                    # For other validation errors, return diagram and let frontend handle
                    print(f"[MERMAID VALIDATION] All retries failed, returning last diagram")
                    return diagram
            
            print(f"[MERMAID VALIDATION] Diagram validated successfully")
            return diagram
            
        except Exception as e:
            last_error = str(e)
            print(f"[ERROR] Attempt {attempt + 1} failed: {last_error}")
            
            if attempt == max_retries - 1:
                raise
    
    raise Exception(f"Failed after {max_retries} attempts. Last error: {last_error}")


def validate_mermaid_syntax(diagram: str, diagram_type: str) -> str | None:
    """
    Basic Mermaid syntax validation. Returns error message if invalid, None if valid.
    """
    if not diagram or len(diagram.strip()) < 10:
        return "Diagram is empty or too short"
    
    diagram_lower = diagram.strip().lower()
    
    # Check diagram starts with correct declaration
    valid_starts = {
        'hld': ['graph', 'flowchart'],
        'dbd': ['erdiagram'],
        'api': ['graph', 'flowchart', 'sequencediagram'],
        'lld': ['classdiagram'],
        'dfd': ['graph', 'flowchart'],
        'component': ['graph', 'flowchart'],
        'security': ['graph', 'flowchart'],
        'infrastructure': ['graph', 'flowchart'],
        'state': ['statediagram', 'statediagram-v2'],
        'journey': ['journey'],
        'sequence': ['sequencediagram'],
        'mindmap': ['mindmap'],
        'gantt': ['gantt'],
        'gitflow': ['gitgraph']
    }
    
    expected_starts = valid_starts.get(diagram_type, [])
    if expected_starts:
        has_valid_start = any(diagram_lower.startswith(start) or 
                             diagram_lower.startswith('%%{init') 
                             for start in expected_starts)
        if not has_valid_start:
            return f"Diagram should start with one of: {expected_starts}, but starts with: {diagram[:50]}"
    
    # Check for common syntax errors
    error_patterns = [
        ('sequencediagram', '=', 'Sequence diagrams should not contain = in messages'),
        ('sequencediagram', '()', 'Sequence diagrams should not contain () in messages'),
        ('gitgraph', 'tag:', 'GitGraph tag syntax may cause errors'),
    ]
    
    for dtype, pattern, error_msg in error_patterns:
        if diagram_type == dtype.replace('diagram', '') and pattern in diagram:
            # Only flag if it's likely causing issues
            if pattern == '=' and '->>:' not in diagram:
                continue  # It's probably fine
            return error_msg
    
    # Special check for LLD - must be a class diagram with proper class definitions
    if diagram_type == 'lld':
        if 'class ' not in diagram.lower() and 'class\n' not in diagram.lower():
            return "LLD must be a classDiagram with class definitions. Found no 'class' keyword."
        if diagram_lower.startswith('graph') or diagram_lower.startswith('flowchart'):
            return "LLD must be classDiagram, not flowchart. Start with 'classDiagram'."
    
    # Skip bracket validation for diagram types that use special syntax
    # erDiagram uses {} for attributes, classDiagram uses {} for class bodies,
    # gantt doesn't use brackets the same way
    skip_bracket_check = ['dbd', 'lld', 'gantt', 'mindmap', 'journey']
    if diagram_type in skip_bracket_check:
        return None  # Valid - skip bracket checks
    
    # Check for unclosed brackets (only for flowchart-based diagrams)
    if diagram.count('{') != diagram.count('}'):
        return f"Mismatched curly braces: {diagram.count('{')} opening, {diagram.count('}')} closing"
    
    if diagram.count('[') != diagram.count(']'):
        return f"Mismatched square brackets: {diagram.count('[')} opening, {diagram.count(']')} closing"
    
    if diagram.count('(') != diagram.count(')'):
        return f"Mismatched parentheses: {diagram.count('(')} opening, {diagram.count(')')} closing"
    
    return None  # Valid


async def parse_json_with_retry(response_text: str, expected_structure: str, system_prompt: str, original_prompt: str, max_retries: int = 5):
    """
    Parse JSON with retry mechanism. If parsing fails, ask Claude to fix the JSON.
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            print(f"[JSON PARSE] Attempt {attempt + 1}/{max_retries}")
            
            # Ensure response_text is a string
            if not isinstance(response_text, str):
                print(f"[WARNING] response_text is not a string, it's {type(response_text)}")
                response_text = str(response_text)
            
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx <= start_idx:
                raise ValueError("No valid JSON object found in response")
            
            json_str = response_text[start_idx:end_idx]
            parsed_data = json.loads(json_str)
            
            # Validate parsed_data is a dict
            if not isinstance(parsed_data, dict):
                raise ValueError(f"Parsed JSON is not a dictionary, it's {type(parsed_data)}")
            
            print(f"[SUCCESS] JSON parsed successfully")
            return parsed_data
            
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            last_error = str(e)
            print(f"[JSON ERROR] Attempt {attempt + 1} failed: {last_error}")
            print(f"[DEBUG] Response text type: {type(response_text)}")
            print(f"[DEBUG] Response text preview: {str(response_text)[:500]}")
            
            if attempt < max_retries - 1:
                # Ask Claude to fix the JSON
                fix_prompt = f"""The following response has a JSON parsing error. Please fix it and return ONLY valid JSON.

Expected Structure: {expected_structure}

Error: {last_error}

Problematic Response:
{str(response_text)[:2000]}

CRITICAL: Return ONLY a valid JSON object starting with {{ and ending with }}. No explanations, no markdown, just pure JSON."""

                # Get fixed response from Claude
                try:
                    response_text = await call_claude_with_retry(
                        model="claude-haiku-4-5-20251001",
                        system_prompt="You are a JSON formatting expert. Return only valid JSON, no explanations.",
                        user_prompt=fix_prompt,
                        max_tokens=4096,
                        max_retries=1
                    )
                except Exception as retry_error:
                    print(f"[ERROR] Failed to get retry response: {str(retry_error)}")
                    raise
            else:
                raise Exception(f"Failed to parse JSON after {max_retries} attempts. Last error: {last_error}")
    
    raise Exception(f"Failed to parse JSON after {max_retries} attempts")

class GenerateRequest(BaseModel):
    type: str
    projectName: str
    industry: str
    methodology: str
    promptSummary: str
    focusAreas: Optional[str] = ""

class FeaturesRequest(BaseModel):
    prompt: str
    previousFeatures: Optional[str] = ""

class Feature(BaseModel):
    title: str
    reason: str
    acceptanceCriteria: str
    problemStatement: str
    businessObjective: str
    userPersona: str
    detailedDescription: str
    successMetrics: str
    dependencies: str

class FeaturesResponse(BaseModel):
    features: list[Feature]

class StoriesRequest(BaseModel):
    features: list[str]
    projectContext: Optional[str] = ""
    previousStories: Optional[str] = ""

class Story(BaseModel):
    title: str
    description: str
    featureRef: str

class StoriesResponse(BaseModel):
    stories: list[Story]

class GenerateResponse(BaseModel):
    content: str

@app.get("/")
async def root():
    return {"message": "AutoAgents API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    try:
        # Build the prompt based on the type
        if request.type == "summary":
            prompt = f"""You are an expert product strategist and business analyst. 

Create a concise executive summary for a {request.industry} initiative called "{request.projectName}".

Project Context:
- Industry: {request.industry}
- Methodology: {request.methodology}
- Project Overview: {request.promptSummary}
- Focus Areas: {request.focusAreas or "customer experience, innovation, operational excellence"}

Requirements:
- Maximum 120 words
- Highlight customer impact and measurable business outcomes
- Use professional, stakeholder-ready language
- Include 2-3 key success metrics or goals
- Emphasize strategic value and market differentiation

Generate only the executive summary text, no additional formatting or preamble."""

        elif request.type == "epics":
            prompt = f"""You are an expert agile product owner and technical architect.

Generate 4-6 epic-level initiatives for a {request.methodology} team launching "{request.projectName}" in the {request.industry} sector.

Project Context:
- Project: {request.projectName}
- Industry: {request.industry}
- Methodology: {request.methodology}
- Description: {request.promptSummary}

Requirements:
- Each epic should be a high-level feature or capability
- Include one sentence justification for business value
- Format: "Epic Title: Brief description explaining customer/business value"
- Focus on deliverable outcomes, not tasks
- Align with {request.methodology} best practices
- Consider technical feasibility and dependencies

Generate 4-6 epic ideas, one per line."""

        elif request.type == "acceptance":
            prompt = f"""You are a quality assurance expert and product manager.

List key acceptance criteria for the MVP release of "{request.projectName}", a {request.industry} product.

Project Context:
- Project: {request.projectName}
- Industry: {request.industry}
- Focus: {request.focusAreas or "customer experience and operational excellence"}
- Description: {request.promptSummary}

Requirements:
- Focus on must-have criteria for MVP launch
- Cover functional, performance, security, and compliance aspects
- Use clear, testable statements
- Format as concise bullet points (•)
- Include 8-12 critical acceptance criteria
- Emphasize quality gates and success metrics

Generate only the bullet-pointed acceptance criteria."""

        elif request.type == "risks":
            prompt = f"""You are a seasoned project risk manager and delivery expert.

Identify the top delivery risks for a {request.methodology} implementation of "{request.projectName}" in {request.industry}.

Project Context:
- Project: {request.projectName}
- Industry: {request.industry}
- Methodology: {request.methodology}
- Description: {request.promptSummary}

Requirements:
- Cover technology, compliance, people, and timeline considerations
- Identify 6-8 critical risk areas
- For each risk, suggest mitigation approach
- Format: "Risk Area: Description and suggested mitigation"
- Prioritize by likelihood and impact
- Focus on actionable insights

Generate the top delivery risks with mitigation strategies."""

        else:
            raise HTTPException(status_code=400, detail="Invalid generation type")

        # Call Claude Haiku with retry mechanism
        generated_content = await call_claude_with_retry(
            model=HAIKU_MODEL,
            system_prompt="You are a helpful AI assistant that generates accurate, professional content for project management.",
            user_prompt=prompt,
            max_tokens=1024,
            max_retries=5,
            fallback_model=SONNET_MODEL
        )

        return GenerateResponse(content=generated_content)

    except Exception as e:
        print(f"[ERROR] Generate content failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/api/generate-features", response_model=FeaturesResponse)
async def generate_features(request: FeaturesRequest):
    try:
        print(f"[DEBUG] Received features request")
        print(f"[DEBUG] Request prompt type: {type(request.prompt)}")
        
        # Ensure prompt is a string
        if isinstance(request.prompt, list):
            print(f"[WARNING] Prompt is a list, converting to string")
            prompt_text = '\n'.join(str(item) for item in request.prompt)
        elif not isinstance(request.prompt, str):
            print(f"[WARNING] Prompt is {type(request.prompt)}, converting to string")
            prompt_text = str(request.prompt)
        else:
            prompt_text = request.prompt
            
        print(f"[DEBUG] Prompt length: {len(prompt_text)}")
        
        # System prompt for Claude
        system_prompt = """You are an elite product strategist and technical architect with expertise in digital product development across multiple industries. Your role is to analyze project requirements and generate comprehensive, production-ready Epic Briefs for features.

CRITICAL DATA TYPE REQUIREMENTS:
- ALL field values MUST be plain text strings (NO arrays, NO lists, NO objects)
- acceptanceCriteria: Single string with bullet points using newlines (\n)
- successMetrics: Single string with metrics separated by newlines (\n)
- dependencies: Single string with items separated by newlines (\n)
- DO NOT use JSON arrays for any field - use newline-separated strings instead

Guidelines:
- Generate EXACTLY 6 distinct, high-value features
- Each feature must be a complete Epic Brief with all required fields as STRINGS
- Provide detailed, actionable information for each field
- Focus on user value, technical feasibility, and market differentiation
- Cover core functionality, user experience, security, and scalability
- Use industry best practices and modern development standards
- If previous features are provided, ensure NEW features complement them without duplication

Output Format (strict JSON with STRING values only):
{
  "features": [
    {
      "title": "Precise feature name (3-7 words)",
      "reason": "One-sentence business justification (15-25 words)",
      "problemStatement": "Clear description of the user/business problem this solves (25-40 words)",
      "businessObjective": "Specific KPI or success metric (e.g., 'Improve 30-day activation from 55% to 75%') (15-30 words)",
      "userPersona": "Primary user type and their needs (e.g., 'SME business owner seeking streamlined onboarding') (10-20 words)",
      "detailedDescription": "End-to-end flow, scope boundaries, and interaction model (40-60 words)",
      "acceptanceCriteria": "- Given scenario 1\n- When action 1\n- Then result 1",
      "successMetrics": "Activation rate > 75%\nSupport tickets < 20%\nUser satisfaction > 4.5/5",
      "dependencies": "Requires user authentication system\nDepends on payment gateway integration"
    }
  ]
}

Ensure features are:
✓ User-centric and outcome-focused
✓ Technically feasible within MVP scope
✓ Aligned with industry standards and compliance
✓ Diverse across functional areas (core, UX, security, analytics, etc.)
✓ Complete Epic Briefs ready for team review
✓ ALL fields are STRING values (never arrays)
✓ Complement previously generated features (if any)"""

        previous_features_section = ""
        if request.previousFeatures:
            # Ensure previousFeatures is a string
            if isinstance(request.previousFeatures, list):
                prev_features_text = '\n'.join(str(item) for item in request.previousFeatures)
            elif not isinstance(request.previousFeatures, str):
                prev_features_text = str(request.previousFeatures)
            else:
                prev_features_text = request.previousFeatures
                
            previous_features_section = f"""\n\n⚠️ CRITICAL - Previously Generated Features (AVOID DUPLICATES):
{prev_features_text}

🚨 YOU MUST GENERATE COMPLETELY NEW AND DIFFERENT FEATURES:
- Cover DIFFERENT functional areas (not the same as above)
- Address DIFFERENT user needs and scenarios
- Create features that COMPLEMENT the ones above
- DO NOT repeat similar features from the list above
- Think of different aspects: admin tools, reporting, integrations, mobile features, etc.\n"""

        user_prompt = f"""Based on the following project specification, generate exactly 6 essential features:{previous_features_section}

{prompt_text}

CRITICAL: Return ONLY valid JSON. All field values must be strings (text), NOT arrays or lists.
For fields like acceptanceCriteria, successMetrics, and dependencies, use newline-separated strings.

Example:
"acceptanceCriteria": "- Given user is logged in\\n- When user clicks button\\n- Then action happens"
"successMetrics": "Metric 1 > 75%\\nMetric 2 < 20%\\nMetric 3 = 100%"

Generate 6 features in strict JSON format."""

        # Call Claude Haiku 4.5 with retry mechanism
        print("[DEBUG] Calling Claude API for feature generation...")
        generated_content = await call_claude_with_retry(
            model="claude-haiku-4-5-20251001",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=4096,
            max_retries=5
        )
        
        print(f"[DEBUG] Received response from Claude, length: {len(generated_content)}")
        print(f"[DEBUG] Response preview: {generated_content[:200]}...")
        
        # Parse JSON with retry mechanism
        expected_structure = """{ "features": [{ "title": "...", "reason": "...", "problemStatement": "...", "businessObjective": "...", "userPersona": "...", "detailedDescription": "...", "acceptanceCriteria": "...", "successMetrics": "...", "dependencies": "..." }] }"""
        
        features_data = await parse_json_with_retry(
            response_text=generated_content,
            expected_structure=expected_structure,
            system_prompt=system_prompt,
            original_prompt=user_prompt,
            max_retries=5
        )
        
        # Ensure we have up to 6 features
        features = features_data.get('features', [])[:6]
        
        # Helper function to safely convert values to strings
        def safe_string(value):
            """Convert value to string, handling lists and other types."""
            if value is None or value == '':
                return 'N/A'
            if isinstance(value, str):
                stripped = value.strip()
                return stripped if stripped else 'N/A'
            if isinstance(value, list):
                if not value:
                    return 'N/A'
                items = [str(item).strip() for item in value if item]
                return '\n'.join(items) if items else 'N/A'
            if isinstance(value, dict):
                return str(value)
            result = str(value).strip()
            return result if result else 'N/A'
        
        # Validate and format features
        formatted_features = []
        for idx, feat in enumerate(features):
            try:
                formatted_features.append(Feature(
                    title=safe_string(feat.get('title', '')),
                    reason=safe_string(feat.get('reason', '')),
                    acceptanceCriteria=safe_string(feat.get('acceptanceCriteria', '')),
                    problemStatement=safe_string(feat.get('problemStatement', '')),
                    businessObjective=safe_string(feat.get('businessObjective', '')),
                    userPersona=safe_string(feat.get('userPersona', '')),
                    detailedDescription=safe_string(feat.get('detailedDescription', '')),
                    successMetrics=safe_string(feat.get('successMetrics', '')),
                    dependencies=safe_string(feat.get('dependencies', ''))
                ))
            except Exception as e:
                print(f"[ERROR] Failed to format feature {idx + 1}: {str(e)}")
                print(f"[DEBUG] Feature data: {feat}")
                raise
        
        return FeaturesResponse(features=formatted_features)

    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON decode error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")
    except Exception as e:
        print(f"[ERROR] Feature generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Feature generation failed: {str(e)}")

@app.post("/api/generate-stories", response_model=StoriesResponse)
async def generate_stories(request: StoriesRequest):
    try:
        # System prompt for Claude
        system_prompt = """You are a senior agile product owner and user story expert with deep expertise in writing clear, actionable user stories that drive development success.

Guidelines:
- Generate EXACTLY 2 user stories per feature provided
- Each story MUST have a UNIQUE and SPECIFIC title that describes the exact functionality
- Story titles should be short, descriptive, and action-oriented (like Jira story summaries)
- Each story MUST have a DIFFERENT user persona (e.g., customer, admin, compliance officer, business owner, mobile user)
- Each story MUST address a DIFFERENT use case or scenario for that feature
- Stories should be specific, testable, and independently deliverable
- Include clear acceptance criteria in the description
- Focus on user value and business outcomes
- Ensure stories are right-sized for a single sprint
- If you see previously generated stories, you MUST create completely different stories with different personas and scenarios

Story Structure:
- Title: Short, specific, action-oriented summary (5-8 words) - NOT the "As a" format, just the feature/action
  Examples: "View Real-Time Account Balance", "Set Up Transaction Alerts", "Generate Monthly Spending Report"
- Description: Full user story in "As a [user], I want to [action] so that [benefit]" format with acceptance criteria (2-3 bullet points)
- featureRef: The parent feature/epic name this story belongs to

Output Format (strict JSON):
{
  "stories": [
    {
      "title": "Specific Action-Oriented Title (5-8 words)",
      "description": "As a [SPECIFIC user type], I want to [SPECIFIC action] so that [SPECIFIC benefit]\\n\\nAcceptance Criteria:\\n- Given...\\n- When...\\n- Then...",
      "featureRef": "Parent Feature Name"
    }
  ]
}

Quality Standards:
✓ Each story has a unique, specific title (NOT generic, NOT "As a" format)
✓ Story titles describe the exact functionality
✓ Each story has a unique user persona
✓ Stories cover different aspects/scenarios of the feature
✓ Clear acceptance criteria included
✓ User-centric language
✓ Testable outcomes
✓ Business value explicit
✓ NO duplicate titles or scenarios"""

        # Build features list
        features_text = "\n".join([f"{i+1}. {feat}" for i, feat in enumerate(request.features)])
        
        context_section = ""
        if request.projectContext:
            context_section = f"\n\nProject Context:\n{request.projectContext}\n\nUse this context to ensure stories align with the overall project vision and requirements.\n"
        
        previous_stories_section = ""
        if request.previousStories:
            previous_stories_section = f"""\n\n⚠️ CRITICAL - Previously Generated Stories (AVOID ALL DUPLICATES):
{request.previousStories}

🚨 YOU MUST GENERATE COMPLETELY NEW AND DIFFERENT STORIES:
- Use DIFFERENT user personas (not the same as above)
- Address DIFFERENT use cases and scenarios
- Create UNIQUE value propositions
- DO NOT repeat any similar stories from the list above
- Think of alternative workflows, edge cases, or different user types\n"""
        
        user_prompt = f"""Generate exactly 2 user stories for each of the following APPROVED features:{context_section}{previous_stories_section}

{features_text}

Total stories to generate: {len(request.features) * 2}

Return the stories in strict JSON format with title, description, and featureRef for each story."""

        # Call Claude Haiku 4.5 with retry mechanism
        print("[DEBUG] Calling Claude API for story generation...")
        generated_content = await call_claude_with_retry(
            model="claude-haiku-4-5-20251001",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=4096,
            max_retries=5
        )
        
        print(f"[DEBUG] Received response from Claude, length: {len(generated_content)}")
        
        # Parse JSON with retry mechanism
        expected_structure = """{ "stories": [{ "title": "As a [user], I want to [action] so that [benefit]", "description": "...", "featureRef": "..." }] }"""
        
        stories_data = await parse_json_with_retry(
            response_text=generated_content,
            expected_structure=expected_structure,
            system_prompt=system_prompt,
            original_prompt=user_prompt,
            max_retries=5
        )
        
        # Get stories
        stories = stories_data.get('stories', [])
        
        # Helper function to safely convert values to strings
        def safe_string(value):
            """Convert value to string, handling lists and other types."""
            if value is None or value == '':
                return 'N/A'
            if isinstance(value, str):
                stripped = value.strip()
                return stripped if stripped else 'N/A'
            if isinstance(value, list):
                if not value:
                    return 'N/A'
                items = [str(item).strip() for item in value if item]
                return '\n'.join(items) if items else 'N/A'
            if isinstance(value, dict):
                return str(value)
            result = str(value).strip()
            return result if result else 'N/A'
        
        # Validate and format stories
        formatted_stories = []
        for story in stories:
            formatted_stories.append(Story(
                title=safe_string(story.get('title', '')),
                description=safe_string(story.get('description', '')),
                featureRef=safe_string(story.get('featureRef', ''))
            ))
        
        return StoriesResponse(stories=formatted_stories)

    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON decode error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")
    except Exception as e:
        print(f"[ERROR] Story generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")

# ============================================================================
# DESIGN GENERATION SYSTEM
# ============================================================================

# Design types and their configurations - Using Haiku for speed, Sonnet as fallback
DESIGN_CONFIG = {
    "hld": {
        "name": "High Level Design",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 4096,
        "requires": []  # First design, no dependencies
    },
    "dbd": {
        "name": "Database Design (ERD)",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 4096,
        "requires": ["hld"]
    },
    "api": {
        "name": "API Design",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 4096,
        "requires": ["hld", "dbd"]
    },
    "lld": {
        "name": "Low Level Design",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 8192,
        "requires": ["hld", "dbd", "api"]
    },
    "dfd": {
        "name": "Data Flow Diagram",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 4096,
        "requires": ["hld", "dbd"]
    },
    "component": {
        "name": "Component Diagram",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 4096,
        "requires": ["hld", "lld"]
    },
    "security": {
        "name": "Security Architecture",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 4096,
        "requires": ["hld", "api"]
    },
    "infrastructure": {
        "name": "Infrastructure Design",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 4096,
        "requires": ["hld", "security"]
    },
    "state": {
        "name": "State Diagram",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 4096,
        "requires": ["hld", "api"]
    },
    "journey": {
        "name": "User Journey Map",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 4096,
        "requires": ["hld", "api"]
    },
    "sequence": {
        "name": "Sequence Diagram",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 4096,
        "requires": ["hld", "api"]
    },
    "mindmap": {
        "name": "Feature Mindmap",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 4096,
        "requires": ["hld"]
    },
    "gantt": {
        "name": "Project Timeline",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 4096,
        "requires": ["hld"]
    },
    "gitflow": {
        "name": "Git Workflow",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 4096,
        "requires": ["infrastructure"]
    },
    "wireframe": {
        "name": "Wireframes",
        "model": HAIKU_MODEL,
        "fallback_model": SONNET_MODEL,
        "max_tokens": 8192,
        "requires": ["hld", "api"]
    }
}

# Professional Mermaid styling theme for flowcharts, class, er diagrams
MERMAID_THEME = """%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#1e3a5f',
    'primaryTextColor': '#ffffff',
    'primaryBorderColor': '#3b82f6',
    'lineColor': '#60a5fa',
    'secondaryColor': '#1e293b',
    'tertiaryColor': '#0f172a',
    'background': '#0f172a',
    'mainBkg': '#1e3a5f',
    'secondBkg': '#1e293b',
    'border1': '#3b82f6',
    'border2': '#60a5fa',
    'arrowheadColor': '#60a5fa',
    'fontFamily': 'Inter, system-ui, sans-serif',
    'fontSize': '14px',
    'textColor': '#e2e8f0',
    'nodeTextColor': '#ffffff',
    'nodeBkg': '#1e3a5f',
    'nodeBorder': '#3b82f6',
    'clusterBkg': '#0f172a',
    'clusterBorder': '#475569',
    'titleColor': '#e2e8f0',
    'edgeLabelBackground': '#1e293b',
    'actorBkg': '#1e3a5f',
    'actorBorder': '#3b82f6',
    'actorTextColor': '#ffffff',
    'actorLineColor': '#60a5fa',
    'signalColor': '#60a5fa',
    'signalTextColor': '#e2e8f0',
    'labelBoxBkgColor': '#1e3a5f',
    'labelBoxBorderColor': '#3b82f6',
    'labelTextColor': '#ffffff',
    'loopTextColor': '#e2e8f0',
    'noteBorderColor': '#3b82f6',
    'noteBkgColor': '#1e3a5f',
    'noteTextColor': '#e2e8f0',
    'activationBorderColor': '#3b82f6',
    'activationBkgColor': '#1e293b',
    'sequenceNumberColor': '#ffffff',
    'sectionBkgColor': '#1e293b',
    'altSectionBkgColor': '#0f172a',
    'sectionBkgColor2': '#1e3a5f',
    'taskBorderColor': '#3b82f6',
    'taskBkgColor': '#1e3a5f',
    'taskTextColor': '#ffffff',
    'taskTextLightColor': '#e2e8f0',
    'taskTextOutsideColor': '#e2e8f0',
    'activeTaskBorderColor': '#60a5fa',
    'activeTaskBkgColor': '#3b82f6',
    'gridColor': '#475569',
    'doneTaskBkgColor': '#1e3a5f',
    'doneTaskBorderColor': '#3b82f6',
    'critBorderColor': '#f59e0b',
    'critBkgColor': '#1e3a5f',
    'todayLineColor': '#60a5fa',
    'relationColor': '#60a5fa',
    'relationLabelColor': '#e2e8f0',
    'relationLabelBackground': '#1e293b',
    'attributeBackgroundColorOdd': '#1e293b',
    'attributeBackgroundColorEven': '#0f172a'
  },
  'flowchart': {
    'nodeSpacing': 50,
    'rankSpacing': 50,
    'curve': 'basis',
    'useMaxWidth': true,
    'htmlLabels': true
  }
}}%%

"""

# Theme for Gantt diagrams (uses different CSS approach)
MERMAID_GANTT_THEME = """%%{init: {
  'theme': 'dark',
  'themeVariables': {
    'darkMode': true,
    'background': '#0f172a',
    'primaryColor': '#1e3a5f',
    'primaryTextColor': '#ffffff',
    'primaryBorderColor': '#3b82f6',
    'lineColor': '#60a5fa',
    'secondaryColor': '#1e293b',
    'tertiaryColor': '#334155',
    'textColor': '#e2e8f0',
    'gridColor': '#334155',
    'todayLineColor': '#f59e0b'
  },
  'gantt': {
    'titleTopMargin': 25,
    'barHeight': 30,
    'barGap': 8,
    'topPadding': 50,
    'leftPadding': 75,
    'gridLineStartPadding': 35,
    'fontSize': 14,
    'sectionFontSize': 16,
    'numberSectionStyles': 4,
    'useMaxWidth': true
  }
}}%%

"""

# Theme for Sequence diagrams  
MERMAID_SEQUENCE_THEME = """%%{init: {
  'theme': 'dark',
  'themeVariables': {
    'darkMode': true,
    'background': '#0f172a',
    'primaryColor': '#1e3a5f',
    'primaryTextColor': '#ffffff',
    'primaryBorderColor': '#3b82f6',
    'lineColor': '#60a5fa',
    'signalColor': '#60a5fa',
    'signalTextColor': '#e2e8f0',
    'textColor': '#e2e8f0',
    'actorBkg': '#1e3a5f',
    'actorBorder': '#3b82f6',
    'actorTextColor': '#ffffff',
    'actorLineColor': '#60a5fa',
    'noteBkgColor': '#1e293b',
    'noteBorderColor': '#3b82f6',
    'noteTextColor': '#e2e8f0',
    'activationBkgColor': '#334155',
    'activationBorderColor': '#3b82f6',
    'labelBoxBkgColor': '#1e293b',
    'labelBoxBorderColor': '#3b82f6',
    'labelTextColor': '#e2e8f0',
    'loopTextColor': '#e2e8f0'
  },
  'sequence': {
    'diagramMarginX': 50,
    'diagramMarginY': 10,
    'actorMargin': 80,
    'width': 180,
    'height': 65,
    'boxMargin': 10,
    'boxTextMargin': 5,
    'noteMargin': 10,
    'messageMargin': 40,
    'mirrorActors': true,
    'useMaxWidth': true
  }
}}%%

"""

# Theme for Journey diagrams
MERMAID_JOURNEY_THEME = """%%{init: {
  'theme': 'dark',
  'themeVariables': {
    'darkMode': true,
    'background': '#0f172a',
    'primaryColor': '#1e3a5f',
    'primaryTextColor': '#ffffff',
    'primaryBorderColor': '#3b82f6',
    'lineColor': '#60a5fa',
    'secondaryColor': '#1e293b',
    'tertiaryColor': '#334155',
    'textColor': '#e2e8f0'
  },
  'journey': {
    'diagramMarginX': 50,
    'diagramMarginY': 10,
    'leftMargin': 150,
    'width': 150,
    'height': 50,
    'boxMargin': 10,
    'boxTextMargin': 5,
    'noteMargin': 10,
    'messageMargin': 35,
    'useMaxWidth': true
  }
}}%%

"""

# Theme for GitGraph diagrams
MERMAID_GITGRAPH_THEME = """%%{init: {
  'theme': 'dark',
  'themeVariables': {
    'darkMode': true,
    'background': '#0f172a',
    'git0': '#3b82f6',
    'git1': '#22c55e',
    'git2': '#f59e0b',
    'git3': '#ec4899',
    'git4': '#8b5cf6',
    'git5': '#06b6d4',
    'git6': '#f97316',
    'git7': '#84cc16',
    'gitBranchLabel0': '#ffffff',
    'gitBranchLabel1': '#ffffff',
    'gitBranchLabel2': '#ffffff',
    'gitBranchLabel3': '#ffffff',
    'gitBranchLabel4': '#ffffff',
    'gitBranchLabel5': '#ffffff',
    'gitBranchLabel6': '#ffffff',
    'gitBranchLabel7': '#ffffff',
    'commitLabelColor': '#e2e8f0',
    'commitLabelBackground': '#1e293b',
    'commitLabelFontSize': '12px',
    'tagLabelColor': '#ffffff',
    'tagLabelBackground': '#3b82f6',
    'tagLabelBorder': '#60a5fa',
    'tagLabelFontSize': '12px'
  },
  'gitGraph': {
    'showBranches': true,
    'showCommitLabel': true,
    'mainBranchName': 'main',
    'mainBranchOrder': 0,
    'rotateCommitLabel': false,
    'parallelCommits': false
  }
}}%%

"""

# Theme for Mindmap diagrams
MERMAID_MINDMAP_THEME = """%%{init: {
  'theme': 'dark',
  'themeVariables': {
    'darkMode': true,
    'background': '#0f172a',
    'primaryColor': '#1e3a5f',
    'primaryTextColor': '#ffffff',
    'primaryBorderColor': '#3b82f6',
    'lineColor': '#60a5fa',
    'secondaryColor': '#1e293b',
    'tertiaryColor': '#334155',
    'textColor': '#e2e8f0'
  },
  'mindmap': {
    'useMaxWidth': true,
    'padding': 10
  }
}}%%

"""

def clean_diagram_styles(diagram: str) -> str:
    """Remove any classDef or style statements from the diagram to ensure theme consistency."""
    import re
    lines = diagram.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip().lower()
        # Skip classDef and style lines
        if stripped.startswith('classdef ') or stripped.startswith('style '):
            continue
        # Also skip lines with fill: or stroke: inline styles
        if ':::' in line and any(x in line.lower() for x in ['fill', 'stroke', 'color']):
            # Remove the style class reference but keep the node
            line = re.sub(r':::\w+', '', line)
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

# ============================================================================
# DESIGN PROMPT TEMPLATES
# ============================================================================

DESIGN_PROMPTS = {
    "summarize_initial": {
        "system": """You are an expert technical summarizer. Your task is to create a concise, information-dense summary of project features and stories that will be used to generate software architecture diagrams.

CRITICAL REQUIREMENTS:
- Extract key entities, actions, and relationships
- Identify core functionalities and user flows
- Note security, compliance, and performance requirements
- Keep summary under 1000 tokens
- Use bullet points for clarity
- Focus on information needed for architecture design""",
        "user_template": """Summarize the following project features and stories for architecture design:

PROJECT CONTEXT:
{project_context}

FEATURES:
{features}

STORIES:
{stories}

Create a structured summary with:
1. Core Entities (users, data objects, external systems)
2. Key Functionalities (main features and capabilities)
3. User Flows (primary user journeys)
4. Technical Requirements (security, performance, compliance)
5. Integration Points (APIs, external services)

Return ONLY the summary, no additional text."""
    },
    
    "summarize_diagram": {
        "system": """You are an expert at creating concise summaries of technical diagrams. Your summaries will be used as context for generating subsequent architecture diagrams.

REQUIREMENTS:
- Capture the key components and their relationships
- Note important architectural decisions
- Keep summary under 500 tokens
- Focus on information useful for downstream design""",
        "user_template": """Summarize the following {diagram_type} diagram for use in generating related architecture diagrams:

DIAGRAM:
{diagram}

Create a summary that captures:
1. Main components/entities
2. Key relationships and flows
3. Architectural patterns used
4. Important constraints or decisions

Return ONLY the summary text."""
    },

    "hld": {
        "system": """You are a senior software architect creating High Level Design (HLD) diagrams. Generate professional, enterprise-grade architecture diagrams using Mermaid syntax.

STYLE REQUIREMENTS:
- Use clean, professional naming conventions
- Include clear layer separation (Client, API, Service, Data)
- Show external integrations and third-party services
- Use subgraphs to group related components
- Add descriptive labels on connections
- Follow microservices or modular monolith patterns as appropriate
- DO NOT include any classDef or style definitions
- DO NOT add any color styling - the theme handles colors

OUTPUT FORMAT:
Return a valid Mermaid flowchart diagram. Use graph TB (top-bottom) or graph LR (left-right).
Do NOT include any markdown code fences. Return ONLY the Mermaid code starting with 'graph'.
Do NOT include any style or classDef statements.""",
        "user_template": """Create a High Level Design (HLD) diagram for this project:

PROJECT SUMMARY:
{summary}

Requirements:
1. Show all major system components
2. Include client applications (web, mobile, admin)
3. Show API gateway and load balancer if applicable
4. Include all backend services
5. Show databases and caching layers
6. Include external integrations (payment, auth, notifications)
7. Use subgraphs for logical grouping (Client Layer, API Layer, Service Layer, Data Layer)
8. Add meaningful labels on all connections

Generate a professional Mermaid flowchart diagram."""
    },

    "dbd": {
        "system": """You are a database architect creating Entity Relationship Diagrams (ERD). Generate professional database designs using Mermaid erDiagram syntax.

STYLE REQUIREMENTS:
- Use proper entity naming (PascalCase for entities)
- Include all relevant attributes with data types
- Show proper relationships (one-to-one, one-to-many, many-to-many)
- Include primary keys (PK) and foreign keys (FK)
- Add indexes for frequently queried fields
- Consider normalization (3NF minimum)

OUTPUT FORMAT:
Return a valid Mermaid erDiagram. Do NOT include any markdown code fences.
Return ONLY the Mermaid code starting with 'erDiagram'.""",
        "user_template": """Create a Database Design (ERD) for this project:

PROJECT SUMMARY:
{summary}

HLD CONTEXT:
{hld_summary}

Requirements:
1. Identify all entities from the features and HLD
2. Define attributes with appropriate data types (string, int, datetime, boolean, etc.)
3. Mark primary keys (PK) and foreign keys (FK)
4. Show all relationships with proper cardinality
5. Include audit fields (created_at, updated_at) where appropriate
6. Consider soft delete patterns (is_deleted, deleted_at)
7. Include status/state fields for entities with workflows

Generate a professional Mermaid erDiagram."""
    },

    "api": {
        "system": """You are an API architect creating API design and sequence diagrams. Generate professional API specifications and interaction flows using Mermaid sequenceDiagram syntax.

STYLE REQUIREMENTS:
- Use RESTful naming conventions
- Show request/response flows clearly
- Include authentication/authorization steps
- Show error handling paths
- Use proper HTTP methods (GET, POST, PUT, DELETE)
- Include relevant headers and status codes in notes

OUTPUT FORMAT:
Return a valid Mermaid sequenceDiagram. Do NOT include any markdown code fences.
Return ONLY the Mermaid code starting with 'sequenceDiagram'.""",
        "user_template": """Create an API Design with sequence diagram for this project:

PROJECT SUMMARY:
{summary}

HLD CONTEXT:
{hld_summary}

DBD CONTEXT:
{dbd_summary}

Requirements:
1. Design key API endpoints based on entities from DBD
2. Show the main user flows as sequence diagrams
3. Include authentication flow (login, token refresh)
4. Show CRUD operations for main entities
5. Include error handling and validation
6. Show interactions between services
7. Include external API calls if any

Generate a professional Mermaid sequenceDiagram showing the main API flow."""
    },

    "lld": {
        "system": """You are a senior software architect creating Low Level Design (LLD) class diagrams. 

!!! ABSOLUTE REQUIREMENT !!!
Your output MUST start with the word 'classDiagram' on line 1.
DO NOT use 'graph', 'flowchart', or any other diagram type.
This is a CLASS DIAGRAM showing classes with attributes and methods.

CRITICAL: Generate a Mermaid CLASS DIAGRAM (not flowchart). The diagram MUST show:
- Classes as rectangles with 3 sections (name, attributes, methods)
- Relationships between classes with proper arrows
- Proper OOP structure

MERMAID CLASS DIAGRAM SYNTAX:
```
classDiagram
    class ClassName {
        -privateAttribute: Type
        +publicAttribute: Type
        #protectedAttribute: Type
        +publicMethod(param: Type): ReturnType
        -privateMethod(): void
    }
    
    ClassA <|-- ClassB : inherits
    ClassA <|.. ClassB : implements
    ClassA --> ClassB : uses
    ClassA o-- ClassB : aggregation
    ClassA *-- ClassB : composition
```

REQUIRED CLASSES (generate ALL):
1. ENTITY CLASSES - One per database table:
   - User, Product, Order, etc.
   - Include all fields with types
   - Include ID fields

2. REPOSITORY INTERFACES (use <<interface>>):
   - IUserRepository, IProductRepository, etc.
   - CRUD methods: save(), findById(), findAll(), delete()

3. SERVICE INTERFACES (use <<interface>>):
   - IUserService, IProductService, etc.
   - Business methods

4. SERVICE IMPLEMENTATIONS:
   - UserService, ProductService, etc.
   - Implements service interface
   - Has repository dependency

5. CONTROLLER CLASSES:
   - UserController, ProductController, etc.
   - HTTP handler methods
   - Has service dependency

EXAMPLE OUTPUT:
classDiagram
    class User {
        -id: Long
        -email: String
        -password: String
        -createdAt: DateTime
        +getId(): Long
        +getEmail(): String
    }
    
    class IUserRepository {
        <<interface>>
        +save(user: User): User
        +findById(id: Long): User
        +findByEmail(email: String): User
        +delete(id: Long): void
    }
    
    class UserRepository {
        -database: Database
        +save(user: User): User
        +findById(id: Long): User
    }
    
    class IUserService {
        <<interface>>
        +register(dto: RegisterDTO): User
        +login(dto: LoginDTO): Token
    }
    
    class UserService {
        -userRepository: IUserRepository
        +register(dto: RegisterDTO): User
        +login(dto: LoginDTO): Token
    }
    
    class UserController {
        -userService: IUserService
        +register(request: Request): Response
        +login(request: Request): Response
    }
    
    IUserRepository <|.. UserRepository
    IUserService <|.. UserService
    UserService --> IUserRepository
    UserController --> IUserService

OUTPUT RULES:
- Start with 'classDiagram' on first line
- NO flowchart, NO graph, NO erDiagram
- Include 15-25 classes minimum
- Show ALL relationships
- Use proper class syntax with curly braces""",
        "user_template": """Create a Low Level Design (LLD) CLASS DIAGRAM.

PROJECT SUMMARY:
{summary}

HLD COMPONENTS:
{hld_summary}

DATABASE TABLES:
{dbd_summary}

API ENDPOINTS:
{api_summary}

GENERATE A MERMAID classDiagram with:
1. Entity classes for each database table (User, Product, Order, etc.)
2. Repository interfaces (IUserRepository, IProductRepository)
3. Repository implementations
4. Service interfaces (IUserService, IProductService)  
5. Service implementations with business logic
6. Controller classes for API endpoints
7. DTO classes for request/response

Show relationships:
- Interfaces implemented by concrete classes (<|..)
- Dependencies between layers (-->)
- Entity relationships (*--, o--)

Generate 15-25 classes with full attributes and methods.
Start output with 'classDiagram' - no other diagram type."""
    },

    "dfd": {
        "system": """You are a systems analyst creating Data Flow Diagrams (DFD). Generate professional DFDs using Mermaid flowchart syntax adapted for data flow.

STYLE REQUIREMENTS:
- Show external entities (users, systems) as rectangles
- Show processes as rounded rectangles  
- Show data stores as cylinders [(Database)]
- Label all data flows clearly
- Use levels (Context, Level 0, Level 1) as appropriate
- DO NOT include any classDef or style definitions
- DO NOT add any color styling - the theme handles colors
- Keep the diagram clean and professional

OUTPUT FORMAT:
Return a valid Mermaid flowchart configured as a DFD. Do NOT include any markdown code fences.
Return ONLY the Mermaid code starting with 'graph'. Do NOT include any style or classDef statements.""",
        "user_template": """Create a Data Flow Diagram (DFD) for this project:

PROJECT SUMMARY:
{summary}

HLD CONTEXT:
{hld_summary}

DBD CONTEXT:
{dbd_summary}

Requirements:
1. Show all external entities (users, external systems)
2. Show main processes that transform data
3. Show data stores (databases, caches, file systems)
4. Label all data flows with what data is being transferred
5. Show the complete data lifecycle
6. Include both input and output flows

Generate a professional Mermaid flowchart as a DFD."""
    },

    "component": {
        "system": """You are a software architect creating Component Diagrams. Generate professional component diagrams using Mermaid flowchart syntax.

STYLE REQUIREMENTS:
- Show components as distinct modules
- Include interfaces (provided and required)
- Show dependencies between components
- Group components by layer or domain using subgraphs
- Include external packages/libraries
- DO NOT include any classDef or style definitions
- DO NOT add any color styling - the theme handles colors

OUTPUT FORMAT:
Return a valid Mermaid flowchart configured as a component diagram. Do NOT include any markdown code fences.
Return ONLY the Mermaid code starting with 'graph'. Do NOT include any style or classDef statements.""",
        "user_template": """Create a Component Diagram for this project:

PROJECT SUMMARY:
{summary}

HLD CONTEXT:
{hld_summary}

LLD CONTEXT:
{lld_summary}

Requirements:
1. Show all major components/modules
2. Show interfaces between components
3. Show external dependencies (libraries, frameworks)
4. Group by domain or layer
5. Show component interactions
6. Include shared/common components

Generate a professional Mermaid component diagram."""
    },

    "security": {
        "system": """You are a security architect creating Security Architecture diagrams. Generate professional security diagrams using Mermaid flowchart syntax.

STYLE REQUIREMENTS:
- Show security boundaries and zones using subgraphs
- Include authentication and authorization flows
- Show encryption points (at rest, in transit)
- Include security controls and monitoring
- Show threat vectors and mitigations
- DO NOT include any classDef or style definitions
- DO NOT add any color styling - the theme handles colors

OUTPUT FORMAT:
Return a valid Mermaid flowchart. Do NOT include any markdown code fences.
Return ONLY the Mermaid code starting with 'graph'. Do NOT include any style or classDef statements.""",
        "user_template": """Create a Security Architecture diagram for this project:

PROJECT SUMMARY:
{summary}

HLD CONTEXT:
{hld_summary}

API CONTEXT:
{api_summary}

Requirements:
1. Show security zones (public, DMZ, private, data)
2. Show authentication flow (OAuth, JWT, sessions)
3. Show authorization mechanisms (RBAC, ABAC)
4. Include encryption (TLS, database encryption)
5. Show security monitoring and logging
6. Include WAF, rate limiting, DDoS protection
7. Show secrets management

Generate a professional Mermaid security architecture diagram."""
    },

    "infrastructure": {
        "system": """You are a DevOps/Cloud architect creating Infrastructure diagrams. Generate professional infrastructure designs using Mermaid flowchart syntax.

STYLE REQUIREMENTS:
- Show cloud provider resources (AWS/GCP/Azure style)
- Include networking (VPC, subnets, load balancers)
- Show compute resources (containers, VMs, serverless)
- Include storage solutions
- Show CI/CD pipeline elements
- Include monitoring and logging infrastructure
- DO NOT include any classDef or style definitions
- DO NOT add any color styling - the theme handles colors

OUTPUT FORMAT:
Return a valid Mermaid flowchart for infrastructure. Do NOT include any markdown code fences.
Return ONLY the Mermaid code starting with 'graph'. Do NOT include any style or classDef statements.""",
        "user_template": """Create an Infrastructure Design diagram for this project:

PROJECT SUMMARY:
{summary}

HLD CONTEXT:
{hld_summary}

SECURITY CONTEXT:
{security_summary}

Requirements:
1. Show cloud infrastructure (VPC, subnets, availability zones)
2. Show compute resources (ECS/EKS, Lambda, EC2)
3. Show database infrastructure (RDS, DynamoDB, Redis)
4. Show load balancing and CDN
5. Show CI/CD pipeline
6. Show monitoring stack (CloudWatch, Prometheus, Grafana)
7. Show backup and disaster recovery

Generate a professional Mermaid infrastructure diagram."""
    },

    "state": {
        "system": """You are a systems analyst creating State Diagrams. Generate professional state machine diagrams using Mermaid stateDiagram-v2 syntax.

STYLE REQUIREMENTS:
- Show all states clearly
- Include transitions with events/triggers
- Show guards/conditions on transitions
- Include entry/exit actions where relevant
- Show composite states if needed

OUTPUT FORMAT:
Return a valid Mermaid stateDiagram-v2. Do NOT include any markdown code fences.
Return ONLY the Mermaid code starting with 'stateDiagram-v2'.""",
        "user_template": """Create State Diagrams for key entities in this project:

PROJECT SUMMARY:
{summary}

HLD CONTEXT:
{hld_summary}

API CONTEXT:
{api_summary}

Requirements:
1. Identify entities with state workflows (orders, users, payments, etc.)
2. Show all possible states for each entity
3. Show transitions between states
4. Include events that trigger transitions
5. Show guards/conditions
6. Include initial and final states

Generate a professional Mermaid stateDiagram-v2 for the main entity workflow."""
    },

    "journey": {
        "system": """You are a UX designer creating User Journey Maps. Generate professional user journey diagrams using Mermaid journey syntax.

STYLE REQUIREMENTS:
- Show user tasks and actions
- Include satisfaction scores (1-5 scale)
- Group tasks by sections/phases
- Show the complete user flow
- Focus on key user personas

OUTPUT FORMAT:
Return a valid Mermaid journey diagram. Do NOT include any markdown code fences.
Return ONLY the Mermaid code starting with 'journey'.""",
        "user_template": """Create a User Journey Map for this project:

PROJECT SUMMARY:
{summary}

HLD CONTEXT:
{hld_summary}

API CONTEXT:
{api_summary}

Requirements:
1. Identify the main user persona
2. Map out the complete user journey from start to finish
3. Include all major touchpoints
4. Rate satisfaction for each step (1-5 scale)
5. Group tasks by logical sections (e.g., Onboarding, Main Actions, Completion)
6. Include at least 8-12 meaningful tasks

Generate a professional Mermaid journey diagram."""
    },

    "sequence": {
        "system": """You are a software architect creating Sequence Diagrams. Generate professional sequence diagrams using Mermaid sequenceDiagram syntax.

CRITICAL SYNTAX RULES - FOLLOW EXACTLY:
1. Start with 'sequenceDiagram' on its own line
2. Define participants with: participant Name or actor Name
3. Use SIMPLE participant names (no spaces, underscores OK): User, API, Database, AuthService
4. Arrow syntax: A->>B: message or A-->>B: response
5. Messages must be SHORT and SIMPLE (no special chars like = or parentheses)
6. Use activate/deactivate for activation boxes
7. Use alt/else/end for conditionals
8. Use loop/end for loops
9. Use Note right of A: text for notes

INVALID - DO NOT USE:
- Complex message text with code (message_id=123)
- Parentheses in messages
- Special characters in participant names
- Long multi-line messages

VALID EXAMPLE:
sequenceDiagram
    participant User
    participant API
    participant DB
    
    User->>API: Login request
    activate API
    API->>DB: Check credentials
    DB-->>API: User data
    API-->>User: JWT token
    deactivate API

OUTPUT FORMAT:
Return ONLY valid Mermaid sequenceDiagram code.
Do NOT include code fences, explanations, or init blocks.""",
        "user_template": """Create a Sequence Diagram for the PRIMARY user flow:

PROJECT SUMMARY:
{summary}

HLD CONTEXT:
{hld_summary}

API CONTEXT:
{api_summary}

Requirements:
1. Show 4-6 participants max (User, Frontend, API, Service, Database)
2. Use SIMPLE short names for participants
3. Keep message labels SHORT (3-5 words max)
4. Show the main happy path flow
5. Include one alt block for error handling
6. Limit to 20-30 interactions max

Generate a clean, simple Mermaid sequenceDiagram."""
    },

    "mindmap": {
        "system": """You are a product strategist creating Feature Mindmaps. Generate professional mindmap diagrams using Mermaid mindmap syntax.

STYLE REQUIREMENTS:
- Use clear hierarchical structure
- Group features by category
- Keep node labels concise
- Use proper indentation for hierarchy
- Include all major feature areas

OUTPUT FORMAT:
Return a valid Mermaid mindmap. Do NOT include any markdown code fences.
Return ONLY the Mermaid code starting with 'mindmap'.""",
        "user_template": """Create a Feature Mindmap for this project:

PROJECT SUMMARY:
{summary}

HLD CONTEXT:
{hld_summary}

Requirements:
1. Put the project name at the center
2. Create main branches for feature categories
3. Add sub-branches for specific features
4. Include technical capabilities
5. Group logically (User Features, Admin Features, Integrations, etc.)
6. Keep labels short and clear

Generate a professional Mermaid mindmap."""
    },

    "gantt": {
        "system": """You are a project manager creating Project Timelines. Generate professional Gantt charts using Mermaid gantt syntax.

CRITICAL SYNTAX RULES - FOLLOW EXACTLY:
1. Start with 'gantt' on line 1
2. Use 'dateFormat YYYY-MM-DD' on line 2
3. Use 'title Project Timeline' on line 3
4. Use 'excludes weekends' (optional)
5. Group tasks with 'section SectionName'
6. Task syntax: TaskName :taskId, startDate, duration
7. Duration format: 1d, 2d, 3d, 1w, 2w (days or weeks)
8. For dependencies use 'after taskId' instead of date

VALID DURATION FORMATS:
- Use 'd' for days: 1d, 2d, 3d, 5d
- Use 'w' for weeks: 1w, 2w
- DO NOT use 'day' or 'days' - only 'd'
- DO NOT use 'week' or 'weeks' - only 'w'

CORRECT SYNTAX EXAMPLE:
gantt
    dateFormat YYYY-MM-DD
    title Development Timeline
    excludes weekends
    
    section Planning
    Requirements Analysis    :req, 2024-01-01, 5d
    Technical Design         :design, after req, 3d
    
    section Development
    Backend API              :backend, after design, 10d
    Frontend UI              :frontend, after design, 12d
    
    section Testing
    Integration Testing      :testing, after backend, 5d
    
    section Deployment
    Production Release       :release, after testing, 2d

AVOID THESE ERRORS:
- NO 'done' or 'active' or 'crit' task modifiers
- NO milestone keyword
- NO complex date calculations
- NO parentheses in task names
- Keep task names simple (no special characters)

OUTPUT FORMAT:
Return ONLY valid Mermaid gantt code starting with 'gantt'.
Do NOT include code fences or explanatory text.""",
        "user_template": """Create a Project Timeline/Gantt chart for this project:

PROJECT SUMMARY:
{summary}

HLD CONTEXT:
{hld_summary}

Requirements:
1. Break down into phases: Planning, Development, Testing, Deployment
2. Use simple duration format: 1d, 2d, 5d, 1w, 2w (d=days, w=weeks)
3. Use 'after taskId' for task dependencies
4. Keep task names simple without special characters
5. Include 5-15 realistic tasks

Generate a professional Mermaid gantt chart."""
    },

    "gitflow": {
        "system": """You are a DevOps engineer creating Git Workflow diagrams. Generate professional git graphs using Mermaid gitGraph syntax.

CRITICAL SYNTAX RULES - FOLLOW EXACTLY:
1. Start with 'gitGraph' on its own line (no options block - theme is added separately)
2. Use 'commit' for commits (optionally with id: "message")
3. Use 'branch branchName' to create branches
4. Use 'checkout branchName' to switch branches
5. Use 'merge branchName' to merge branches
6. Do NOT use 'tag' command - it often causes errors
7. Keep commit messages short (under 30 chars)
8. Branch names should be simple: develop, feature-auth, release-1, hotfix-bug

CORRECT SYNTAX EXAMPLE:
gitGraph
    commit id: "initial"
    branch develop
    checkout develop
    commit id: "setup"
    branch feature-auth
    checkout feature-auth
    commit id: "add-login"
    commit id: "add-logout"
    checkout develop
    merge feature-auth
    branch release-1
    checkout release-1
    commit id: "version-1"
    checkout main
    merge release-1

OUTPUT FORMAT:
Return ONLY valid Mermaid gitGraph code starting with 'gitGraph'.
Do NOT include code fences, init blocks, or explanatory text.""",
        "user_template": """Create a Git Workflow diagram for this project:

PROJECT SUMMARY:
{summary}

INFRASTRUCTURE CONTEXT:
{infrastructure_summary}

Generate a Mermaid gitGraph showing:
1. main branch with initial commit
2. develop branch created from main
3. 2-3 feature branches (feature-xxx) with work and merges
4. A release branch workflow
5. A hotfix branch if applicable

Keep it simple and ensure valid syntax. Use simple branch names without special characters."""
    },

    "wireframe": {
        "system": """You are a UI/UX designer creating wireframes. Generate professional, responsive HTML/CSS wireframes using Tailwind CSS classes.

STYLE REQUIREMENTS:
- Use a dark theme matching the application design (#0f172a, #1e293b, #3b82f6)
- Create responsive layouts (mobile-first)
- Include navigation, headers, and footers
- Show form elements, buttons, cards
- Use modern UI patterns
- Include placeholder content

OUTPUT FORMAT:
Return valid HTML with inline Tailwind CSS classes. Include a complete page layout.
Return ONLY the HTML code starting with <!DOCTYPE html> or <div>.""",
        "user_template": """Create UI wireframes for this project:

PROJECT SUMMARY:
{summary}

HLD CONTEXT:
{hld_summary}

API CONTEXT:
{api_summary}

Requirements:
1. Create wireframe for the main dashboard
2. Include navigation (sidebar or top nav)
3. Show key data displays (cards, tables, charts placeholders)
4. Include form examples for main entities
5. Use the dark theme (#0f172a background, #3b82f6 accent)
6. Make it responsive
7. Include common UI elements (buttons, inputs, modals)

Generate a professional HTML wireframe with Tailwind CSS."""
    }
}

# ============================================================================
# REQUEST/RESPONSE MODELS FOR DESIGNS
# ============================================================================

class DesignRequest(BaseModel):
    project_summary: str
    features_summary: Optional[str] = ""
    stories_summary: Optional[str] = ""
    hld_summary: Optional[str] = ""
    dbd_summary: Optional[str] = ""
    api_summary: Optional[str] = ""
    lld_summary: Optional[str] = ""
    dfd_summary: Optional[str] = ""
    component_summary: Optional[str] = ""
    security_summary: Optional[str] = ""
    infrastructure_summary: Optional[str] = ""
    state_summary: Optional[str] = ""
    journey_summary: Optional[str] = ""
    sequence_summary: Optional[str] = ""
    mindmap_summary: Optional[str] = ""
    gantt_summary: Optional[str] = ""
    gitflow_summary: Optional[str] = ""

class SummarizeRequest(BaseModel):
    project_context: str
    features: list[dict]
    stories: list[dict]

class SummarizeDiagramRequest(BaseModel):
    diagram_type: str
    diagram: str

class DesignResponse(BaseModel):
    design_type: str
    diagram: str
    summary: str
    status: str
    tokens_used: Optional[dict] = None

class GenerateAllRequest(BaseModel):
    project_context: str
    features: list[dict]
    stories: list[dict]

class GenerateAllResponse(BaseModel):
    designs: dict
    summaries: dict
    status: str
    total_tokens: dict

# ============================================================================
# DESIGN GENERATION ENDPOINTS
# ============================================================================

@app.post("/api/designs/summarize")
async def summarize_project(request: SummarizeRequest):
    """Summarize features and stories for design generation"""
    try:
        print(f"[DEBUG] Summarizing project - Features: {len(request.features)}, Stories: {len(request.stories)}")
        
        # Format features and stories for the prompt
        features_text = "\n".join([
            f"- {f.get('title', 'Unknown')}: {f.get('reason', '')} | {f.get('detailedDescription', '')}"
            for f in request.features
        ])
        
        stories_text = "\n".join([
            f"- [{s.get('featureRef', 'Unknown')}] {s.get('title', '')}: {s.get('description', '')}"
            for s in request.stories
        ])
        
        prompt_config = DESIGN_PROMPTS["summarize_initial"]
        user_prompt = prompt_config["user_template"].format(
            project_context=request.project_context,
            features=features_text,
            stories=stories_text
        )
        
        print(f"[DEBUG] Calling Claude for summarization...")
        summary = await call_claude_with_retry(
            model=HAIKU_MODEL,
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            max_tokens=2048,
            max_retries=5,
            fallback_model=SONNET_MODEL
        )
        
        print(f"[DEBUG] Summary generated, length: {len(summary)}")
        
        return {
            "summary": summary,
            "status": "success"
        }
        
    except Exception as e:
        print(f"[ERROR] Summarization failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@app.post("/api/designs/summarize-diagram")
async def summarize_diagram(request: SummarizeDiagramRequest):
    """Summarize a generated diagram for use in subsequent designs"""
    try:
        print(f"[DEBUG] Summarizing {request.diagram_type} diagram...")
        
        prompt_config = DESIGN_PROMPTS["summarize_diagram"]
        user_prompt = prompt_config["user_template"].format(
            diagram_type=request.diagram_type,
            diagram=request.diagram
        )
        
        summary = await call_claude_with_retry(
            model=HAIKU_MODEL,
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            max_tokens=1024,
            max_retries=5,
            fallback_model=SONNET_MODEL
        )
        
        print(f"[DEBUG] Diagram summary generated, length: {len(summary)}")
        
        return {
            "diagram_type": request.diagram_type,
            "summary": summary,
            "status": "success"
        }
        
    except Exception as e:
        print(f"[ERROR] Diagram summarization failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Diagram summarization failed: {str(e)}")


@app.post("/api/designs/hld", response_model=DesignResponse)
async def generate_hld(request: DesignRequest):
    """Generate High Level Design diagram"""
    try:
        print(f"[DEBUG] Generating HLD...")
        
        prompt_config = DESIGN_PROMPTS["hld"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary
        )
        
        diagram = await generate_mermaid_with_validation(
            model=DESIGN_CONFIG["hld"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            diagram_type="hld",
            max_tokens=DESIGN_CONFIG["hld"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["hld"].get("fallback_model")
        )
        
        # Clean any custom styles and add professional theme
        diagram = clean_diagram_styles(diagram)
        if not diagram.startswith("%%{init"):
            diagram = MERMAID_THEME + diagram
        
        print(f"[DEBUG] HLD generated, length: {len(diagram)}")
        
        # Generate summary using separate summarizer
        summary_response = await summarize_diagram(SummarizeDiagramRequest(
            diagram_type="HLD",
            diagram=diagram
        ))
        
        return DesignResponse(
            design_type="hld",
            diagram=diagram,
            summary=summary_response["summary"],
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] HLD generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"HLD generation failed: {str(e)}")


@app.post("/api/designs/dbd", response_model=DesignResponse)
async def generate_dbd(request: DesignRequest):
    """Generate Database Design (ERD) diagram"""
    try:
        print(f"[DEBUG] Generating DBD...")
        
        if not request.hld_summary:
            raise HTTPException(status_code=400, detail="HLD summary is required for DBD generation")
        
        prompt_config = DESIGN_PROMPTS["dbd"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary,
            hld_summary=request.hld_summary
        )
        
        diagram = await generate_mermaid_with_validation(
            model=DESIGN_CONFIG["dbd"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            diagram_type="dbd",
            max_tokens=DESIGN_CONFIG["dbd"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["dbd"].get("fallback_model")
        )
        
        print(f"[DEBUG] DBD generated, length: {len(diagram)}")
        
        # Generate summary
        summary_response = await summarize_diagram(SummarizeDiagramRequest(
            diagram_type="DBD",
            diagram=diagram
        ))
        
        return DesignResponse(
            design_type="dbd",
            diagram=diagram,
            summary=summary_response["summary"],
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] DBD generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"DBD generation failed: {str(e)}")


@app.post("/api/designs/api", response_model=DesignResponse)
async def generate_api_design(request: DesignRequest):
    """Generate API Design with sequence diagram"""
    try:
        print(f"[DEBUG] Generating API Design...")
        
        if not request.hld_summary or not request.dbd_summary:
            raise HTTPException(status_code=400, detail="HLD and DBD summaries are required for API generation")
        
        prompt_config = DESIGN_PROMPTS["api"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary,
            hld_summary=request.hld_summary,
            dbd_summary=request.dbd_summary
        )
        
        diagram = await generate_mermaid_with_validation(
            model=DESIGN_CONFIG["api"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            diagram_type="api",
            max_tokens=DESIGN_CONFIG["api"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["api"].get("fallback_model")
        )
        
        print(f"[DEBUG] API Design generated, length: {len(diagram)}")
        
        # Generate summary
        summary_response = await summarize_diagram(SummarizeDiagramRequest(
            diagram_type="API",
            diagram=diagram
        ))
        
        return DesignResponse(
            design_type="api",
            diagram=diagram,
            summary=summary_response["summary"],
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] API generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"API generation failed: {str(e)}")


@app.post("/api/designs/lld", response_model=DesignResponse)
async def generate_lld(request: DesignRequest):
    """Generate Low Level Design (Class Diagram)"""
    try:
        print(f"[DEBUG] Generating LLD...")
        
        if not request.hld_summary or not request.dbd_summary or not request.api_summary:
            raise HTTPException(status_code=400, detail="HLD, DBD, and API summaries are required for LLD generation")
        
        prompt_config = DESIGN_PROMPTS["lld"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary,
            hld_summary=request.hld_summary,
            dbd_summary=request.dbd_summary,
            api_summary=request.api_summary
        )
        
        diagram = await generate_mermaid_with_validation(
            model=DESIGN_CONFIG["lld"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            diagram_type="lld",
            max_tokens=DESIGN_CONFIG["lld"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["lld"].get("fallback_model")
        )
        
        print(f"[DEBUG] LLD generated, length: {len(diagram)}")
        
        # Generate summary
        summary_response = await summarize_diagram(SummarizeDiagramRequest(
            diagram_type="LLD",
            diagram=diagram
        ))
        
        return DesignResponse(
            design_type="lld",
            diagram=diagram,
            summary=summary_response["summary"],
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] LLD generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"LLD generation failed: {str(e)}")


@app.post("/api/designs/dfd", response_model=DesignResponse)
async def generate_dfd(request: DesignRequest):
    """Generate Data Flow Diagram"""
    try:
        print(f"[DEBUG] Generating DFD...")
        
        if not request.hld_summary or not request.dbd_summary:
            raise HTTPException(status_code=400, detail="HLD and DBD summaries are required for DFD generation")
        
        prompt_config = DESIGN_PROMPTS["dfd"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary,
            hld_summary=request.hld_summary,
            dbd_summary=request.dbd_summary
        )
        
        diagram = await generate_mermaid_with_validation(
            model=DESIGN_CONFIG["dfd"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            diagram_type="dfd",
            max_tokens=DESIGN_CONFIG["dfd"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["dfd"].get("fallback_model")
        )
        
        print(f"[DEBUG] DFD generated, length: {len(diagram)}")
        
        # Generate summary
        summary_response = await summarize_diagram(SummarizeDiagramRequest(
            diagram_type="DFD",
            diagram=diagram
        ))
        
        return DesignResponse(
            design_type="dfd",
            diagram=diagram,
            summary=summary_response["summary"],
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] DFD generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"DFD generation failed: {str(e)}")


@app.post("/api/designs/component", response_model=DesignResponse)
async def generate_component(request: DesignRequest):
    """Generate Component Diagram"""
    try:
        print(f"[DEBUG] Generating Component Diagram...")
        
        if not request.hld_summary or not request.lld_summary:
            raise HTTPException(status_code=400, detail="HLD and LLD summaries are required for Component diagram generation")
        
        prompt_config = DESIGN_PROMPTS["component"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary,
            hld_summary=request.hld_summary,
            lld_summary=request.lld_summary
        )
        
        diagram = await generate_mermaid_with_validation(
            model=DESIGN_CONFIG["component"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            diagram_type="component",
            max_tokens=DESIGN_CONFIG["component"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["component"].get("fallback_model")
        )
        
        print(f"[DEBUG] Component Diagram generated, length: {len(diagram)}")
        
        # Generate summary
        summary_response = await summarize_diagram(SummarizeDiagramRequest(
            diagram_type="Component",
            diagram=diagram
        ))
        
        return DesignResponse(
            design_type="component",
            diagram=diagram,
            summary=summary_response["summary"],
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] Component diagram generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Component diagram generation failed: {str(e)}")


@app.post("/api/designs/security", response_model=DesignResponse)
async def generate_security(request: DesignRequest):
    """Generate Security Architecture Diagram"""
    try:
        print(f"[DEBUG] Generating Security Architecture...")
        
        if not request.hld_summary or not request.api_summary:
            raise HTTPException(status_code=400, detail="HLD and API summaries are required for Security architecture generation")
        
        prompt_config = DESIGN_PROMPTS["security"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary,
            hld_summary=request.hld_summary,
            api_summary=request.api_summary
        )
        
        diagram = await generate_mermaid_with_validation(
            model=DESIGN_CONFIG["security"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            diagram_type="security",
            max_tokens=DESIGN_CONFIG["security"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["security"].get("fallback_model")
        )
        
        print(f"[DEBUG] Security Architecture generated, length: {len(diagram)}")
        
        # Generate summary
        summary_response = await summarize_diagram(SummarizeDiagramRequest(
            diagram_type="Security",
            diagram=diagram
        ))
        
        return DesignResponse(
            design_type="security",
            diagram=diagram,
            summary=summary_response["summary"],
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] Security architecture generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Security architecture generation failed: {str(e)}")


@app.post("/api/designs/infrastructure", response_model=DesignResponse)
async def generate_infrastructure(request: DesignRequest):
    """Generate Infrastructure Design Diagram"""
    try:
        print(f"[DEBUG] Generating Infrastructure Design...")
        
        if not request.hld_summary or not request.security_summary:
            raise HTTPException(status_code=400, detail="HLD and Security summaries are required for Infrastructure design generation")
        
        prompt_config = DESIGN_PROMPTS["infrastructure"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary,
            hld_summary=request.hld_summary,
            security_summary=request.security_summary
        )
        
        diagram = await generate_mermaid_with_validation(
            model=DESIGN_CONFIG["infrastructure"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            diagram_type="infrastructure",
            max_tokens=DESIGN_CONFIG["infrastructure"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["infrastructure"].get("fallback_model")
        )
        
        print(f"[DEBUG] Infrastructure Design generated, length: {len(diagram)}")
        
        # Generate summary
        summary_response = await summarize_diagram(SummarizeDiagramRequest(
            diagram_type="Infrastructure",
            diagram=diagram
        ))
        
        return DesignResponse(
            design_type="infrastructure",
            diagram=diagram,
            summary=summary_response["summary"],
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] Infrastructure design generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Infrastructure design generation failed: {str(e)}")


@app.post("/api/designs/state", response_model=DesignResponse)
async def generate_state(request: DesignRequest):
    """Generate State Diagram"""
    try:
        print(f"[DEBUG] Generating State Diagram...")
        
        if not request.hld_summary or not request.api_summary:
            raise HTTPException(status_code=400, detail="HLD and API summaries are required for State diagram generation")
        
        prompt_config = DESIGN_PROMPTS["state"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary,
            hld_summary=request.hld_summary,
            api_summary=request.api_summary
        )
        
        diagram = await generate_mermaid_with_validation(
            model=DESIGN_CONFIG["state"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            diagram_type="state",
            max_tokens=DESIGN_CONFIG["state"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["state"].get("fallback_model")
        )
        
        print(f"[DEBUG] State Diagram generated, length: {len(diagram)}")
        
        # Generate summary
        summary_response = await summarize_diagram(SummarizeDiagramRequest(
            diagram_type="State",
            diagram=diagram
        ))
        
        return DesignResponse(
            design_type="state",
            diagram=diagram,
            summary=summary_response["summary"],
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] State diagram generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"State diagram generation failed: {str(e)}")


@app.post("/api/designs/journey", response_model=DesignResponse)
async def generate_journey(request: DesignRequest):
    """Generate User Journey Map"""
    try:
        print(f"[DEBUG] Generating User Journey Map...")
        
        if not request.hld_summary or not request.api_summary:
            raise HTTPException(status_code=400, detail="HLD and API summaries are required for Journey map generation")
        
        prompt_config = DESIGN_PROMPTS["journey"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary,
            hld_summary=request.hld_summary,
            api_summary=request.api_summary
        )
        
        diagram = await generate_mermaid_with_validation(
            model=DESIGN_CONFIG["journey"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            diagram_type="journey",
            max_tokens=DESIGN_CONFIG["journey"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["journey"].get("fallback_model")
        )
        
        print(f"[DEBUG] Journey Map generated, length: {len(diagram)}")
        
        # Generate summary
        summary_response = await summarize_diagram(SummarizeDiagramRequest(
            diagram_type="User Journey",
            diagram=diagram
        ))
        
        return DesignResponse(
            design_type="journey",
            diagram=diagram,
            summary=summary_response["summary"],
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] Journey map generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Journey map generation failed: {str(e)}")


@app.post("/api/designs/sequence", response_model=DesignResponse)
async def generate_sequence(request: DesignRequest):
    """Generate Sequence Diagram"""
    try:
        print(f"[DEBUG] Generating Sequence Diagram...")
        
        if not request.hld_summary or not request.api_summary:
            raise HTTPException(status_code=400, detail="HLD and API summaries are required for Sequence diagram generation")
        
        prompt_config = DESIGN_PROMPTS["sequence"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary,
            hld_summary=request.hld_summary,
            api_summary=request.api_summary
        )
        
        diagram = await generate_mermaid_with_validation(
            model=DESIGN_CONFIG["sequence"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            diagram_type="sequence",
            max_tokens=DESIGN_CONFIG["sequence"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["sequence"].get("fallback_model")
        )
        
        print(f"[DEBUG] Sequence Diagram generated, length: {len(diagram)}")
        
        # Generate summary
        summary_response = await summarize_diagram(SummarizeDiagramRequest(
            diagram_type="Sequence",
            diagram=diagram
        ))
        
        return DesignResponse(
            design_type="sequence",
            diagram=diagram,
            summary=summary_response["summary"],
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] Sequence diagram generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Sequence diagram generation failed: {str(e)}")


@app.post("/api/designs/mindmap", response_model=DesignResponse)
async def generate_mindmap(request: DesignRequest):
    """Generate Feature Mindmap"""
    try:
        print(f"[DEBUG] Generating Feature Mindmap...")
        
        if not request.hld_summary:
            raise HTTPException(status_code=400, detail="HLD summary is required for Mindmap generation")
        
        prompt_config = DESIGN_PROMPTS["mindmap"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary,
            hld_summary=request.hld_summary
        )
        
        diagram = await generate_mermaid_with_validation(
            model=DESIGN_CONFIG["mindmap"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            diagram_type="mindmap",
            max_tokens=DESIGN_CONFIG["mindmap"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["mindmap"].get("fallback_model")
        )
        
        print(f"[DEBUG] Mindmap generated, length: {len(diagram)}")
        
        # Generate summary
        summary_response = await summarize_diagram(SummarizeDiagramRequest(
            diagram_type="Feature Mindmap",
            diagram=diagram
        ))
        
        return DesignResponse(
            design_type="mindmap",
            diagram=diagram,
            summary=summary_response["summary"],
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] Mindmap generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Mindmap generation failed: {str(e)}")


@app.post("/api/designs/gantt", response_model=DesignResponse)
async def generate_gantt(request: DesignRequest):
    """Generate Project Timeline (Gantt Chart)"""
    try:
        print(f"[DEBUG] Generating Project Timeline...")
        
        if not request.hld_summary:
            raise HTTPException(status_code=400, detail="HLD summary is required for Gantt chart generation")
        
        prompt_config = DESIGN_PROMPTS["gantt"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary,
            hld_summary=request.hld_summary
        )
        
        diagram = await generate_mermaid_with_validation(
            model=DESIGN_CONFIG["gantt"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            diagram_type="gantt",
            max_tokens=DESIGN_CONFIG["gantt"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["gantt"].get("fallback_model")
        )
        
        print(f"[DEBUG] Gantt chart generated, length: {len(diagram)}")
        
        # Generate summary
        summary_response = await summarize_diagram(SummarizeDiagramRequest(
            diagram_type="Project Timeline",
            diagram=diagram
        ))
        
        return DesignResponse(
            design_type="gantt",
            diagram=diagram,
            summary=summary_response["summary"],
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] Gantt chart generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Gantt chart generation failed: {str(e)}")


@app.post("/api/designs/gitflow", response_model=DesignResponse)
async def generate_gitflow(request: DesignRequest):
    """Generate Git Workflow Diagram"""
    try:
        print(f"[DEBUG] Generating Git Workflow...")
        
        if not request.infrastructure_summary:
            raise HTTPException(status_code=400, detail="Infrastructure summary is required for Git workflow generation")
        
        prompt_config = DESIGN_PROMPTS["gitflow"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary,
            infrastructure_summary=request.infrastructure_summary
        )
        
        diagram = await generate_mermaid_with_validation(
            model=DESIGN_CONFIG["gitflow"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            diagram_type="gitflow",
            max_tokens=DESIGN_CONFIG["gitflow"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["gitflow"].get("fallback_model")
        )
        
        print(f"[DEBUG] Git workflow generated, length: {len(diagram)}")
        
        # Generate summary
        summary_response = await summarize_diagram(SummarizeDiagramRequest(
            diagram_type="Git Workflow",
            diagram=diagram
        ))
        
        return DesignResponse(
            design_type="gitflow",
            diagram=diagram,
            summary=summary_response["summary"],
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] Git workflow generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Git workflow generation failed: {str(e)}")


@app.post("/api/designs/wireframe", response_model=DesignResponse)
async def generate_wireframe(request: DesignRequest):
    """Generate UI Wireframes"""
    try:
        print(f"[DEBUG] Generating Wireframes...")
        
        if not request.hld_summary or not request.api_summary:
            raise HTTPException(status_code=400, detail="HLD and API summaries are required for Wireframe generation")
        
        prompt_config = DESIGN_PROMPTS["wireframe"]
        user_prompt = prompt_config["user_template"].format(
            summary=request.project_summary,
            hld_summary=request.hld_summary,
            api_summary=request.api_summary
        )
        
        wireframe = await call_claude_with_retry(
            model=DESIGN_CONFIG["wireframe"]["model"],
            system_prompt=prompt_config["system"],
            user_prompt=user_prompt,
            max_tokens=DESIGN_CONFIG["wireframe"]["max_tokens"],
            max_retries=5,
            fallback_model=DESIGN_CONFIG["wireframe"].get("fallback_model")
        )
        
        # Clean up wireframe - DON'T add Mermaid theme since wireframes are HTML
        wireframe = wireframe.strip()
        if wireframe.startswith("```html"):
            wireframe = wireframe[7:]  # Remove ```html
        elif wireframe.startswith("```"):
            wireframe = wireframe.split("\n", 1)[1]
        if wireframe.endswith("```"):
            wireframe = wireframe.rsplit("```", 1)[0]
        wireframe = wireframe.strip()
        
        # DO NOT add MERMAID_THEME to wireframes - they are HTML, not Mermaid!
        
        print(f"[DEBUG] Wireframe generated, length: {len(wireframe)}")
        
        return DesignResponse(
            design_type="wireframe",
            diagram=wireframe,
            summary="UI Wireframe with responsive layout and dark theme",
            status="success"
        )
        
    except Exception as e:
        print(f"[ERROR] Wireframe generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Wireframe generation failed: {str(e)}")


@app.post("/api/designs/generate-all", response_model=GenerateAllResponse)
async def generate_all_designs(request: GenerateAllRequest):
    """Generate all designs sequentially with proper context chaining"""
    try:
        print(f"[DEBUG] Starting full design generation chain...")
        
        designs = {}
        summaries = {}
        
        # Step 1: Summarize features and stories
        print(f"[CHAIN] Step 1/11: Summarizing project...")
        summary_result = await summarize_project(SummarizeRequest(
            project_context=request.project_context,
            features=request.features,
            stories=request.stories
        ))
        summaries["project"] = summary_result["summary"]
        project_summary = summary_result["summary"]
        
        # Step 2: Generate HLD
        print(f"[CHAIN] Step 2/11: Generating HLD...")
        hld_result = await generate_hld(DesignRequest(project_summary=project_summary))
        designs["hld"] = hld_result.diagram
        summaries["hld"] = hld_result.summary
        
        # Step 3: Generate DBD
        print(f"[CHAIN] Step 3/11: Generating DBD...")
        dbd_result = await generate_dbd(DesignRequest(
            project_summary=project_summary,
            hld_summary=summaries["hld"]
        ))
        designs["dbd"] = dbd_result.diagram
        summaries["dbd"] = dbd_result.summary
        
        # Step 4: Generate API
        print(f"[CHAIN] Step 4/11: Generating API Design...")
        api_result = await generate_api_design(DesignRequest(
            project_summary=project_summary,
            hld_summary=summaries["hld"],
            dbd_summary=summaries["dbd"]
        ))
        designs["api"] = api_result.diagram
        summaries["api"] = api_result.summary
        
        # Step 5: Generate LLD
        print(f"[CHAIN] Step 5/11: Generating LLD...")
        lld_result = await generate_lld(DesignRequest(
            project_summary=project_summary,
            hld_summary=summaries["hld"],
            dbd_summary=summaries["dbd"],
            api_summary=summaries["api"]
        ))
        designs["lld"] = lld_result.diagram
        summaries["lld"] = lld_result.summary
        
        # Step 6: Generate DFD
        print(f"[CHAIN] Step 6/11: Generating DFD...")
        dfd_result = await generate_dfd(DesignRequest(
            project_summary=project_summary,
            hld_summary=summaries["hld"],
            dbd_summary=summaries["dbd"]
        ))
        designs["dfd"] = dfd_result.diagram
        summaries["dfd"] = dfd_result.summary
        
        # Step 7: Generate Component Diagram
        print(f"[CHAIN] Step 7/11: Generating Component Diagram...")
        component_result = await generate_component(DesignRequest(
            project_summary=project_summary,
            hld_summary=summaries["hld"],
            lld_summary=summaries["lld"]
        ))
        designs["component"] = component_result.diagram
        summaries["component"] = component_result.summary
        
        # Step 8: Generate Security Architecture
        print(f"[CHAIN] Step 8/11: Generating Security Architecture...")
        security_result = await generate_security(DesignRequest(
            project_summary=project_summary,
            hld_summary=summaries["hld"],
            api_summary=summaries["api"]
        ))
        designs["security"] = security_result.diagram
        summaries["security"] = security_result.summary
        
        # Step 9: Generate Infrastructure
        print(f"[CHAIN] Step 9/11: Generating Infrastructure Design...")
        infra_result = await generate_infrastructure(DesignRequest(
            project_summary=project_summary,
            hld_summary=summaries["hld"],
            security_summary=summaries["security"]
        ))
        designs["infrastructure"] = infra_result.diagram
        summaries["infrastructure"] = infra_result.summary
        
        # Step 10: Generate State Diagram
        print(f"[CHAIN] Step 10/11: Generating State Diagram...")
        state_result = await generate_state(DesignRequest(
            project_summary=project_summary,
            hld_summary=summaries["hld"],
            api_summary=summaries["api"]
        ))
        designs["state"] = state_result.diagram
        summaries["state"] = state_result.summary
        
        # Step 11: Generate Wireframes
        print(f"[CHAIN] Step 11/11: Generating Wireframes...")
        wireframe_result = await generate_wireframe(DesignRequest(
            project_summary=project_summary,
            hld_summary=summaries["hld"],
            api_summary=summaries["api"]
        ))
        designs["wireframe"] = wireframe_result.diagram
        
        print(f"[CHAIN] All designs generated successfully!")
        
        return GenerateAllResponse(
            designs=designs,
            summaries=summaries,
            status="success",
            total_tokens={"estimated": "~25000"}
        )
        
    except Exception as e:
        print(f"[ERROR] Full design generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Design generation failed: {str(e)}")


# Get design dependencies for frontend
@app.get("/api/designs/config")
async def get_design_config():
    """Get design configuration including dependencies"""
    return {
        "designs": DESIGN_CONFIG,
        "order": ["hld", "dbd", "api", "lld", "dfd", "component", "security", "infrastructure", "state", "wireframe"]
    }


# ============================================================================
# MERMAID DIAGRAM FIX ENDPOINT
# ============================================================================

class FixDiagramRequest(BaseModel):
    diagram: str
    diagram_type: str
    error_message: str

class FixDiagramResponse(BaseModel):
    fixed_diagram: str
    was_fixed: bool
    fix_description: str

@app.post("/api/designs/fix-diagram", response_model=FixDiagramResponse)
async def fix_mermaid_diagram(request: FixDiagramRequest):
    """Fix invalid Mermaid diagram syntax using AI"""
    try:
        print(f"[DEBUG] Fixing {request.diagram_type} diagram...")
        print(f"[DEBUG] Error: {request.error_message}")
        
        system_prompt = """You are an expert in Mermaid diagram syntax. Your task is to fix invalid Mermaid diagrams.

CRITICAL RULES:
1. Return ONLY the fixed Mermaid code, no explanations or markdown fences
2. Preserve the original diagram structure and intent
3. Fix syntax errors like:
   - Missing or extra brackets
   - Invalid characters in node IDs (use alphanumeric only)
   - Incorrect relationship syntax
   - Missing semicolons or line breaks
   - Invalid subgraph definitions
4. For erDiagram: Use proper syntax like "User ||--o{ Order : places"
5. For classDiagram: Use proper syntax like "ClassA --> ClassB"
6. For flowchart/graph: Use proper node syntax like "A[Label]"
7. For sequenceDiagram: Use proper syntax like "Alice->>Bob: Hello"
8. For stateDiagram-v2: Use proper syntax like "[*] --> State1"

DO NOT include any markdown code fences (``` or ```mermaid).
Return ONLY the raw Mermaid code starting with the diagram type (graph, erDiagram, classDiagram, etc.)"""
        
        user_prompt = f"""Fix this invalid Mermaid diagram:

DIAGRAM TYPE: {request.diagram_type}

ERROR MESSAGE:
{request.error_message}

INVALID DIAGRAM:
{request.diagram}

Return the fixed Mermaid diagram code only. No explanations."""
        
        # Use Sonnet directly for fixing - it's better at understanding errors
        fixed_diagram = await call_claude_with_retry(
            model=SONNET_MODEL,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=4096,
            max_retries=2,
            fallback_model=SONNET_MODEL
        )
        
        # Clean up the response
        fixed_diagram = fixed_diagram.strip()
        if fixed_diagram.startswith("```"):
            # Remove markdown code fences
            lines = fixed_diagram.split("\n")
            # Skip first line (```mermaid or ```)
            start_idx = 1
            # Find end fence
            end_idx = len(lines)
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() == "```":
                    end_idx = i
                    break
            fixed_diagram = "\n".join(lines[start_idx:end_idx]).strip()
        
        print(f"[DEBUG] Fixed diagram length: {len(fixed_diagram)}")
        
        return FixDiagramResponse(
            fixed_diagram=fixed_diagram,
            was_fixed=True,
            fix_description=f"Fixed {request.diagram_type} diagram syntax"
        )
        
    except Exception as e:
        print(f"[ERROR] Diagram fix failed: {str(e)}")
        traceback.print_exc()
        # Return original diagram if fix fails
        return FixDiagramResponse(
            fixed_diagram=request.diagram,
            was_fixed=False,
            fix_description=f"Could not fix diagram: {str(e)}"
        )


# ============================================================================
# WIREFRAME MULTI-PAGE GENERATION ENDPOINT
# ============================================================================

from agents.orchestrator import WireframeOrchestrator

class WireframePage(BaseModel):
    id: str
    name: str
    type: str
    html: str
    description: Optional[str] = ""
    error: Optional[str] = None

class WireframePagesResponse(BaseModel):
    pages: list[WireframePage]
    shared_components: dict
    plan: dict
    status: str
    metadata: dict

class WireframePagesRequest(BaseModel):
    project_summary: str
    features_summary: Optional[str] = ""
    hld_summary: Optional[str] = ""
    api_summary: Optional[str] = ""
    page_mode: Optional[str] = "auto"  # 'auto' or 'manual'
    page_count: Optional[int] = None   # Number of pages when manual mode

@app.post("/api/designs/wireframe-pages", response_model=WireframePagesResponse)
async def generate_wireframe_pages(request: WireframePagesRequest):
    """
    Generate multi-page wireframes using agent orchestration.
    Returns multiple HTML pages with shared components.
    """
    try:
        print(f"[DEBUG] Starting multi-page wireframe generation...")
        print(f"[DEBUG] Page mode: {request.page_mode}, Page count: {request.page_count}")
        
        # Initialize orchestrator
        orchestrator = WireframeOrchestrator(anthropic_client)
        
        # Prepare context with page settings
        context = {
            "project_summary": request.project_summary,
            "features_summary": request.features_summary or "",
            "hld_summary": request.hld_summary or "",
            "api_summary": request.api_summary or "",
            "page_mode": request.page_mode or "auto",
            "page_count": request.page_count
        }
        
        # Generate wireframes
        result = await orchestrator.generate_wireframes(context)
        
        print(f"[DEBUG] Wireframe generation complete: {len(result['pages'])} pages")
        
        return WireframePagesResponse(
            pages=[WireframePage(**page) for page in result["pages"]],
            shared_components=result["shared_components"],
            plan=result["plan"],
            status="success",
            metadata=result["metadata"]
        )
        
    except Exception as e:
        print(f"[ERROR] Wireframe pages generation failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Wireframe generation failed: {str(e)}")


class RegeneratePageRequest(BaseModel):
    page_id: str
    page_name: str
    page_type: str
    project_context: str
    shared_components: Optional[dict] = None

@app.post("/api/designs/wireframe-page/regenerate")
async def regenerate_wireframe_page(request: RegeneratePageRequest):
    """Regenerate a single wireframe page"""
    try:
        print(f"[DEBUG] Regenerating page: {request.page_name}")
        
        from agents.orchestrator import generate_single_page
        
        result = await generate_single_page(
            client=anthropic_client,
            page_type=request.page_type,
            page_name=request.page_name,
            project_context=request.project_context,
            components=request.shared_components
        )
        
        return {
            "page": WireframePage(**result),
            "status": "success"
        }
        
    except Exception as e:
        print(f"[ERROR] Page regeneration failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Page regeneration failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
