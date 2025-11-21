import json
import logging
import asyncio
import urllib3

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet.callbacks import player as player_signals
from pyplanet.contrib.setting import Setting


class ChatRelay(AppConfig):
    name = 'ChatRelay'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.endpoint_url = 'http://localhost:3000'
        self.http_timeout = 1.0

        self.setting_endpoint_url = Setting(
            'chat_relay_webhook_url',
            'ChatRelay webhook URL',
            Setting.CAT_GENERAL,
            type=str,
            default=self.endpoint_url,
            description='Endpoint URL to receive player chat messages.'
        )

        self.setting_http_timeout = Setting(
            'chat_relay_http_timeout',
            'ChatRelay request timeout',
            Setting.CAT_GENERAL,
            type=float,
            default=self.http_timeout,
            description='How long to wait for sending chat messages.'
        )

        self.http = urllib3.PoolManager()
        self.logger = logging.getLogger(self.name)

    async def on_start(self):
        await self.context.setting.register(
            self.setting_endpoint_url,
            self.setting_http_timeout
        )

        player_signals.player_chat.register(self.on_player_chat)

    async def on_player_chat(self, *args, **kwargs):
        self.endpoint_url = await self.setting_endpoint_url.get_value()
        self.http_timeout = await self.setting_http_timeout.get_value()

        player = kwargs.get("player") if "player" in kwargs else args[0] if len(args) > 0 else None
        text = kwargs.get("text") if "text" in kwargs else args[1] if len(args) > 1 else ""
        is_command = kwargs.get("is_command") if "is_command" in kwargs else args[2] if len(args) > 2 else False

        if not player or not player.login:
            return

        payload = {
            "login": player.login,
            "nickname": player.nickname,
            "message": text,
            "is_command": is_command,
        }

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.send_message_sync, payload)

    def send_message_sync(self, payload):
        self.logger.info(f"Sending message from {payload['login']} to {self.endpoint_url}")

        try:
            body = json.dumps(payload).encode("utf-8")
            self.http.request(
                "POST",
                self.endpoint_url,
                body=body,
                headers={"Content-Type": "application/json"},
                timeout=urllib3.Timeout(connect=self.http_timeout, read=self.http_timeout),
                retries=urllib3.Retry(total=False)
            )
        except Exception as e:
            self.logger.error(f"Failed sending chat payload from {payload['login']}: {e}")
