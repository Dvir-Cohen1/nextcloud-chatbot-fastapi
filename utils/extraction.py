import json

def extract_actor(data):
    actor = data.get("actor", {})
    return {
        "type": actor.get("type"),
        "id": actor.get("id"),
        "name": actor.get("name")
    }

def extract_object(data):
    object_data = data.get("object", {})
    content_str = object_data.get("content", "")
    try:
        content_data = json.loads(content_str)
    except json.JSONDecodeError:
        content_data = {}

    return {
        "type": object_data.get("type"),
        "id": object_data.get("id"),
        "name": object_data.get("name"),
        "content": content_data,
        "media_type": object_data.get("mediaType")
    }

def extract_target(data):
    target = data.get("target", {})
    return {
        "type": target.get("type"),
        "id": target.get("id"),
        "name": target.get("name")
    }