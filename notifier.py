"""
Notifications
==============
Desktop toast notifications when new jobs are found.
Optional email alerts (configure in config.py).
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from config import (
    ENABLE_DESKTOP_NOTIFICATIONS,
    EMAIL_ENABLED,
    EMAIL_TO,
    EMAIL_FROM,
    EMAIL_PASSWORD,
    SMTP_SERVER,
    SMTP_PORT,
)


def notify_new_jobs(new_jobs, total_jobs):
    """Send notifications about new jobs found."""
    if not new_jobs:
        return

    count = len(new_jobs)
    print(f"\n  🔔 {count} NEW job(s) found!")

    # Desktop notification
    if ENABLE_DESKTOP_NOTIFICATIONS:
        send_desktop_notification(new_jobs)

    # Email notification
    if EMAIL_ENABLED and EMAIL_TO:
        send_email_notification(new_jobs, total_jobs)


def send_desktop_notification(new_jobs):
    """Send a Windows toast notification."""
    count = len(new_jobs)

    # Build notification message
    if count == 1:
        job = new_jobs[0]
        title = "New Job Found! 🎯"
        message = f"{job['title']} at {job['company']}"
    else:
        title = f"{count} New Jobs Found! 🎯"
        # Show top 3
        top_jobs = new_jobs[:3]
        lines = [f"• {j['title']} @ {j['company']}" for j in top_jobs]
        if count > 3:
            lines.append(f"  ...and {count - 3} more")
        message = "\n".join(lines)

    try:
        # Try using win10toast if available
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(
                title,
                message[:256],
                duration=10,
                threaded=True,
            )
            return
        except ImportError:
            pass

        # Fallback: use PowerShell toast notification (works on Windows 10/11)
        # Escape quotes for PowerShell
        ps_title = title.replace("'", "''")
        ps_message = message.replace("'", "''").replace("\n", ". ")[:200]

        ps_script = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$template = @'
<toast>
    <visual>
        <binding template="ToastText02">
            <text id="1">{ps_title}</text>
            <text id="2">{ps_message}</text>
        </binding>
    </visual>
</toast>
'@
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Job Search Automation").Show($toast)
"""
        # Write script to temp file and execute
        script_path = os.path.join(os.environ.get("TEMP", "."), "job_notify.ps1")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(ps_script)

        os.system(f'powershell -ExecutionPolicy Bypass -File "{script_path}"')

    except Exception as e:
        # Fallback: just print to console
        print(f"  [Notification] {title}: {message}")


def send_email_notification(new_jobs, total_jobs):
    """Send email notification with new jobs."""
    if not EMAIL_TO or not EMAIL_FROM or not EMAIL_PASSWORD:
        return

    try:
        # Build email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🎯 {len(new_jobs)} New Remote Internships Found!"
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO

        # HTML email body
        html = build_email_html(new_jobs, total_jobs)
        msg.attach(MIMEText(html, "html"))

        # Send
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"  📧 Email sent to {EMAIL_TO}")

    except Exception as e:
        print(f"  [Email Error] {e}")


def build_email_html(new_jobs, total_jobs):
    """Build HTML email body."""
    rows = ""
    for job in new_jobs[:20]:  # Max 20 jobs in email
        salary = job.get("salary", "Not specified")
        link = job.get("link", "#")
        rows += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">
                <a href="{link}" style="color: #2563eb; text-decoration: none; font-weight: bold;">
                    {job.get('title', 'N/A')}
                </a>
            </td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{job.get('company', 'N/A')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{salary}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{job.get('source', '')}</td>
        </tr>
        """

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #1e293b;">🎯 {len(new_jobs)} New Remote Internships Found!</h2>
        <p style="color: #64748b;">Found on {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <tr style="background: #f1f5f9;">
                <th style="padding: 10px; text-align: left;">Role</th>
                <th style="padding: 10px; text-align: left;">Company</th>
                <th style="padding: 10px; text-align: left;">Salary</th>
                <th style="padding: 10px; text-align: left;">Source</th>
            </tr>
            {rows}
        </table>
        <p style="margin-top: 20px; color: #64748b; font-size: 14px;">
            Total jobs tracked: {total_jobs} | Open jobs_found.csv for full list
        </p>
    </body>
    </html>
    """
    return html
