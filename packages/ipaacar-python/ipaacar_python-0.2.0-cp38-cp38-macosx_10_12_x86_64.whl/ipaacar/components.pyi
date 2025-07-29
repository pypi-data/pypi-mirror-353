from typing import Awaitable, Callable, Optional

class IU:

    def __new__(cls, category: str, component_name: str, payload: str | bytes, links: Optional[dict[str, list[str]]] = None) -> IU:
        ...

    async def get_category(self) -> str:
        ...

    async def get_uid(self) -> str:
        ...

    async def get_owner_buffer_uid(self) -> str | None:
        ...

    async def is_committed(self) -> bool:
        ...

    async def is_open(self) -> bool:
        ...

    async def is_retracted(self) -> bool:
        ...

    async def get_payload(self) -> str:
        ...

    async def get_payload_bytes(self) -> bytes:
        ...

    async def get_component_name(self) -> str:
        ...

    async def get_links(self) -> dict[str, list[str]]:
        ...

    async def set_payload(self, payload: str | bytes):
        ...

    async def add_target_to_link(self, link_name: str, target: str):
        ...

    async def remove_target_from_link(self, link_name: str, target: str):
        ...

    async def remove_link(self, link_name: str):
        ...

    async def add_callback(self, callback: Callable[..., Awaitable[None]]):
        ...

    async def announce_change_over_backend(self):
        ...


class OutputBuffer:

    @classmethod
    async def new_with_connect(
        cls, 
        uid: str, 
        component_name: str, 
        address: str, 
        qos: int | None = None, 
        username: str | None = None,
        password: str | None = None, 
    ) -> OutputBuffer:
        ...

    async def create_new_iu(self, category: str, payload: str | bytes, links: dict[str, list[str]] | None = None, publish: bool = True) -> IU:
        ...

    async def publish_iu(self, iu: IU):
        ...

    async def commit_iu(self, iu: IU):
        ...

    async def retract_iu(self, iu: IU):
        ...

    async def send_message(self, topic: str, message: str | bytes):
        ...


class InputBuffer:

    @classmethod
    async def new_with_connect(
        cls, 
        uid: str, 
        component_name: str, 
        address: str, 
        qos: int | None = None,
        username: str | None = None,
        password: str | None = None, 
    ) -> InputBuffer:
        ...

    async def get_received_iu_ids(self) -> list[str]:
        ...

    async def get_iu_by_id(self, uid: str) -> IU:
        ...

    async def get_all_ius(self) -> list[IU]:
        ...

    async def listen_for_ius(self, category: str, callback: Callable[..., Awaitable[None]]) -> str: 
        ...

    async def listen_for_messages(self, category: str, callback: Callable[..., Awaitable[None]]) -> str:
        ...

    async def remove_listener(self, listener_id: str):
        ...


class IUEvent:
    PUBLISHED = ...
    """The IU has been published."""
    UPDATED = ...
    """The payload of the IU has been updated."""
    COMMITTED = ...
    """The IU has been committed."""
    RETRACTED = ...
    """The IU has been retracted."""
    LINKSUPDATED = ...
    """The links of the IU have been updated."""


async def create_mqtt_pair(
    input_uid: str, 
    output_uid: str, 
    component_name: str, 
    address: str, 
    qos: int | None = None,
    username: str | None = None,
    password: str | None = None, 
) -> tuple[InputBuffer, OutputBuffer]:
    ...
