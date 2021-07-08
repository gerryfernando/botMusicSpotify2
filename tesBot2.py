import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update,KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,CallbackQueryHandler, ConversationHandler, CallbackContext
from owlready2 import *
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

onto = get_ontology("file://music.owl").load()
onto = get_ontology("file://music-N.owl").load()

cred = credentials.Certificate('firebase-sdk.json')
firebase_admin.initialize_app(cred, {
	'databaseURL':'https://musik-chatbot-default-rtdb.asia-southeast1.firebasedatabase.app/'
	})


def cek(x):
    y = db.reference('/chatbot2/{}'.format(x)).get()
    if y == None:
        return True
    else:
        return False

def newUsr(x):
    if cek(x):
        ref = db.reference('/chatbot2/')
        ref.child(x).set({
                "model":""            
        })
    else:
        ref = db.reference('/chatbot2/{}'.format(x))
        ref.set({
            "model":""
        })

def add(data,id):
    dat =db.reference('/chatbot2/{}/model'.format(id)).get()
    if dat=="":
        dat =  dat + data
    else:
        dat = dat + "," + data
    ref = db.reference('/chatbot2/{}/'.format(id))
    ref.update({
        "model" : dat
    })

def dModel(id):
    dat = db.reference('/chatbot2/{}/model'.format(id)).get()
    dat = str(dat)
    data = dat.split(",")
    return data

def searchDurasi(kata1,kata2):
    for i in onto.classes():
        temp = str(i).split(".")
        if(temp[1] == kata1):
            x = i

    pops = onto.search(is_a = onto.search(is_a = x))
    
    for pop in pops:
        temp = str(pop).split(".")
        if temp[1] == kata2:
            for prop in pop.get_properties():
                for value in prop[pop]:
                    temp = str(value).split(".")
                    x = onto.search(hasDuration = value)
    return list(x)

def searchElement(kata1,kata2):
    for i in onto.classes():
        temp = str(i).split(".")
        if(temp[1] == kata1):
            x = i
    
    pops = onto.search(is_a = onto.search(is_a = x))
    for pop in pops:
        temp = str(pop).split(".")
        if temp[1] == kata2:
            for prop in pop.get_properties():
                for value in prop[pop]:
                    temp = str(value).split(".")
                    x = onto.search(haveElement = value)
    return list(x)

def searchAtr(x):
    temp = ["","",""]
    temp1 = ""
    for prop in x.get_properties():
        for value in prop[x]:
            if(str(prop)=="music.hasGenre"):
                temp[0] = str(value)
            elif(str(prop)=="music.performed"):
                temp1 = str(value).replace("music-N.","")
                temp1 = temp1.replace("_"," ")
                temp[1] = temp1
            elif(str(prop)=="music.Year"):
                temp[2] = str(value)
                
    return temp

def searchElement2(kata1,kata2):
    for i in onto.classes():
        temp = str(i).split(".")
        if(temp[1] == kata1):
            x = i
    pops = onto.search(is_a = onto.search(is_a = x))
    for pop in pops:
        temp = str(pop).split(".")
        if temp[1] == kata2:
            for prop in pop.get_properties():
                for value in prop[pop]:
                    temp = str(value).split(".")
                    x = onto.search(needElement = value)
    return list(x)

def searchPopular(kata1,kata2):
    for i in onto.classes():
        temp = str(i).split(".")
        if(temp[1] == kata1):
            x = i

    pops = onto.search(is_a = onto.search(is_a = x))
    for pop in pops:
        temp = str(pop).split(".")
        if temp[1] == kata2:
            for prop in pop.get_properties():
                for value in prop[pop]:
                    temp = str(value).split(".")
                    x = onto.search(isPopuler = value)
    return list(x)

