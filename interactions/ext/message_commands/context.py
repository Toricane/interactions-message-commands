from interactions import ActionRow, Button, Context, Message, SelectMenu
from typing import List, Optional


class MessageContext(Context):
    """Context for message-based commands"""

    def __init__(self, _client, **kwargs):
        super().__init__(**kwargs)
        self._client = _client

    async def send(
        self,
        content: Optional[str] = None,
        *,
        tts: Optional[bool] = False,
        # attachments: Optional[List[Any]] = None,  # TODO: post-v4: Replace with own file type.
        embeds=None,
        allowed_mentions=None,
        components=None,
    ):
        """
        Sends a message in the channel

        :param content?: The contents of the message as a string or string-converted value.
        :type content: Optional[str]
        :param tts?: Whether the message utilizes the text-to-speech Discord programme or not.
        :type tts: Optional[bool]
        :param embeds?: An embed, or list of embeds for the message.
        :type embeds: Optional[Union[Embed, List[Embed]]]
        :param allowed_mentions?: The message interactions/mention limits that the message can refer to.
        :type allowed_mentions: Optional[MessageInteraction]
        :param components?: A component, or list of components for the message.
        :type components: Optional[Union[ActionRow, Button, SelectMenu, List[Union[ActionRow, Button, SelectMenu]]]]
        :return: The sent message as an object.
        :rtype: Message

        ```py
        await ctx.send(content="Hello world!")
        ```
        """
        _content: str = "" if content is None else content
        _tts: bool = False if tts is None else tts
        # _file = None if file is None else file
        # _attachments = [] if attachments else None
        _embeds: list = []
        _allowed_mentions: dict = {} if allowed_mentions is None else allowed_mentions
        _components: List[dict] = [{"type": 1, "components": []}]
        if embeds:
            if isinstance(embeds, list):
                _embeds = [embed._json for embed in embeds]
            else:
                _embeds = [embeds._json]

        # TODO: Break this obfuscation pattern down to a "builder" method.
        if components:
            if isinstance(components, list) and all(
                isinstance(action_row, ActionRow) for action_row in components
            ):
                _components = [
                    {
                        "type": 1,
                        "components": [
                            (
                                component._json
                                if component._json.get("custom_id")
                                or component._json.get("url")
                                else []
                            )
                            for component in action_row.components
                        ],
                    }
                    for action_row in components
                ]
            elif isinstance(components, list) and all(
                isinstance(component, (Button, SelectMenu)) for component in components
            ):
                for component in components:
                    if isinstance(component, SelectMenu):
                        component._json["options"] = [
                            options._json if not isinstance(options, dict) else options
                            for options in component._json["options"]
                        ]
                _components = [
                    {
                        "type": 1,
                        "components": [
                            (
                                component._json
                                if component._json.get("custom_id")
                                or component._json.get("url")
                                else []
                            )
                            for component in components
                        ],
                    }
                ]
            elif isinstance(components, list) and all(
                isinstance(action_row, (list, ActionRow)) for action_row in components
            ):
                _components = []
                for action_row in components:
                    for component in (
                        action_row
                        if isinstance(action_row, list)
                        else action_row.components
                    ):
                        if isinstance(component, SelectMenu):
                            component._json["options"] = [
                                option._json for option in component.options
                            ]
                    _components.append(
                        {
                            "type": 1,
                            "components": [
                                (
                                    component._json
                                    if component._json.get("custom_id")
                                    or component._json.get("url")
                                    else []
                                )
                                for component in (
                                    action_row
                                    if isinstance(action_row, list)
                                    else action_row.components
                                )
                            ],
                        }
                    )
            elif isinstance(components, ActionRow):
                _components[0]["components"] = [
                    (
                        component._json
                        if component._json.get("custom_id")
                        or component._json.get("url")
                        else []
                    )
                    for component in components.components
                ]
            elif isinstance(components, Button):
                _components[0]["components"] = (
                    [components._json]
                    if components._json.get("custom_id") or components._json.get("url")
                    else []
                )
            elif isinstance(components, SelectMenu):
                components._json["options"] = [
                    options._json if not isinstance(options, dict) else options
                    for options in components._json["options"]
                ]
                _components[0]["components"] = (
                    [components._json]
                    if components._json.get("custom_id") or components._json.get("url")
                    else []
                )
        else:
            _components = []

        # TODO: post-v4: Add attachments into Message obj.
        payload = Message(
            content=_content,
            tts=_tts,
            # file=file,
            # attachments=_attachments,
            embeds=_embeds,
            allowed_mentions=_allowed_mentions,
            components=_components,
        )

        res = await self._client.create_message(
            channel_id=int(self.channel.id), payload=payload._json
        )
        return Message(**res, _client=self._client)
