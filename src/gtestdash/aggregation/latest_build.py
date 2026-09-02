"""!
@file latest_build.py
@brief Latest-build resolution (FR-009).

Each ResultRecord's build_id already folds jenkins_build_number and the
folder-name fallback together (see record_builder.buildNormalizedRecord), so
only two tiers remain to distinguish here: the highest numeric build id, and
- when no build id is numeric at all - the latest build timestamp.
"""


def resolveLatestBuild(builds):
    """!
    @brief Pick the latest build among per-build identity dicts (FR-009).
    @param builds List of dicts, each with "buildId" (str) and "buildTimestamp"
           (str or None) keys - e.g. the summaries from
           aggregation.build_history.summarizeBuildsByBuild().
    @return The build dict judged latest: the highest numeric buildId when any
            exist, otherwise the one with the greatest buildTimestamp; None
            when builds is empty (FR-036 spirit: no data, no crash).
    """
    if not builds:
        return None

    numericBuilds = [build for build in builds if str(build["buildId"]).isdigit()]
    if numericBuilds:
        return max(numericBuilds, key=lambda build: int(build["buildId"]))

    return max(builds, key=lambda build: build.get("buildTimestamp") or "")
