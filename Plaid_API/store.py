from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class WebhookRecord:
    direction: str  # "sent" | "received"
    url: Optional[str]
    body: Dict[str, Any]


@dataclass
class ItemRecord:
    item_id: str
    client_user_id: str
    access_token: str


@dataclass
class MemoryStore:
    users: Dict[str, str] = field(default_factory=dict)  # client_user_id -> user_id
    link_tokens: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # link_token -> info
    public_tokens: Dict[str, str] = field(default_factory=dict)  # public_token -> item_id
    access_tokens: Dict[str, str] = field(default_factory=dict)  # access_token -> item_id
    items: Dict[str, ItemRecord] = field(default_factory=dict)  # item_id -> record
    webhook_log: List[WebhookRecord] = field(default_factory=list)

    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def create_user(self, client_user_id: str) -> str:
        with self._lock:
            if client_user_id in self.users:
                return self.users[client_user_id]
            user_id = f"user-{uuid.uuid4()}"
            self.users[client_user_id] = user_id
            return user_id

    def create_link_token(self, client_user_id: str, metadata: Dict[str, Any]) -> str:
        link_token = f"link-{uuid.uuid4()}"
        with self._lock:
            self.link_tokens[link_token] = {"client_user_id": client_user_id, **metadata}
        return link_token

    def create_item_from_public_token(self, public_token: str, client_user_id: str) -> Dict[str, str]:
        item_id = f"item-{uuid.uuid4()}"
        access_token = f"access-{uuid.uuid4()}"
        with self._lock:
            self.public_tokens[public_token] = item_id
            self.access_tokens[access_token] = item_id
            self.items[item_id] = ItemRecord(item_id=item_id, client_user_id=client_user_id, access_token=access_token)
        return {"item_id": item_id, "access_token": access_token}

    def resolve_item_by_access_token(self, access_token: str) -> Optional[ItemRecord]:
        with self._lock:
            item_id = self.access_tokens.get(access_token)
            if not item_id:
                return None
            return self.items.get(item_id)

    def resolve_item_by_public_token(self, public_token: str) -> Optional[ItemRecord]:
        with self._lock:
            item_id = self.public_tokens.get(public_token)
            if not item_id:
                return None
            return self.items.get(item_id)

    def append_webhook(self, direction: str, url: Optional[str], body: Dict[str, Any]) -> None:
        with self._lock:
            self.webhook_log.append(WebhookRecord(direction=direction, url=url, body=body))


# Singleton store
store = MemoryStore()
