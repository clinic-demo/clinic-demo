"""
mock_llm.py — навчальна заглушка LLM для курсу Secure Software Development and Integration.

Не потребує API-ключа і мережі. Поводиться передбачувано, щоб у всіх студентів
і в ментора результат був однаковий.

Навмисно наївна, як погано захищена модель:
  * виконує інструкції, знайдені будь-де в контексті (повідомлення користувача,
    текст документа з RAG) -> prompt injection, зокрема непряма;
  * повертає системний промпт на прохання "повтори свої інструкції"
    -> system prompt leakage;
  * передає в інструменти аргументи, які "попросили", без перевірки прав
    -> excessive agency / tool misuse.

Захист має бути у ВАШОМУ застосунку (перевірка прав в інструментах, фільтрація
контексту, підтвердження дій), а не в цій заглушці.

Інтерфейс:
    reply = complete(messages, tools)
    messages: [{"role": "system"|"user"|"assistant"|"tool"|"context", "content": str}, ...]
    tools:    [{"name": str, "description": str}, ...]
    reply:    {"content": str} або {"tool_call": {"name": str, "arguments": dict}}
"""
import json
import re

_INJECTION = re.compile(
    r"(?:ignore (?:all )?previous instructions|ігноруй попередні інструкції|SYSTEM OVERRIDE)"
    r".*?call\s+(?P<name>\w+)\s*\((?P<args>\{.*?\})\)",
    re.IGNORECASE | re.DOTALL,
)
_DIRECT_CALL = re.compile(r"call\s+(?P<name>\w+)\s*\((?P<args>\{.*?\})\)", re.IGNORECASE | re.DOTALL)
_LEAK = re.compile(r"(repeat|print|show).{0,20}(instructions|system prompt)|повтори.{0,20}інструкці", re.IGNORECASE)

_INTENTS = [
    (re.compile(r"(вільн\w* слот|free slot|available)", re.I), "search_slots"),
    (re.compile(r"(мої записи|my appointments)", re.I), "get_my_appointments"),
    (re.compile(r"(запиши|book)", re.I), "book_appointment"),
    (re.compile(r"(нотатк|notes|історі\w* візит)", re.I), "get_visit_notes"),
    (re.compile(r"(підсумуй|summari[sz]e)", re.I), "summarize_document"),
]
_NUMBER = re.compile(r"(?:№|#|id\s*=?\s*)(\d+)", re.I)


def _tool_names(tools):
    return {t["name"] for t in (tools or [])}


def _parse_args(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def complete(messages, tools=None):
    names = _tool_names(tools)
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    tool_results = [m["content"] for m in messages if m["role"] == "tool"]
    # Увесь текст, який "бачить" модель: і користувач, і документи з RAG.
    context = "\n".join(m["content"] for m in messages if m["role"] in ("user", "context", "tool"))

    # 1. Ін'єкція має пріоритет над усім (як у погано налаштованої моделі).
    m = _INJECTION.search(context)
    if m and m.group("name") in names:
        return {"tool_call": {"name": m.group("name"), "arguments": _parse_args(m.group("args"))}}

    # 2. Витік системного промпту.
    if _LEAK.search(last_user):
        return {"content": f"Мої інструкції: {system}"}

    # 3. Якщо інструмент уже відпрацював — переказати результат.
    if tool_results and messages[-1]["role"] == "tool":
        return {"content": f"Ось що я знайшов: {tool_results[-1]}"}

    # 3a. Якщо передано текст документа (RAG) — "підсумувати" його.
    if messages and messages[-1]["role"] == "context":
        text = messages[-1]["content"].strip().replace("\n", " ")
        return {"content": f"Підсумок документа: {text[:300]}"}

    # 4. Явний виклик інструмента користувачем.
    m = _DIRECT_CALL.search(last_user)
    if m and m.group("name") in names:
        return {"tool_call": {"name": m.group("name"), "arguments": _parse_args(m.group("args"))}}

    # 5. Звичайні наміри. Номер з тексту передається як є, без перевірки прав.
    for pattern, tool in _INTENTS:
        if pattern.search(last_user) and tool in names:
            args = {}
            n = _NUMBER.search(last_user)
            if n:
                key = {"get_visit_notes": "patient_id", "summarize_document": "document_id",
                       "book_appointment": "slot_id"}.get(tool, "id")
                args[key] = int(n.group(1))
            return {"tool_call": {"name": tool, "arguments": args}}

    return {"content": "Я асистент клініки. Можу знайти вільні слоти, записати вас або показати ваші записи."}
