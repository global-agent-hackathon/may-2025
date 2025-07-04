from database.models import MailTagValue

INTERNAL_ARCHIVE_TAG = "Archive"

DB_TAG_MAP = {
    MailTagValue.INBOX: "INBOX",
    MailTagValue.SENT: "SENT",
    MailTagValue.IMPORTANT: "IMPORTANT",
    MailTagValue.ARCHIVE: INTERNAL_ARCHIVE_TAG,
}