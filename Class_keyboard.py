from telebot import types



class Keyboard:
    def __init__(self):
        self.keyboard = types.InlineKeyboardMarkup()
        self.button = types.InlineKeyboardButton(text= '', callback_data='')
    def add_button(self,_text, _call_back_data):
        self.button = types.InlineKeyboardButton(text= _text, callback_data= _call_back_data)
        self.keyboard.add(self.button)
    def get_keyboard(self):
        return self.keyboard
    def __del__(self):
        del self.keyboard
        del self.button

