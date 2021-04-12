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

#API token (set to input() as a debuggin mesure)
TelegramAPIToken = input("Enter bot token: ")

#Logging config
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

###- Bot Commands -###
def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def main() -> None:
    #Setup updater
    telegramUpdater = Updater(TelegramAPIToken)
    
    #Grab dispatcher as well
    telegramDispatcher = telegramUpdater.dispatcher

if __name__ == '__main__':
    main()