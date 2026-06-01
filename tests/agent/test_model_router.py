from agent.model_router import classify_message, resolve_model_route


def test_classify_message_coding_beats_fast_terms():
    assert classify_message("quickly fix the failing pytest") == "coding"


def test_classify_message_memory_status():
    assert classify_message("where are we at with our upgrades") == "memory"


def test_disabled_config_keeps_current_route():
    decision = resolve_model_route(
        "fix this bug",
        {},
        current_provider="copilot-acp",
        current_model="composer-2.5-fast",
    )
    assert decision.enabled is False
    assert decision.reason == "disabled"
    assert decision.provider == "copilot-acp"
    assert decision.model == "composer-2.5-fast"


def test_explicit_override_bypasses_routing():
    config = {
        "model_routing": {
            "enabled": True,
            "routes": {
                "coding": {"provider": "copilot-acp", "model": "composer-2.5-fast"},
            },
        }
    }
    decision = resolve_model_route(
        "implement model routing",
        config,
        current_provider="openrouter",
        current_model="anthropic/claude-sonnet-4",
        explicit_model=True,
    )
    assert decision.enabled is False
    assert decision.reason == "explicit_override"
    assert decision.provider == "openrouter"
    assert decision.model == "anthropic/claude-sonnet-4"


def test_configured_coding_route_applies_provider_and_model():
    config = {
        "model_routing": {
            "enabled": True,
            "routes": {
                "coding": {"provider": "copilot-acp", "model": "composer-2.5-fast"},
            },
        }
    }
    decision = resolve_model_route(
        "implement automatic routing",
        config,
        current_provider="openrouter",
        current_model="anthropic/claude-sonnet-4",
    )
    assert decision.enabled is True
    assert decision.route == "coding"
    assert decision.reason == "matched"
    assert decision.provider == "copilot-acp"
    assert decision.model == "composer-2.5-fast"
    assert decision.source == "model_routing.routes.coding"


def test_missing_specific_route_uses_default_route_if_present():
    config = {
        "model_routing": {
            "enabled": True,
            "routes": {
                "default": {"provider": "openrouter", "model": "openai/gpt-5.1"},
            },
        }
    }
    decision = resolve_model_route(
        "research current benchmarks",
        config,
        current_provider="copilot-acp",
        current_model="composer-2.5-fast",
    )
    assert decision.route == "research"
    assert decision.reason == "matched"
    assert decision.provider == "openrouter"
    assert decision.model == "openai/gpt-5.1"
    assert decision.source == "model_routing.routes.default"


def test_empty_route_keeps_current_provider_model():
    config = {
        "model_routing": {
            "enabled": True,
            "routes": {
                "fast": {},
            },
        }
    }
    decision = resolve_model_route(
        "quick summary please",
        config,
        current_provider="copilot-acp",
        current_model="composer-2.5-fast",
    )
    assert decision.route == "fast"
    assert decision.reason == "no_configured_route"
    assert decision.provider == "copilot-acp"
    assert decision.model == "composer-2.5-fast"
