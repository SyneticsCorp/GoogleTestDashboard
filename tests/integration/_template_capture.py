"""!
@file _template_capture.py
@brief Shared render_template() context capture helper for Phase 6's new
       integration tests, so the Flask template_rendered wiring is defined
       once instead of duplicated per test file (CLAUDE.md no-duplicate rule).
"""
from contextlib import contextmanager

from flask import template_rendered


@contextmanager
def capturedTemplateContext(app):
    """!
    @brief Capture the context dict passed to render_template() during a request.
    @param app Flask app instance whose template_rendered signal to observe.
    @return List that will hold one context dict per template render, in order.
    """
    captured = []

    def _record(_sender, template, context, **_extra):
        captured.append(context)

    template_rendered.connect(_record, app)
    try:
        yield captured
    finally:
        template_rendered.disconnect(_record, app)
