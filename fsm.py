from transitions.extensions import GraphMachine
import os
import random
#
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import shutil
import requests

class TocMachine(GraphMachine):
    bot = None
    voice_flag = None
    realtime_photo_flag = None
    realtime_photo_enable = None
    #
    browser = None
    URL_table = None

    mutex_lock = None

    def __init__(self, **machine_configs):
        global browser

        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )
        self.voice_flag = True
        self.realtime_photo_flag = False
        self.mutex_lock = False
        #
        if os.path.isfile('enable.photoupdate'):
            f = open('enable.photoupdate', 'r')
            temp = f.readline().strip()
            username = f.readline().strip()
            password = f.readline().strip()
            f.close()
            if len(temp) == 1 and int(temp) == 1:
                browser = webdriver.Firefox()
                browser.get('https://accounts.pixiv.net/login?lang=zh_tw&source=pc&view_type=page&ref=wwwtop_accounts_index')
                input_username = browser.find_element_by_xpath('//*[@id="LoginComponent"]/form/div[1]/div[1]/input')
                input_username.send_keys(username)
                input_password = browser.find_element_by_xpath('//*[@id="LoginComponent"]/form/div[1]/div[2]/input')
                input_password.send_keys(password)
                submit_btn = browser.find_element_by_xpath('//*[@id="LoginComponent"]/form/button')
                submit_btn.send_keys(Keys.ENTER)
                time.sleep(3)
                self.random_find_a_photo_update()
                self.realtime_photo_enable = True
            else :
                self.realtime_photo_enable = False
        else:
            f = open('enable.photoupdate', 'w', encoding='UTF-8')
            f.close()
            self.realtime_photo_enable = False

    def set_bot(self, bot):
        self.bot = bot

    def my_reset(self, update):
        self.time_reset(update)

    def is_idle_goto_main(self, update):
        text = update.message.text
        if text.lower() == 'voice on':
            update.message.reply_text("voice on")
            self.voice_flag = True
            return False
        elif text.lower() == 'voice off':
            update.message.reply_text("voice off")
            self.voice_flag = False
            return False       
        elif text.lower() == 'bismarck' or text == 'ビス子' :
            update.message.reply_text("もう～！この私を放置するなんて、貴方も相当偉くなったものね！")
            if self.voice_flag:
                file_src = open('src_voice/Bismarck29.ogg', 'rb')
                self.bot.send_voice(chat_id=update.message.chat_id, voice=file_src)
                file_src.close()
            return True
        elif text.lower() == 'voice':
            update.message.reply_text(str(self.voice_flag))
            return False
        return False

    def is_main_goto_main(self, update):
        text = update.message.text
        if text.lower() == 'bismarck' or text == 'ビス子' :
            update.message.reply_text("Admiral?")
            return True
        elif text.lower() == 'voice on':
            update.message.reply_text("voice on")
            self.voice_flag = True
            return True
        elif text.lower() == 'voice off':
            update.message.reply_text("voice off")
            self.voice_flag = False
            return True
        elif text.lower() == 'voice':
            update.message.reply_text(str(self.voice_flag))
            return True
        elif text.lower() == 'photo local':
            update.message.reply_text("Stop updating photo from Internet")
            self.realtime_photo_flag = False
            return True
        return False
    '''
    def on_enter_main(self, update):
        print('enter main')

    def on_exit_main(self, update):
        print('leave main')
    '''
    def is_main_goto_talk(self, update):
        text = update.message.text
        if '聊天' in text or 'talk' in text.lower() or 'しゃべりしませんか' in text:
            update.message.reply_text('いいよ')
            return True
        return False

    def is_main_goto_help(self, update):
        text = update.message.text
        if '不理我' in text or 'help' in text.lower():
            update.message.reply_text('叫我的名字 再說talk或photo')
            update.message.reply_text('有新年和聖誕節話題')
            return True
        return False

    def is_talk_goto_main(self, update):
        text = update.message.text
        if text.lower() == 'bismarck' or text == 'ビス子' :
            update.message.reply_text('Admiral?')
            return True
        return False

    def is_talk_goto_talk(self, update):
        text = update.message.text
        if 'Xmas' in text or 'merry christmas' in text.lower() or 'クリスマス' in text or '聖誕' in text:
            if 'present' in text.lower() or 'プレゼント' in text or '禮物' in text:
                update.message.reply_text('これを私に？･･･Danke schön!')
            else :
                update.message.reply_text('今年もクリスマスの季節なのね。早いわね。さ、プレゼント渡していいのよ？')
                if self.voice_flag:
                    file_src = open('src_voice/Bismarck02christmas.ogg', 'rb')
                    self.bot.send_voice(chat_id=update.message.chat_id, voice=file_src)
                    file_src.close()
        elif 'new year' in text.lower() or '新年' in text:
            if 'happy new year' in text.lower() or '新年快樂' in text:
                update.message.reply_text('あけましておめでとうございます!')
            else:
                update.message.reply_text('提督、新年も頑張っていきましょう。もちろん私は、いつだって頑張ってるわ。')
                if self.voice_flag:
                    file_src = open('src_voice/Bismarck02_NewYear.ogg', 'rb')
                    self.bot.send_voice(chat_id=update.message.chat_id, voice=file_src)
                    file_src.close()
        elif 'あけましておめでとう' in text or 'あけおめ' in text:
            update.message.reply_text('あけましておめでとうございます!')
        elif '疲れ' in text or '累' in text:
            update.message.reply_text('アトミラール、何事もあまり頑張り過ぎちゃだめよ。気分転換も、大事なのよ？')
            if self.voice_flag:
                file_src = open('src_voice/Bismarck01.ogg', 'rb')
                self.bot.send_voice(chat_id=update.message.chat_id, voice=file_src)
                file_src.close()
        elif '幹' in text or 'fuck' in text.lower():
            update.message.reply_text('Scheiße')
        else:
            update.message.reply_text('なに？')
        return True

    def is_main_goto_photo(self, update):
        text = update.message.text
        if '看' in text or '照片' in text or '写真' in text or 'photo' in text.lower():
            if self.realtime_photo_flag:
                if not self.mutex_lock:
                    self.mutex_lock = True
                    update.message.reply_text('いいよ')
                    self.random_find_a_photo(update)
                    self.mutex_lock = False
                else:
                    update.message.reply_text('我在忙碌中><')
            else:
                update.message.reply_text('いいよ')
                self.random_send_a_photo(update)
            return True
        return False

    def is_photo_goto_main(self, update):
        text = update.message.text
        if text.lower() == 'bismarck' or text == 'ビス子' :
            update.message.reply_text('Admiral?')
            return True
        return False

    def is_photo_goto_photo(self, update):
        text = update.message.text
        if '見たい' in text or '再一張' in text:
            if self.realtime_photo_flag:
                if not self.mutex_lock:
                    self.mutex_lock = True
                    update.message.reply_text('どう？')
                    self.random_find_a_photo(update)
                    self.mutex_lock = False
                else:
                    update.message.reply_text('我在忙碌中><')
            else:
                update.message.reply_text('どう？')
                self.random_send_a_photo(update)
        elif '新' in text:
            if self.realtime_photo_flag:
                if not self.mutex_lock:
                    self.mutex_lock = True
                    self.random_find_a_photo_update()
                    self.mutex_lock = False
                    update.message.reply_text('OK')
                else:
                    update.message.reply_text('我在忙碌中><')
            elif self.realtime_photo_enable:
                self.realtime_photo_flag = True
                update.message.reply_text('OK')
        return True
    
    def is_help_goto_main(self, update):
        text = update.message.text
        if text.lower() == 'bismarck' or text == 'ビス子' :
            update.message.reply_text('Admiral?')
            return True
        return False 

    def is_help_goto_help(self, update):
        update.message.reply_text('叫我的名字 再說talk或photo')
        update.message.reply_text('talk有新年和聖誕節話題')
        return True

    def random_send_a_photo(self, update):
        count = 0

        for root, subFolders, files in os.walk('src1'):
            file_name = random.choice(files)
            file_src = open('src1/'+file_name, 'rb')
            self.bot.send_photo(chat_id=update.message.chat_id, photo=file_src)
            file_src.close()

    def set_voice_flag(self, update, flag):
        self.voice_flag = flag

    def get_voice_flag(self, update):
        return self.voice_flag

    def random_find_a_photo_update(self):
        global browser
        global URL_table

        URL_table = {}

        browser.get('https://www.pixiv.net/search.php?s_mode=s_tag_full&word=%E3%83%93%E3%82%B9%E3%83%9E%E3%83%AB%E3%82%AF(%E8%89%A6%E9%9A%8A%E3%81%93%E3%82%8C%E3%81%8F%E3%81%97%E3%82%87%E3%82%93)')
        soup = BeautifulSoup(browser.page_source,'lxml')
        image_list_soup = soup.find("section", id="js-react-search-mid")
        image_list_soup = image_list_soup.find("div")
        image_list = image_list_soup.find("div")
        class_name = image_list.get('class')
        class_name = class_name[0]

        image_list = image_list_soup.find_all("div", class_name)
        
        for image_link in image_list:
            score = image_link.find("a", "_ui-tooltip bookmark-count")
            if score == None:
                continue
            score = score.text
            URL = image_link.find("a", rel="noopener")
            URL = 'https://www.pixiv.net' + URL.get('href')
            URL_table[URL] = score
        '''
        count = 0
        score = 0
        continue_flag = 1
        while score < 10 and count < 10 and continue_flag:
            count += 1
            URL, score = random.choice(list(URL_table.items()))
            score = int(score)
        
        browser.get(URL)
        soup = BeautifulSoup(browser.page_source,'lxml')
        image_URL = soup.find("div", "_layout-thumbnail ui-modal-trigger")
        if image_URL == None:
            image_URL = soup.find_all("div", "_layout-thumbnail")
            image_URL = image_URL[3]
            image_URL = image_URL.find("img")
            image_URL = image_URL.get('src')
        else:
            image_URL = image_URL.find("img")
            image_URL = image_URL.get('src')

        res = requests.get(image_URL, headers=headers, stream=True)
        f = open("temp.jpg",'wb')
        shutil.copyfileobj(res.raw, f)
        f.close()

        file_src = open("temp.jpg", 'rb')
        self.bot.send_photo(chat_id=update.message.chat_id, photo=file_src)
        file_src.close()
        '''

    def random_find_a_photo(self, update):
        global URL_table
        global browser

        count = 0
        score = 0
        continue_flag = 1
        while score < 10 and count < 10 and continue_flag:
            count += 1
            URL, score = random.choice(list(URL_table.items()))
            score = int(score)

        headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0',
         'Accept':'image/webp,image/apng,image/*,*/*;q=0.8',
         'Accept-Language':'en-US,en;q=0.5', 'Accept-Encoding':'gzip, deflate, br',
         'referer': URL,
         'Connection':'keep-alive'}

        browser.get(URL)
        soup = BeautifulSoup(browser.page_source,'lxml')
        image_URL = soup.find("div", "_layout-thumbnail ui-modal-trigger")
        if image_URL == None:
            image_URL = soup.find_all("div", "_layout-thumbnail")
            image_URL = image_URL[3]
            image_URL = image_URL.find("img")
            image_URL = image_URL.get('src')
        else:
            image_URL = image_URL.find("img")
            image_URL = image_URL.get('src')

        if not image_URL == None:
            res = requests.get(image_URL, headers=headers, stream=True)
            f = open("temp.jpg",'wb')
            shutil.copyfileobj(res.raw, f)
            f.close()
            del res

            file_src = open("temp.jpg", 'rb')
            self.bot.send_photo(chat_id=update.message.chat_id, photo=file_src)
            file_src.close()
        else:
            update.message.reply_text("碰到一點小麻煩 再試一次QQ")

