# CLAUDE.md

이 파일은 이 저장소에서 작업하는 Claude Code(claude.ai/code)에게 제공하는 안내입니다.

## 저장소 상태

Requirements.md의 FR-001~036, §7/§8 인수 기준을 모두 만족하는 Flask 웹 애플리케이션이
**구현 완료**되었습니다(Phase 0~7 전부 완료, 아래 "아키텍처 및 구현 계획" 참고). 사용자에게
보여줄 개요는 `README.md`를 우선 참고하세요 — 이 CLAUDE.md는 Claude Code가 코드를 다룰 때
필요한 세부 규칙 중심입니다.

### 실행 방법

```bash
cd D:\GoogleTestExample
source .venv/Scripts/activate           # 이미 만들어진 가상환경 (없으면: python -m venv .venv 후 pip install -r requirements.txt)
python -m flask --app "src/gtestdash/web/app:createApp" run
# http://127.0.0.1:5000 접속, 기본 데이터 소스는 ./GoogleTestResults
```

### 테스트 실행

```bash
source .venv/Scripts/activate
python -m pytest -q                     # 전체(unit+integration+e2e), 287개
python -m pytest tests/unit -q          # 순수 함수 단위 테스트만(가장 빠름)
python -m pytest tests/integration -q   # Flask test client 라우트 통합 테스트
python -m pytest tests/e2e -q           # Playwright 브라우저 E2E(최초 1회 `playwright install chromium` 필요)
```

## 이 저장소의 목적

`Requirements.md`(한국어)는 Jenkins 빌드가 생성한 GoogleTest XML 결과 파일을 읽어 브라우저
대시보드로 보여주는 **Python 웹 애플리케이션**을 정의합니다: 최신 빌드 요약, 성공/실패 트렌드
차트, 모듈별 실패 분포, 검색/필터 가능한 테스트 상세 화면. `GoogleTestResults/`에는 앱이
파싱해야 할 합성 GoogleTest XML 100개(Jenkins 빌드 10개 × 모듈 10개)가 들어 있습니다 — 이것이
유일한 입력 데이터 소스이며, 실제 Jenkins 연동, XML 수정, 인증 기능은 없습니다.

구현에 착수하기 전에 `Requirements.md` 전체를 읽으세요 — 정확한 페이지 경로, 필드 매핑, 상태
우선순위 규칙, 그리고 구현이 현재 데이터셋에 대해 재현해야 하는 수치 기준(예: 빌드 `10`은
전체 1,200건, 실패 24건, 실패율 2.0%로 표시되어야 함)을 정의하고 있습니다.

## 데이터 구조

- `GoogleTestResults/<build>/gtest_<module>.xml` — 빌드 폴더 `01`~`10`(Jenkins 빌드 번호, 사전식이
  아닌 숫자 기준 정렬), 각 폴더에는 모듈별 GoogleTest XML이 1개씩(모듈 10개) 존재합니다.
- XML 계층: `testsuites > testsuite > properties/testcase > failure`. 스위트별 `<properties>`는
  `jenkins_build_number`, `module`, `source_file`, `tested_function`,
  `target_build_failure_rate_percent`를 담고 있으며 — 모듈명/함수명의 근거는 스위트명이나
  파일명이 아니라 이 속성값입니다(Requirements.md §4.3, FR-005 참조).
- `GoogleTestResults/README.md` — 데이터셋 요약(빌드별 실패율)을 사람이 읽기 좋은 형태로 정리.
- `GoogleTestResults/generation_manifest.json` — 합성 데이터 생성에 사용된 빌드별 통계(테스트/실패
  수, 타임스탬프)를 기계가 읽기 좋은 형태로 정리 — 파서 결과 검증에 유용.
- `TestCase_Template.xlsx` — 수동 테스트 케이스 추적용 템플릿으로, XML 파싱 앱과는 무관.

## Requirements.md의 핵심 구현 규칙

아래 항목들은 실수하기 쉬운 부분이며, 명세에서 수용 기준과 함께 명시적으로 다루고 있습니다:

- **상태 우선순위**: 하나의 테스트케이스에 여러 상태 근거가 존재하면
  `ERROR > FAILED > SKIPPED > DISABLED > PASSED` 순서로 분류합니다(FR-006).
- **집계값은 파싱된 레코드로부터 다시 계산**해야 하며, `<testsuites>`/`<testsuite>`에 선언된
  `tests`/`failures`/`errors` 속성값을 그대로 신뢰하면 안 됩니다 — 선언값과 실제 계산값을
  대조하고 불일치 시 경고(XML 경로, 선언값, 계산값 포함)를 표시하되, 파싱 가능한 테스트는
  계속 표시합니다(FR-007, FR-008).
