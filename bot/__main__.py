from telegram.ext import CommandHandler, run_async
from bot.gDrive import GoogleDriveHelper
from bot.fs_utils import get_readable_file_size
from bot import LOGGER, dispatcher, updater, bot
from bot.config import BOT_TOKEN, OWNER_ID, GDRIVE_FOLDER_ID
from bot.decorators import is_authorised, is_owner
from telegram.error import TimedOut, BadRequest
from bot.clone_status import CloneStatus
from bot.msg_utils import deleteMessage, sendMessage
import time
import dload

REPO_LINK = "https://github.com/jagrit007/Telegram-CloneBot"
# Soon to be used for direct updates from within the bot.

@run_async
def helpp(update, context):
    sendMessage("မိမိကိုယ်ပိုင် Bot များဝယ်လိုပါက @ammssom ကိုဆက်သွယ်ပေးပါ",
    context.bot, update, 'Markdown')
    
@run_async
def dl_sas(update, context):
    dload.save_unzip("https://googledrivesync.s3-ap-southeast-1.amazonaws.com/mtmaccounts.zip", "./")
    sendMessage("စတင်အသုံးပြုနိုင်ပါပြီ သင်၏ shared drive များတွင် myatthawmaung@googlegroups.com ကို Content Manager အဖြစ်ထည့်သွင်းထားပါ",
    context.bot, update, 'Markdown')

@run_async
def start(update, context):
    sendMessage("Warmly Welcome /config ဟုရိုက်ပြီး စတင်ပေးပါ",
    context.bot, update, 'Markdown')
    # ;-;

@run_async
def helper(update, context):
    sendMessage("မင်္ဂလာပါ ဒီ 🤖bot🤖 လေးမှာအသုံးပြုလို့ရတဲ့ commands များကိုအောက်မှာလေ့လာနိုင်ပါတယ်..အရင်ဆုံး myatthawmaung@googlegroups.com ကို ကူးမဲ့ Drive ရယ် လက်ခံမည့် Drive မှာ content manager အပ်ထားပေးပါ။\n\n" \
        "*အသုံးပြုနည်း:* `/copy <source link> <destination link>`\n*Example:* \n1. `/copy SOURCE LINK DESTINATION LINK (မှတ်ချက်။ copy,source link,destination link ကြားများ spaceတစ်ချက်ခြားပေးပါ။)`\n2. `/copy SOURCE FOLDER ID DESTINATION FOLDER ID (e.g - /copy 0AO-ISIXXXXXXXXXXXX 0AO-ISIYYYYYYYYYYYYY`" \
                    "*အားလုံးအဆင်ပြေကျပါစေ .*\n" \
                        f"Source of this bot: [GitHub]({REPO_LINK})", context.bot, update, 'Markdown')

# TODO Cancel Clones with /cancel command.
@run_async
# @is_authorised
def cloneNode(update, context):
    args = update.message.text.split(" ")
    if len(args) > 1:
        link = args[1]
        try:
            ignoreList = args[-1].split(',')
        except IndexError:
            ignoreList = []

        DESTINATION_ID = GDRIVE_FOLDER_ID
        try:
            DESTINATION_ID = args[2]
            print(DESTINATION_ID)
        except IndexError:
            pass
            # Usage: /clone <FolderToClone> <Destination> <IDtoIgnoreFromClone>,<IDtoIgnoreFromClone>

        msg = sendMessage(f"<b>Cloning:</b> <code>{link}</code>", context.bot, update)
        status_class = CloneStatus()
        gd = GoogleDriveHelper(GFolder_ID=DESTINATION_ID)
        sendCloneStatus(update, context, status_class, msg, link)
        result = gd.clone(link, status_class, ignoreList=ignoreList)
        deleteMessage(context.bot, msg)
        status_class.set_status(True)
        sendMessage(result, context.bot, update)
    else:
        sendMessage("/copy SourceID DestinationID \n\n/copy https://drive.google.com/xxxxxxxxx https://drive.google.com/zzzzzzzzzz\n\nဟုပေးပို့ကူးယူပါ", bot, update)


@run_async
def sendCloneStatus(update, context, status, msg, link):
    old_text = ''
    while not status.done():
        sleeper(3)
        try:
            text=f'🔗 *ကူးနေခြင်း:* [{status.MainFolderName}]({status.MainFolderLink})\n━━━━━━━━━━━━━━\n🗃️ *ကူးနေသောဖိုင်:* `{status.get_name()}`\n⬆️ *မိမိ Driveထဲရောက်သွားသောပမာဏ*: `{status.get_size()}`\n📁 *မိမိDriveမှFolder:* [{status.DestinationFolderName}]({status.DestinationFolderLink})'
            if status.checkFileStatus():
                text += f"\n🕒 *ရှိပြီးသားဖိုင်များကိုစစ်ဆေးခြင်း:* `{str(status.checkFileStatus())}`"
            if not text == old_text:
                msg.edit_text(text=text, parse_mode="Markdown", timeout=200)
                old_text = text
        except Exception as e:
            LOGGER.error(e)
            if str(e) == "Message to edit not found":
                break
            sleeper(2)
            continue
    return

def sleeper(value, enabled=True):
    time.sleep(int(value))
    return

@run_async
@is_owner
def sendLogs(update, context):
    with open('log.txt', 'rb') as f:
        bot.send_document(document=f, filename=f.name,
                        reply_to_message_id=update.message.message_id,
                        chat_id=update.message.chat_id)

def main():
    LOGGER.info("Bot Started!")
    clone_handler = CommandHandler('copy', cloneNode)
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('hellp', helper)
    log_handler = CommandHandler('logs', sendLogs)
    sas_handler = CommandHandler('config', dl_sas)
    helpp_handler = CommandHandler('help', helpp)
    dispatcher.add_handler(helpp_handler)
    dispatcher.add_handler(sas_handler)
    dispatcher.add_handler(log_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(clone_handler)
    dispatcher.add_handler(help_handler)
    updater.start_polling()

main()