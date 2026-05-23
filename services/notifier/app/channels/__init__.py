"""Channels module."""
from app.channels.base import BaseChannel
from app.channels.dingtalk import DingTalkChannel
from app.channels.wechat import WeChatChannel
from app.channels.feishu import FeishuChannel
from app.channels.sms import SmsChannel
from app.channels.email import EmailChannel
from app.channels.webhook import WebhookChannel

CHANNEL_MAP: dict[str, type[BaseChannel]] = {
    "dingtalk": DingTalkChannel,
    "wechat": WeChatChannel,
    "feishu": FeishuChannel,
    "sms": SmsChannel,
    "email": EmailChannel,
    "webhook": WebhookChannel,
}
