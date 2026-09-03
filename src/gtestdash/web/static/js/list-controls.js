/**
 * @file list-controls.js
 * @brief Progressive enhancement for the shared search/filter/sort form
 *        (_list_controls.html, form.query-controls): auto-submits the form
 *        the moment a checkbox or <select> changes, so "실패 테스트만" and
 *        the status/module/함수·스위트/정렬/페이지 크기 controls apply
 *        immediately instead of requiring a separate "적용" click.
 *
 *        The free-text search input (input[type=search]) is intentionally
 *        left alone -- it still only submits on Enter or the "적용" button,
 *        since submitting on every keystroke would be disruptive.
 *
 *        Without this script the form still works exactly as before (plain
 *        GET submission via the "적용" button) -- this is an enhancement
 *        layered on top, not a replacement.
 */
(function attachAutoSubmitBehavior() {
  "use strict";

  /**
   * @brief Wire one query-controls form so any checkbox/select change
   *        inside it submits the form immediately.
   * @param form The form.query-controls element to enhance.
   */
  function enhanceForm(form) {
    var autoSubmitControls = form.querySelectorAll("input[type='checkbox'], select");
    autoSubmitControls.forEach(function attachChangeListener(control) {
      control.addEventListener("change", function submitOnChange() {
        if (typeof form.requestSubmit === "function") {
          form.requestSubmit();
        } else {
          form.submit();
        }
      });
    });
  }

  document.querySelectorAll("form.query-controls").forEach(enhanceForm);
})();
