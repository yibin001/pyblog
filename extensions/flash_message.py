# -*- coding: UTF-8 -*-
import tornado


class FlashMessage(object):
    _cookie_name = 'flash'

    def flash(self, message, category='message'):
        messages = self.messages()
        messages.append((category, message))
        self.set_secure_cookie(self._cookie_name, tornado.escape.json_encode(messages), expires_days=None)

    def messages(self):
        messages = self.get_secure_cookie(self._cookie_name)
        messages = tornado.escape.json_decode(messages) if messages else []
        return messages

    def get_flashed_messages(self):
        messages = self.messages()
        self.clear_cookie(self._cookie_name)
        return messages
