#Telegram bot for tagging images via DeepHydrus
#By Sciguy429

#Imports
import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

###- Bot constants -###

#Hydrus nural model location
HydrusNuralModelPath = "./model-resnet_custom_v5.h5.e40"

#Hydrus nural model tag list location
HydrusNuralModelTags = "tags.txt"

#API token (set to input() as a debugging mesure)
TelegramAPIToken = input("Enter bot token: ")

#Logging config
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

###- Arg parse config -###
#TODO

###- Bot Commands -###

#SciBot Command
def sciBotCommand(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Main command recieved!")
    print(update.message)
    if update.message.reply_to_message:
        update.message.reply_text("Reply Detected! Orignal image info: " + update.message.reply_to_message.photo[0].file_id)

def main() -> None:
    #Setup updater
    telegramUpdater = Updater(TelegramAPIToken)
    
    #Grab dispatcher as well
    telegramDispatcher = telegramUpdater.dispatcher
    
    telegramDispatcher.add_handler(MessageHandler(Filters.regex("(?i)^(/SciBot)"), sciBotCommand))
    #telegramDispatcher.add_handler(MessageHandler(Filters.all, sciBotCommand))
    
    telegramUpdater.start_polling()
    
    telegramUpdater.idle()

if __name__ == '__main__':
    main()