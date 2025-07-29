from aiogram.types import Message


    
class TestingMessage(Message):
    # _testing_msg: Message

    async def reply(self, text, *args, parse_mode=None, **kwargs):
        try:
            res = await super().reply(*args, text, **kwargs, parse_mode=parse_mode)
            return res
        except Exception as ex:
            text = f'<blockquote>replied from {self.from_user.full_name}:\n{self.text}</blockquote>\n{text}'
            res = await super().answer(*args, text, **kwargs, parse_mode='html')
            return res
