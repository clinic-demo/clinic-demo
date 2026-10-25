from __future__ import annotations

from typing import Any, Dict, List

from mock_llm import complete


def complete_with_llm(messages, tools, current_user=None, db=None):
    return complete(messages, tools)
