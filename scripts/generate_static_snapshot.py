#!/usr/bin/env python3
"""! @file generate_static_snapshot.py
@brief 샘플 데이터(GoogleTestResults)로 앱을 렌더링해 target/에 정적 HTML 스냅샷을 생성한다.

Flask test client로 주요 화면을 요청해 응답 HTML을 파일로 저장하고, 정적 자산(css/js)을
target/static/로 복사한 뒤 페이지 안의 절대 경로(`/static/...`)를 상대 경로로 바꾼다.
빌드/모듈/테스트 간 내부 링크(`/builds/...` 등)는 실제 서버 없이는 동작하지 않는
미리보기용 스냅샷이라는 점을 README.md에 함께 안내한다.
"""
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from gtestdash.web.app import createApp  # noqa: E402

TARGET_DIR = REPO_ROOT / "target"
STATIC_SRC = REPO_ROOT / "src" / "gtestdash" / "web" / "static"


def rewriteStaticPaths(html):
    """! 절대 정적 자산 경로(/static/..)를 스냅샷 상대 경로(static/..)로 바꾼다."""
    return html.replace('"/static/', '"static/').replace("'/static/", "'static/")


def findFirstTestDetailPath(html):
    """! 빌드 10 페이지 HTML에서 첫 번째 테스트 상세 링크 경로를 찾는다."""
    match = re.search(r'href="(/builds/10/tests/[^"?]+)', html)
    return match.group(1) if match else None


def saveSnapshot(client, urlPath, outFileName):
    """! 한 라우트를 요청해 정적 스냅샷 파일로 저장하고 저장한 HTML을 반환한다."""
    response = client.get(urlPath)
    html = rewriteStaticPaths(response.get_data(as_text=True))
    outFile = TARGET_DIR / outFileName
    outFile.write_text(html, encoding="utf-8")
    print(f"{urlPath} -> target/{outFileName} ({response.status_code}, {len(html)} bytes)")
    return html


def main():
    """! 정적 스냅샷 5종을 생성한다: 대시보드/빌드 상세/모듈 상세/테스트 상세/검색 결과."""
    TARGET_DIR.mkdir(exist_ok=True)
    if (TARGET_DIR / "static").exists():
        shutil.rmtree(TARGET_DIR / "static")
    shutil.copytree(STATIC_SRC, TARGET_DIR / "static")

    app = createApp(str(REPO_ROOT / "GoogleTestResults"))
    with app.test_client() as client:
        saveSnapshot(client, "/", "index.html")
        saveSnapshot(client, "/builds/10", "build_10.html")
        saveSnapshot(client, "/builds/10/modules/ChildLockController", "module_child_lock_controller.html")

        failedOnlyResponse = client.get("/builds/10?failedOnly=true")
        failedOnlyHtml = failedOnlyResponse.get_data(as_text=True)
        testDetailPath = findFirstTestDetailPath(failedOnlyHtml)
        if testDetailPath:
            saveSnapshot(client, testDetailPath, "test_detail_example.html")
        else:
            print("경고: 실패 전용 빌드 10 페이지에서 테스트 상세 링크를 찾지 못했습니다.")

        saveSnapshot(client, "/search?status=FAILED", "search_results_failed.html")

    print("\n완료: target/ 아래 정적 스냅샷 생성됨.")


if __name__ == "__main__":
    main()
