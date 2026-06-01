"""Deterministic, opt-in model routing for Hermes turns.

This module intentionally avoids LLM calls and provider/network lookups.  It
classifies a user turn into a small route name, then overlays a configured
provider/model route if one exists.  Callers remain responsible for resolving
provider credentials and falling back if runtime resolution fails.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class RouteDecision:
    """Decision returned by the deterministic model router."""

    enabled: bool
    route: str
    reason: str
    provider: str
    model: str
    toolsets: tuple[str, ...] = ()
    source: str = "current"


def _norm(value: Any) -> str:
    return str(value or "").strip()


def _lower_message(message: Any) -> str:
    if isinstance(message, str):
        return message.lower()
    if isinstance(message, list):
        parts: list[str] = []
        for item in message:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content") or ""
                if isinstance(text, str):
                    parts.append(text)
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts).lower()
    return str(message or "").lower()


def classify_message(message: Any) -> str:
    """Classify a user turn into a conservative route name.

    Order matters: specific work routes beat generic "quick" wording.
    """

    text = _lower_message(message)
    compact = " ".join(text.split())

    memory_phrases = (
        "where are we at",
        "where did we leave",
        "what did we do",
        "what were we working on",
        "remember when",
        "last time",
        "previous session",
        "session history",
    )
    if any(phrase in compact for phrase in memory_phrases):
        return "memory"

    coding_terms = (
        "implement",
        "fix",
        "debug",
        "refactor",
        "test",
        "pytest",
        "commit",
        "push",
        "pull request",
        " pr ",
        "code",
        "script",
        "function",
        "class",
        "bug",
        "feature",
        "wire",
        "build",
    )
    if any(term in f" {compact} " for term in coding_terms):
        return "coding"

    wiki_terms = (
        "wiki",
        "docs",
        "documentation",
        "obsidian",
        "simplemem",
        "memory oracle",
        "knowledge base",
        "knowledge graph",
        "system map",
    )
    if any(term in compact for term in wiki_terms):
        return "wiki"

    research_terms = (
        "research",
        "search",
        "web",
        "arxiv",
        "paper",
        "papers",
        "news",
        "current",
        "latest",
        "market",
        "compare",
        "benchmark",
    )
    if any(term in compact for term in research_terms):
        return "research"

    fast_terms = (
        "quick",
        "brief",
        "briefly",
        "simple",
        "summarize",
        "summary",
        "explain",
        "what is",
        "what's",
        "why",
    )
    if any(term in compact for term in fast_terms):
        return "fast"

    return "default"


def _route_config(config: Mapping[str, Any], route: str) -> Mapping[str, Any]:
    routing = config.get("model_routing", {}) if isinstance(config, Mapping) else {}
    if not isinstance(routing, Mapping):
        return {}
    routes = routing.get("routes", {})
    if not isinstance(routes, Mapping):
        return {}
    entry = routes.get(route) or {}
    if not isinstance(entry, Mapping):
        return {}
    return entry


def _routing_enabled(config: Mapping[str, Any]) -> bool:
    routing = config.get("model_routing", {}) if isinstance(config, Mapping) else {}
    return bool(isinstance(routing, Mapping) and routing.get("enabled"))


def _toolsets(entry: Mapping[str, Any]) -> tuple[str, ...]:
    raw = entry.get("toolsets")
    if not isinstance(raw, (list, tuple)):
        return ()
    return tuple(str(item).strip() for item in raw if str(item).strip())


def resolve_model_route(
    message: Any,
    config: Mapping[str, Any],
    current_provider: str,
    current_model: str,
    *,
    explicit_model: bool = False,
    explicit_provider: bool = False,
) -> RouteDecision:
    """Resolve an optional provider/model route for one user turn.

    Empty route entries mean "keep current provider/model".  Missing provider
    or model in a configured route also falls back field-by-field to current.
    """

    provider = _norm(current_provider)
    model = _norm(current_model)

    if not _routing_enabled(config):
        return RouteDecision(
            enabled=False,
            route="default",
            reason="disabled",
            provider=provider,
            model=model,
        )

    if explicit_model or explicit_provider:
        return RouteDecision(
            enabled=False,
            route="default",
            reason="explicit_override",
            provider=provider,
            model=model,
        )

    route = classify_message(message)
    entry = _route_config(config, route)
    source = f"model_routing.routes.{route}" if entry else "current"

    if not entry and route != "default":
        entry = _route_config(config, "default")
        if entry:
            source = "model_routing.routes.default"

    routed_provider = _norm(entry.get("provider")) or provider
    routed_model = _norm(entry.get("model")) or model

    return RouteDecision(
        enabled=True,
        route=route,
        reason="matched" if source != "current" else "no_configured_route",
        provider=routed_provider,
        model=routed_model,
        toolsets=_toolsets(entry),
        source=source,
    )
