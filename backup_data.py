#!/usr/bin/env python3


import smtplib
from datetime import date
from subprocess import run
from email.mime.text import MIMEText
from pathlib import Path

BACKUP_PATH = Path("/media/Data_Backup/")
DATA_PATH = Path("/media/xxx/")

EMAIL_HOST = "mail.gmx.net"
FROM_EMAIL = "xxx@yyy.de"
EMAIL_PASSWORD = "xxxx"
TO_EMAIL = "xxx@zzz.de"


def search_old_backups(date_today):
    if not next(BACKUP_PATH.glob(f"{date_today:%Y}-*"), None):
        return "full"
    else:
        return "hardlinks"


def make_backup(backup_mode, date_today):
    log_file = BACKUP_PATH / "Logs" / f"{date_today:%Y-%m-%d}.log"
    command = [
        "rsync",
        "-vahHA",
        f"--log-file={log_file}",
        DATA_PATH,
        BACKUP_PATH / f"{date_today:%Y-%m-%d}",
    ]
    if backup_mode == "hardlinks":
        hardlink_folder = max(BACKUP_PATH.iterdir())
        command.append(f"--link-dest={hardlink_folder}")
        text = "Hardlinks-Backup"
    else:
        text = "Full-Backup - Extern sichern!"
    run(command, check=True)
    return text


def send_mail(state, text):
    message = MIMEText(text)
    message["Subject"] = state
    message["From"] = FROM_EMAIL
    message["To"] = TO_EMAIL
    with smtplib.SMTP_SSL(EMAIL_HOST) as server:
        server.login(FROM_EMAIL, EMAIL_PASSWORD)
        server.sendmail(FROM_EMAIL, TO_EMAIL, message.as_string())


def main():
    try:
        run(["mount", BACKUP_PATH], check=True)
        date_today = date.today()
        backup_mode = search_old_backups(date_today)
        text = make_backup(backup_mode, date_today)
        run(["umount", BACKUP_PATH], check=True)
        send_mail("Backup erfolgreich!", text)
    except Exception as e:
        send_mail("Backup nicht erfolgreich!", str(e))


if __name__ == "__main__":
    main()
