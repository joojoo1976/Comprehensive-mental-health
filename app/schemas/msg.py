# نماذج الرسائل البسيطة

from pydantic import BaseModel


class Msg(BaseModel):
    """
    نموذج بسيط للرسائل
    """
    msg: str
