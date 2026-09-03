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


PREVIEW_BANNER = (
    '<div style="background:#fff3cd;color:#664d03;padding:10px 16px;'
    'font-size:14px;border-bottom:1px solid #ffe69c;">'
    "이 페이지는 샘플 데이터로 미리 렌더링한 정적 미리보기입니다. "
    "실제 서버가 없어 내부 링크(빌드/모듈/테스트 이동, 검색, 새로고침)는 비활성화되어 "
    "있습니다 — 실제로 써보려면 앱을 로컬에서 실행하세요(README.md 참고).</div>"
)


def rewriteStaticPaths(html):
    """! 절대 정적 자산 경로(/static/..)를 스냅샷 상대 경로(static/..)로 바꾼다."""
    return html.replace('"/static/', '"static/').replace("'/static/", "'static/")


def disableInternalNavigation(html):
    """! 서버 없이는 깨지는 내부 링크(href="/...")를 비활성화한다.

    file://로 정적 스냅샷을 열었을 때 href="/builds/10" 같은 절대 경로를 클릭하면
    브라우저가 이를 로컬 드라이브 루트 경로로 해석해 chrome-error:// 페이지로 이동하는
    문제가 있었다. 정적 자산(/static/..)이 아닌 절대 경로 href는 전부 무력화한다.
    """
    html = re.sub(
        r'href="(/(?!static/)[^"]*)"',
        r'href="javascript:void(0)" data-preview-target="\1" title="정적 미리보기 — 이동은 실제 앱 실행 후 가능합니다"',
        html,
    )
    html = re.sub(r"(<body[^>]*>)", r"\1" + PREVIEW_BANNER, html, count=1)
    return html


def disableForms(html):
    """! 검색/필터/새로고침 폼도 서버 없이는 동작하지 않으므로 제출을 막는다."""
    return re.sub(r"<form ", '<form onsubmit="return false;" ', html)


def findFirstTestDetailPath(html):
    """! 빌드 10 페이지 HTML에서 첫 번째 테스트 상세 링크 경로를 찾는다."""
    match = re.search(r'href="(/builds/10/tests/[^"?]+)', html)
    return match.group(1) if match else None


def saveSnapshot(client, urlPath, outFileName):
    """! 한 라우트를 요청해 정적 스냅샷 파일로 저장하고 저장한 HTML을 반환한다."""
    response = client.get(urlPath)
    html = rewriteStaticPaths(response.get_data(as_text=True))
    html = disableInternalNavigation(html)
    html = disableForms(html)
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