def reksis(usmod):
    print(usmod)
    rec = []
    key = ["Dance", "Famous","Akustik","Loud","Durasi","Mood"]
    ind  = onto.search(is_a = onto.search(is_a = onto.Title))
    if usmod[1] == "awal":
        temp1 = ["2010","2011","2012","2013"]
    elif usmod[1] == "tengah":
        temp1 = ["2014","2015","2016"]
    elif usmod[1] == "baru":
        temp1 = ["2017","2018","2019"]

    #search genre

    temp = "*"+usmod[0]+"*"
    genre = onto.search(hasGenre = temp)
    sum = 0
    for i in ind:
        if i in list(genre):
            rec.append(i)
            sum += 1

    #search year   

    temp = temp1
    hasil = []
    for i in temp:
        temp = np.array(onto.search(Year = i))
        for x in temp:
            hasil.append(x)

    temp=[]    
    for i in rec:
        if i in list(hasil):
            temp.append(i)
    if(len(temp) != 0 ):
        rec = temp

    arr =[]
    indMenari=[]
    indPopular= []
    indAkustik = []
    indLoud= []
    indValence = []
    indDurasi = []
    #Functional Music
    if(usmod[2]!= "tidak"):
        indMenari = searchElement(key[0],usmod[2])
    if(usmod[3]!= "tidak"):
        indPopular = searchPopular(key[1],usmod[3])
    if(usmod[4]!= "tidak"):
        indAkustik = searchElement(key[2],usmod[4])
    if len(usmod) >  5:
        if(usmod[5]!= "tidak"):
            indLoud = searchElement(key[3],usmod[5])
        indDurasi = searchDurasi(key[4],usmod[6])
        if(usmod[7]!="tidak"):
            indValence =searchElement2(key[5],usmod[7])
            print(str(len(indValence)),usmod[7])  
      
    for i in rec:
        temp1 = np.array([i])
        arr.append(temp1)

    i = 0
    for ar in arr:
        util = 0
        reason = ""
        
        if ar in list(indMenari):
            util = util + 1
        if ar in list(indPopular):
            util = util + 1
        if ar in list(indAkustik):
            util = util+ 1
        if(len(usmod) > 5):
            if ar in list(indLoud):
                util += 1
            if ar in list(indDurasi):
                util += 1
            if ar in list(indValence):
                util += 1
        temp = [util]
        arr[i] = np.append(ar,temp)
        i = i+1


    #sorting
    i = 1
    
    arr.sort(key = lambda arr: arr[1] , reverse= True)
    arr = list(arr)[:10]
    i = 0
    sum = 0
    kat = ""
    for ar in arr:
        i = 0 
        x = ar[0]
        atr = searchAtr(x)
        sum = sum + 1
        kat = kat + str(sum)+". "
        for x in ar:
            if i != 1:
                temp = str(x).replace("_"," ")
                temp = temp.replace("music.","")
                kat = kat+temp
            i = i+1 
            kat = kat+"\n"
    return kat



i = 0
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
 
logger = logging.getLogger(__name__)
# Enable logging
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

# Callback data
key = [""]

FIRST, SECOND, THIRD, FOURTH, FIFTH,SIXTH,SEVENTH,EIGHT,NINTH = range(9)
def start(update, context):
    """Send a message when the command /start is issued."""
    button = [
              [KeyboardButton("/musicrecommendation"),
               KeyboardButton("/home" )
              ]
            ]
    reply_markup = ReplyKeyboardMarkup(button,resize_keyboard = True)
    
    update.message.reply_text('Hallo, selamat datang di chatbot ini , silahkan pilih menu kami dibawah ini ? ',reply_markup=reply_markup)
 
