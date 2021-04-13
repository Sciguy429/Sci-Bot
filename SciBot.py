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

#Acuracy
ModelOutputAcuracy = 2

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

#Start command
def start(update: Update, context: CallbackContext) -> None:
    #Intro string
    introString = "Hello!\n\nI am a bot desinged to tag images useing an AI neural network!"\
                  " This process is not perfectly acreate, nor fast, but it is able to come up" \
                  " with interesting results most of the time. The AI was trained via aroud 60,000"\
                  " pre-tagged images from a self made Hydrus Database and as such is biased twords"\
                  " the things I trained it with. It can, and will, struggle with things it hasn't"\
                  " seen before. Futhermore the AI has the tendency to slap certian tags on everything"\
                  " you give it. These are all incorrect, the tags themselfs are either too broad for"\
                  " the AI to properly figure out, or so common that their simply is no pattern to them."
    
    #Dm String
    dmString =    "I have deteced this is a dm. Please just send any images you would like me"\
                  " to tag in this chat. I will not respond to direct commands."
    
    #Group string
    groupString = "I have detected this is a group of some kind. Please reply to any image you"\
                  " would like me to tag with '/SciBot'."
    
    #Print differing replys depending on wether we are in a server or dm
    if (update.message.chat.type == update.message.chat.PRIVATE):
        #We are in a dm
        update.message.reply_text(introString + "\n\n" + dmString)
        logging.info("START: Recieved start command in dm id: %d", update.message.chat_id)
    else:
        #We are in a group of some kind
        update.message.reply_text(introString + "\n\n" + groupString)
        logging.info("START: Recieved start command in group id: %d", update.message.chat_id)

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
    postReply = update.message.reply_to_message.reply_text("Processing image...", quote=True)
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
            newText = newText + tag + ": " + str(round((certainty * 100), ModelOutputAcuracy)) + "%, "
    else:
        newText = "No tags found..."
        
    postReply.edit_text(newText)
    logging.info("POST TRACKING: Updated tracked message in chat %d, at message %d, for reply %d", postReply.chat_id, postReply.message_id, update.message.reply_to_message.message_id)
    
    #Clean up file
    os.remove(tempPhotoPath)
    logging.info("PHOTO PROCESSING: Deleted photo ID: %s", photo.file_id)

#Image send in DM
def dmImage(update: Update, _: CallbackContext) -> None:
    #Make sure we were sent a picture
    if (not update.message.photo):
        update.message.reply_text("No pictures detected!")
        logging.info("FAILED CHECK (DM): No valid media in chat %d, at message %d)", update.message.chat_id, update.message.message_id)
        return
    
    #Log sucess
    logging.info("PASSED CHECK (DM): Valid post in chat %d, at message %d", update.message.chat_id, update.message.message_id)
    
    #Create new message
    postReply = update.message.reply_text("Processing image...", quote=True)
    logging.info("POST TRACKING (DM): Created new tracked message in chat %d, at message %d", postReply.chat_id, postReply.message_id)
    
    #Download image
    photo = update.message.photo[-1]
    photoFile = photo.get_file()
    
    photoFileExt = pathlib.Path(photoFile.file_path).suffix
    tempPhotoPath = MediaTempFolder + photo.file_id + photoFileExt
    
    photoFile.download(custom_path=tempPhotoPath)
    logging.info("PHOTO PROCESSING (DM): Downloaded photo ID: %s", photo.file_id)
    
    #Process image
    imageTags = deepHydrus.evaluate(tempPhotoPath, 0.4)
    logging.info("PHOTO PROCESSING (DM): Processed photo ID: %s", photo.file_id)
    
    #Update post
    if (imageTags):
        newText = "Tags found:\n\n"
        for tag, certainty in imageTags.items():
            newText = newText + tag + ": " + str(round((certainty * 100), ModelOutputAcuracy)) + "%, "
    else:
        newText = "No tags found..."
        
    postReply.edit_text(newText)
    logging.info("POST TRACKING (DM): Updated tracked message in chat %d, at message %d", postReply.chat_id, postReply.message_id)
    
    #Clean up file
    os.remove(tempPhotoPath)
    logging.info("PHOTO PROCESSING (DM): Deleted photo ID: %s", photo.file_id)

def main() -> None:
    #Setup updater
    telegramUpdater = Updater(TelegramAPIToken)
    
    #Grab dispatcher as well
    telegramDispatcher = telegramUpdater.dispatcher
    
    #Start command handeler
    telegramDispatcher.add_handler(CommandHandler("start", start))
    
    #Main command handeler
    telegramDispatcher.add_handler(MessageHandler(Filters.regex("(?i)^(/SciBot)"), sciBotCommand))
    
    #Dm handeler
    telegramDispatcher.add_handler(MessageHandler(Filters.chat_type.private, dmImage))
    
    telegramUpdater.start_polling()
    
    telegramUpdater.idle()

if __name__ == '__main__':
    main()