# -*- coding: utf-8 -*-

from mastodon import *
import time, re, sys, os, json, random, io, gc
import threading, requests, pprint, codecs
from time import sleep
from datetime import datetime
from pytz import timezone
import warnings, traceback
import xlrd, xlsxwriter
from xml.sax.saxutils import unescape as unesc
import asyncio

#Winのプロンプトから起動するならこれ追加ね↓
"""
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,
                              encoding=sys.stdout.encoding,
                              errors='backslashreplace',
                              line_buffering=sys.stdout.line_buffering)
                              """
warnings.simplefilter("ignore", UnicodeWarning)

"""ログイントークン取得済みで動かしてね（*'∀'人）"""

url_ins = open("instance.txt").read()

mastodon = Mastodon(
    client_id="cred.txt",
    access_token="auth.txt",
    api_base_url=url_ins)  # インスタンス

jst_now = datetime.now(timezone('Asia/Tokyo'))
nowing = str(jst_now.strftime("%Y%m%d%H%M%S"))
with open('log\\' + 'log_' + nowing + '.txt', 'w') as f:
    f.write(str(jst_now)+'\n')

class Re1():  # Content整頓用関数
    def text(text):
        return (re.sub('<p>|</p>|<a.+"tag">|<a.+"_blank">|<a.+mention">|<span>|'
                       '</span>|</a>|<span class="[a-z-]+">', "",
                       str(text)))

class Log():  # toot記録用クラス٩(๑❛ᴗ❛๑)۶
    def __init__(self, status):
        self.account = status["account"]
        self.mentions = status["mentions"]
        self.content = Re1.text(status["content"])
        self.content = unesc(self.content)
        self.non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

    def read(self):
        name = self.account["display_name"]
        acct = self.account["acct"]
        non_bmp_map = self.non_bmp_map
        print(str(name).translate(non_bmp_map) + "@" + str(
            acct).translate(self.non_bmp_map))
        print(str(self.content).translate(non_bmp_map))
        print(str(self.mentions).translate(non_bmp_map))

    def write(self):
        global nowing
        text = self.content
        acct = self.account["acct"]
        with codecs.open('log\\' + 'log_' + nowing + '.txt', 'a', 'UTF-8') as f:
            f.write(re.sub('<br />', '\\n', str(text)) + ',<acct="' + acct + '">\r\n')


