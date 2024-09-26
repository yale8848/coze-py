import json
from enum import Enum
from typing import Dict, List, Iterator, Union, TYPE_CHECKING, Optional

from cozepy.auth import Auth
from cozepy.model import CozeModel
from cozepy.request import Requester

if TYPE_CHECKING:
    from .message import MessageClient as ChatMessageClient


class MessageRole(str, Enum):
    # Indicates that the content of the message is sent by the user.
    user = "user"
    # Indicates that the content of the message is sent by the bot.
    assistant = "assistant"


class MessageType(str, Enum):
    # User input content.
    # 用户输入内容。
    question = "question"
    # The message content returned by the Bot to the user, supporting incremental return. If the workflow is bound to a message node, there may be multiple answer scenarios, and the end flag of the streaming return can be used to determine that all answers are completed.
    # Bot 返回给用户的消息内容，支持增量返回。如果工作流绑定了消息节点，可能会存在多 answer 场景，此时可以用流式返回的结束标志来判断所有 answer 完成。
    answer = "answer"
    # Intermediate results of the function (function call) called during the Bot conversation process.
    # Bot 对话过程中调用函数（function call）的中间结果。
    function_call = "function_call"
    # Results returned after calling the tool (function call).
    # 调用工具 （function call）后返回的结果。
    tool_output = "tool_output"
    # Results returned after calling the tool (function call).
    # 调用工具 （function call）后返回的结果。
    tool_response = "tool_response"
    # If the user question suggestion switch is turned on in the Bot configuration, the reply content related to the recommended questions will be returned.
    # 如果在 Bot 上配置打开了用户问题建议开关，则会返回推荐问题相关的回复内容。不支持在请求中作为入参。
    follow_up = "follow_up"
    # In the scenario of multiple answers, the server will return a verbose package, and the corresponding content is in JSON format. content.msg_type = generate_answer_finish represents that all answers have been replied to.
    # 多 answer 场景下，服务端会返回一个 verbose 包，对应的 content 为 JSON 格式，content.msg_type =generate_answer_finish 代表全部 answer 回复完成。不支持在请求中作为入参。
    verbose = "verbose"

    unknown = ""


class MessageContentType(str, Enum):
    # Text.
    # 文本。
    text = "text"
    # Multimodal content, that is, a combination of text and files, or a combination of text and images.
    # 多模态内容，即文本和文件的组合、文本和图片的组合。
    object_string = "object_string"
    # message card. This enum value only appears in the interface response and is not supported as an input parameter.
    # 卡片。此枚举值仅在接口响应中出现，不支持作为入参。
    card = "card"


class MessageObjectStringType(str, Enum):
    """
    The content type of the multimodal message.
    """

    text = "text"
    file = "file"
    image = "image"


class MessageObjectString(CozeModel):
    # The content type of the multimodal message.
    # 多模态消息内容类型
    type: MessageObjectStringType
    # Text content. Required when type is text.
    # 文本内容。
    text: str
    # The ID of the file or image content.
    # 在 type 为 file 或 image 时，file_id 和 file_url 应至少指定一个。
    file_id: str
    # The online address of the file or image content.<br>Must be a valid address that is publicly accessible.
    # file_id or file_url must be specified when type is file or image.
    # 文件或图片内容的在线地址。必须是可公共访问的有效地址。
    # 在 type 为 file 或 image 时，file_id 和 file_url 应至少指定一个。
    file_url: str


class Message(CozeModel):
    # The entity that sent this message.
    role: MessageRole
    # The type of message.
    type: MessageType = ""
    # The content of the message. It supports various types of content, including plain text, multimodal (a mix of text, images, and files), message cards, and more.
    # 消息的内容，支持纯文本、多模态（文本、图片、文件混合输入）、卡片等多种类型的内容。
    content: str
    # The type of message content.
    # 消息内容的类型
    content_type: MessageContentType
    # Additional information when creating a message, and this additional information will also be returned when retrieving messages.
    # Custom key-value pairs should be specified in Map object format, with a length of 16 key-value pairs. The length of the key should be between 1 and 64 characters, and the length of the value should be between 1 and 512 characters.
    # 创建消息时的附加消息，获取消息时也会返回此附加消息。
    # 自定义键值对，应指定为 Map 对象格式。长度为 16 对键值对，其中键（key）的长度范围为 1～64 个字符，值（value）的长度范围为 1～512 个字符。
    meta_data: Optional[Dict[str, str]] = None

    id: str = None
    conversation_id: str = None
    bot_id: str = None
    chat_id: str = None
    created_at: int = None
    updated_at: int = None

    @staticmethod
    def user_text_message(content: str, meta_data: Optional[Dict[str, str]] = None) -> "Message":
        return Message(
            role=MessageRole.user,
            type=MessageType.question,
            content=content,
            content_type=MessageContentType.text,
            meta_data=meta_data,
        )

    @staticmethod
    def assistant_text_message(content: str, meta_data: Optional[Dict[str, str]] = None) -> "Message":
        return Message(
            role=MessageRole.assistant,
            type=MessageType.answer,
            content=content,
            content_type=MessageContentType.text,
            meta_data=meta_data,
        )


