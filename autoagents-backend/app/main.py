from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableSerializable
from langchain_community.llms.fake import FakeListLLM
from pydantic import BaseModel, Field, ConfigDict

from .agents import (
    AgentResult,
    AgentStoriesResult,
    ClaudeAgent,
    ClaudeStoryAgent,
    ClaudeVisualizationAgent,
    FeatureSpec,
    StorySpec,
    VisualizationResult,
)
from .storage import (
    load_agent1_features,
    load_agent2_stories,
    load_prompt,
    load_dot_asset,
    load_mermaid_asset,
    store_agent1_snapshot,
    store_agent2_snapshot,
    store_visualization_assets,
)


logger = logging.getLogger("uvicorn.error")

load_dotenv()

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
AGENT_MODEL = "claude-3-5-haiku-latest"
agent_1: ClaudeAgent | None = None
agent_2: ClaudeStoryAgent | None = None
agent_3: ClaudeVisualizationAgent | None = None


def build_right_now_chain() -> RunnableSerializable:
    """Create a lightweight LangChain pipeline for demo purposes."""

    prompt = PromptTemplate(
        input_variables=["context"],
        template=(
            "You are Autoagents' status summarizer. Read the context and produce "
            "one energetic sentence that highlights the current focus.\n\n"
            "Context:\n{context}\n\n"
            "Energetic single-sentence status:"
        ),
    )

    # FakeListLLM avoids external API calls so the sample runs offline.
    llm = FakeListLLM(responses=[
        "Autoagents is syncing new user onboarding workflows across Gmail and Teams right now!"
    ])

    return prompt | llm


@lru_cache(maxsize=1)
def get_right_now_chain() -> RunnableSerializable:
    return build_right_now_chain()


def build_chat_chain() -> RunnableSerializable:
    prompt = PromptTemplate(
        input_variables=["message"],
        template=(
            "You are AutoAgents' AI concierge. Read the customer's message and craft "
            "a short, friendly reply summarizing how you can help them.\n\n"
            "Customer message: {message}"
        ),
    )

    def respond(message: dict[str, str] | str) -> str:
        customer_message = message["message"] if isinstance(message, dict) else str(message)
        return (
            "AutoAgents Assistant: Thanks for reaching out! I understand that you're saying "
            f"\"{customer_message}\". I'm here to help with onboarding, communication tools, "
            "or any workflow questions you have."
        )

    return prompt | RunnableLambda(respond)


@lru_cache(maxsize=1)
def get_chat_chain() -> RunnableSerializable:
    return build_chat_chain()


