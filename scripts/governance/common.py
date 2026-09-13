from __future__ import annotations

import json
import re
import urllib.error
import urllib.request


class GitHubAPIError(RuntimeError):
    pass


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def exactly_one(pattern: str, text: str, field: str, *, flags: int = re.M) -> str:
    matches = re.findall(pattern, text, flags=flags)
    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one valid `{field}` field; found {len(matches)}."
        )
    match = matches[0]
    if isinstance(match, tuple):
        if len(match) != 1:
            raise ValueError(f"Pattern for `{field}` must capture exactly one value.")
        return match[0]
    return match


def github_get_json(url: str, token: str, user_agent: str) -> object:
    if not token:
        raise GitHubAPIError("GitHub token is missing.")
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": user_agent,
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise GitHubAPIError(f"GitHub API returned HTTP {exc.code}.") from exc
    except urllib.error.URLError as exc:
        raise GitHubAPIError(f"GitHub API request failed: {exc.reason}.") from exc
    except json.JSONDecodeError as exc:
        raise GitHubAPIError("GitHub API returned invalid JSON.") from exc