class men_toot(StreamListener):
    def on_update(self, status):
        try:
            HTL.HTL(status)
            pass
        except Exception as e:
            print("エラー情報【USER】\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
            pass

    def on_notification(self, notification):
        try:
            print("===通知が来ました===")
            non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
            if notification["type"] == "mention":
                status = notification["status"]
                account = status["account"]
                mentions = status["mentions"]
                content = unesc(Re1.text(status["content"]))
                log = threading.Thread(Log(status).read())
                log.run()
                bot.thank(account, 64)
                if mentions:
                    if re.compile("おは|おあひょ").search(content):
                        toot_now = "@" + str(account["acct"]) + " " + "（*'∀'人）おあひょーーーー♪"
                        g_vis = status["visibility"]
                        bot.rets(8, toot_now, g_vis, status['id'])
                    elif re.compile("こんに").search(content):
                        toot_now = "@" + str(account["acct"]) + " " + "（*'∀'人）こんにちはーーーー♪"
                        g_vis = status["visibility"]
                        bot.rets(8, toot_now, g_vis, status['id'])
                    elif re.compile("こんば").search(content):
                        toot_now = "@" + str(account["acct"]) + " " + "（*'∀'人）こんばんはーーーー♪"
                        g_vis = status["visibility"]
                        bot.rets(8, toot_now, g_vis, status['id'])
                    elif re.compile("\d+[dD]\d+").search(content):
                        inp = (re.sub("<span class(.+)</span></a></span>|<p>|</p>", "",
                                      str(status['content']).translate(non_bmp_map)))
                        result = game.dice(inp)
                        g_vis = status["visibility"]
                        toot_now = ":@" + str(account["acct"]) + ": @" + account["acct"] + "\n" + result
                        bot.rets(5, toot_now, g_vis, status['id'])
                    elif re.compile("(アラーム|[Aa][Rr][Aa][Mm])(\d+)").search(content):
                        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
                        content = str(status['content']).translate(non_bmp_map)
                        account = status['account']
                        com = re.search("(アラーム|[Aa][Rr][Aa][Mm])(\d+)([秒分]?)", content)
                        sec = int(com.group(2))
                        clo = com.group(3)
                        if clo == "分":
                            sec = sec * 60
                        else:
                            pass
                        print(str(sec))
                        if re.compile("(アラーム|[Aa][Rr][Aa][Mm])(.*)「(.*)」").search(content):
                            mes = re.search("「(.*)」", content)
                            toot_now = ("@" + account["acct"] + " " + "（*'∀'人）時間だよーー♪♪\n"
                                        "「" + mes.group(1) + "」")
                        else:
                            toot_now = "@" + account["acct"] + " " + "（*'∀'人）時間だよーー♪♪"
                        g_vis = status["visibility"]
                        in_reply_to_id = status["id"]
                        t = threading.Timer(sec, bot.toot, [toot_now, g_vis, status['id']])
                        t.start()
                        #bot.rets(sec,toot_now, g_vis,status['id'] )
                    elif re.compile(
                                    "(フォロー|follow)(して|く[うぅー]*ださ[あぁー]*い|お願[あぁー]*い|"
                                    "おねが[あぁー]*い|頼[むみ]|たの[むみ]|ぷりーず|プリーズ|please)").search(
                                    content):
                        mastodon.account_follow(account["id"])
                        toot_now = "@" + account["acct"] + " " + "（*'∀'人）フォローしました♪♪"
                        g_vis = status["visibility"]
                        in_reply_to_id = status["id"]
                        bot.rets(8, toot_now, g_vis, status['id'])
                    elif re.compile("(こそこそ)<br />(.+)").search(content):  # 悪用されないように変えてます
                        if status["visibility"] == "direct":
                            print("○受け取りました")
                            com = re.search("(こそこそ).*<br />(.+)", str(content))
                            messe = com.group(2)
                            toot_now = messe
                            g_vis = "public"
                            bot.rets(1, toot_now, g_vis)
                    elif re.compile("連想ゲーム開始").search(content):
                        if rensou_time:
                            toot_now = ("@" + account["acct"] + " "
                                        + "（*'∀'人）ごめんね、今開催中なの♪♪")
                            g_vis = status["visibility"]
                            in_reply_to_id = status["id"]
                            bot.rets(5, toot_now, g_vis, status['id'])
                        else:
                            t = threading.Timer(0, game.rensou)
                            t.start()
                            rensou_time = True
                    elif account["acct"] == "twotwo":
                        if re.compile("").search(content):
                            pass
                    else:
                        pass
                v = threading.Timer(5, bot.fav_now,[status["id"]])
                v.start()
            elif notification["type"] == "favourite":
                account = notification["account"]
                print(str(account["display_name"]).translate(non_bmp_map) + "@" + str(
                    account["acct"]) + "からニコってくれたよ₍₍ ◝(●˙꒳˙●)◜ ₎₎")
                print()
                bot.thank(account, 32)
                print("---")
            elif notification["type"] == "reblog":
                account = notification["account"]
                print(str(account["display_name"]).translate(non_bmp_map) + "@" + str(
                    account["acct"]) + "がブーストしてくれたよ(๑˃́ꇴ˂̀๑)")
                print()
                bot.thank(account, 32)
                print("---")
            pass
        except Exception as e:
            print("エラー情報【USER】\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
            pass


class res_toot(StreamListener):
    def on_update(self, status):
        try:
            print("===タイムライン===")
            log = threading.Thread(Log(status).read())
            log.run()
            Log(status).write()
            ltl = threading.Thread(LTL.LTL(status))
            ltl.run()
            print("   ")
            pass
        except Exception as e:
            print("エラー情報【LOCAL】\n" + traceback.format_exc())
            with open('error.log', 'a') as f:
                traceback.print_exc(file=f)
            pass

    def on_delete(self, status_id):
        print(str("===削除されました【{}】===").format(str(status_id)))

class HTL():
    def HTL(status):
        account = status["account"]
        ct = account["statuses_count"]
        if account["acct"] == "JC":
            path = 'thank\\' + account["acct"] + '.txt'
            if os.path.exists(path):
                f = open(path, 'r')
                x = f.read()
                f.close()
                ct += 1
                if re.match('^\d+000$', str(ct)):
                    toot_now = "°˖✧◝(⁰▿⁰)◜✧˖" + str(ct) + 'toot達成ーーーー♪♪'
                    g_vis = "public"
                    bot.rets(4, toot_now, g_vis)
        else:
            bot.check03(status)


class LTL():
    def LTL(status):  # ここに受け取ったtootに対してどうするか追加してね（*'∀'人）
        # 以下bot機能の一覧
        bot.check01(status)
        bot.fav01(status)
        bot.res01(status)
        bot.res02(status)
        bot.res03(status)
        bot.check00(status)
        bot.check02(status)
        game.poem(status)
        game.senryu(status)
        game.cinema(status)
        # ここまで

class bot():
    def _init_(self):
        pass

    def res(sec):
        count.end = count.end - sec
        if count.end < 0:
            count.end = 0

    def rets(sec, toot_now, g_vis, rep=None, spo=None):
        now = time.time()
        delay = now - count.CT
        loss = count.end - int(delay)
        if loss < 0:
            loss = 0
        ing = sec + loss
        t = threading.Timer(ing, bot.toot, [toot_now, g_vis, rep, spo])
        t.start()
        print("【次までのロスタイム:" + str(count.end+sec) + "】")
        s = threading.Timer(ing, bot.res, [sec])
        s.start()
        del t
        del s
        gc.collect()
        count.CT = time.time()
        count.end = ing

    def toot(toot_now, g_vis, rep=None, spo=None):
        mastodon.status_post(status=toot_now,
                             visibility=g_vis,
                             in_reply_to_id=rep,
                             spoiler_text=spo)
        print("【次までのロスタイム:" + str(count.end) + "】")
        """
        visibility これで公開範囲を指定できるよ！: public, unlisted, private, direct
        """

    def standby():
        print("「(๑•̀ㅁ•́๑)✧＜tootｽﾃﾝﾊﾞｰｲ」")

    def block01(status):
        f = codecs.open("NG\sekuhara.txt", 'r', 'utf-8')
        l = []
        for x in f:
            l.append(x.rstrip("\r\n"))
        f.close()
        m = len(l)
        for x in range(m):
            if re.compile(str(l[x])).search(re.sub("<p>|</p>", "", str(status))):
                j = True
                print(str(l[x]))
                # bot.thank(account, -64)
                break
            else:
                j = False
        return j

    def res03(status):
        account = status["account"]
        if account['acct'] != "kiri_bot01":
            if account["acct"] != "JC":
                if re.compile("ももな(.*)[1-5][dD]\d+").search(status['content']):
                    print("○hitしました♪")
                    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
                    coro = (re.sub("<p>|</p>", "", str(status['content']).translate(non_bmp_map)))
                    toot_now = ":@" + account["acct"] + ": @" + account["acct"] + "\n" + game.dice(coro)
                    bot.rets(8, toot_now, status["visibility"])
                elif re.compile("ももな(.*)([6-9]|\d{2})[dD](\d*)").search(status['content']):
                    toot_now = "@{} ６回以上の回数は畳む内容だからメンションの方で送ってーー！！".format(account["acct"])
                    bot.rets(6, toot_now, status["visibility"],status["id"])

    def check00(status):
        account = status["account"]
        ct = account["statuses_count"]
        path = 'thank\\' + account["acct"] + '.txt'
        if os.path.exists(path):
            f = open(path, 'r')
            x = f.read()
            f.close()
        if int(x) >= -10:
            if account["acct"] == "JC":
                pass
                #ct += 1
                #if re.match('^\d+000$', str(ct)):
                #    toot_now = "°˖✧◝(⁰▿⁰)◜✧˖" + str(ct) + 'toot達成ーーーー♪♪'
                #    g_vis = "public"
                #    bot.rets(4, toot_now, g_vis)
            else:
                if re.match('^\d+0000$', str(ct)):
                    toot_now = (" :@" + account['acct'] + ": @" +
                                account['acct'] + "\n°˖✧◝(⁰▿⁰)◜✧˖" + str(ct) +
                                'tootおめでとーーーー♪♪')
                    g_vis = "public"
                    bot.rets(4, toot_now, g_vis)
                elif re.match('^\d000$', str(ct)):
                    toot_now = (" :@" + account['acct'] + ": @" +
                                account['acct'] + "\n（*'∀'人）" + str(ct) +
                                'tootおめでとーー♪')
                    g_vis = "public"
                    bot.rets(4, toot_now, g_vis)
        else:
            pass

    def check03(status):
        account = status["account"]
        ct = account["statuses_count"]
        if account["acct"] == "Knzk":  # 神崎おにいさん監視隊
            ct += 5
            if re.match('^\d+000$', str(ct)):
                toot_now = "@Knzk (๑•̀ㅁ•́๑)神崎おにいさん！！\n" + str(ct) + 'tootまであと5だよ！！！！'
                g_vis = "direct"
                bot.rets(4, toot_now, g_vis)
        elif account["acct"] == "5":  # やなちゃん監視隊
            ct += 5
            if re.match('^\d+0000$', str(ct)):
                toot_now = "@5 (๑•̀ㅁ•́๑)やなちゃん！！\n" + str(ct) + 'tootまであと5だよ！！！！'
                g_vis = "direct"
                bot.rets(4, toot_now, g_vis)
        elif account["acct"] == "yzhsn":  # 裾野監視隊
            ct += 5
            if re.match('^\d+000$', str(ct)):
                toot_now = "@yzhsn (๑•̀ㅁ•́๑)おい裾野！！\n" + str(ct) + 'tootまであと5だよ！！！！'
                g_vis = "direct"
                bot.rets(4, toot_now, g_vis)
        elif account["acct"] == "lamazeP":  # ラマーズＰ監視隊
            ct += 5
            if re.match('^\d+000$', str(ct)):
                toot_now = "@lamazeP (๑•̀ㅁ•́๑)" + str(ct) + 'tootまであと5だよ！！！！'
                g_vis = "direct"
                bot.rets(4, toot_now, g_vis)
        else:  # テスト
            ct += 5
            if re.match('^\d+000$', str(ct)):
                toot_now = ("@" + account["acct"] +
                            " (๑•̀ㅁ•́๑)ただいまフォローしてる方にテスト中！\n" + str(ct) +
                            'tootまであと5だよ！！！！')
                g_vis = "direct"
                bot.rets(4, toot_now, g_vis)

    def res01(status):
        account = status["account"]
        content = re.sub("<p>|</p>", "", str(status['content']))
        path = 'thank\\' + account["acct"] + '.txt'
        if os.path.exists(path):
            f = open(path, 'r')
            x = f.read()
            f.close()
        if int(x) >= -10:
            if account["acct"] != "JC" and account["acct"] != "kiri_bot01":
                if count.timer_hello == 0:
                    if re.compile("ももな(.*)おは|ももな(.*)おあひょ").search(content):
                        print("○hitしました♪")
                        print("○あいさつします（*'∀'人）")
                        toot_now = "(๑•̀ㅁ•́๑)✧おはありでーーーーす♪" + "\n#ニコフレ挨拶部"
                        g_vis = "public"
                        bot.rets(20, toot_now, g_vis)
                        count.timer_hello = 1
                else:
                    if re.compile("寝(ます|る|マス)([よかぞね]?|[…。うぅー～！]+)$|^ねる$|"
                                  "[寝ね](ます|る|マス)(.*)[ぽお]や[すし]|ももな(.*)[ぽお]や[すしー]").search(content):
                        if not re.compile("[寝ね]る(人|ひと)").search(status['content']):
                            print("○hitしました♪")
                            print("○おやすみします（*'∀'人）")
                            if account['acct'] == "5":  # やなちゃん専用挨拶
                                print("○やなちゃんだ！！（*'∀'人）")
                                toot_now = (":@" + account['acct'] + ":" +
                                            "やなちゃん！！！！！！" + "\n" +
                                            '(｡>﹏<｡)あとで一緒に寝るーーーー！！！！'
                                             + "\n#ニコフレ挨拶部")
                            else:
                                toot_now = (":@" + account['acct'] + ":" + account[
                                    'display_name'] + "\n" + '(ृ 　 ु *`ω､)ु ⋆゜おやすみーーーー♪'
                                             + "\n#ニコフレ挨拶部")
                            g_vis = "public"
                            bot.rets(6, toot_now, g_vis)
                    elif re.compile("([いイ行逝]って|出かけて|(風呂|ふろ).*(入|はい)って)(くる|きま[あぁー]*す|[きキ]マストドン)[^？\?]|"
                                    "おでかけ(する|しま[あぁー]*す|[しシ]マストドン)[^？\?]|(ふろ|風呂)って(くる|きます)|"
                                    "(出勤|離脱|しゅっきん|りだつ)(する[^な]|しま[あぁー]*す[^？\?]|[しシ]マストドン)|"
                                    "(出勤|離脱)$|(.+)して(くる|きま[あぁー]*す[^？\?]|[きキ]マストドン)([ー～！。よぞね]|$)|"
                                    "(仕事|しごと).*(戻|もど)(る|りゅ|りま[すつ])|(飯|めし)って(くる|きます)|(めし|飯)([い行]く|[お落]ち)"
                                    ).search(content):
                        print("○hitしました♪")
                        print("○見送ります（*'∀'人）")
                        if account['acct'] == "5":  # やなちゃん専用挨拶
                            print("○やなちゃんだ！！（*'∀'人）")
                            toot_now = (":@" + account['acct'] + ":" + "やなちゃん！！！！！！" +
                                        "\n" + '(*>_<*)ﾉいってらいってらーーーー！！！！'
                                         + "\n#ニコフレ挨拶部")
                        else:
                            toot_now = (":@" + account['acct'] + ":" + account['display_name'] +
                                        "\n" + 'いってらーーーー！！' + "\n#ニコフレ挨拶部")
                        g_vis = "public"
                        bot.rets(6, toot_now, g_vis)
                    elif re.compile("ただいま(です|[！あー～。…]*(<br/ >|$)|(もど|戻)(ってきた|った|りました))|ただいマストドン"
                                    "|(おうち|家).*([着つ]いた|帰った|帰ってきた)|(帰宅|きたく)(した|しました|$)|"
                                    "^ただいま|(飯|めし|ふろ|風呂|シャワー).*(もど|戻)ってき(た|ました)|ほかってき(た|ました)").search(content):
                        print("○hitしました♪")
                        print("○優しく迎えます（*'∀'人）")
                        if account['acct'] == "5":  # やなちゃん専用挨拶
                            print("○やなちゃんだ！！（*'∀'人）")
                            toot_now = (":@" + account['acct'] + ":" + "やなちゃん！！！！！！" +
                                        "\n" + '٩(๑❛ᴗ❛๑)۶おかえりおかえりーー！！' + "\n#ニコフレ挨拶部"
                                        )
                        else:
                            toot_now = (":@" + account['acct'] + ":" + account['display_name']
                                        + "\n" + '( 〃 ❛ᴗ❛ 〃 )おかえりおかえりーー！！'
                                        + "\n#ニコフレ挨拶部")
                        g_vis = "public"
                        bot.rets(6, toot_now, g_vis)
                    else:
                        try:
                            f = codecs.open('at_time\\' + account["acct"] + '.txt', 'r', 'UTF-8')
                            nstr = f.read()
                            f.close
                            print(nstr)
                            tstr = re.sub("\....Z", "", nstr)
                            last_time = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S')
                            nstr = status['created_at']
                            tstr = re.sub("\....Z", "", nstr)
                            now_time = datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%S')
                            delta = now_time - last_time
                            print(delta)
                            if delta.total_seconds() >= 604800:
                                if account['acct'] == "5":  # やなちゃん専用挨拶
                                    print("○やなちゃんだ！！（*'∀'人）")
                                    toot_now = (":@" + account['acct'] + ":" + "やなちゃん！！！！！！" +
                                                "\n" + "（*'∀'人）おひさひさーーーー♪"
                                                + "\n#ニコフレ挨拶部")
                                else:
                                    toot_now = (" :@" + account['acct'] + ":\n" + account['acct']
                                                + "\n" + "（*'∀'人）おひさひさーーーー♪" + "\n#ニコフレ挨拶部")
                                g_vis = "public"
                                bot.rets(6, toot_now, g_vis)
                            elif delta.total_seconds() >= 10800:
                                if now_time.hour in range(3, 9):
                                    to_r = bot.rand_w('time\\kon.txt')
                                elif now_time.hour in range(9, 19):
                                    to_r = bot.rand_w('time\\kob.txt')
                                else:
                                    to_r = bot.rand_w('time\\oha.txt')
                                if account['acct'] == "5":  # やなちゃん専用挨拶
                                    print("○やなちゃんだ！！（*'∀'人）")
                                    toot_now = (":@" + account['acct'] + ":" + "やなちゃん！！！！！！"
                                                + "\n" + to_r + "\n#ニコフレ挨拶部")
                                else:
                                    print("○あいさつします（*'∀'人）")
                                    if account['display_name'] == "":
                                        toot_now = (":@" + account['acct'] + ":" +
                                                    account['acct'] + "\n" + to_r + "\n#ニコフレ挨拶部")
                                    else:
                                        toot_now = (":@" + account['acct'] + ":" +
                                                    account['display_name'] + "\n" + to_r + "\n#ニコフレ挨拶部")
                                g_vis = "public"
                                bot.rets(6, toot_now, g_vis)
                        except:
                            print("○初あいさつします（*'∀'人）")
                            if account['statuses_count'] <= 2:
                                if account['display_name'] == "":
                                    toot_now = (" :@" + account['acct'] + ": @" + account[
                                        'acct'] + "\n" + account['acct'] + "\n" +
                                                'ようこそようこそーーーー♪' + "\n#ニコフレ挨拶部")
                                else:
                                    toot_now = (" :@" + account['acct'] + ": @" + account[
                                        'acct'] + "\n" + account['display_name'] + "\n" +
                                                'ようこそようこそーーーー♪' + "\n#ニコフレ挨拶部")
                                shinki = True
                            else:
                                if account['display_name'] == "":
                                    toot_now = (" :@" + account['acct'] + ": @" + account[
                                            'acct'] + "\n" + 'いらっしゃーーーーい♪' + "\n#ニコフレ挨拶部")
                                else:
                                    toot_now = (" :@" + account['acct'] + ": @" + account[
                                            'acct'] + "\n" + 'いらっしゃーーーーい♪' + "\n#ニコフレ挨拶部")
                                shinki = False
                            g_vis = "public"
                            bot.rets(6, toot_now, g_vis)
                            if shinki is True:
                                bot.toot("@lamazeP 新規さんが来たよーー（小声）\n【" + str(account['acct']) + "】",
                                         "direct", status["id"])

        else:
            print("○反応がない人なので挨拶しません（*'∀'人）")

    def res02(status):
        account = status["account"]
        content = Re1.text(status["content"])
        if account["acct"] != "JC":
            if re.compile("(.+)とマストドン(どちら|どっち)が大[切事]か[分わ]かってない").search(content):
                print("○hitしました♪")
                sekuhara = bot.block01(status)
                if len(content) > 60:
                    toot_now = "٩(๑`^´๑)۶長い！！！！！！"
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
                else:
                    if not sekuhara:
                        print("○だったら")
                        # if re.compile("(.+)するのとマストドン(どちら|どっち)が大[切事]か[分わ]かってない").search(content):
                        toot_now = ":@" + account["acct"] + ":" + (
                        re.sub('<span(.+)span>|<p>|とマストドン(.*)', "", str(content))) + "しながらマストドンして❤"
                        g_vis = "public"
                        bot.rets(5, toot_now, g_vis)
                    else:
                        toot_now = "そんなセクハラ分かりません\n(* ,,Ծ‸Ծ,, )ﾌﾟｰ"
                        g_vis = "public"
                        bot.rets(5, toot_now, g_vis)

    def fav01(status):
        account = status["account"]
        if re.compile("(ももな|:@JC:|ちゃんもも|:nicoru\d*:|JC)").search(status['content']):
            bot.thank(account, 8)
            v = threading.Timer(5, bot.fav_now,[status["id"]])
            v.start()

    def check01(status):
        account = status["account"]
        created_at = status['created_at']
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        with codecs.open('acct\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:  # 書き込みモードで開く
            f.write(str(status["account"]).translate(non_bmp_map))  # アカウント情報の更新
        path = 'thank\\' + account["acct"] + '.txt'
        if os.path.exists(path):
            f = open(path, 'r')
            x = f.read()
            print("現在の評価値:" + str(x))
            f.close()
        else:
            f = open(path, 'w')
            f.write("0")
            f.close()  # ファイルを閉じる

    def check02(status):
        account = status["account"]
        created_at = status['created_at']
        with codecs.open('at_time\\' + account["acct"] + '.txt', 'w', 'UTF-8') as f:  # 書き込みモードで開く
            f.write(str(status["created_at"]))  # \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z

    def thank(account, point):
        path = 'thank\\' + account["acct"] + '.txt'
        if os.path.exists(path):
            f = open(path, 'r')
            x = f.read()
            y = int(x)
            y += point
            f.close()
            f = open(path, 'w')
            f.write(str(y))
            f.close()
            print("現在の評価値:" + str(y))
        else:
            f = open(path, 'w')
            f.write(str(point))
            f.close()  # ファイルを閉じる
            print("現在の評価値:" + str(0))

    def fav_now(fav):  # ニコります
        mastodon.status_favourite(fav)
        print("◇Fav")

    def rand_w(txt_deta):
        f = codecs.open(txt_deta, 'r', 'utf-8')
        l = []
        for x in f:
            l.append(x.rstrip("\r\n").replace('\\n', '\n'))
        f.close()
        m = len(l)
        s = random.randint(1, m)
        return l[s - 1]

    def t_local():
        try:
            listener = res_toot()
            mastodon.local_stream(listener)
        except:
            print("例外情報\n" + traceback.format_exc())
            with open('except.log', 'a') as f:
                jst_now = datetime.now(timezone('Asia/Tokyo'))
                f.write("\n\n【" + str(jst_now) + "】\n")
                traceback.print_exc(file=f)
            sleep(180)
            bot.t_local()
            pass

    def t_user():
        try:
            listener = men_toot()
            mastodon.user_stream(listener)
        except:
            print("例外情報\n" + traceback.format_exc())
            with open('except.log', 'a') as f:
                jst_now = datetime.now(timezone('Asia/Tokyo'))
                f.write("\n\n【" + str(jst_now) + "】\n")
                traceback.print_exc(file=f)
            sleep(180)
            bot.t_user()
            pass


class game():
    def fav(id):
        mastodon.status_favourite(id)

    def cinema(status):
        account = status["account"]
        content = Re1.text(status["content"])
        gameIn = ("(劇場|げきじょう|[Cc]inema|シネマ)(ゲーム|げーむ)[：:]"+
                  "<br />【(.+)】<br />起[：:](.+)<br />承[：:](.+)<br />転[：:](.+)<br />結[：:](.+)")
        gameOut = "(劇場|げきじょう|[Cc]inema|シネマ)(ゲーム|げーむ)"+".*(ひとつ|おねが[いひ]|お願[いひ]|[1１一]つ)"
        if re.compile(gameIn).search(content):
            print("○hitしました♪")
            word = re.search(gameIn+"<br />.*", str(content))
            sekuhara = bot.block01(status)
            if sekuhara:
                bot.rets(5, "٩(๑`^´๑)۶えっちなのはよくない！！！！", "public")
            else:
                Title = word.group(3)
                Ki = word.group(4)
                Sho = word.group(5)
                Ten = word.group(6)
                Kets = word.group(7)
                if len(Ki) > 80 or len(Sho) > 80 or len(Ten) > 80 or len(Kets) > 80 or len(Title) > 60:
                    bot.rets(5, "٩(๑`^´๑)۶長い！！！！！！", "public")
                    pass
                else:
                    f = codecs.open('game\\cinema_word.txt', 'a', 'UTF-8')
                    f.write(Title+">>"+Ki+">>"+Sho+">>"+Ten+">>"+Kets+">>"+account["acct"]+"\r\n" )
                    f.close()
                    v = threading.Timer(5, game.fav, [status["id"]])
                    v.start()
                    print("◆　成功しました(∩´∀｀)∩　◆")
            return
        elif re.compile("ももな.*"+gameOut).search(content):
            if account["acct"] != "JC":
                f = codecs.open('game\\cinema_word.txt', 'r', 'utf-8')
                word1 = []
                for x in f:
                    word1.append(x.rstrip("\r\n").replace('\\n', '\n'))
                f.close()
                m = len(word1)
                word2 = []
                name = []
                for x in range(5):
                    s = random.randint(0, m-1)
                    word2.append((word1[s]).split('>>'))
                c0 = word2[0]
                c1 = word2[1]
                c2 = word2[2]
                c3 = word2[3]
                c4 = word2[4]
                c5 = [c0[5],c1[5],c2[5],c3[5],c4[5]]
                cast = list(set(c5[1:]))
                toot_now = ("【タイトル】\n"+unesc(c0[0])+"\n\n【あらすじ】\n"+unesc(c1[1])+
                            "\n"+unesc(c2[2])+"\n"+unesc(c3[3])+"\n"+unesc(c4[4])+"\n\n"
                            "【スタッフ】\n監督：:@"+c0[5]+":\n主演キャスト：:@"+str("::@".join(cast)))+ ":\n#劇場げーむ"
                spo = ":@" + account["acct"] + ":さんに上映開始のお知らせ"
                return bot.rets(6, toot_now, "public", None, spo)


    def world(status):
        account = status["account"]
        content = Re1.text(status["content"])
        hitting = 'セカイが(.+)になっちゃ(っ[たて]|いま[すし])'
        if re.compile(hitting).search(content):
            wrd = re.search(hitting, str(content))
            toot_now = 'セカイが' + wrd(1) + 'になっちゃった♪'
            bot.rets(5, toot_now, "public")
        else:
            pass

    def rensou(status):
        """
        toot = bot.toot
        toot("٩(๑❛ᴗ❛๑)۶今から連想ゲームを始めます！！", "")

　　　　"""
        pass

    def quiz(status):
        account = status["account"]
        content = Re1.text(status["content"])
        if re.compile("クイズ(問題|もんだい)[：:]<br />").search(content):
            try:
                qz = re.search("クイズ(問題|もんだい)[：:]<br />[QqＱｑ][.．](.+)<br />"
                               "[AaＡａ][.．](.+)", str(content))
                #ファイル読み書きモードで呼び出し
                #lenを確認して番号振り
                #書き出し処理＆保存
                return ("クイズ問題、登録しました（*'∀'人）\n"
                        "問題番号"+ "xxx")
            except:
                return "クイズ問題、登録に失敗しました(｡>﹏<｡)"
                pass
            pass
        elif re.compile("クイズ(回答|解答|かいとう)[：:]<br />").search(content):
            ans = re.search("クイズ(回答|解答|かいとう)[：:]<br />[QqＱｑ][.．](.+)<br />"
                            "[AaＡａ][.．](.+)", str(content))
            pass

    def memo(status):
        account = status["account"]
        content = Re1.text(status["content"])
        if re.compile("ももな.*(メモ|めも)[：:]").search(content):
            try:
                memo = re.search("ももな.*(メモ|めも)[：:]?(<br />)(.+)?(<br />)", str(content))
                tex = memo.group(3)  #記録用の要素取り出し
                #書き出し処理＆保存
                f = codecs.open('game\\memo_word.txt', 'a', 'UTF-8')
                f.write(tex + ">>" + account["acct"] + "\r\n" )
                f.close()
                # bot.rets(5, "メモしました（*'∀'人）", "public")
                return "メモしました（*'∀'人）"
            except:
                # bot.rets(5, "メモに失敗しました(｡>﹏<｡)", "public")
                return "メモに失敗しました(｡>﹏<｡)"
                pass
            pass
        # ある程度溜まったらメモまとめをお願いするシステムの予定
        pass

    def poem(status):
        account = status["account"]
        content = Re1.text(status["content"])
        if account["acct"] == "twotwo":
            if re.compile("ﾄｩﾄｩﾄｩﾄｩｰﾄｩ[：:]").search(content):
                poes = re.search("(ﾄｩﾄｩﾄｩ)(ﾄｩｰﾄｩ)[：:]<br />(.*)", str(content))
                Poe = poes.group(3)
                if len(content) > 60:
                    toot_now = "٩(๑`^´๑)۶ﾄｩﾄｩ！！！！！！"
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
                else:
                    Poe = re.sub("<br />", "\\n", Poe)
                    f = codecs.open('game\\poem_word.txt', 'a', 'UTF-8')
                    f.write(str(Poe) + " &,@" + account["acct"] + "\r\n" )
                    f.close()
                    v = threading.Timer(5, game.fav, [status["id"]])
                    v.start()
            elif re.compile("ﾄｩﾄｩﾄｩﾄｩｰﾄｩﾄｩ!").search(content):
                f = codecs.open('game\\poem_word.txt', 'r', 'utf-8')
                word1 = []
                for x in f:
                    word1.append(x.rstrip("\r\n").replace('\\n', '\n'))
                f.close()
                m = len(word1)
                word2 = []
                for x in range(5):
                    s = random.randint(0, m-1)
                    word2.append((word1[s]).split(' &,@'))
                poe0 = word2[0]
                poe1 = word2[1]
                poe2 = word2[2]
                poe3 = word2[3]
                poe4 = word2[4]
                toot_now = poe0[0] + "\n" + poe1[0] + "\n" + poe2[0] + "\n" + poe3[
                    0] + "\n" + poe4[0] + "\n(by:@" + poe0[1] + ":-:@" + poe1[1] + ":-:@" + poe2[
                        1] + ":-:@" + poe3[1] + ":-:@"+poe4[1] + ":)\n#ぽえむげーむ"
                g_vis = "public"
                spo = ":@" + account["acct"] + ":トゥートゥー♪♪"
                bot.rets(6, toot_now, g_vis, None, spo)
        else:
            if re.compile("(ぽえむ|ポエム)(ゲーム|げーむ)[：:]").search(content):
                poes = re.search("(ぽえむ|ポエム)(ゲーム|げーむ)[：:]<br />(.*)", str(content))
                Poe = poes.group(3)
                Poe = unesc(Poe)
                sekuhara = bot.block01(status)
                if sekuhara:
                    toot_now = "٩(๑`^´๑)۶えっちなのはよくない！！！！"
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
                if len(content) > 60:
                    toot_now = "٩(๑`^´๑)۶長い！！！！！！"
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
                else:
                    Poe = re.sub("<br />", "\\\\n", Poe)
                    f = codecs.open('game\\poem_word.txt', 'a', 'UTF-8')
                    f.write(str(Poe) + " &,@" + account["acct"] + "\r\n" )
                    f.close()
                    v = threading.Timer(5, game.fav, [status["id"]])
                    v.start()
            elif re.compile("ももな.*(ぽえむ|ポエム)(ゲーム|げーむ).*(ひとつ|おねがい|お願い|１つ|一つ)").search(content):
                if account["acct"] != "JC":
                    f = codecs.open('game\\poem_word.txt', 'r', 'utf-8')
                    word1 = []
                    for x in f:
                        word1.append(x.rstrip("\r\n").replace('\\n', '\n'))
                    f.close()
                    m = len(word1)
                    word2 = []
                    for x in range(5):
                        s = random.randint(0, m-1)
                        word2.append((word1[s]).split(' &,@'))
                    poe0 = word2[0]
                    poe1 = word2[1]
                    poe2 = word2[2]
                    poe3 = word2[3]
                    poe4 = word2[4]
                    toot_now = poe0[0] + "\n" + poe1[0] + "\n" + poe2[0] + "\n" + poe3[
                        0] + "\n" + poe4[0] + "\n(by:@" + poe0[1] + ":-:@" + poe1[1] + ":-:@" + poe2[
                            1] + ":-:@" + poe3[1] + ":-:@"+poe4[1] + ":)\n#ぽえむげーむ"
                    g_vis = "public"
                    spo = ":@" + account["acct"] + ":にぽえむ♪♪"
                    bot.rets(6, toot_now, g_vis, None, spo)

    def senryu(status):
        account = status["account"]
        content = Re1.text(status["content"])
        if account["acct"] == "twotwo":
            if re.compile("ﾄｩｰﾄｩｰﾄｩｰﾄｩ[：:]<br />(.+)<br />(.+)<br />(.+)").search(content):
                poes = re.search("(ﾄｩｰﾄｩｰ)(ﾄhuｩｰﾄｩ)[：:]<br />(.+)<br />(.+)<br />(.+)", str(content))
                sen1 = poes.group(3)
                sen2 = poes.group(4)
                sen3 = poes.group(5)
                if len(sen1) > 6 or len(sen2) > 8 or len(sen3) > 6:
                    pass
                else:
                    f = codecs.open('game\\senryu_word.txt', 'a', 'UTF-8')
                    f.write(unesc(sen1) + ">>>" + unesc(sen2) + ">>>" +
                            unesc(sen3) + ">>>" + account["acct"] + "\r\n" )
                    f.close()
                    v = threading.Timer(5, game.fav, [status["id"]])
                    v.start()
            elif re.compile("ﾄｩﾄｩﾄｩ-ﾄｩｰﾄｩ!").search(content):
                f = codecs.open('game\\senryu_word.txt', 'r', 'utf-8')
                word1 = []
                for x in f:
                    word1.append(x.rstrip("\r\n").replace('\\n', '\n'))
                f.close()
                m = len(word1)
                word2 = []
                for x in range(4):
                    s = random.randint(0, m-1)
                    word2.append((word1[s]).split('>>>'))
                h0 = word2[0]
                h1 = word2[1]
                h2 = word2[2]
                h3 = word2[3]
                toot_now = (h0[0] + "\n" + h1[1] + "\n" + h2[2] +"\n（作者：:@" +
                            h3[3] + ":）\n:@" + account["acct"] +":ﾄｩｰﾄｩﾄｩﾄｩｰﾄｩ❤\n#川柳げーむ")
                g_vis = "public"
                bot.rets(6, toot_now, g_vis)
        else:
            if re.compile("(せんりゅう|川柳)(ゲーム|げーむ)[：:]<br />(.+)<br />(.+)<br />(.+)").search(content):
                poes = re.search("(せんりゅう|川柳)(ゲーム|げーむ)[：:]<br />(.+)<br />(.+)<br />(.+)", str(content))
                sen1 = poes.group(3)
                sen2 = poes.group(4)
                sen3 = poes.group(5)
                sekuhara = bot.block01(status)
                if sekuhara:
                    toot_now = "٩(๑`^´๑)۶えっちなのはよくない！！！！"
                    g_vis = "public"
                    bot.rets(5, toot_now, g_vis)
                if len(sen1) > 6 or len(sen2) > 8 or len(sen3) > 6:
                    pass
                else:
                    f = codecs.open('game\\senryu_word.txt', 'a', 'UTF-8')
                    f.write(str(sen1) + ">>>" + str(sen2) + ">>>" +
                            str(sen3) + ">>>" + account["acct"] + "\r\n" )
                    f.close()
                    v = threading.Timer(5, game.fav, [status["id"]])
                    v.start()
            elif re.compile("ももな.*(せんりゅう|川柳)(ゲーム|げーむ).*(一句|ひとつ|おねがい|お願い|一つ|１つ)").search(content):
                if account["acct"] != "JC":
                    f = codecs.open('game\\senryu_word.txt', 'r', 'utf-8')
                    word1 = []
                    for x in f:
                        word1.append(x.rstrip("\r\n").replace('\\n', '\n'))
                    f.close()
                    m = len(word1)
                    word2 = []
                    for x in range(4):
                        s = random.randint(0, m-1)
                        word2.append((word1[s]).split('>>>'))
                    h0 = word2[0]
                    h1 = word2[1]
                    h2 = word2[2]
                    h3 = word2[3]
                    toot_now = (h0[0] + "\n" + h1[1] + "\n" + h2[2] + "\n（作者：:@" +
                                h3[3] + ":）\n:@" + account["acct"] +":からのリクエストでした❤\n#川柳げーむ")
                    g_vis = "public"
                    bot.rets(6, toot_now, g_vis)
        pass

    def dice(inp):
        l = []
        n = []
        m = []
        x = 0
        try:
            inp = re.sub("&lt;", "<", str(inp))
            inp = re.sub("&gt;", ">", str(inp))
            com = re.search("(\d+)[dD](\d+)([:<>]*)(\d*)([\+\-\*/\d]*)(.*)", str(inp))
            print(str(com.group()))
            for v in range(1, 7):
                m.append(com.group(v))
            print(m)
            if int(m[1]) == 0:
                result = "面が0の数字は振れないよ……"
            elif int(m[0]) >= 51:
                result = "回数が長すぎるとめんどくさいから振らないよ……？"
            elif int(m[0]) == 0:
                result = "えっ……回数0？　じゃあ振らなーーーーい！"
            else:
                print("○サイコロ振ります（*'∀'人）")
                for var in range(0, int(m[0])):
                    num = random.randint(1, int(m[1]))
                    num = str(num)
                    print(num)
                    if m[4] == True:
                        ad = m[4]
                    else:
                        ad = ""
                    try:
                        if ad == "":
                            dd = 0
                        else:
                            dd = int(ad)
                        if m[5] == "":
                            fd = "[" + m[3] + m[4] + "]→"
                        else:
                            fd = "[" + m[5] + "(" + m[3] + m[4] + ")]→"
                        sd = ad + fd
                        if str(m[2]) == ">":
                            if int(num) >= int(m[3]) + dd:
                                result = "ｺﾛｺﾛ……" + num + sd + "成功だよ！！"
                            else:
                                result = "ｺﾛｺﾛ……" + num + sd + "失敗だよ……"
                        else:
                            if int(num) + dd <= int(m[3]) + dd:
                                result = "ｺﾛｺﾛ……" + num + sd + "成功だよ！！"
                            else:
                                result = "ｺﾛｺﾛ……" + num + sd + "失敗だよ……"
                    except:
                        result = "ｺﾛｺﾛ……" + num
                    l.append(result)
                    n.append(int(num))
                    x += int(num)
                if ad != "":
                    x += int(ad)
                if int(m[0]) != 1:
                    result = str(n) + str(ad) + " = " + str(x)
                    l.append(result)
                print(l)
                result = '\n'.join(l)
                if len(result) > 400:
                    result = "文字数制限に引っ掛かっちゃった……"
        except:
            result = "えっ？"
        return result


class count():
    CT = time.time()
    end = 0
    sec = 0
    timer_hello = 0

    def emo01(time=10800):  # 定期的に評価を下げまーーす♪（無慈悲）
        while 1:
            sleep(time)
            data_dir_path = u"./thank/"
            file_list = os.listdir(r'./thank/')
            for file_name in file_list:
                root, ext = os.path.splitext(file_name)
                if ext == u'.txt':
                    abs_name = data_dir_path + '/' + file_name
                    f = open(abs_name, 'r')
                    x = f.read()
                    y = int(x)
                    y += -1
                    f.close()
                    f = open(abs_name, 'w')
                    f.write(str(y))
                    f.close()

    def emo02(point):
        data_dir_path = u"./thank/"
        file_list = os.listdir(r'./thank/')
        for file_name in file_list:
            root, ext = os.path.splitext(file_name)
            if ext == u'.txt':
                abs_name = data_dir_path + '/' + file_name
                f = open(abs_name, 'r')
                x = f.read()
                y = int(x)
                y += point
                f.close()
                f = open(abs_name, 'w')
                f.write(str(y))
                f.close()
        pass

    def emo03(user, point):
        data_dir_path = u"./thank/"
        file_list = os.listdir(r'./thank/')
        abs_name = data_dir_path + '/' + user + '.txt'
        f = open(abs_name, 'r')
        x = f.read()
        y = int(x)
        y += point
        f.close()
        f = open(abs_name, 'w')
        f.write(str(y))
        f.close()
        pass


def enu():
    threading.enumerate()

def go():
    count.timer_hello = 1

def stop():
    count.timer_hello = 0


if __name__ == '__main__':
    count()
    go()
    bot.timer_toot = False
    m = input("start: ")
    if m is "":
        pass
    else:
        bot.rets(5, "(*ﾟ﹃ﾟ*)……はっ！！！！", "public")
        bot.rets(5, m, "public")
    uuu = threading.Thread(target=bot.t_local)
    lll = threading.Thread(target=bot.t_user)
    fff = threading.Thread(target=count.emo01)
    uuu.start()
    lll.start()
    fff.start()