def recom(update: Update, _: CallbackContext) -> int:
  user = update.message.from_user
  id = str(user.id)
  newUsr(id)
  logger.info("User %s started the conversation.", user.first_name)
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
  global model
  model = []
  keyboard = [
        [
           InlineKeyboardButton("Pop", callback_data="pop"),
            InlineKeyboardButton("Hip Hop", callback_data="hip"),
            InlineKeyboardButton("Boy Band", callback_data="boyband"),
            InlineKeyboardButton("Electronic", callback_data="electronic"),
            InlineKeyboardButton("R & B", callback_data="r&b"),
            InlineKeyboardButton("Rock", callback_data="rock"),
        ]
    ]
  text = "1. Baik selamat datang di dialog ini, Sebelum itu saya akan menanyakan beberapa pertanyaan seputar yang akan menjadi dasar dalam merekomendasikan musik tentunya :) , Harap untuk mennjawab setiap pertanyaan hingga selesai. Baik untuk yang pertama GENRE musik apa yang anda inginkan? \n\nDeskripsi Singkat : \n\n1. Pop adalah genre musik yang sederhana dan mengikuti perkembangan zaman \n\n2. Rock adalah musik dengan tempo yang cepat dan musik yang sedikit lebih keras \n\n3. Hip Hop merupakan subgenre R&B. dimana melibatkan teknik rap \n\n4. Electronic merupakan genre musik yang hanya menggunakan alat musik elektronik dan dibuat dengan cara elektromekanis (musik elektroakustik) \n\n5. Boy Band merupakan suatu grup vokal yang terdiri dari beberapa remaja pria dan menyanyikan lagu tentang cinta \n\n6. R&B adalah genre musik tradisional masyarakat Afro-Amerika, yang menggabungkan jazz, gospel, dan blues"
  reply_markup = InlineKeyboardMarkup(keyboard)
  # Send message with text and appended InlineKeyboard
  update.message.reply_text(text, reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
  return FIRST


def home(update,context):
  button = [
              [KeyboardButton("/start")
              ]
            ]
  reply_markup = ReplyKeyboardMarkup(button,resize_keyboard = True)
  update.message.reply_text('Hallo, selamat datang di chatbot ini , Chatbot ini merupakan proyek tugas besar saya dimana chatbot ini mampu merekomendasikan musik sesuai keinginan anda, Silahkan kembali dengan cara menekan /start',reply_markup=reply_markup)
 
 
def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Ini adalah fitur untuk meminta bantuan!!!')
 



def year(update: Update, _: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    data  = query.data
    add(data,str(query.from_user.id))
    keyboard = [
        [
            InlineKeyboardButton("2010-2013", callback_data="awal"),
            InlineKeyboardButton("2014-2016", callback_data="tengah"),
            InlineKeyboardButton("2017-2019", callback_data="baru"),
            ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="2. Baik untuk pertanyaan selanjutnya , untuk tahun lagunya mau yang kapan nih ?  ", reply_markup=reply_markup
    )
    return SECOND

def dance(update: Update, _: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    data  = query.data
    add(data,str(query.from_user.id))
    keyboard = [
        [
            InlineKeyboardButton("Menari ", callback_data="Menari"),
            InlineKeyboardButton("Tidak", callback_data="tidak"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="3. Untuk lagunya  apakah anda ingin lagu yang dapat digunakan untuk menari?", reply_markup=reply_markup
    )
    return THIRD

def popular(update: Update, _: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    data  = query.data
    add(data,str(query.from_user.id))
    keyboard = [
        [
            InlineKeyboardButton("Lagu Popular", callback_data="Terkenal"),
            InlineKeyboardButton("Biasa ", callback_data="tidak"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="4. Apakah anda ingin lagu yang terkenal atau anda ingin lagu yang biasa?", reply_markup=reply_markup
    )
    return FOURTH


def akustik(update: Update, _: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    data  = query.data
    add(data,str(query.from_user.id))
    keyboard = [
        [
            InlineKeyboardButton("Lagu Akustik", callback_data="musikAkustik"),
            InlineKeyboardButton("Tidak", callback_data="tidak"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="5. Untuk lagunya sendiri apakah anda ingin lagu yang akustik atau tidak? (Setelah menjawab pertanyaan ini harap tunggu sekitar 10 detik hingga hasil rekomendasi muncul)", reply_markup=reply_markup
    )
    return FIFTH


def loud(update: Update, _: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Tenang", callback_data="musikPelan"),
            InlineKeyboardButton("Tidak ", callback_data="tidak"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="6. Apakah anda ingin lagu yang tenang?", reply_markup=reply_markup
    )
    return SEVENTH


def durasi(update: Update, _: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    data  = query.data
    add(data,str(query.from_user.id))
    keyboard = [
        [
            InlineKeyboardButton("Lama", callback_data="durasiLama"),
            InlineKeyboardButton("Sedang", callback_data="durasiSedang"),
            InlineKeyboardButton("Cepat", callback_data="durasiCepat"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="7. Untuk lagunya apakah anda ingin lagu dengan durasi lama , sedang atau cepat?", reply_markup=reply_markup
    )
    return EIGHT

def mood(update: Update, _: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    data  = query.data
    add(data,str(query.from_user.id))
    keyboard = [
        [
            InlineKeyboardButton("Ya", callback_data="moodPositive"),
            InlineKeyboardButton("Tidak", callback_data="tidak"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="8. Untuk lagunya apakah anda ingin lagu yang membawa mood positif atau tidak? (Setelah menjawab pertanyaan ini harap tunggu sekitar 10 detik hingga hasil rekomendasi muncul)", reply_markup=reply_markup
    )
    return NINTH



def end(update: Update, _: CallbackContext) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    query = update.callback_query
    query.answer()
    data  = query.data
    add(data,str(query.from_user.id))
    hasil = reksis(dModel(query.from_user.id))
    
    keyboard = [
        [
            InlineKeyboardButton("Sesuai", callback_data="ya"),
            InlineKeyboardButton("Belum ", callback_data="tidak"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Terima kasih atas perhatian Anda, ini adalah rekomendasi musik Anda : \n\n {} , \n\nApakah rekomendasi lagu diatas sudah sesuai dengan keinginan anda?".format(hasil),reply_markup=reply_markup)
    return SIXTH

def end2(update: Update, _: CallbackContext) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    query = update.callback_query
    query.answer()
    data  = query.data
    add(data,str(query.from_user.id))
    hasil = reksis(dModel(query.from_user.id))
    
    query.edit_message_text(text="Terima kasih atas perhatian Anda, ini adalah rekomendasi musik Anda : \n {} \n\nSampai jumpa lagi!".format(hasil))
    return ConversationHandler.END


def endSection(update: Update, _: CallbackContext) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    query = update.callback_query
    query.answer()
    hasil = reksis(dModel(query.from_user.id))
    
    query.edit_message_text(text="Terima kasih atas perhatian Anda, ini adalah rekomendasi musik Anda : \n {}\n\nSampai jumpa lagi!".format(hasil))
    return ConversationHandler.END

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def get_last_chat(update, context):
  return update.message.text 
  
def err_message(update,context):
  update.message.reply_text("Maaf Kata yang anda masukan salah, tolong input sesuai dengan pilihan yang ada !!!")
 
def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1893557965:AAGTWrHO6B37aEMHdpQSwqeotntggvmHdCk", use_context=True)
 
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    #conversation Handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("musicrecommendation", recom)],
        states={
            FIRST: [
                CallbackQueryHandler(year, pattern="hip"),
                CallbackQueryHandler(year, pattern="pop"),
                CallbackQueryHandler(year, pattern="boyband"),
                CallbackQueryHandler(year, pattern="electronic"),
                CallbackQueryHandler(year, pattern="r&b"),
                CallbackQueryHandler(year, pattern="rock"),
            ],
            SECOND: [
                CallbackQueryHandler(dance, pattern= "awal" ),
                CallbackQueryHandler(dance, pattern="tengah"  ),
                CallbackQueryHandler(dance, pattern="baru"  ),
            ],

            THIRD: [
                CallbackQueryHandler(popular, pattern= "Menari" ),
                CallbackQueryHandler(popular, pattern="tidak"  ),
            ],

            FOURTH: [
                CallbackQueryHandler(akustik, pattern= "Terkenal" ),
                CallbackQueryHandler(akustik, pattern="tidak"),
            ],

            FIFTH: [
                CallbackQueryHandler(end, pattern= "musikAkustik" ),
                CallbackQueryHandler(end, pattern= "tidak" ),
            ],
            
            SIXTH: [
                CallbackQueryHandler(endSection, pattern= "ya" ),
                CallbackQueryHandler(loud, pattern= "tidak" ),
            ],
            
            SEVENTH: [
                CallbackQueryHandler(durasi, pattern= "musikPelan" ),
                CallbackQueryHandler(durasi, pattern= "tidak" ),
            ],
            
            EIGHT: [
                CallbackQueryHandler(mood, pattern= "durasiLama" ),
                CallbackQueryHandler(mood, pattern= "durasiSedang" ),
                CallbackQueryHandler(mood, pattern= "durasiCepat" ),
            ],
            
            NINTH: [
                CallbackQueryHandler(end2, pattern= "moodPositive" ),
                CallbackQueryHandler(end2, pattern= "tidak" ),
            ],
            
        },
        fallbacks=[CommandHandler('start', start)],
    )
    dp.add_handler(conv_handler)
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("musicrecommendation", recom))
    dp.add_handler(CommandHandler("home", home))
    dp.add_handler(CommandHandler("help", help))
 
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.regex("hi"), start))
    dp.add_handler(MessageHandler(Filters.regex("Hello"), start))
    dp.add_handler(MessageHandler(Filters.regex("Hi"), start))
    dp.add_handler(MessageHandler(Filters.regex("Halo"), start))
    dp.add_handler(MessageHandler(Filters.text, err_message))

   
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
 
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

 
 
if __name__ == '__main__':
    main()
