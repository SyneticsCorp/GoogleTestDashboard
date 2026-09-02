# 인수 기준 대응표 (Phase 7)

이 문서는 `Requirements.md` §7(현재 데이터 기반 인수 기준)과 §8(구현 완료 판정, 7개 조건)의
각 항목이 실제로 어느 테스트에서 검증되는지 감사(audit)한 결과다. Phase 0~6에서 이미 폭넓게
커버되어 있었고, 감사 과정에서 발견된 유일한 격차(§8 조건 7의 "결과 없음" 중 "빌드가 전혀
없는 결과 루트" 케이스)는 `tests/integration/test_final_acceptance.py`를 신설해 메웠다.

## 1. §7 항목별 대응표

| § 7 검증 항목 | 기대값 | 검증 테스트 |
|---|---|---|
| 빌드 수 | 10 | `tests/integration/test_snapshot_acceptance.py::test_discovery_findsTenBuildsAndOneHundredXmlFiles`, `tests/e2e/test_e2e_fr001_004_discovery_parsing.py::test_tcFr00201_...`(빌드 목록 10개, 숫자순 정렬) |
| XML 파일 수 | 100 | `tests/integration/test_snapshot_acceptance.py::test_discovery_findsTenBuildsAndOneHundredXmlFiles`, `tests/e2e/test_e2e_fr001_004_discovery_parsing.py::test_tcFr00301_tenModulesPerBuildOneHundredXmlTotal`(10모듈×10빌드=100) |
| 모듈 수 | 10 | `tests/e2e/test_e2e_fr001_004_discovery_parsing.py::test_tcFr00301_tenModulesPerBuildOneHundredXmlTotal`(모든 빌드에서 module-table 10행), `tests/integration/test_build_detail_route.py::test_buildDetailRoute_build10_moduleDistributionHasTenModulesSummingToTwentyFourFailures` |
| 빌드별 테스트 수 | 1,200 | `tests/e2e/test_e2e_fr001_004_discovery_parsing.py::test_tcFr00401_twelveThousandRecordsAcrossTenBuilds`(10개 빌드 전부 1,200건씩 개별 확인) |
| 전체 테스트 레코드 | 12,000 | `tests/integration/test_snapshot_acceptance.py::test_buildSnapshot_hasNoWarningsAndTwelveThousandRecords`, `tests/e2e/test_e2e_fr001_004_discovery_parsing.py::test_tcFr00401_twelveThousandRecordsAcrossTenBuilds` |
| 최신 빌드 | 10 | `tests/integration/test_dashboard_route.py::test_dashboardRoute_showsLatestBuildSummary`, `tests/unit/test_latest_build.py` |
| 최신 빌드 통과 수 | 1,176 | `tests/integration/test_dashboard_route.py::test_dashboardRoute_showsLatestBuildSummary`, `tests/integration/test_snapshot_acceptance.py::test_buildSnapshot_build10HasExactCountsFromSpec` |
| 최신 빌드 실패 수 | 24 | 위와 동일 + `tests/integration/test_dashboard_route.py::test_dashboardRoute_showsTwentyFourLatestFailures`, `tests/integration/test_build_detail_route.py::test_buildDetailRoute_build10_failedOnlyToggle_matchesExactlyTwentyFourTests` |
| 최신 빌드 실패율 | 2.0% | `tests/integration/test_dashboard_route.py::test_dashboardRoute_showsLatestBuildSummary`, `tests/integration/test_snapshot_acceptance.py::test_buildSnapshot_build10HasExactCountsFromSpec` |
| 빌드별 실패율 | 8/4/9/6/3/7/5/10/4/2% | `tests/integration/test_snapshot_acceptance.py::test_buildSnapshot_perBuildFailureRatesMatchExpectedSequence`, `tests/integration/test_dashboard_route.py::test_dashboardRoute_trendMatchesExpectedFailureRateSequence` |
| §7.1 빌드 10의 모듈별 전체/실패 수 (10개 모듈 전부, 합계 1200/24) | 표 전체 | `tests/e2e/test_e2e_acc_acceptance.py::test_tcAcc007a01_allTenModulesMatchSection71TableExactly` — 10개 모듈 각각을 `§7.1` 표값과 정확히 대조하고 합계 1,200/24를 재확인하는 단일 테스트 |

## 2. §8 완료 판정 7개 조건 대응표

| § 8 조건 | 검증 테스트 | 비고 |
|---|---|---|
| (1) FR-001~036 수용 기준 전체 통과 | `tests/unit/*`, `tests/integration/*`, `tests/e2e/test_e2e_fr001_004_*.py` ~ `test_e2e_fr032_036_*.py`(FR 범위별로 파일 분리) | 각 e2e 파일명이 담당 FR 범위를 명시(`fr001_004`, `fr005_008`, `fr009_017`, `fr018_021`, `fr022_024`, `fr025_031`, `fr032_036`). 유닛 테스트는 각 집계/파싱/쿼리 모듈 1:1 대응(`test_status_resolver.py`→FR-006, `test_module_distribution.py`→FR-014/015 등) |
| (2) XML 100개 파싱, 12,000개 테스트를 중복 없이 조회 | `tests/integration/test_snapshot_acceptance.py::test_buildSnapshot_hasNoWarningsAndTwelveThousandRecords`(경고/제외 없이 정확히 12,000건), `tests/unit/test_discovery.py::test_findXmlFiles_findsXmlRecursivelyWithoutDuplicates`(동일 파일 재탐색 방지, FR-003), `tests/e2e/test_e2e_fr001_004_discovery_parsing.py::test_tcFr00401_twelveThousandRecordsAcrossTenBuilds` | |
| (3) 메인 페이지가 빌드 10을 최신 결과로 표시 | `tests/integration/test_dashboard_route.py::test_dashboardRoute_showsLatestBuildSummary`, `tests/e2e/test_e2e_fr001_004_discovery_parsing.py::test_tcFr00101_...`(`#latest-summary-heading`에 "10" 표시) | |
| (4) 실패율 트렌드 · 최신 빌드 모듈별 실패 차트 집계값이 상세 목록과 일치 | `tests/e2e/test_e2e_acc_acceptance.py::test_tcAcc00840_1_trendChartBuildTenFailedCountMatchesFailedOnlyListing`(트렌드 차트 24 == `/builds/10?failedOnly=true` 24행), `::test_tcAcc00840_2_moduleChartFailedCountsMatchEachModulesFailedOnlyListing`(모듈 차트 값 == 각 모듈 `?failedOnly=true` 행수, 모듈별 정확 일치), `::test_tcAcc00840_3_cumulativeModuleChartSumMatchesSumOfAllBuildsFailedCounts`(누적 범위 합계 696 == 빌드 이력 실패수 합계) | 세 테스트가 §8-4를 문자 그대로 구현: "집계값이 상세 목록과 일치" |
| (5) 빌드 10의 실패 전용 필터가 24개 결과 표시 | `tests/integration/test_build_detail_route.py::test_buildDetailRoute_build10_failedOnlyToggle_matchesExactlyTwentyFourTests`, `tests/e2e/test_e2e_acc_acceptance.py::test_tcAcc00840_1_...`(리스트 24행) | |
| (6) 검색 결과에서 테스트를 선택해 실패 메시지/파일/줄 번호까지 확인 | `tests/e2e/test_e2e_acc_acceptance.py::test_tcAcc00860_1_searchToFailureDetailShowsMessageFileAndLineUninterrupted` — `/search?failedOnly=true`에서 행 선택 → 상세 페이지의 실패 유형/요약/전체 본문/파일:줄 번호가 잘림 없이 노출됨을 확인 | `tests/integration/test_test_detail_route.py::test_testDetailRoute_failedTest_responseContainsFullFailureDetailVerbatim`도 실패 본문 무손실 보존을 별도로 검증 |
| (7) 손상 XML, 결과 없음, 실패 없음 조건에서 애플리케이션이 중단되지 않음 | **손상 XML**: `tests/integration/test_snapshot_warnings_route.py`(3개 테스트), `tests/e2e/test_e2e_fr032_036_navigation_state_refresh_errors.py::test_tcFr03501_...`, `::test_tcFr03502_appKeepsServingOtherPagesWithCorruptedXmlPresent`. **실패 없음**: `tests/integration/test_empty_results_route.py::test_dashboardRoute_buildWithNoFailures_*`(`zero_failures_build` 픽스처). **결과 없음**: `tests/integration/test_empty_results_route.py::test_searchRoute_noMatchingQuery_...` / `test_buildDetailRoute_filterMatchesNothing_...`(검색·필터 결과 없음) + **신규** `tests/integration/test_final_acceptance.py::test_dashboardRoute_emptyResultsRoot_showsGuidanceAndNoException`, `::test_searchRoute_emptyResultsRoot_showsGuidanceAndNoException`(빌드가 전혀 없는 결과 루트 — 검색/필터가 "0건으로 좁혀진" 경우가 아니라 애초에 빌드 자체가 없는 경우) | 아래 "발견된 격차" 참고 |

## 3. 발견된 격차와 보강 내역

기존 테스트는 §8 조건 7의 "결과 없음"을 두 가지 하위 케이스로만 다루고 있었다.

- 실패는 있지만 검색/필터 조건에 맞는 결과가 0건인 경우 (`test_empty_results_route.py`의
  `test_searchRoute_noMatchingQuery_...`, `test_buildDetailRoute_filterMatchesNothing_...`)
- 빌드는 존재하지만 실패가 0건인 경우 (`zero_failures_build` 픽스처)

그러나 **결과 루트 자체에 빌드 폴더가 전혀 없는 경우**(가장 근본적인 "결과 없음" 상태)는 라우트
수준에서 한 번도 실행되지 않았다. `dashboard.html`과 `dashboard.py`(`_splitLatestAndPrevious`)를
확인한 결과 이 경로는 이미 올바르게 구현되어 있었다(`latestSummary`가 `None`일 때
"표시할 빌드 결과가 없습니다" 안내를 렌더링), 다만 이를 실행하는 테스트가 없어 회귀 방지가
되지 않는 상태였다.

`tests/integration/test_final_acceptance.py`를 신설해 다음 3개 테스트를 TDD로 추가했다
(작성 직후 실행 시 즉시 GREEN — 기존 구현이 이미 이 경로를 올바르게 처리하고 있었음을
확인했고, 이제 회귀가 발생하면 실패하도록 고정했다):

- `test_dashboardRoute_emptyResultsRoot_showsGuidanceAndNoException`: 빈 디렉터리(빌드 0개)로
  `createApp()` 후 `GET /`가 200과 "표시할 빌드 결과가 없습니다" 안내를 반환.
- `test_searchRoute_emptyResultsRoot_showsGuidanceAndNoException`: 동일 조건에서 `GET /search`가
  200과 "조건에 맞는 테스트가 없습니다" 안내를 반환.
- `test_dashboardRoute_realDataset_isUnaffectedByEmptyRootHandling`: 가드레일 — 실제
  `GoogleTestResults`에 대해서는 이 분기가 전혀 개입하지 않고 여전히 빌드 10을 최신 결과로
  표시함을 재확인.

## 4. §4 제외 범위 점검

`src/gtestdash/` 전체를 검색한 결과 다음을 확인했다(§4.2 제외 범위 위반 없음):

- Jenkins 서버 API 직접 연동 코드 없음 — `jenkins_build_number` 등은 XML의 `<property>` 값을
  읽는 필드명일 뿐, 실제 Jenkins 서버로의 HTTP 호출은 존재하지 않는다.
- 사용자 인증/권한 관리 코드 없음 — `login`, `password`, `session[`, `flask_login`,
  `authenticate` 등의 패턴이 `src/` 어디에도 없다.
- 원본 XML을 수정하는 코드 없음 — 새로고침(`POST /refresh`, FR-034)은 다시 파싱만 하며
  `GoogleTestResults/`에 쓰기 작업을 하지 않는다.

## 5. 최종 `pytest -q` 결과

```
287 passed in 40.80s
```

(Phase 6까지의 284개 + Phase 7에서 신설한 3개 = 287개, 전체 통과. `tests/unit`, `tests/integration`,
`tests/e2e`를 모두 포함한 수치이며 `GoogleTestResults/`는 어떤 테스트에서도 수정되지 않았다.)

## 6. 결론

§8의 7개 완료 조건 모두 충족한다.

1. FR-001~036 수용 기준 전체 통과 — 예 (287개 테스트 전부 GREEN, FR 범위별 전담 테스트 파일 존재).
2. XML 100개 파싱, 12,000개 테스트 중복 없이 조회 — 예 (경고/제외 파일 0건 상태에서 정확히
   12,000건, 파일 재탐색 방지 별도 검증).
3. 메인 페이지가 빌드 10을 최신 결과로 표시 — 예.
4. 실패율 트렌드·모듈별 실패 차트 집계값이 상세 목록과 일치 — 예 (세 개의 전용 E2E 테스트로
   차트값 대 목록값을 직접 대조).
5. 빌드 10의 실패 전용 필터가 24개 결과 표시 — 예.
6. 검색 결과에서 테스트 선택 시 실패 메시지/파일/줄 번호까지 확인 가능 — 예.
7. 손상 XML/결과 없음/실패 없음 조건에서 애플리케이션이 중단되지 않음 — 예 (이번 Phase 7에서
   "빌드가 전혀 없는 결과 루트" 하위 케이스의 테스트 공백을 보강함).
