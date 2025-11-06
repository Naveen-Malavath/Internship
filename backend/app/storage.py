from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from .schemas import Conversation, Message

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"


class ConversationStorage:
    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not CONVERSATIONS_FILE.exists():
            default_conversation = self._create_empty_conversation_dict(
                title="Welcome Chat",
                intro_message="Welcome! Ask me anything and I'll respond with a helpful message."
            )
            self._write_data({"conversations": [default_conversation]})

    def list_conversations(self) -> List[Conversation]:
        data = self._read_data()
        return [self._dict_to_conversation(item) for item in data.get("conversations", [])]

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        for conversation in self.list_conversations():
            if conversation.id == conversation_id:
                return conversation
        return None

    def create_conversation(self, title: Optional[str] = None) -> Conversation:
        conversations = self.list_conversations()
        conversation_dict = self._create_empty_conversation_dict(title=title)
        conversations.insert(0, self._dict_to_conversation(conversation_dict))
        self._write_data({"conversations": [conv.dict(by_alias=True) for conv in conversations]})
        return self._dict_to_conversation(conversation_dict)

    def delete_conversation(self, conversation_id: str) -> None:
        conversations = [conv for conv in self.list_conversations() if conv.id != conversation_id]
        self._write_data({"conversations": [conv.dict(by_alias=True) for conv in conversations]})

    def clear_conversations(self) -> Conversation:
        new_conversation = self._dict_to_conversation(self._create_empty_conversation_dict())
        self._write_data({"conversations": [new_conversation.dict(by_alias=True)]})
        return new_conversation

    def add_message(self, conversation_id: str, message: Message) -> Conversation:
        conversations = self.list_conversations()
        updated_conversations: List[Conversation] = []
        target_conversation: Optional[Conversation] = None

        for conv in conversations:
            if conv.id == conversation_id:
                conv.messages.append(message)
                conv.updated_at = message.timestamp
                target_conversation = conv
            updated_conversations.append(conv)

        if target_conversation is None:
            raise ValueError("Conversation not found")

        self._write_data({"conversations": [conv.dict(by_alias=True) for conv in updated_conversations]})
        return target_conversation

    def update_conversation(self, conversation: Conversation) -> None:
        conversations = self.list_conversations()
        updated_conversations = [conversation if conv.id == conversation.id else conv for conv in conversations]
        self._write_data({"conversations": [conv.dict(by_alias=True) for conv in updated_conversations]})

    def generate_id(self) -> str:
        return uuid4().hex

    def _create_empty_conversation_dict(self, title: Optional[str] = None, intro_message: Optional[str] = None) -> Dict:
        now = datetime.now(timezone.utc)
        conversation_dict = {
            "id": self.generate_id(),
            "title": title or "New Chat",
            "messages": [],
            "createdAt": now.isoformat(),
            "updatedAt": now.isoformat()
        }

        if intro_message:
            intro_message_dict = Message(
                id=self.generate_id(),
                content=intro_message,
                role="assistant",
                timestamp=now,
            ).dict(by_alias=True)
            conversation_dict["messages"].append(intro_message_dict)

        return conversation_dict

    def _read_data(self) -> Dict:
        with CONVERSATIONS_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write_data(self, data: Dict) -> None:
        with CONVERSATIONS_FILE.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    @staticmethod
    def _dict_to_conversation(data: Dict) -> Conversation:
        return Conversation.parse_obj(data)


storage = ConversationStorage()
