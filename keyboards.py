
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

class KeyBoards():
    def __init__(self,resize_keyboard=False,one_time_keyboard=False):
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.rows = [[]]

    def addButton(self,text,request_contact=False,request_location=False,one_row=False):
        if one_row is True:
            self.addRow()
        self.rows[len(self.rows)-1].append(KeyboardButton(text=text,request_contact=request_contact,request_location=request_location))

        if len(self.rows[len(self.rows)-1]) > 12:
            raise ValueError('Max 12 buttons on a line! Check addButton on block {0}'.format(len(self.rows)))

        if sum(len(i) for i in self.rows) > 300:
            print(len(self.rows))
            raise ValueError('Raised Max 300 elements!')

        if one_row is True:
            self.addRow()

    def addRow(self):
        self.rows.append([])

    def deleteKeyboard(self):
        return ReplyKeyboardRemove()

    def getKeyboard(self):
        return ReplyKeyboardMarkup(self.rows,resize_keyboard=self.resize_keyboard,one_time_keyboard=self.one_time_keyboard)

class InLineKeyBoards():
    def __init__(self):
        self.rows = [[]]

    def addButton(self,text,callback_data='',one_row=False,new_row=False):
        if one_row is True:
            self.addRow()

        if new_row is True:
            self.addRow()

        self.rows[len(self.rows)-1].append(InlineKeyboardButton(text=text,callback_data=callback_data))
        
        if len(self.rows[len(self.rows)-1]) > 8:
            raise ValueError('Max 8 buttons on a line! Check addButton on block {0}'.format(len(self.rows)))
        
        if sum(len(i) for i in self.rows) > 100:
            raise ValueError('Raised Max 100 elements!')

        if one_row is True:
            self.addRow()

    def addRow(self):
        self.rows.append([])

    def deleteKeyboard(self):
        return ReplyKeyboardRemove()

    def getKeyboard(self):
        return InlineKeyboardMarkup(inline_keyboard=self.rows)

'''
k = KeyBoards()


for z in range(300):
    
    for i in range(1):
        k.addButton(i)
    k.addRow()
print(k.getKeyboard())
'''