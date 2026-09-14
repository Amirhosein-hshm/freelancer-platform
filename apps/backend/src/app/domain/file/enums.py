from enum import StrEnum


class FileAssetContext(StrEnum):
    RESUME = "resume"
    PORTFOLIO = "portfolio"
    DELIVERY = "delivery"
    TICKET_ATTACHMENT = "ticket_attachment"
    GENERIC = "generic"
