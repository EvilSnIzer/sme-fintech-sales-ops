"""Send alerts to Slack or fall back to a local file when no webhook is set.

I chose Slack because email reports often get buried. Slack keeps the daily
ops signal visible in the team channel.
"""
import json
import os
from datetime import datetime
from urllib.parse import urljoin

import requests

from src.config import SLACK_ENABLED, SLACK_WEBHOOK_URL, SLACK_CHANNEL


def _format_currency(value) -> str:
    try:
        return f"${int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def send_slack_alert(
    stalled_count: int,
    at_risk_count: int,
    open_pipeline: int,
    report_path: str,
) -> str:
    """Post a short daily summary to Slack, or save it locally if not configured."""
    today = datetime.now().strftime("%Y-%m-%d")
    text = (
        f"📊 *SME Fintech Sales Ops — {today}*\n"
        f"• Open pipeline: {_format_currency(open_pipeline)}\n"
        f"• Stalled deals: {stalled_count}\n"
        f"• At-risk accounts: {at_risk_count}\n"
        f"• Full report: `{os.path.basename(report_path)}`"
    )

    payload = {
        "channel": SLACK_CHANNEL,
        "username": "sales-ops-bot",
        "text": text,
        "icon_emoji": ":chart_with_upwards_trend:",
    }

    if not SLACK_ENABLED:
        # Save the message so the team can still see what would be sent.
        alert_dir = "outputs/alerts"
        os.makedirs(alert_dir, exist_ok=True)
        alert_path = os.path.join(
            alert_dir,
            f"slack_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        with open(alert_path, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"Slack disabled. Message saved to {alert_path}")
        return alert_path

    if not SLACK_WEBHOOK_URL:
        raise ValueError("SLACK_WEBHOOK_URL must be set when SLACK_ENABLED=true")

    response = requests.post(
        SLACK_WEBHOOK_URL,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    print(f"Slack alert sent to {SLACK_CHANNEL}")
    return ""
