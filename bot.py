import logging
import datetime
import ServerManager as sm
import os
import schedule
import telebot
from threading import Thread
from time import sleep

from datetime import timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler
from ServerManager import getToDoList

TOKEN = '填你自己的'
bot = telebot.TeleBot(TOKEN)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)

TASK, DATE, INVALIDDATE, TIME, INVALIDTIME = range(5)
RECESSDATE,EXAMDATE,EXAM,LEVEL = range(4)
reply_keyboard = [['List', 'Add','Remove','Help','Exam']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = True, one_time_keyboard = False)
keyboard2 = [['Cancel']]
markup2 = ReplyKeyboardMarkup(keyboard2, resize_keyboard = True, one_time_keyboard = True)
#keyboard3 = [['AddExam','Cancel']]
#markup3 = ReplyKeyboardMarkup(keyboard3, resize_keyboard = True, one_time_keyboard = True)

def start(update, context):
    reply = " Hi there, I'm Cronus and I can help you to keep track of your tasks and manage your time wisely!⌛️ \n \n"
    reply += "Here are some buttons that you may find useful: \n"
    reply += "*List*📝: Get the list of tasks you have \n"
    reply += "*Add*➕: Add tasks to your list \n"
    reply += "*Remove*🗑: Remove tasks from your list when you are done \n"
    reply += "*Help*🔍: Get information regarding Cronus \n"
    reply += "*Exam*: Get exam review schedule \n\n"
    reply += "Let’s start by clicking on the *Add* button!"
    userId = update.message.chat_id
    context.bot.send_message(chat_id=update.message.chat_id, text=reply, parse_mode = ParseMode.MARKDOWN,
                             reply_markup = markup)


def help(update, context):
    reply = "*List*📝: Get the list of tasks you have \n"
    reply += "*Add*➕: Add tasks to your list \n"
    reply += "*Remove*🗑: Remove tasks from your list when you are done \n"
    reply += "*Exam*: Get exam review schedule \n"
    reply += "Type */start* to reset the bot\n"
    update.message.reply_text(reply, parse_mode = ParseMode.MARKDOWN)

