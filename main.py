import telegram
import sqlite3
from telegram.ext import ConversationHandler
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


ADMIN_CHAT_ID = 840145341
# Константы для определения состояний разговора
FIRST_NAME, LAST_NAME, GROUP_NUMBER, UNION_TICKET, BIRTH_DATE, ADD = range(6)
INPUT_INFO, SPREAD_INFO = range(2)
# Функция для начала процесса добавления студента
def start_adding_student(update, context):
    update.message.reply_text('Давайте добавим нового студента в базу данных.\n'
                              'Введите имя студента:')
    return FIRST_NAME

# Функция для обработки имени студента
def process_first_name(update, context):
    # Обработка ввода имени студента
    first_name = update.message.text
    # Сохранение имени в контексте
    context.user_data['first_name'] = first_name
    if (first_name == "/cancel"):
        update.message.reply_text('Добавление студента отменено')
        return ConversationHandler.END
    update.message.reply_text('Введите фамилию студента:')
    return LAST_NAME


# Функция для обработки фамилии студента
def process_last_name(update, context):
    # Обработка ввода фамилии студента
    last_name = update.message.text

    # Сохранение фамилии в контексте
    context.user_data['last_name'] = last_name
    if (last_name == "/cancel"):
        update.message.reply_text('Добавление студента отменено')
        return ConversationHandler.END

    update.message.reply_text('Введите номер группы студента:')
    return GROUP_NUMBER

# Функция обработки ввода номера группы
def process_group_number(update, context):
    group_number = update.message.text
    context.user_data['group_number'] = group_number
    if (group_number == "/cancel"):
        update.message.reply_text('Добавление студента отменено')
        return ConversationHandler.END
    update.message.reply_text('Введите номер профсоюзного билета студента:')
    return UNION_TICKET


# Функция обработки ввода номера профсоюзного билета
def process_union_ticket(update, context):
    union_ticket_number = update.message.text
    context.user_data['union_ticket_number'] = union_ticket_number
    if (union_ticket_number == "/cancel"):
        update.message.reply_text('Добавление студента отменено')
        return ConversationHandler.END
    update.message.reply_text('Введите дату рождения студента:')
    return BIRTH_DATE


# Функция обработки ввода даты рождения
def process_birth_date(update, context):
    birth_date = update.message.text
    if (birth_date == "/cancel"):
        update.message.reply_text('Добавление студента отменено')
        return ConversationHandler.END
    # Проверка правильности формата даты рождения
    try:
        datetime.strptime(birth_date, '%d.%m.%Y')
    except ValueError:
        update.message.reply_text('Ошибка в формате даты рождения. Пожалуйста, используйте формат: дд.мм.гггг')
        return BIRTH_DATE

    context.user_data['birth_date'] = birth_date

    # Получение всех данных о студенте из контекста
    chat_id = update.message.chat_id
    first_name = context.user_data['first_name']
    last_name = context.user_data['last_name']
    group_number = context.user_data['group_number']
    union_ticket_number = context.user_data['union_ticket_number']
    birth_date = context.user_data['birth_date']

    # Вызов функции для добавления студента в базу данных
    add_student(first_name, last_name, group_number, union_ticket_number, birth_date, chat_id)

    update.message.reply_text('Студент добавлен успешно!')

    # Очистка данных о студенте в контексте
    context.user_data.clear()
    return ConversationHandler.END




def add_student(first_name, last_name, group_number, union_ticket_number, birth_date, chat_id ):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    # Вставка новой записи в таблицу "Студенты"
    cursor.execute(
        "INSERT INTO students (first_name, last_name, group_number, union_ticket_number, birth_date, chat_id) VALUES (?, ?, ?, ?, ?, ?)",
        (first_name, last_name, group_number, union_ticket_number, birth_date, chat_id))
    conn.commit()

    cursor.close()
    conn.close()


def start_input_info(update, context):
    if update.message.chat_id != ADMIN_CHAT_ID:
        update.message.reply_text('Извините, у вас нет прав доступа для отправки информации студентам.')
        return
    update.message.reply_text('Введите важное сообщение для студентов:')
    return INPUT_INFO

def process_input_info(update, context):
    message = update.message.text

    # Сохранение информации в контексте
    context.user_data['info_message'] = message

    # Переход к распространению информации
    return SPREAD_INFO

# Функция для отправки информации всем студентам
def send_info_to_students(update, context):
    message = context.user_data['info_message']
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    # Получение всех чат-идентификаторов студентов из базы данных
    cursor.execute("SELECT chat_id FROM students")
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    bot = context.bot

    # Отправка сообщения каждому студенту
    for result in results:
        chat_id = result[0]
        bot.send_message(chat_id=chat_id, text=message)

    update.message.reply_text('Информация успешно отправлена студентам!')
    # Очистка сохраненной информации из контекста
    context.user_data.pop('info_message', None)

    return ConversationHandler.END
# Функция для приветствия
def greet(update, context):
    user_name = update.message.from_user.first_name
    message = f"Привет, {user_name}! Здесь ты можешь получить ответы на свои вопросы и узнать актуальную информацию."
    update.message.reply_text(message)

def contact(update, context):
    update.message.reply_text("Вот некоторая информация, которая может вам пригодиться\n "
                              "Где нас найти?\n 3-206 \n "
                              "\n Контакты \n Председатель комиссии: Чайкин Никита (https://vk.com/nichay01) "
                              "\n Также на ваши вопросы могут ответить \n"
                              " Милешина Екатерина  (https://vk.com/ekaterin_a_lexandrovna) \n"
                              "Овчинников Алексей (https://vk.com/aleksovch) ")

