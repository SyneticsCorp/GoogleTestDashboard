#!/usr/bin/env python3
"""PostToolUse hook: tdd-flow 서브에이전트 완료 시 sw-system-tester 호출을 상기시킨다."""
import json
import sys

TRIGGER_SUBAGENT = "tdd-flow"
MESSAGE = (
    "tdd-flow 서브에이전트의 구현 작업이 완료되었습니다. "
    "이어서 sw-system-tester 서브에이전트를 Agent 도구로 호출해 "
    "Requirements.md 요구사항을 근거로 TestCase_Template.xlsx 형식의 "
    "테스트 케이스를 생성/갱신하십시오."
)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print("{}")
        return

    tool_input = data.get("tool_input") or {}
    is_tdd_flow_agent_call = (
        data.get("tool_name") == "Agent"
        and tool_input.get("subagent_type") == TRIGGER_SUBAGENT
    )

    if is_tdd_flow_agent_call:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": MESSAGE,
            }
        }))
    else:
        print("{}")


if __name__ == "__main__":
    main()