class ChatStatus(str, Enum):
    """
    The running status of the session
    """

    # The session has been created.
    created = "created"

    # The Bot is processing.
    in_progress = "in_progress"

    # The Bot has finished processing, and the session has ended.
    completed = "completed"

    # The session has failed.
    failed = "failed"

    # The session is interrupted and requires further processing.
    requires_action = "requires_action"


class Chat(CozeModel):
    # The ID of the chat.
    id: str
    # The ID of the conversation.
    conversation_id: str
    # The ID of the bot.
    bot_id: str
    # Indicates the create time of the chat. The value format is Unix timestamp in seconds.
    created_at: Optional[int] = None
    # Indicates the end time of the chat. The value format is Unix timestamp in seconds.
    completed_at: Optional[int] = None
    # Indicates the failure time of the chat. The value format is Unix timestamp in seconds.
    failed_at: Optional[int] = None
    # Additional information when creating a message, and this additional information will also be returned when retrieving messages.
    # Custom key-value pairs should be specified in Map object format, with a length of 16 key-value pairs. The length of the key should be between 1 and 64 characters, and the length of the value should be between 1 and 512 characters.
    meta_data: Optional[Dict[str, str]] = None
    # When the chat encounters an exception, this field returns detailed error information, including:
    # Code: The error code. An integer type. 0 indicates success, other values indicate failure.
    # Msg: The error message. A string type.

    # The running status of the session. The values are:
    # created: The session has been created.
    # in_progress: The Bot is processing.
    # completed: The Bot has finished processing, and the session has ended.
    # failed: The session has failed.
    # requires_action: The session is interrupted and requires further processing.
    status: ChatStatus

    # Details of the information needed for execution.


class Event(str, Enum):
    # Event for creating a conversation, indicating the start of the conversation.
    # 创建对话的事件，表示对话开始。
    conversation_chat_created = "conversation.chat.created"

    # The server is processing the conversation.
    # 服务端正在处理对话。
    conversation_chat_in_progress = "conversation.chat.in_progress"

    # Incremental message, usually an incremental message when type=answer.
    # 增量消息，通常是 type=answer 时的增量消息。
    conversation_message_delta = "conversation.message.delta"

    # The message has been completely replied to. At this point, the streaming package contains the spliced results of all message.delta, and each message is in a completed state.
    # message 已回复完成。此时流式包中带有所有 message.delta 的拼接结果，且每个消息均为 completed 状态。
    conversation_message_completed = "conversation.message.completed"

    # The conversation is completed.
    # 对话完成。
    conversation_chat_completed = "conversation.chat.completed"

    # This event is used to mark a failed conversation.
    # 此事件用于标识对话失败。
    conversation_chat_failed = "conversation.chat.failed"

    # The conversation is interrupted and requires the user to report the execution results of the tool.
    # 对话中断，需要使用方上报工具的执行结果。
    conversation_chat_requires_action = "conversation.chat.requires_action"

    # Error events during the streaming response process. For detailed explanations of code and msg, please refer to Error codes.
    # 流式响应过程中的错误事件。关于 code 和 msg 的详细说明，可参考错误码。
    error = "error"

    # The streaming response for this session ended normally.
    # 本次会话的流式返回正常结束。
    done = "done"


class ChatEvent(CozeModel):
    event: Event
    chat: Chat = None
    message: Message = None