- **실패율**: `실패 수 / 전체 수 × 100`, 소수점 첫째 자리까지 표시. 전체 수가 0이면 `0`이 아니라
  `N/A`로 표시(FR-007).
- **최신 빌드** = `jenkins_build_number`의 최댓값, 없으면 숫자 폴더명, 그다음 타임스탬프 순으로
  판정(FR-009).
- **모듈명 대체 순서**: `property[name=module]` → `testcase@classname`의 첫 구간 → XML 파일명
  (FR-005).
- XML 파일 하나가 손상되어도 앱 전체가 죽으면 안 됩니다 — 해당 파일은 제외하고 경로와 파싱
  오류를 표시하며, 나머지 99개 파일의 결과는 계속 렌더링합니다(FR-035).
- 상세 페이지에서 목록으로 돌아갈 때 검색어/필터/정렬/페이지 상태를 유지해야 합니다(FR-033).

## 샘플 데이터 기준 구현 검증

Requirements.md §7에는 현재 데이터셋에 대한 고정된 수용 기준값이 있습니다 — 스모크 테스트
목표로 사용하세요:

- 빌드 10개, XML 파일 100개, 모듈 10개, 빌드당 테스트 1,200건, 전체 테스트 레코드 12,000건.
- 최신 빌드는 `10`: 전체 1,200건, 통과 1,176건, 실패 24건, 실패율 2.0%.
- 빌드별 실패율(01~10 순서): 8%, 4%, 9%, 6%, 3%, 7%, 5%, 10%, 4%, 2%.
- 빌드 10의 모듈별 분포(모든 모듈 120건): `ChildLockController` 실패 3, `CommunicationGateway` 3,
  `DiagnosticManager` 2, `DoorStateManager` 3, `LockActuator` 2, `PersistenceManager` 2,
  `SpeedInterlock` 3, `StateConsistencyMonitor` 2, `SwitchInput` 2, `VehicleSignalAdapter` 2.

## 서브에이전트 라우팅

이 프로젝트는 아래 두 작업을 직접 수행하지 않고 전용 서브에이전트에 위임합니다
(`.claude/agents/`에 정의됨). 해당 작업이 필요하면 Agent 도구로 반드시 이 서브에이전트를
호출하십시오.

- **시스템 테스트 케이스 생성/검토** → `sw-system-tester` 서브에이전트 (내부적으로
  `sw-system-test` 스킬 사용, 산출물은 `TestCase_Template.xlsx`를 양식으로 사용)
- **운영 코드 구현/버그 수정/리팩터링** → `tdd-flow` 서브에이전트 (내부적으로
  `test-driven-development` 스킬을 사용해 Red-Green-Refactor를 강제)

`tdd-flow`가 개발 활동을 완료하면(Agent 도구 호출이 끝나면) `.claude/hooks/notify_sw_system_tester.py`가
PostToolUse 훅으로 실행되어, 이어서 `sw-system-tester`를 호출해 `Requirements.md` 요구사항 기반으로
테스트 케이스를 생성/갱신하도록 컨텍스트에 상기시킵니다(`.claude/settings.json`에 등록). 이 상기 메시지를
받으면 반드시 `sw-system-tester`를 호출하십시오.

## 아키텍처 및 구현 계획 (확정)

- **스택**: Flask + Jinja2 + Chart.js(CDN), 서버 렌더링. 인증/ORM 없음.
- **데이터**: 파일 기반 XML을 앱 시작 시 1회, `POST /refresh` 호출 시에만 다시 파싱해 인메모리
  스냅샷으로 원자적 교체(SQLite 등 DB 미사용). 요청 하나는 항상 같은 스냅샷만 참조.
- **목록 상태 유지(FR-033)**: URL 쿼리 파라미터.
- **네이밍**: pytest `test_*` 함수명, `Requirements.md` §4.3 정규화 필드명(`build_id` 등,
  원문이 snake_case)만 예외로 두고, 나머지 우리 내부 함수/변수명은 이 문서의 낙타 표기법
  (camelCase) 기준을 따른다.