def exam(update, context):
    update.message.reply_text(
        'Hi! When is the begin date for recess week? \nEnter in the format: _DD/MM/YYYY_', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
    return RECESSDATE

def getRecessDate(update, context):
    date = update.message.text
    try:
        d,m,y = map(int, date.split('/'))
        validDate = datetime.date(y, m, d)
        todayDate = datetime.date.today()
        if int((validDate - todayDate).days) >= 0:
            context.user_data['recessdate'] = date
            update.message.reply_text('When is the begin date for exam? \nEnter in the format: _DD/MM/YYYY_', reply_markup = markup2,  parse_mode = ParseMode.MARKDOWN)
            return EXAMDATE
        else:
            update.message.reply_text('Please enter a future date!', reply_markup = markup2)
            return RECESSDATE
    except ValueError:
        update.message.reply_text('Date entered is invalid! \nPlease re-enter in the format: _DD/MM/YYYY_', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return RECESSDATE

def getExamDate(update, context):
    date = update.message.text
    try:
        d, m, y = map(int, date.split('/'))
        validDate = datetime.date(y, m, d)
        todayDate = datetime.date.today()
        if int((validDate - todayDate).days) >= 0:
            context.user_data['examdate'] = date
            update.message.reply_text('What is the exam module you would like to add?', reply_markup=markup2,
                                      parse_mode=ParseMode.MARKDOWN)
            context.user_data['module'] = []
            context.user_data['level'] = []
            return EXAM
        else:
            update.message.reply_text('Please enter a future date!', reply_markup=markup2)
            return EXAMDATE
    except ValueError:
        update.message.reply_text('Date entered is invalid! \nPlease re-enter in the format: _DD/MM/YYYY_',
                                  reply_markup=markup2, parse_mode=ParseMode.MARKDOWN)
        return EXAMDATE
def addExam(update, context):
    moduleName = update.message.text
    if moduleName != 'q':
        context.user_data['module'].append(moduleName)
        update.message.reply_text(
            "What is the level of the module you would like to add? \nPlease enter the number: 1/2/3. \nPay "
            "attention: There are three levels. Level 1 means the module you invest the most energy and so on.",
            reply_markup=markup2)
        return LEVEL
    else:
        sm.addreviewtime(update.message.chat_id, context.user_data.get('recessdate'),
                         context.user_data.get('examdate'))
        sm.addexam(update.message.chat_id,context.user_data.get('module'), context.user_data.get('level'))
        context.user_data.clear()
        return ConversationHandler.END

def addLevel(update,context):
    level = update.message.text
    print(level)
    if level != '1' and level != '2' and level != '3':
        update.message.reply_text('请输入正确格式')
        return LEVEL
    else:
        context.user_data['level'].append(level)
        update.message.reply_text('What is the exam module you would like to add?', reply_markup=markup2,
                                  parse_mode=ParseMode.MARKDOWN)
        return EXAM

def add(update, context):
    update.message.reply_text("Hi! What is the name of the task you would like to add?", reply_markup = markup2)
    return TASK

def getTask(update, context):
    taskName = update.message.text
    context.user_data['task'] = taskName
    update.message.reply_text(
        'When is the due date for *{}*? \nEnter in the format: _DD/MM/YYYY_'.format(taskName), reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
    return DATE

def getDate(update, context):
    date = update.message.text
    try:
        d,m,y = map(int, date.split('/'))
        validDate = datetime.date(y, m, d)
        todayDate = datetime.date.today()
        if int((validDate - todayDate).days) >= 0:
            context.user_data['date'] = date
            update.message.reply_text('What time is it due? \nEnter in the format: _HH:MM AM/PM_', reply_markup = markup2,  parse_mode = ParseMode.MARKDOWN)
            return TIME
        else:
            update.message.reply_text('Please enter a future date!', reply_markup = markup2)
            return INVALIDDATE
    except ValueError:
        update.message.reply_text('Date entered is invalid! \nPlease re-enter in the format: _DD/MM/YYYY_', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return INVALIDDATE
    
def invalidDate(update, context):
    date = update.message.text
    try:
        d, m, y = map(int, date.split('/'))
        validDate = datetime.date(y, m, d)
        todayDate = datetime.date.today()
        if int((validDate - todayDate).days) >= 0:
            context.user_data['date'] = date
            update.message.reply_text('What time is it due? \nEnter in the format: _HH:MM AM/PM_', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
            return TIME
        else:
            update.message.reply_text('Please enter a future date!', reply_markup = markup2)
            return INVALIDDATE
    except ValueError:
        update.message.reply_text('Date entered is invalid! \nPlease re-enter in the format: _DD/MM/YYYY_', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return INVALIDDATE
        
def getTime(update, context):
    time = update.message.text
    date = context.user_data.get('date')
    newTime = time.lower().replace('pm', '').replace('am', '')
    validTime = newTime + ":00"

    try:
        validTime = datetime.datetime.strptime(validTime, "%H:%M:%S")
        hr, minute = map(int, newTime.split(":")) 
        if "pm" in time.lower():
            hr += 12
        now = datetime.datetime.now()
        d,m,y = map(int, date.split('/'))
        new = datetime.datetime(y, m, d, hr, minute)
        time_diff = new - now 
        if (time_diff < datetime.timedelta(0)):
            update.message.reply_text('Please enter a future time!', reply_markup = markup2)
            return INVALIDTIME
        else:
            context.user_data['time'] = time
            context.user_data['formatTime'] = str(hr) + ":" + str(minute)
            doneAdding(update, context)
            return ConversationHandler.END
    except ValueError:
        update.message.reply_text('Time entered is invalid! \nPlease enter in the format: _HH:MM AM/PM_!', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return INVALIDTIME

#have to re-code, too slow
def invalidTime(update, context):
    time = update.message.text
    date = context.user_data.get('date')
    newTime = time.lower().replace('pm', '').replace('am', '') 
    validTime = newTime + ":00"

    try:
        validTime = datetime.datetime.strptime(validTime, "%H:%M:%S")
        hr, minute = map(int, newTime.split(":")) 
        if "pm" in time.lower():
            hr += 12
        now = datetime.datetime.now()
        d,m,y = map(int, date.split('/'))
        new = datetime.datetime(y, m, d, hr, minute)
        time_diff = new - now 
        if (time_diff < datetime.timedelta(0)):
            update.message.reply_text('Please enter a future time!', reply_markup = markup2)
            return INVALIDTIME
        else:
            context.user_data['time'] = time
            context.user_data['formatTime'] = str(hr) + ":" + str(minute)
            doneAdding(update, context)
            return ConversationHandler.END
    except ValueError:
        update.message.reply_text('Time entered is invalid!\nPlease enter in the format _HH:MM AM/PM_!', reply_markup = markup2, parse_mode = ParseMode.MARKDOWN)
        return INVALIDTIME

def doneAdding(update, context):
    user_data = context.user_data
    userId = update.message.chat_id
    task = user_data.get('task')
    date = user_data.get('date')
    time = user_data.get('time')
    update.message.reply_text('*' + task + '*' + ' due on *' + date + '* at *' + 
        time + '* has been added!', reply_markup = markup, parse_mode = ParseMode.MARKDOWN)

    formattedTime = user_data.get('formatTime')
    deadline = formatDatetime(date, formattedTime)
    sm.addTask(userId, task, deadline)
    user_data.clear()


def cancel(update, context): 
    context.user_data.clear()
    update.message.reply_text("Adding of task has been cancelled, until next time!", reply_markup = markup)
    return ConversationHandler.END

def examcancel(update, context): 
    context.user_data.clear()
    update.message.reply_text("Getting exam review schedule has been cancelled, until next time!", reply_markup = markup)
    return ConversationHandler.END

def formatDatetime(date, time):
    d, m, y = map(str, date.split("/"))
    formatted = y + "/" + m + "/" + d + " " + time + ":00"
    #print(formatted)
    return formatted

def list(update, context):
    userId = update.message.chat_id
    update.message.reply_text(sm.getToDoList(userId),parse_mode = ParseMode.MARKDOWN)

def remove(update, context):
    userId = update.message.chat_id
    arr = sm.getArrayList(userId)
    keyboard= []
    
    for row in arr:
        task = row[0]
        deadline = row[1]
        time = deadline.strftime('%H:%M')
        hr, minute = map(int, time.split(':'))
        if hr > 12: #account for 12am later
            hr -= 12
            time = str(hr) + ":" + deadline.strftime('%M') + "PM"
        elif hr == 12: 
            time = str(hr) + ":" + deadline.strftime('%M') + "PM"
        else:
            time = str(hr) + ":" + deadline.strftime('%M') + "AM"
        option = "\"" + str(task) + "\"\n Due on: " + deadline.strftime('%d/%m/%Y') + " " + time 
        rawData = str(userId) + "|" + str(row[0]) + "|" + row[1].strftime('%Y/%m/%d %H:%M:%S') 
        keyboard.append([InlineKeyboardButton(str(option), callback_data = rawData)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Click on the completed task!', reply_markup=reply_markup, parse_mode = ParseMode.MARKDOWN)

def button(update, context):
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    query.answer()

    rawData = (query.data).split('|')
    sm.removeTask(rawData[0], rawData[1], rawData[2])
    replyMsg = "\"" + rawData[1] + "\" due on " + rawData[2]
    query.edit_message_text(text="Great! You have completed: \n{}".format("*" + rawData[1]+ "*"), parse_mode = ParseMode.MARKDOWN) #edit later to include deadline

def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1) 


def groupsend():
    group=sm.alluserId()
    for id in group:
        bot.send_message(chat_id=id[0], text=sm.getToDoList(id[0]),parse_mode = ParseMode.MARKDOWN)
def sendlistdaily():
     return groupsend()


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    sm.creatTable()
    updater = Updater(TOKEN, use_context=True,request_kwargs={'proxy_url': '填你自己的'})
    job = updater.job_queue
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Add$'), add)],
        states={
            TASK: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getTask)],
            DATE: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getDate)],
            INVALIDDATE: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), invalidDate)],
            TIME: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getTime)],
            INVALIDTIME: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), invalidTime)]
        },
        fallbacks=[MessageHandler(Filters.regex('^Cancel$'), cancel)],
        allow_reentry = True
    )
    conv_handler2 = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Exam$'), exam)],
        states={
            RECESSDATE: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getRecessDate)],
            EXAMDATE : [MessageHandler(Filters.regex('^((?!Cancel).)*$'), getExamDate)],
            EXAM : [MessageHandler(Filters.regex('^((?!Cancel).)*$'), addExam)],
            LEVEL: [MessageHandler(Filters.regex('^((?!Cancel).)*$'), addLevel)]
        },
        fallbacks=[MessageHandler(Filters.regex('^Cancel$'), examcancel)],
        allow_reentry = True
    )
    dp.add_error_handler(error)
    dp.add_handler(conv_handler)
    dp.add_handler(conv_handler2)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.regex('^List$'), list))
    dp.add_handler(MessageHandler(Filters.regex('^Remove'), remove))
    dp.add_handler(MessageHandler(Filters.regex('^Help$'), help))

    schedule.every().day.at("16:57").do(sendlistdaily)
    Thread(target=schedule_checker).start()
	
    
    updater.bot.setWebhook('https://yourownappname.herokuapp.com/' + TOKEN)
    updater.start_polling()
    updater.idle() 

if __name__=='__main__':
    main()


