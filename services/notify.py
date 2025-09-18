from __future__ import annotations

import json
import os
from typing import Optional
from urllib import request as urlrequest


class SlackNotifier:
    """Send simple Slack messages via an incoming webhook URL in SLACK_WEBHOOK_URL."""

    def __init__(self, webhook_url: Optional[str] = None) -> None:
        self.webhook_url = webhook_url or os.environ.get('SLACK_WEBHOOK_URL')

    def send(self, text: str) -> bool:
        if not self.webhook_url:
            return False
        try:
            data = json.dumps({'text': text}).encode('utf-8')
            req = urlrequest.Request(self.webhook_url, data=data, headers={'Content-Type': 'application/json'})
            with urlrequest.urlopen(req, timeout=5) as resp:
                return resp.status in (200, 204)
        except Exception:
            return False

