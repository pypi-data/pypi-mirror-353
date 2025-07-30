from typing import Optional, Any, cast
from uuid import uuid4

from .types import (
    AskOptions,
    Message,
    RequestId,
    SessionId,
    TaskId,
    TaskParams,
    TaskResponse,
    TaskStatusUpdateEvent,
    Task,
)

# Base URLs for different environments
BASE_URLS = {
    'LIVE': 'https://agent.payman.ai',
    'TEST': 'https://agent.payman.dev',
    'INTERNAL': 'https://payman.ngrok.dev',
}

# API Endpoints
API_ENDPOINTS = {
    'OAUTH_TOKEN': '/api/oauth2/token',
    'TASKS_SEND': '/api/a2a/tasks/send',
    'TASKS_SEND_SUBSCRIBE': '/api/a2a/tasks/sendSubscribe',
}

def generate_task_id() -> TaskId:
    """Generate a new task ID."""
    return f'tsk-{uuid4()}'

def generate_session_id() -> SessionId:
    """Generate a new session ID."""
    return f'ses-{uuid4()}'

def generate_request_id() -> RequestId:
    """Generate a new request ID."""
    return f'req-{uuid4()}'

def create_message(text: str, options: Optional[AskOptions] = None) -> Message:
    """Creates a message object from text and options."""
    parts = [{'type': 'text', 'text': text, 'metadata': options.get('part_metadata') if options else None}]
    return cast(Message, {
        'role': 'user',
        'parts': parts,
        'metadata': options.get('message_metadata') if options else None,
    })

def create_task_request(message: Message, session_id: str, options: Optional[AskOptions] = None) -> TaskParams:
    """Creates a task request object from a message and session ID."""
    return cast(TaskParams, {
        'id': 'task-id',  # Replace with actual task ID generation if needed
        'message': message,
        'session_id': session_id,
        'metadata': options.get('metadata') if options else None,
    })

def create_task_response_from_status_event(
    status_event: TaskStatusUpdateEvent,
) -> TaskResponse:
    """Create a TaskResponse from a TaskStatusUpdateEvent."""
    task: Task = {
        'id': status_event['id'],
        'session_id': None,
        'status': status_event['status'],
        'artifacts': [],
        'metadata': status_event['metadata'],
    }
    return {
        'jsonrpc': '2.0',
        'id': f'req-{status_event["id"][4:]}',
        'result': task,
        'error': None,
    } 