def help(update, context):
    update.message.reply_text("Если у вас возникла какая-либо неприятная ситуация в процессе вашего обучения напишите Милешиной Екатерине (https://vk.com/ekaterin_a_lexandrovna) \n"
                              "В сообщение пожалуйста укажите свое ФИО, группу и опишите подробно ситуацию\n"
                              "Мы постараемя разобраться в вашей ситуации ")
def matpod(update, context):
    update.message.reply_text("Основания для получения материальной поддержки от профсоюза:\n\n"
                                      "- Член Профсоюза, создавший молодую семью\n"
                                      "- Рождение ребёнка у члена Профсоюза\n"
                                      "- Член Профсоюза, попавший в непредвиденные чрезвычайные обстоятельства (пожар, стихийные бедствия, кража имущества и другие\n"
                                      "- Смерть члена Профсоюза, смерть одного из ближайших родственников\n"
                                      "- Лечение члена Профсоюза (приобретение медикаментов, прохождение платного медицинского обследования, операция в течение года до момента оформления материальной помощи)\n"
                                      "- Член Профсоюза, попавший в другие непредвиденные трудные жизненные обстоятельства, непредусмотренные категориями, но требующие материальной помощи)")
    update.message.reply_text(
        "Материальную поддержку от профсоюза может получить только член профсоюза.\n"
        "Чтобы получить выплату вам необходимо написать Милешиной Екатерине (https://vk.com/ekaterin_a_lexandrovna)\n"
        "В сообщение укажите ваше ФИО, группу и категорию, по которой вы хотите получить выплату ")
def info(update, context):
    update.message.reply_text("Что такое профсоюз? \n"
                              "-Профсоюз это добровольная организация, основной задачей которой является защита ваших прав и интересов\n"
                              "Члены профсоюза имеют право на получение материальной поддержки от профсоюза.\n"
                              "Членам профсоюза предоставляются бесплатные билеты на посещение театра и спортивных матчей (баскетбол, футбол, хоккей и тд.)\n"
                              "Члены профсоюза могут быть участником программы скидок и лояльностей profcards \n\n"

                              
                              "Как стать членом профсоюза?\n"
                              "-Чтобы стать членом профсоюза вам необходимо заполнить анкету на вступление и заплатить профсоюзный взнос 8 рублей \n"
                              "Сделать это можно в кабинете 3-206 в часы работы профбюро или по предварительной записи у Милешиной Екатерины (https://vk.com/ekaterin_a_lexandrovna)\n"
                              "Какие обязанности члена профсоюза?\n"
                              "-Продление профсоюзного билета (8 рублей в месяц или 3% со стипендии(вычитаются автоматически)")

def profcards(update, context):
    update.message.reply_text("Что бы зарегестрироваться в системе Profcards вам необходимо ввести ваш номер профсоюзного билета\n"
                              "Если вы еще не получили свой профсоюзный билет, то можете это сделать в кабинете 3-206\n"
                              "Сайт: https://profcards.ru/ \n"
                              "Информация о программе: https://profcards.ru/about-program")
def main():
    # Создание экземпляра телеграм-бота
    bot_token = ''
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Установка соединения с базой данных
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    # Создание таблицы "Студенты"
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        first_name TEXT,
                        last_name TEXT,
                        group_number TEXT,
                        union_ticket_number TEXT,
                        birth_date TEXT,
                        chat_id INTEGER)''')

    # Закрытие курсора
    cursor.close()

    # Функция для отмены добавления студента
    def cancel_adding_student(update, context):
        update.message.reply_text('Добавление студента отменено.')
        context.user_data.clear()
        return ConversationHandler.END

    cancel_handler = CommandHandler('cancel', cancel_adding_student)
    # Регистрация обработчиков разговора
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add_student', start_adding_student)],
        states=
        {
            FIRST_NAME: [MessageHandler(Filters.text, process_first_name)],
            LAST_NAME: [MessageHandler(Filters.text, process_last_name)],
            GROUP_NUMBER: [MessageHandler(Filters.text, process_group_number)],
            UNION_TICKET: [MessageHandler(Filters.text, process_union_ticket)],
            BIRTH_DATE: [MessageHandler(Filters.text, process_birth_date)],
            ADD: [MessageHandler(Filters.text, add_student)]
        },
        fallbacks=[cancel_handler]
    )
    dispatcher.add_handler(conv_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('sendinfo', start_input_info)],
        states={
            INPUT_INFO: [MessageHandler(Filters.text, process_input_info)],
            SPREAD_INFO: [MessageHandler(Filters.command, send_info_to_students)]
        },
        fallbacks=[]
    )
    dispatcher.add_handler(conv_handler)

    # Регистрация обработчиков команд и сообщений
    dispatcher.add_handler(CommandHandler('start', greet))
    dispatcher.add_handler(CommandHandler('contact', contact))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('matpodderzka', matpod))
    dispatcher.add_handler(CommandHandler('info', info))
    dispatcher.add_handler(CommandHandler('profcards', profcards))


    # Запуск телеграм-бота
    updater.start_polling()

    # Закрываем соединение
    conn.close()

if __name__ == '__main__':
    main()
