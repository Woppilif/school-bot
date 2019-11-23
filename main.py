import DORM
from schoold.models import *

import logging
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, LabeledPrice)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler,PreCheckoutQueryHandler)
from keyboards import KeyBoards, InLineKeyBoards
from datetime import date,datetime, timedelta
import random
import time
from django.db.models import Q
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

GROUP_LEVEL, GROUP_NAME, GROUP_DAYS_ONE, GROUP_DAYS_TWO, GROUP_TIMES_ONE, GROUP_TIMES_TWO, GROUP_MEMBERS = range(7)

NAME, AGE, PHONE, GROUP = range(4)
TRIAL_AGE, TRIAL_DATE, TRIAL_TIME = range(3)

teachers = ['Марина','Катя','Настя','Ашот','Ферверхмаксудизин']

times = ['12:45','16:36','18:35','08:46','15:14']

days = ['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВС']

excluded = []

memlist = ['A','B','C','D','E','F','J','K','L']

GROUP_DATA = {
    "name":None,
    "level":None,
    "date_one":None,
    "date_two":None,
    "time_one":None,
    "time_two":None,
    "members":[]
}

LESSON_MEMBER = 0

TEMP_DATA = []

def user_obj(update):
    obj, created = Users.objects.update_or_create(
        id = update.message.from_user.id
        #first_name = update.message.from_user.first_name,
        #last_name = update.message.from_user.last_name
    )
    return obj

def start(update, context):
    update.message.reply_text(
        'Привет! Это бот школы Алгоритм языка!'
        'Сейчас вы пройдёте короткую регистрацию. Для отмены введите /cancel\n\n'
        'Укажите Ваше имя')
    context.bot.send_document(update.message.from_user.id,"https://psv4.userapi.com/c848124/u151064932/docs/d16/5dabb0e72ce5/1_Barashkova_-_Glagoly_be_have_can_must.pdf?extra=n6EwAOaZFyYJ_xqeSb4WnkNuS4iq6uJnxANldC4BiP0b8fHE3ALlVC21nwT5qS9vv0bBekSz8ez41k33T-bt28pBk8Wxu2xzKqVFWuvRQQfA7jTrq5ZWQ0KSqgG8K-Pl81i9a01ZvkgoZedYxRSUhA&dl=1")
    print(user_obj(update))
    return NAME

