# CLAUDE.md

이 파일은 이 저장소에서 작업하는 Claude Code(claude.ai/code)에게 제공하는 안내입니다.

## 저장소 상태

이 저장소에는 현재 **애플리케이션 코드가 없습니다** — 아직 구현되지 않은 웹 앱의 명세와 샘플
데이터셋만 존재합니다. 빌드 시스템, 패키지 매니페스트, 테스트 러너가 없습니다. 코드를 작성하기
전에 그 사이 구현이 추가되었는지 확인하세요(예: `src/`, `app/` 등의 디렉터리, 그리고
`requirements.txt`/`pyproject.toml`). 그런 것이 있다면 이 문서보다 우선하는 것으로 간주하고,
실제 명령어와 아키텍처를 반영하도록 이 파일을 갱신하세요.

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
  `sw-system-test` 스킬 사용)
- **운영 코드 구현/버그 수정/리팩터링** → `tdd-flow` 서브에이전트 (내부적으로
  `test-driven-development` 스킬을 사용해 Red-Green-Refactor를 강제)

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