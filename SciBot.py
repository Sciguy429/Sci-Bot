#Telegram bot for tagging images via DeepHydrus
#By Sciguy429

#Imports
import DeepHydrus

import logging
import pathlib
import os
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

###- Bot constants -###

#Hydrus nural model location
HydrusNuralModelPath = "./model-resnet_custom_v5.h5.e40"

#Hydrus nural model tag list location
HydrusNuralModelTags = "tags.txt"

#Model size
HydrusNuralModelHeight = 512
HydrusNuralModelWidth = 512

#Temp folder
MediaTempFolder = "./sc-temp/"

#API token (set to input() as a debugging mesure)
TelegramAPIToken = input("Enter bot token: ")

#Logging config
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#Gloabal DeepHydrus object
deepHydrus = DeepHydrus.DeepHydrus(HydrusNuralModelPath, HydrusNuralModelTags, HydrusNuralModelHeight, HydrusNuralModelWidth)

###- Arg parse config -###
#TODO

###- Bot Commands -###

#SciBot Command
def sciBotCommand(update: Update, context: CallbackContext) -> None:
    #Check for a reply
    if (not update.message.reply_to_message):
        update.message.reply_text("No reply detected!")
        logging.info("FAILED CHECK: No reply in chat %d, at message %d)", update.message.chat_id, update.message.message_id)
        return
    
    #Make sure reply contains an image
    if (not update.message.reply_to_message.photo):
        update.message.reply_text("No pictures detected!")
        logging.info("FAILED CHECK: No valid media in chat %d, at message %d, reply %d)", update.message.chat_id, update.message.message_id, update.message.reply_to_message.message_id)
        return
    
    #Log sucess
    logging.info("PASSED CHECK: Valid post in chat %d, at message %d, reply %d", update.message.chat_id, update.message.message_id, update.message.reply_to_message.message_id)
    
    #Create new message
    postReply = update.message.reply_to_message.reply_text("Processing image...")
    logging.info("POST TRACKING: Created new tracked message in chat %d, at message %d, for reply %d", postReply.chat_id, postReply.message_id, update.message.reply_to_message.message_id)
    
    #Download image
    photo = update.message.reply_to_message.photo[-1]
    photoFile = photo.get_file()
    
    photoFileExt = pathlib.Path(photoFile.file_path).suffix
    tempPhotoPath = MediaTempFolder + photo.file_id + photoFileExt
    
    photoFile.download(custom_path=tempPhotoPath)
    logging.info("PHOTO PROCESSING: Downloaded photo ID: %s", photo.file_id)
    
    #Process image
    imageTags = deepHydrus.evaluate(tempPhotoPath, 0.4)
    logging.info("PHOTO PROCESSING: Processed photo ID: %s", photo.file_id)
    
    #Update post
    if (imageTags):
        newText = "Tags found:\n\n"
        for tag, certainty in imageTags.items():
            newText = newText + tag + ": " + str(round((certainty * 100), 4)) + "%, "
    else:
        newText = "No tags found..."
        
    postReply.edit_text(newText)
    logging.info("POST TRACKING: Updated tracked message in chat %d, at message %d, for reply %d", postReply.chat_id, postReply.message_id, update.message.reply_to_message.message_id)
    
    #Clean up file
    os.remove(tempPhotoPath)
    logging.info("PHOTO PROCESSING: Deleted photo ID: %s", photo.file_id)

def main() -> None:
    #Setup updater
    telegramUpdater = Updater(TelegramAPIToken)
    
    #Grab dispatcher as well
    telegramDispatcher = telegramUpdater.dispatcher
    
    telegramDispatcher.add_handler(MessageHandler(Filters.regex("(?i)^(/SciBot)"), sciBotCommand))
    
    telegramUpdater.start_polling()
    
    telegramUpdater.idle()

if __name__ == '__main__':
    main()