app = FastAPI(title="Autoagents Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    port = 8000
    logger.info("Autoagents backend started on port %s", port)
    global agent_1, agent_2, agent_3
    if CLAUDE_API_KEY:
        agent_1 = ClaudeAgent(api_key=CLAUDE_API_KEY, model=AGENT_MODEL)
        logger.info("Agent_1 initialised with Claude model %s", AGENT_MODEL)
        agent_2 = ClaudeStoryAgent(api_key=CLAUDE_API_KEY, model=AGENT_MODEL)
        logger.info("Agent_2 initialised with Claude model %s", AGENT_MODEL)
        agent_3 = ClaudeVisualizationAgent(api_key=CLAUDE_API_KEY, model=AGENT_MODEL)
        logger.info("Agent_3 initialised with Claude model %s", AGENT_MODEL)
    else:
        logger.warning("CLAUDE_API_KEY not set. Agent endpoints will return 503.")


@app.get("/", summary="Health check")
async def read_root() -> dict[str, str]:
    return {"message": "Autoagents backend is running"}


@app.get("/status/right-now", summary="Right now status")
async def right_now_status() -> dict[str, str]:
    chain = get_right_now_chain()
    context = (
        "New signups are flowing in and the communications team is coordinating launch updates."
    )
    status = chain.invoke({"context": context})
    return {"status": status}


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", summary="Chat with AutoAgents assistant", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    chain = get_chat_chain()
    reply = chain.invoke({"message": request.message})
    return ChatResponse(reply=reply)


class FeatureItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    title: str
    description: str
    acceptance_criteria: list[str] = Field(default_factory=list, alias="acceptanceCriteria")


class AgentFeatureRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    prompt: str = Field(default="")
    decision: Literal["again", "keep", "keep_all"] | None = None
    run_id: str | None = None
    features: list[FeatureItem] | None = None


class AgentFeatureResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    run_id: str
    summary: str | None = None
    features: list[FeatureItem] = Field(default_factory=list)
    message: str
    decision: Literal["generated", "kept"]
    debug: dict[str, Any] | None = None


class StoryItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    feature_title: str = Field(alias="featureTitle")
    user_story: str = Field(alias="userStory")
    acceptance_criteria: list[str] = Field(default_factory=list, alias="acceptanceCriteria")
    implementation_notes: list[str] = Field(default_factory=list, alias="implementationNotes")


class AgentStoryRequest(BaseModel):
    prompt: str | None = None
    features: list[FeatureItem] | None = None
    stories: list[StoryItem] | None = None
    decision: Literal["again", "keep"] | None = None
    run_id: str | None = None


class AgentStoryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    run_id: str
    summary: str | None = None
    stories: list[StoryItem] = Field(default_factory=list)
    message: str
    decision: Literal["generated", "kept"]
    debug: dict[str, Any] | None = None


class VisualizationDiagram(BaseModel):
    mermaid: str
    dot: str
    mermaid_path: str | None = Field(default=None, alias="mermaidPath")
    dot_path: str | None = Field(default=None, alias="dotPath")
    mermaid_updated_at: str | None = Field(default=None, alias="mermaidUpdatedAt")
    dot_updated_at: str | None = Field(default=None, alias="dotUpdatedAt")


class AgentVisualizationRequest(BaseModel):
    prompt: str | None = None
    features: list[FeatureItem] | None = None
    stories: list[StoryItem] | None = None


class AgentVisualizationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    run_id: str
    summary: str
    diagrams: VisualizationDiagram
    callouts: list[str] = Field(default_factory=list)
    message: str
    debug: dict[str, Any] | None = None


class MermaidAssetResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    mermaid: str
    path: str | None = None
    updated_at: str | None = Field(default=None, alias="updatedAt")


class MermaidAssetUpdateRequest(BaseModel):
    mermaid: str


@app.post(
    "/agent/features",
    summary="Generate or approve feature specs with Agent_1",
    response_model=AgentFeatureResponse,
)
async def agent_features(request: AgentFeatureRequest) -> AgentFeatureResponse:
    logger.info(
        "Agent_1 request received | decision=%s run_id=%s",
        request.decision,
        request.run_id,
    )

    if request.decision in {"keep", "keep_all"}:
        if not request.run_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="run_id is required when decision is 'keep' or 'keep_all'.",
            )
        if not request.features:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="features payload is required when approving Agent_1 output.",
            )

        feature_specs = [
            FeatureSpec(
                title=item.title,
                description=item.description,
                acceptance_criteria=item.acceptance_criteria,
            )
            for item in request.features
        ]
        store_agent1_snapshot(request.run_id, request.prompt, feature_specs)
        logger.info(
            "Agent_1 approval snapshot stored | run_id=%s features=%d",
            request.run_id,
            len(feature_specs),
        )
        action = "All feature sets approved" if request.decision == "keep_all" else "Feature set approved"
        logger.info("Agent_1 approval | action=%s run_id=%s", request.decision, request.run_id)
        return AgentFeatureResponse(
            run_id=request.run_id,
            summary=None,
            features=[],
            message=f"{action}. Proceeding with scope.",
            decision="kept",
            debug=None,
        )

    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A non-empty prompt is required to generate features.",
        )

    if agent_1 is None:
        logger.error("Agent_1 requested but Claude API key is missing.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent_1 is unavailable. Missing Claude API configuration.",
        )

    try:
        result: AgentResult = await agent_1.generate_features(prompt)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Agent_1 failed to generate features.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate features. Please try again.",
        ) from exc

    features = [
        FeatureItem(
            title=spec.title,
            description=spec.description,
            acceptance_criteria=spec.acceptance_criteria,
        )
        for spec in result.features
    ]

    logger.debug(
        "Agent_1 success | run_id=%s features=%d",
        result.run_id,
        len(features),
    )

    return AgentFeatureResponse(
        run_id=result.run_id,
        summary=result.summary,
        features=features,
        message="Generated feature concepts.",
        decision="generated",
        debug=result.debug,
    )