def name(update, context):
    keyboard = KeyBoards()
    for i in Age.objects.all():
        keyboard.addButton(i.age)
    user = update.message.from_user
    logger.info("Name of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Отлично! Теперь нам необходимо знать возраст нашего нового ученика!',reply_markup=keyboard.getKeyboard())
    u = user_obj(update)
    u.first_name = update.message.text
    u.save()
    return AGE

def age(update, context):
    user = update.message.from_user
    logger.info("Age of %s: %s", user.first_name, update.message.text)
    keyboard = KeyBoards()
    keyboard.addButton('Отправить номер телефона',request_contact=True)
    update.message.reply_text('Замечательно! Сейчас, отправьте мне ваш контакт.',reply_markup=keyboard.getKeyboard())
    u = user_obj(update)
    u.age = Age.objects.get(age=update.message.text)
    u.save()
    return PHONE

def phone(update, context):
    user = update.message.from_user
    logger.info("Phone of %s: %s", user.first_name, update.message.text)
    keyboard = KeyBoards()
    for i in Trial.objects.filter(status=True):
        keyboard.addButton('{0}'.format(i.date),one_row=True)
    
    update.message.reply_text('Замечательно! Теперь осталось выбрать подходящее время для пробного занятия.',reply_markup=keyboard.getKeyboard())
    u = user_obj(update)
    u.phone = update.message.contact.phone_number
    u.save()
    return GROUP

def group(update, context):
    user = update.message.from_user
    chat_id = update.message.chat_id
    logger.info("Date of %s: %s", user.first_name, update.message.text)
    trial_o = Trial.objects.get(date=update.message.text)
    update.message.reply_text('Отлично!\nВаш преподаватель: {0}\nБудет ждать вас {1} часов по адресу: Салиха Батыева.\nМы пришлём вам уведомление в этот день!'.format(trial_o.teacher,trial_o.date),reply_markup=ReplyKeyboardRemove())
    t_group = TrialGroups.objects.create(trial=trial_o,student=user_obj(update))
    new_job = context.job_queue.run_once(alarm, 60, context=chat_id)
    context.chat_data['job'] = new_job
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def alarm(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Это уведомление, которое пришло через минуту оно может приходить конкретному пользователю КОГДА будет нужно!')
'''
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
'''
def trial_start(update, context):
    if user_obj(update).role != 2:
        return None
    keyboard = KeyBoards()
    for i in Age.objects.all():
        keyboard.addButton(i.age)
    update.message.reply_text('Пожалуйста укажите возрастную группу для пробного занятия',reply_markup=keyboard.getKeyboard())
    return TRIAL_AGE

def trial_age(update, context):
    user = update.message.from_user
    if user_obj(update).role != 2:
        return None
    logger.info("Trial Age of %s: %s", user.first_name, update.message.text)
    keyboard = KeyBoards()
    for i in range(8):
        keyboard.addButton('{0}'.format(date.today() + timedelta(days=i)),one_row=True)
    update.message.reply_text('Замечательно! Теперь осталось выбрать дату для пробного занятия.',reply_markup=keyboard.getKeyboard())
    Trial.objects.create(
        teacher = user_obj(update),
        age = Age.objects.get(age=update.message.text)
    )
    return TRIAL_DATE

def trial_date(update, context):
    user = update.message.from_user
    logger.info("Trial Date of %s: %s", user.first_name, update.message.text)
    t_obj = Trial.objects.filter(teacher = user_obj(update)).last()
    t_obj.date = update.message.text
    t_obj.save()
    keyboard = KeyBoards()
    for i in range(8,20):
        '''
        if i < time.localtime().tm_hour:
            continue
        '''
        keyboard.addButton('{0}:00'.format(i),one_row=True)
    update.message.reply_text('Замечательно! Теперь осталось выбрать время для пробного занятия.',reply_markup=keyboard.getKeyboard())
    return TRIAL_TIME

def trial_time(update, context):
    user = update.message.from_user
    chat_id = update.message.chat_id
    logger.info("Trial time of %s: %s", user.first_name, update.message.text)
    t_obj = Trial.objects.filter(teacher = user_obj(update)).last()
    t_obj.date = datetime(year=t_obj.date.year,month=t_obj.date.month,day=t_obj.date.day,hour=int(update.message.text.split(':')[0]))
    t_obj.status = True
    t_obj.save()
    update.message.reply_text('Отлично! Система пришлёт уведомление в день занятия',
                              reply_markup=ReplyKeyboardRemove())
    new_job = context.job_queue.run_once(alarm, 60, context=chat_id)
    context.chat_data['job'] = new_job
    return ConversationHandler.END

def group_start(update, context):
    keyboard = KeyBoards()
    Group.objects.create(teacher=user_obj(update))
    for i in Level.objects.all():
        keyboard.addButton(i.level)
    update.message.reply_text('Пожалуйста укажите уровень группы',reply_markup=keyboard.getKeyboard())
    return GROUP_LEVEL

def group_level(update, context):
    user = update.message.from_user
    t_obj = Group.objects.filter(teacher = user_obj(update)).last()
    t_obj.level = Level.objects.get(level=update.message.text)
    t_obj.save()
    #GROUP_DATA['level'] = update.message.text
    logger.info("Level of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Отлично! Теперь укажите название группы',reply_markup=ReplyKeyboardRemove())
    return GROUP_NAME

def group_name(update, context):
    user = update.message.from_user
    logger.info("Name of %s: %s", user.first_name, update.message.text)
    t_obj = Group.objects.filter(teacher = user_obj(update)).last()
    t_obj.name = update.message.text
    t_obj.save()
    #GROUP_DATA['name'] = update.message.text
    keyboard = KeyBoards()
    for i in days:
        keyboard.addButton(i)
    update.message.reply_text('Отлично! Теперь выберите первый день занятия',reply_markup=keyboard.getKeyboard())
    return GROUP_DAYS_ONE

def get_date(day_name):
    today = datetime.now().date()
    start = today - timedelta(days=today.weekday())
    dates = [start + timedelta(days=i) for i in range(7)]
    x = 0
    for i in days:
        if i == day_name:
            return dates[x]
        x+=1
    return None

def group_days_one(update, context):
    user = update.message.from_user
    logger.info("Days of %s: %s", user.first_name, update.message.text)
    t_obj = Group.objects.filter(teacher = user_obj(update)).last()
    t_obj.first_date = get_date(update.message.text)
    t_obj.save()
    #GROUP_DATA['date_one'] = update.message.text
    keyboard = KeyBoards()
    for i in days:
        if i == update.message.text:
            continue
        keyboard.addButton(i)
    update.message.reply_text('А теперь второй день занятия',reply_markup=keyboard.getKeyboard())
    return GROUP_DAYS_TWO

def group_days_two(update, context):
    user = update.message.from_user
    logger.info("Days of %s: %s", user.first_name, update.message.text)
    t_obj = Group.objects.filter(teacher = user_obj(update)).last()
    t_obj.second_date = get_date(update.message.text)
    t_obj.save()
    #GROUP_DATA['date_two'] = update.message.text
    keyboard = KeyBoards()
    for i in range(8,20):
        '''
        if i < time.localtime().tm_hour:
            continue
        '''
        keyboard.addButton('{0}:00'.format(i),one_row=True)
    update.message.reply_text('Укажите время для первого',reply_markup=keyboard.getKeyboard())
    return GROUP_TIMES_ONE

def group_times_one(update, context):
    user = update.message.from_user
    logger.info("Times of %s: %s", user.first_name, update.message.text)
    t_obj = Group.objects.filter(teacher = user_obj(update)).last()
    t_obj.first_date = datetime(year=t_obj.first_date.year,month=t_obj.first_date.month,day=t_obj.first_date.day,hour=int(update.message.text.split(':')[0]))
    t_obj.save()
    #GROUP_DATA['time_one'] = update.message.text
    keyboard = KeyBoards()
    for i in range(8,20):
        '''
        if i < time.localtime().tm_hour:
            continue
        '''
        keyboard.addButton('{0}:00'.format(i),one_row=True)
    update.message.reply_text('Укажите время для второго',reply_markup=keyboard.getKeyboard())
    return GROUP_TIMES_TWO

def group_times_two(update, context):
    user = update.message.from_user
    t_obj = Group.objects.filter(teacher = user_obj(update)).last()
    t_obj.second_date = datetime(year=t_obj.second_date.year,month=t_obj.second_date.month,day=t_obj.second_date.day,hour=int(update.message.text.split(':')[0]))
    t_obj.save()
    #GROUP_DATA['time_two'] = update.message.text
    #memlist.append(user.id)
    #GROUP_DATA['members'] = []

    logger.info("Times of %s: %s", user.first_name, update.message.text)
    keyboard = KeyBoards()
    for i in TrialGroups.objects.filter(trial__teacher=user_obj(update),status=False):
        keyboard.addButton(i.student.first_name,one_row=True)
    update.message.reply_text('Теперь осталось добавить учеников в группу',reply_markup=keyboard.getKeyboard())

    return GROUP_MEMBERS

def group_members(update, context):
    user = update.message.from_user
    logger.info("Times of %s: %s", user.first_name, update.message.text)
    #excluded.append(update.message.text)
    GROUP_DATA['members'].append(update.message.text)
    user = TrialGroups.objects.get(student=Users.objects.get(first_name=update.message.text),status=False,trial__teacher=user_obj(update))
    user.status = True
    user.save()
    t_obj = Group.objects.filter(teacher = user_obj(update)).last()
    student = Students.objects.create(
        student = user.student,
        group = t_obj,
        start_date = t_obj.first_date,
        end_date =  t_obj.second_date
        
    )
    keyboard = KeyBoards()
    trial_count = TrialGroups.objects.filter(status=False,trial__teacher=user_obj(update)).count()
    if trial_count > 1:
        for i in TrialGroups.objects.filter(trial__teacher=user_obj(update),status=False):
            keyboard.addButton("{0} {1}".format(i.student.first_name,i.student.phone),one_row=True)
        update.message.reply_text('Добавьте еще одного или введите /stop для завершения',reply_markup=keyboard.getKeyboard())
    else:
        update.message.reply_text('Ученики закончились введите /stop',reply_markup=ReplyKeyboardRemove())

    if Students.objects.filter(group=t_obj).count() == 10:
        sendInfo(update,context)
        update.message.reply_text('Отлично! Группа сформирована {0}'.format(str(GROUP_DATA)),reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    return GROUP_MEMBERS


def group_members_stop(update, context):
    user = update.message.from_user
    logger.info("User %s stopped", user.first_name)
    update.message.reply_text('Отлично! Группа сформирована {0}'.format(str(GROUP_DATA)),reply_markup=ReplyKeyboardRemove())

    chat_id = update.message.chat_id
    new_job = context.job_queue.run_once(alarm, 60, context=chat_id)
    context.chat_data['job'] = new_job
    sendInfo(update,context)
    return ConversationHandler.END

def sendInfo(update,context):
    
    t_obj = Group.objects.filter(teacher = user_obj(update)).last()
    for i in Students.objects.filter(group=t_obj):
        print(i)
        context.bot.send_message(chat_id=i.student.id,text='Вы были добавлены в группу {0}\nДля того, чтобы начать занятия вам нужно оплатить их. Введите /pay для оплаты банковской картой.'.format(t_obj.info()))
    return True

def start_without_shipping_callback(update, context):
    chat_id = update.message.chat_id
    p_obj = Students.objects.filter(student_id=chat_id,payment=None)
    if p_obj.count() < 1:
        update.message.reply_text('Вы еще не добавлены ни в одну группу.')
        return None
    p_obj = p_obj.last()
    p_obj.payment = Transactions.objects.create(
        student = p_obj.student,
        group = p_obj.group,
        amount = 100,
        status = False,
        end_date = p_obj.group.first_date + timedelta(days=30)
    )
    p_obj.save()
    title = "Payment Example"
    description = "Payment Example using python-telegram-bot"
    # select a payload just for you to recognize its the donation from your bot
    payload = "Custom-Payload"
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    provider_token = "381764678:TEST:12473"
    start_parameter = "test-payment"
    currency = "RUB"
    # price in dollars
    price = 100
    # price * 100 so as to include 2 decimal points
    prices = [LabeledPrice("Test", price * 100)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    context.bot.send_invoice(chat_id, title, description, payload,
                             provider_token, start_parameter, currency, prices)


# after (optional) shipping, it's the pre-checkout
def precheckout_callback(update, context):
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'Custom-Payload':
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)


# finally, after contacting the payment provider...
def successful_payment_callback(update, context):
    # do something after successfully receiving payment?
    tr = Transactions.objects.get(student=user_obj(update))
    tr.status = True
    tr.save()
    update.message.reply_text("Вы успешно оплатили месяц занятий!")

def begin_lesson(update, context):
    user = update.message.from_user
    logger.info("Start of %s: %s", user.first_name, update.message.text)
    group = Group.objects.filter(Q(first_date__date=datetime.now().date()) | Q(second_date__date=datetime.now().date()),teacher=user_obj(update))
    if group.count() < 1:
        update.message.reply_text('Сегодня у вас нет занятий',reply_markup=ReplyKeyboardRemove())
        table(update,context)
        return False
    keyboard = KeyBoards()
    for i in Students.objects.filter(group=group[0]):
        keyboard.addButton(i.student.first_name,one_row=True)
    update.message.reply_text('Пожалуйста, отметьте учеников, присутствующих на занятии\n/end для завершения занятия',reply_markup=keyboard.getKeyboard())
    print(TEMP_DATA)
    return LESSON_MEMBER

def lesson_member(update, context):
    user = update.message.from_user
    logger.info("Start of %s: %s", user.first_name, update.message.text)
    today = datetime.now().date()
    group = Group.objects.filter(Q(first_date__date=today) | Q(second_date__date=today),teacher=user_obj(update))
    keyboard = KeyBoards()
    StudentsMarks.objects.create(
        student=Users.objects.get(first_name=update.message.text),
        group = group[0],
        date = today
    )
    slist = [i.student.first_name for i in StudentsMarks.objects.filter(group=group[0],date=today)]
    print(slist)
    s_all = Students.objects.filter(group=group[0])
    for i in s_all:
        if i.student.first_name in slist:
            continue
        keyboard.addButton(i.student.first_name,one_row=True)
    
    if len(slist) == s_all.count():
        update.message.reply_text('Все ученики отмечены\n/end для завершения занятия',reply_markup=ReplyKeyboardRemove())
        return LESSON_MEMBER
    
    update.message.reply_text('Ученик {0} был отмечен\n/end для завершения занятия'.format(update.message.text),reply_markup=keyboard.getKeyboard())

    return LESSON_MEMBER

def end_lesson(update, context):
    user = update.message.from_user
    logger.info("End of %s: %s", user.first_name, update.message.text)
    group = Group.objects.filter(Q(first_date__date=datetime.now().date()) | Q(second_date__date=datetime.now().date()),teacher=user_obj(update))
    group = group[0]
    if group.first_date.date() == datetime.now().date():
        group.first_date = group.first_date + timedelta(days=7)
    else:
        group.second_date = group.second_date + timedelta(days=7)
    group.save()
    update.message.reply_text("Урок был окончен.",reply_markup=ReplyKeyboardRemove())
    TEMP_DATA = []
    return ConversationHandler.END

def my_groups(update, context):
    t_obj = Group.objects.filter(teacher = user_obj(update))
    keyboard = KeyBoards()
    for i in t_obj:
        keyboard.addButton("/ged {0}".format(i),one_row=True)
    update.message.reply_text('Список ваших групп\nНажмите на одну из них для редактирования',reply_markup=keyboard.getKeyboard())
    return True

def ged(update, context):
    pass

def my_trials(update, context):
    t_obj = Trial.objects.filter(teacher = user_obj(update))
    keyboard = KeyBoards()
    for i in t_obj:
        keyboard.addButton("/ted {0}".format(i),one_row=True)
    update.message.reply_text('Список ваших пробных занятий\nНажмите на одну из них для редактирования',reply_markup=keyboard.getKeyboard())
    return True

def ted(update, context):
    pass


def table(update, context):
    user = update.message.from_user
    print(user)
    logger.info("TimeTable of %s", user.first_name)
    p_obj = Students.objects.filter(student_id=update.message.chat_id,payment=True).last()

    update.message.reply_text("info: {0}".format(p_obj.group.info()),reply_markup=ReplyKeyboardRemove())
    return True


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("872754919:AAFgBuqp0mVa-8G7_7ozeQiDclbmh5WwIXA", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            NAME: [MessageHandler(Filters.text, name)],

            AGE: [MessageHandler(Filters.regex('^(5-7|7-12|от 13)$'), age)],

            PHONE: [MessageHandler(Filters.contact, phone)],

            #PHONE: [MessageHandler(Filters.regex('^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$ '), phone)],

            GROUP: [MessageHandler(Filters.text, group)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    create_trial = ConversationHandler(
        entry_points=[CommandHandler('trial', trial_start)],

        states={
            

            TRIAL_AGE: [MessageHandler(Filters.regex('^(5-7|7-12|от 13)$'), trial_age)],

            TRIAL_DATE: [MessageHandler(Filters.regex('([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))'), trial_date)],

            TRIAL_TIME: [MessageHandler(Filters.regex('^(0[0-9]|1[0-9]|2[0-3]|[0-9]):[0-5][0-9]$'), trial_time)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    create_group = ConversationHandler(
        entry_points=[CommandHandler('cgroup', group_start)],

        states={
            
            GROUP_LEVEL: [MessageHandler(Filters.regex('^(Начинающий|Продолжающий)$'), group_level)],

            GROUP_NAME: [MessageHandler(Filters.text, group_name)],

            GROUP_DAYS_ONE: [MessageHandler(Filters.text, group_days_one)],
            GROUP_DAYS_TWO: [MessageHandler(Filters.text, group_days_two)],

            GROUP_TIMES_ONE: [MessageHandler(Filters.text, group_times_one)],
            GROUP_TIMES_TWO: [MessageHandler(Filters.text, group_times_two)],
            GROUP_MEMBERS: [MessageHandler(Filters.text, group_members)],
        },

        fallbacks=[CommandHandler('stop', group_members_stop)]
    )

    create_lesson = ConversationHandler(
        entry_points=[CommandHandler('begin', begin_lesson)],

        states={
            LESSON_MEMBER: [MessageHandler(Filters.text, lesson_member)]
        },

        fallbacks=[CommandHandler('end', end_lesson)]
    )
    dp.add_handler(conv_handler)
    dp.add_handler(create_trial)
    dp.add_handler(create_group)
    dp.add_handler(create_lesson)

    dp.add_handler(CommandHandler("pay", start_without_shipping_callback))
    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    dp.add_handler(CommandHandler("mgroups", my_groups))
    dp.add_handler(CommandHandler("mtrials", my_trials))
    dp.add_handler(CommandHandler("table", table))
    # Success! Notify your user!
    dp.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))
    # log all errors
    #dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()