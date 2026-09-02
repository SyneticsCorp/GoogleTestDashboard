# 대화 로그

이 문서는 `SyneticsCorp/GoogleTestDashboard` 저장소를 Claude Code와 함께 진행한 세션의 대화
내용을 요약해 기록한다. 코드 리뷰나 감사(audit) 목적의 참고 자료이며, 개인정보나 인증 정보는
포함하지 않는다.

## 2026-09-02

### 1. CLAUDE.md 최초 작성

저장소에는 애플리케이션 코드가 전혀 없고 `Requirements.md`(GoogleTest 결과 분석 웹 앱 기능
요구사항), `GoogleTestResults/01~10`(합성 GoogleTest XML 100개), `TestCase_Template.xlsx`만
있는 상태에서 `CLAUDE.md`를 생성했다. 내용은 저장소 상태, 목적, 데이터 구조, Requirements.md의
핵심 구현 규칙, 샘플 데이터 기준 검증값을 요약했다(처음에는 영어로 작성).

### 2. 외부 스킬/플러그인 도입

- `github.com/obra/superpowers`에서 `test-driven-development`(및 참고자료
  `writing-good-tests.md`), `requesting-code-review`(및 `code-reviewer.md` 템플릿),
  `receiving-code-review` 스킬을 `.claude/skills/`에 프로젝트 스킬로 복사했다.
- `github.com/multica-ai/andrej-karpathy-skills`를 Claude Code 플러그인 마켓플레이스로 추가하고
  `andrej-karpathy-skills@karpathy-skills` 플러그인을 프로젝트 스코프로 설치했다(사고 전
  가정 명시/단순함 우선/외과적 수정/목표 지향 실행 4원칙).
- `github.com/nextlevelbuilder/ui-ux-pro-max-skill`을 같은 방식으로 설치했다(UI/UX 디자인
  인텔리전스 스킬 7종 — `ui-ux-pro-max`, `banner-design`, `brand`, `design-system`, `design`,
  `slides`, `ui-styling`).

### 3. 원격 저장소 연결

이 프로젝트 디렉터리를 처음으로 git 저장소로 초기화하고, 빈 원격 저장소
`https://github.com/SyneticsCorp/GoogleTestDashboard.git`에 최초 커밋을 푸시했다. 이후
버전 관리는 이 저장소의 `main` 브랜치를 통해 이루어진다.

### 4. 한국어 전환

`CLAUDE.md`를 한국어로 재작성하고, 이 프로젝트에서는 앞으로 한국어로만 소통하기로 확정했다.
동시에 `CLAUDE.md`에 소스코드 품질 기준(함수 라인수 80줄 이하, 순환복잡도 10 이하, 주석 비율
20% 이상·Doxygen 방식, 중복코드 100토큰 이상 금지, 함수 Calling 5회 이하·Called by 7회 이하,
순환 의존성 금지, 함수명/변수명 3글자 이상·낙타 표기법)이 추가되었다(사용자가 직접 저장소
파일을 편집).

### 5. 서브에이전트 구성

- `sw-system-tester` 서브에이전트를 `.claude/agents/`에 생성해 `sw-system-test` 스킬(ISO 26262
  Part 6, A-SPICE SWE.4/5/6, ISO 29119/ISTQB, ISO 25000 기반 방법론)과 연결했다. 산출물은
  `TestCase_Template.xlsx` 양식을 그대로 사용한다.
- `tdd-flow` 서브에이전트를 생성해 `test-driven-development` 스킬(Red-Green-Refactor 철칙)과
  연결했다. 두 서브에이전트 모두 "해당 작업이 필요할 때 프로액티브하게 자동 호출"되도록
  `description`을 작성했고, `CLAUDE.md`에 "서브에이전트 라우팅" 절로 규칙을 명시했다.
- `tdd-flow`(Agent 도구) 호출이 끝날 때마다 `sw-system-tester` 호출을 상기시키는
  `PostToolUse` 훅(`.claude/hooks/notify_sw_system_tester.py`)을 `.claude/settings.json`에
  등록했다.

### 6. Requirements.md 분석 및 개발 계획 수립

`Requirements.md`(FR-001~036, §7 인수 기준, §8 완료 판정)를 분석해 Plan 모드로 구체적인
아키텍처와 8단계(phase) 구현 계획을 설계했다. 사용자가 확정한 사항:

- 네이밍: pytest `test_*`, `Requirements.md` §4.3 필드명(snake_case)만 예외, 나머지는
  camelCase.
- 웹 프레임워크: **Flask + Jinja2 + Chart.js**(서버 렌더링, 인증/ORM 없음).
- 데이터 저장: 파일 기반 XML → 인메모리 스냅샷(SQLite 불필요).
- 새로고침(FR-034): **수동 버튼**(`POST /refresh`).
- 목록 상태 유지(FR-033): **URL 쿼리 파라미터**.

계획 원문은 세션 로컬 계획 파일(`~/.claude/plans/delightful-dazzling-cook.md`)에 저장되었고,
핵심 내용은 `CLAUDE.md`의 "아키텍처 및 구현 계획" 절에 요약되어 저장소에 커밋되었다.

### 7. 개발 프로세스 확정

Phase 0~7을 다음 규칙으로 자동 진행하기로 확정했다:

- 각 phase가 끝날 때마다 커밋 및 `origin/main` 푸시.
- 사용자 수준 브라우저 테스트: **Playwright**(Python, `pytest-playwright`). `sw-system-tester`가
  생성한 `TestCase_Template.xlsx`의 시스템 테스트 케이스를 `tdd-flow`가 읽고 수동으로
  Playwright 테스트로 옮긴다(케이스 ID로 추적성 유지). xlsx를 자동 파싱해 테스트를 생성하지는
  않는다. CI(GitHub Actions) 자동화는 이번 범위에 포함하지 않는다(로컬 실행 전용).
- 이 대화 로그(`docs/conversation-log.md`)를 저장소에 커밋해 기록으로 남긴다.
- `.claude/settings.json`에 `autoMemoryEnabled: true`를 설정해 프로젝트 자동 메모리 기능을
  명시적으로 활성화했다.
- 이후 Phase 0부터 Phase 7까지는 사용자 확인 없이 자동으로 진행하고, 완료 후 결과를 보고하기로
  했다.