@app.post(
    "/agent/stories",
    summary="Generate or approve user stories with Agent_2",
    response_model=AgentStoryResponse,
)
async def agent_stories(request: AgentStoryRequest) -> AgentStoryResponse:
    logger.info(
        "Agent_2 request received | decision=%s run_id=%s",
        request.decision,
        request.run_id,
    )

    feature_items = request.features or []
    feature_specs = [
        FeatureSpec(
            title=item.title,
            description=item.description,
            acceptance_criteria=item.acceptance_criteria,
        )
        for item in feature_items
    ]

    story_items = request.stories or []
    story_specs = [
        StorySpec(
            feature_title=item.feature_title,
            user_story=item.user_story,
            acceptance_criteria=item.acceptance_criteria,
            implementation_notes=item.implementation_notes,
        )
        for item in story_items
    ]

    if request.decision == "keep":
        if not request.run_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="run_id is required when decision is 'keep'.",
            )
        if not story_specs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stories are required when approving Agent_2 output.",
            )

        if not feature_specs:
            feature_specs = load_agent1_features()
            if not feature_specs:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to locate features to store with approved stories.",
                )

        prompt = request.prompt or load_prompt()
        store_agent2_snapshot(request.run_id, prompt, feature_specs, story_specs)
        logger.info("Agent_2 stories approved and snapshot stored | run_id=%s", request.run_id)
        return AgentStoryResponse(
            run_id=request.run_id,
            summary="Stories approved for downstream visualization.",
            stories=[
                StoryItem(
                    featureTitle=story.feature_title,
                    userStory=story.user_story,
                    acceptanceCriteria=story.acceptance_criteria,
                    implementationNotes=story.implementation_notes,
                )
                for story in story_specs
            ],
            message="Stories approved. Handoff complete.",
            decision="kept",
            debug=None,
        )

    prompt = request.prompt or load_prompt()

    if not feature_specs:
        feature_specs = load_agent1_features()
        if not feature_specs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No features supplied and no approved snapshot available.",
            )

    if agent_2 is None:
        logger.error("Agent_2 requested but Claude API key is missing.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent_2 is unavailable. Missing Claude API configuration.",
        )

    try:
        story_result: AgentStoriesResult = await agent_2.generate_stories(feature_specs)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Agent_2 failed to generate stories.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate user stories. Please try again.",
        ) from exc

    stories = [
        StoryItem(
            featureTitle=story.feature_title,
            userStory=story.user_story,
            acceptanceCriteria=story.acceptance_criteria,
            implementationNotes=story.implementation_notes,
        )
        for story in story_result.stories
    ]

    logger.debug(
        "Agent_2 success | run_id=%s stories=%d",
        story_result.run_id,
        len(stories),
    )

    return AgentStoryResponse(
        run_id=story_result.run_id,
        summary=story_result.summary,
        stories=stories,
        message="Generated user stories.",
        decision="generated",
        debug=story_result.debug,
    )


@app.post(
    "/agent/visualizer",
    summary="Generate visualization artifacts with Agent_3",
    response_model=AgentVisualizationResponse,
)
async def agent_visualizer(request: AgentVisualizationRequest) -> AgentVisualizationResponse:
    if agent_3 is None:
        logger.error("Agent_3 requested but Claude API key is missing.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent_3 is unavailable. Missing Claude API configuration.",
        )

    feature_items = request.features or []
    story_items = request.stories or []

    feature_specs = [
        FeatureSpec(
            title=item.title,
            description=item.description,
            acceptance_criteria=item.acceptance_criteria,
        )
        for item in feature_items
    ]
    if not feature_specs:
        feature_specs = load_agent1_features()

    story_specs = [
        StorySpec(
            feature_title=item.feature_title,
            user_story=item.user_story,
            acceptance_criteria=item.acceptance_criteria,
            implementation_notes=item.implementation_notes,
        )
        for item in story_items
    ]
    if not story_specs:
        story_specs = load_agent2_stories()

    if not feature_specs or not story_specs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Visualization requires approved features and stories.",
        )

    try:
        visualization: VisualizationResult = await agent_3.generate_visualization(
            feature_specs,
            story_specs,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Agent_3 failed to generate visualization.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate visualization. Please try again.",
        ) from exc

    store_visualization_assets(visualization.mermaid, visualization.dot)
    mermaid_text, mermaid_path, mermaid_updated_at = load_mermaid_asset()
    dot_text, dot_path, dot_updated_at = load_dot_asset()

    diagrams = VisualizationDiagram(
        mermaid=mermaid_text or visualization.mermaid,
        dot=dot_text or visualization.dot,
        mermaid_path=mermaid_path,
        dot_path=dot_path,
        mermaid_updated_at=mermaid_updated_at,
        dot_updated_at=dot_updated_at,
    )

    return AgentVisualizationResponse(
        run_id=visualization.run_id,
        summary=visualization.summary,
        diagrams=diagrams,
        callouts=visualization.callouts,
        message="Generated visualization blueprint.",
        debug=visualization.debug,
    )


@app.get(
    "/agent/visualizer/mermaid",
    summary="Retrieve the latest Mermaid diagram asset",
    response_model=MermaidAssetResponse,
)
async def get_mermaid_asset() -> MermaidAssetResponse:
    mermaid, path, updated_at = load_mermaid_asset()
    return MermaidAssetResponse(mermaid=mermaid, path=path, updated_at=updated_at)


@app.post(
    "/agent/visualizer/mermaid",
    summary="Persist Mermaid diagram edits",
    response_model=MermaidAssetResponse,
    status_code=status.HTTP_200_OK,
)
async def save_mermaid_asset(payload: MermaidAssetUpdateRequest) -> MermaidAssetResponse:
    mermaid = payload.mermaid.strip()
    if not mermaid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mermaid diagram cannot be empty.",
        )

    store_visualization_assets(mermaid, None)
    saved_mermaid, path, updated_at = load_mermaid_asset()
    return MermaidAssetResponse(mermaid=saved_mermaid, path=path, updated_at=updated_at)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

