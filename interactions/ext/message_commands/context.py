from interactions import Channel, Context, Guild, Message
from typing import Optional


class MessageContext(Context):
    """Context for message-based commands"""

    def __init__(self, _client, **kwargs):
        super().__init__(**kwargs)
        self._client = _client
        self.channel._json["_client"] = _client
        self.channel = Channel(**self.channel._json)
        self.guild._json["_client"] = _client
        self.guild = Guild(**self.guild._json)

    async def send(
        self,
        content: Optional[str] = None,
        *,
        tts: Optional[bool] = False,
        # attachments: Optional[List[Any]] = None,  # TODO: post-v4: Replace with own file type.
        embeds=None,
        allowed_mentions=None,
        components=None,
    ) -> Message:
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
        return await self.channel.send(
            content,
            tts=tts,
            # attachments=attachments,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
        )