class ChatIterator(object):
    def __init__(self, iters: Iterator[bytes]):
        self._iters = iters

    def __iter__(self):
        return self

    def __next__(self) -> ChatEvent:
        event = ""
        data = ""
        line = ""
        times = 0

        while times < 2:
            line = next(self._iters).decode("utf-8")
            if line == "":
                continue
            elif line.startswith("event:"):
                if event == "":
                    event = line[6:]
                else:
                    raise Exception(f"invalid event: {line}")
            elif line.startswith("data:"):
                if data == "":
                    data = line[5:]
                else:
                    raise Exception(f"invalid event: {line}")
            else:
                raise Exception(f"invalid event: {line}")

            times += 1

        if event == Event.done:
            raise StopIteration
        elif event == Event.error:
            raise Exception(f"error event: {line}")
        elif event in [Event.conversation_message_delta, Event.conversation_message_completed]:
            return ChatEvent(event=event, message=Message.model_validate(json.loads(data)))
        elif event in [
            Event.conversation_chat_created,
            Event.conversation_chat_in_progress,
            Event.conversation_chat_completed,
            Event.conversation_chat_failed,
            Event.conversation_chat_requires_action,
        ]:
            return ChatEvent(event=event, chat=Chat.model_validate(json.loads(data)))
        else:
            raise Exception(f"unknown event: {line}")


class ChatClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._message = None

    def create(
        self,
        *,
        bot_id: str,
        user_id: str,
        additional_messages: List[Message] = None,
        custom_variables: Dict[str, str] = None,
        auto_save_history: bool = True,
        meta_data: Dict[str, str] = None,
        conversation_id: str = None,
    ) -> Chat:
        """
        Create a conversation.
        Conversation is an interaction between a bot and a user, including one or more messages.
        """
        return self._create(
            bot_id=bot_id,
            user_id=user_id,
            additional_messages=additional_messages,
            stream=False,
            custom_variables=custom_variables,
            auto_save_history=auto_save_history,
            meta_data=meta_data,
            conversation_id=conversation_id,
        )

    def stream(
        self,
        *,
        bot_id: str,
        user_id: str,
        additional_messages: List[Message] = None,
        custom_variables: Dict[str, str] = None,
        auto_save_history: bool = True,
        meta_data: Dict[str, str] = None,
        conversation_id: str = None,
    ) -> ChatIterator:
        """
        Create a conversation.
        Conversation is an interaction between a bot and a user, including one or more messages.
        """
        return self._create(
            bot_id=bot_id,
            user_id=user_id,
            additional_messages=additional_messages,
            stream=True,
            custom_variables=custom_variables,
            auto_save_history=auto_save_history,
            meta_data=meta_data,
            conversation_id=conversation_id,
        )

    def _create(
        self,
        *,
        bot_id: str,
        user_id: str,
        additional_messages: List[Message] = None,
        stream: bool = False,
        custom_variables: Dict[str, str] = None,
        auto_save_history: bool = True,
        meta_data: Dict[str, str] = None,
        conversation_id: str = None,
    ) -> Union[Chat, ChatIterator]:
        """
        Create a conversation.
        Conversation is an interaction between a bot and a user, including one or more messages.
        """
        url = f"{self._base_url}/v3/chat"
        body = {
            "bot_id": bot_id,
            "user_id": user_id,
            "additional_messages": [i.model_dump() for i in additional_messages] if additional_messages else [],
            "stream": stream,
            "custom_variables": custom_variables,
            "auto_save_history": auto_save_history,
            "conversation_id": conversation_id if conversation_id else None,
            "meta_data": meta_data,
        }
        if not stream:
            return self._requester.request("post", url, Chat, body=body, stream=stream)

        return ChatIterator(self._requester.request("post", url, Chat, body=body, stream=stream))

    def retrieve(
        self,
        *,
        conversation_id: str,
        chat_id: str,
    ) -> Chat:
        """
        Create a conversation.
        Conversation is an interaction between a bot and a user, including one or more messages.
        """
        url = f"{self._base_url}/v3/chat/retrieve"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }
        return self._requester.request("post", url, Chat, params=params)

    def cancel(
        self,
        *,
        conversation_id: str,
        chat_id: str,
    ) -> Chat:
        """
        Call this API to cancel an ongoing chat.
        """
        url = f"{self._base_url}/v3/chat/cancel"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }
        return self._requester.request("post", url, Chat, params=params)

    @property
    def message(
        self,
    ) -> "ChatMessageClient":
        if self._message is None:
            from .message import MessageClient

            self._message = MessageClient(self._base_url, self._auth, self._requester)
        return self._message
