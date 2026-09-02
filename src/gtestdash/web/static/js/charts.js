/**
 * charts.js
 * Renders the dashboard's trend line chart (FR-012/013) and module failure
 * bar chart (FR-014/015) using Chart.js, and wires point/bar clicks to their
 * drilldown URLs. Reads gtestDashData set by dashboard.html's inline script.
 */
(function () {
  "use strict";

  // Validated categorical/sequential slots from the dataviz reference palette
  // (references/palette.md): series-1 blue for normal points/bars, red for
  // the highlighted latest trend point.
  var SERIES_COLOR = "#2a78d6";
  var LATEST_COLOR = "#e34948";
  var GRIDLINE_COLOR = "#e1e0d9";

  /** Navigate the browser to a drilldown URL, ignoring clicks with no target. */
  function navigateTo(url) {
    if (url) {
      window.location.href = url;
    }
  }

  /**
   * Render the build-number-ordered failure-rate trend line, highlighting
   * the latest build's point (FR-012) and navigating to a build's detail
   * page when its point is clicked (FR-013).
   */
  function initTrendChart(canvasId, trendPoints, latestBuildId) {
    var canvas = document.getElementById(canvasId);
    if (!canvas || !trendPoints.length) {
      return null;
    }

    var pointColors = trendPoints.map(function (point) {
      return point.buildId === latestBuildId ? LATEST_COLOR : SERIES_COLOR;
    });
    var pointRadii = trendPoints.map(function (point) {
      return point.buildId === latestBuildId ? 7 : 4;
    });

    var chart = new Chart(canvas, {
      type: "line",
      data: {
        labels: trendPoints.map(function (point) { return point.buildId; }),
        datasets: [{
          label: "실패율 (%)",
          data: trendPoints.map(function (point) { return point.failureRate; }),
          borderColor: SERIES_COLOR,
          backgroundColor: SERIES_COLOR,
          pointBackgroundColor: pointColors,
          pointBorderColor: pointColors,
          pointRadius: pointRadii,
          borderWidth: 2,
          tension: 0.15,
        }],
      },
      options: {
        scales: {
          x: { title: { display: true, text: "빌드 번호" }, grid: { color: GRIDLINE_COLOR } },
          y: { title: { display: true, text: "실패율 (%)" }, beginAtZero: true, grid: { color: GRIDLINE_COLOR } },
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function (ctx) {
                var point = trendPoints[ctx.dataIndex];
                return "전체 " + point.total + ", 실패 " + point.failed + ", 실패율 " + point.failureRate + "%";
              },
            },
          },
        },
        onClick: function (_evt, elements) {
          if (elements.length) {
            navigateTo(trendPoints[elements[0].index].buildUrl);
          }
        },
      },
    });
    return chart;
  }

  /**
   * Render the latest (or scoped) module failure counts as a horizontal bar
   * chart sorted by failure count (FR-014), navigating to the module's
   * failed-only detail page when its bar is clicked (FR-015).
   */
  function initModuleChart(canvasId, moduleDistribution) {
    var canvas = document.getElementById(canvasId);
    if (!canvas || !moduleDistribution.length) {
      return null;
    }

    var chart = new Chart(canvas, {
      type: "bar",
      data: {
        labels: moduleDistribution.map(function (entry) { return entry.module; }),
        datasets: [{
          label: "실패 수",
          data: moduleDistribution.map(function (entry) { return entry.failed; }),
          backgroundColor: SERIES_COLOR,
        }],
      },
      options: {
        indexAxis: "y",
        scales: {
          x: { title: { display: true, text: "실패 수" }, beginAtZero: true, grid: { color: GRIDLINE_COLOR } },
          y: { grid: { display: false } },
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function (ctx) {
                var entry = moduleDistribution[ctx.dataIndex];
                return "실패 " + entry.failed + " / 전체 " + entry.total + " (" + entry.failureRate + "%)";
              },
            },
          },
        },
        onClick: function (_evt, elements) {
          if (elements.length) {
            navigateTo(moduleDistribution[elements[0].index].moduleUrl);
          }
        },
      },
    });
    return chart;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var data = window.gtestDashData || { trendPoints: [], moduleDistribution: [], latestBuildId: null };
    initTrendChart("trendChart", data.trendPoints, data.latestBuildId);
    initModuleChart("moduleChart", data.moduleDistribution);
  });

  window.gtestDashCharts = { initTrendChart: initTrendChart, initModuleChart: initModuleChart };
})();