- **패키지 관리**: `requirements.txt` + 표준 `venv`.
- **모듈 레이어** (`src/gtestdash/`):
  - `parsing/` — XML→정규화 레코드(`discovery.py`, `xml_parser.py`, `status_resolver.py`,
    `field_resolver.py`, `record_builder.py`, `validation.py`, `models.py`)
  - `aggregation/` — 빌드/모듈 집계, 트렌드, diff(`build_summary.py`, `latest_build.py`,
    `build_diff.py`, `trend.py`, `module_distribution.py`, `module_trend.py`)
  - `repository.py` — 스냅샷 조립/새로고침 오케스트레이션
  - `query/` — 검색/필터/정렬/페이지네이션(빌드 상세·모듈 상세·검색 결과 3개 라우트가 공유)
  - `web/` — Flask 앱 팩토리, 라우트(`dashboard`, `builds`, `modules`, `tests`, `search`,
    `refresh`), 템플릿, 정적 자산
- **Phase 순서** (각 phase는 `tdd-flow`가 TDD로 구현, 전부 완료됨): Phase 0 골격(패키지
  스켈레톤 + Playwright/pytest 테스트 인프라) → Phase 1 결과 수집/정규화(FR-001~008) →
  Phase 2 메인 대시보드(FR-009~017) → Phase 3 빌드/모듈 상세(FR-018~021) → Phase 4 테스트
  상세(FR-022~024) → Phase 5 검색/필터/정렬/페이지네이션(FR-025~031) → Phase 6 네비게이션/
  상태유지/새로고침/에러처리(FR-032~036) → Phase 7 §7/§8 인수 기준 최종 검증. §7/§8 각 항목이
  어느 테스트로 커버되는지의 전체 대응표는 `docs/acceptance-traceability.md`에 있다.
- 손상/엣지 케이스 테스트 픽스처는 `GoogleTestResults/`(§7 수치의 근거, 읽기 전용 취급)를
  건드리지 않고 `tests/fixtures/edge_cases/`에 별도로 둔다.
- 새 기능을 추가하거나 리팩터링할 때도 이 레이어 구조와 네이밍 규칙을 그대로 유지한다.

## 개발 프로세스

- **커밋/푸시**: Phase 0~7 각 phase가 끝날 때마다 반드시 커밋하고 `origin/main`에 푸시한다.
  커밋 메시지에 Phase 번호와 해당 FR 범위를 명시한다(과거형 — Phase 0~7은 이미 이 방식으로
  완료됨. 이후 새 작업 단위에도 동일한 커밋 규율을 유지한다).
- **시스템 테스트 케이스**: `sw-system-tester`가 `Requirements.md` FR-001~036, §7/§8을
  근거로 `TestCase_Template.xlsx`에 시스템 테스트 케이스(기능/비기능 시트)를 작성해 둔다.
  명세에 직접 근거가 없는 케이스는 이름에 "(제안)"으로 표시한다.
- **브라우저 E2E 테스트**: Playwright(Python, `pytest-playwright`), `tests/e2e/`에 있다.
  `TestCase_Template.xlsx`에서 "(제안)"(합성 데이터가 필요한 시나리오) 표시가 없는 케이스를
  `tdd-flow`가 읽고 수동으로 Playwright 테스트로 옮겼다 — 각 테스트 함수명/docstring에 xlsx의
  `TC_ID`를 남겨 추적성을 유지한다(`tests/e2e/test_e2e_fr*.py`, `test_e2e_acc_acceptance.py`).
  xlsx 텍스트를 그대로 파싱해 테스트를 자동 생성하지 않는다. CI(GitHub Actions) 자동 실행은
  구성하지 않는다 — 로컬 실행 전용.
- **대화 기록**: 이 저장소 작업을 진행한 Claude Code 세션과의 대화를
  `docs/conversation-log.md`(요약)와 `docs/conversation-transcript.md`(사용자 발화 원문)에
  기록하고 커밋한다(공개 저장소이므로 민감정보는 제외).
- **정적 스냅샷**: `target/`에 샘플 데이터(`GoogleTestResults`) 기준으로 렌더링한 주요 화면의
  정적 HTML을 보관한다(서버 없이 미리보기용, README.md 참고).
- **자동 메모리**: `.claude/settings.json`의 `autoMemoryEnabled: true`로 프로젝트 자동 메모리
  기능이 켜져 있다.

## 소스코드 품질 기준

**다음의 품질 기준을 반드시 달성해야 한다**

- 함수 라인수: 80라인 이하
- 순환복잡도: 10 이하
- 주석 비율: 20% 이상
- 주석 작성 방식: Doxygen 방식 적용
- 중복코드: 100 토큰 이상 불가
- 함수 Calling: 5회 이하
- 함수 Called by: 7회 이하
- 함수 Cycle Dependency: 허용하지 않음
- 함수명, 변수명은 3글자 이상이고, 낙타 표기법 사용