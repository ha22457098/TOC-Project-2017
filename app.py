import sys
from io import BytesIO

import telegram
from flask import Flask, request, send_file

from fsm import TocMachine

import time
import datetime
import os

#last_time = datetime.datetime.now()
reset_time = datetime.timedelta(seconds=59)

time_table = {}
state_table = {}
voice_flag_table = {}
API_TOKEN = None
WEBHOOK_URL = None

if os.path.isfile('.token'):
    f = open('.token', 'r')
    API_TOKEN = f.readline().strip()
    f.close()
else:
    f = open('.token', 'w', encoding='UTF-8')
    f.close()
    print('Paste token in the ".token" file')
    input("Press Enter to continue...")
    f = open('.token', 'r')
    API_TOKEN = f.readline().strip()
    print("API_TOKEN : " + API_TOKEN)
    f.close()

if os.path.isfile('.webhook'):
    print('Check webhook URL in ".webhook" file if it is correct')
    input('Press Enter to continue...')
    f = open('.webhook', 'r')
    WEBHOOK_URL = f.readline().strip()
    f.close()
    if '/hook' not in WEBHOOK_URL:
        WEBHOOK_URL = WEBHOOK_URL + '/hook'
else:
    f = open('.webhook', 'w', encoding='UTF-8')
    f.close()
    print('Paste webhook URL in the ".webhook" file')
    input("Press Enter to continue...")
    f = open('.webhook', 'r')
    WEBHOOK_URL = f.readline().strip()
    f.close()
    if '/hook' not in WEBHOOK_URL:
        WEBHOOK_URL = WEBHOOK_URL + '/hook'
    
app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)
machine = TocMachine(
    states=[
        'idle',
        'main',
        'talk',
        'photo',
        'help'
    ],
    transitions=[
        {
            'trigger': 'edge_idle',
            'source': 'idle',
            'dest': 'main',
            'conditions': 'is_idle_goto_main'
        },
        {
            'trigger': 'edge_main',
            'source': 'main',
            'dest': 'main',
            'conditions': 'is_main_goto_main'
        },
        {
            'trigger': 'edge_main',
            'source': 'main',
            'dest': 'talk',
            'conditions': 'is_main_goto_talk'
        },
        {
            'trigger': 'edge_main',
            'source': 'main',
            'dest': 'photo',
            'conditions': 'is_main_goto_photo'
        },
        {
            'trigger': 'edge_main',
            'source': 'main',
            'dest': 'help',
            'conditions': 'is_main_goto_help'
        },
        {
            'trigger': 'edge_talk',
            'source': 'talk',
            'dest': 'main',
            'conditions': 'is_talk_goto_main'
        },
        {
            'trigger': 'edge_talk',
            'source': 'talk',
            'dest': 'talk',
            'conditions': 'is_talk_goto_talk'
        },
        {
            'trigger': 'edge_photo',
            'source': 'photo',
            'dest': 'main',
            'conditions': 'is_photo_goto_main'
        },
        {
            'trigger': 'edge_photo',
            'source': 'photo',
            'dest': 'photo',
            'conditions': 'is_photo_goto_photo'
        },
        {
            'trigger': 'edge_help',
            'source': 'help',
            'dest': 'main',
            'conditions': 'is_help_goto_main'
        },
        {
            'trigger': 'edge_help',
            'source': 'help',
            'dest': 'help',
            'conditions': 'is_help_goto_help'
        },
        {
            'trigger': 'time_reset',
            'source': '*',
            'dest': 'idle'
        }
    ],
    initial='main',
    auto_transitions=False,
    show_conditions=True,
)

def check_time(update):
    '''
    global last_time

    now_time = datetime.datetime.now()
    diff = now_time - last_time
    print(diff)
    print(diff > reset_time)
    
    if ( diff > reset_time ):
        machine.my_reset(update)
    
    last_time = now_time
    '''
    now_time = datetime.datetime.now()
    diff = now_time - time_table[update.message.chat_id]
    #print(diff)
    #print(diff > reset_time)

    if ( diff > reset_time ):
        machine.my_reset(update)

    time_table[update.message.chat_id] = now_time

def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))

@app.route('/hook', methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    #print(" ====== up ======")
    #print("chat_id = " + str(update.message.chat_id))
    #print("content = " + update.message.text)
    #print("before state = " + machine.state)
    if update.message == None:
        return 'ok'

    if update.message.chat_id not in state_table:
        machine.machine.set_state('main')
        state_table[update.message.chat_id] = machine.state
    else:
        machine.machine.set_state(state_table[update.message.chat_id])

    if update.message.chat_id not in time_table:
        time_table[update.message.chat_id] = datetime.datetime.now()
    else:
        check_time(update)

    if update.message.chat_id not in voice_flag_table:
        voice_flag_table[update.message.chat_id] = True
    else:
        machine.set_voice_flag(update, voice_flag_table[update.message.chat_id])

    #print("now state = " + machine.state)

    if machine.state == 'idle':
        machine.edge_idle(update)
    elif machine.state == 'main':
        machine.edge_main(update)
    elif machine.state == 'talk':
        machine.edge_talk(update)
    elif machine.state == 'photo':
        machine.edge_photo(update)
    elif machine.state == 'help':
        machine.edge_help(update)

    #print("after state = " + machine.state)
    state_table[update.message.chat_id] = machine.state
    voice_flag_table[update.message.chat_id] = machine.get_voice_flag(update)
    #print(" ======down======")
    return 'ok'


@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')


if __name__ == "__main__":

    _set_webhook()
    machine.set_bot(bot)
    app.run()
