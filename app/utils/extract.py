from app.core.session_memory import get_param, store_param

def extract_param(params: dict, key: str, session_id: str) -> str:
    """
    Extrait proprement une valeur depuis Dialogflow ou depuis la mémoire.
    Si la valeur est une liste ou RepeatedComposite, on prend le premier élément.
    Elle est aussi stockée en session mémoire.
    """
    value = params.get(key)
    
    # Si RepeatedComposite ou liste
    if hasattr(value, "__iter__") and not isinstance(value, str):
        if len(value) > 0:
            value = str(value[0])
        else:
            value = ""
    elif isinstance(value, str):
        value = value.strip()
    else:
        # Si rien dans les paramètres, on tente la mémoire
        value = get_param(session_id, key) or ""

    # Stocker si valeur présente
    if value:
        store_param(session_id, key, value)

    return value

def extract_session_id(data: dict) -> str:
    raw = data.get("session")
    return raw.split("/")[-1] if raw and "/" in raw else raw
