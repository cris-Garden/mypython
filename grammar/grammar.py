import sqlite3
import re
from urllib import request
from bs4 import BeautifulSoup

# データベースファイルのパス
dbpath = 'grammar.db'

# データベース接続とカーソル生成
connection = sqlite3.connect(dbpath)
# 自動コミットにする場合は下記を指定（コメントアウトを解除のこと）
# connection.isolation_level = None
cursor = connection.cursor()



def scraping():
    #url 1-1561
    #特別　１２０３　９
    for a in range(1560,1590):
        grammar = Grammar()
        grammar.id = str(10000+a)
        url = "https://grammar.izaodao.com/grammar.php?action=view&id="+str(a)+"&level=&cha="
        print(grammar.id + ": " + url)
        #get html
        html = request.urlopen(url)
    
        #set BueatifulSoup
        soup = BeautifulSoup(html, "html.parser")
    
        #get title
        title_span = soup.find("span",class_="whitetxt fs38")
        if title_span:
            grammar.title = title_span.string
        else:
            continue
        #get level
        gammarspantop_spans = soup.find_all("span",class_="gammarspantop")
        for a in gammarspantop_spans:
            pattern = r"level="
            if re.search(pattern,str(a)):
                grammar.level = a.a.string

        #get like and about
        list9_ul = soup.find("ul",class_ = "list9")
        all_li = list9_ul.find_all("li")
        for li in all_li:
            pattern = r"<li>近似："
            if re.search(pattern,str(li)):
                grammar.like = cutHeadAndFoot("<li>近似：","</li>",str(li)).strip()
            pattern = r"<li>相关："
            if re.search(pattern,str(li)):
                grammar.about = cutHeadAndFoot("<li>相关：","</li>",str(li)).strip()
        grammar.save()


        #get means
        box2_divs = soup.find_all("div",class_="box2")
        index = 100
        for box2 in box2_divs:
            means = Means()
            means.id = grammar.id + str(index)
            means.grammar_id = grammar.id
            index = index + 1
            #get format
            mark1_div = box2.find("div",class_ = "mark1")
            pattern = r"接续</span>.*</div>"
            match = re.search(pattern,str(mark1_div))
            if match:
                means.format = cutHeadAndFoot("接续</span>","</div>",match.group())

            #get mean
            mark2_1_div = box2.find("div",class_ = "mark2-1")
            pattern = r"意思</span>.*<!--<a"
            match = re.search(pattern,str(mark2_1_div))
            if match:
                means.mean = cutHeadAndFoot("意思</span>","<!--<a",match.group())

            #get type
            mark2_1_div = mark2_1_div.find_next("div",class_ = "mark2-1")
            pattern = r"</span>用于表达.*的场景</div>"
            match = re.search(pattern,str(mark2_1_div))
            if match:
                means.type = cutHeadAndFoot("</span>用于表达","的场景</div>",match.group())

            #get example,explain,notice,mixup
            all_dt = box2.find_all("dt")
            for dt in all_dt:
                #example
                pattern = r">例句</span>"
                match = re.search(pattern,str(dt))
                if match:
                    dd = dt.find_next("dd")
                    ul = dd.find("ul")
                    means.example = cutHeadAndFoot("<ul>","</ul>",str(ul)).strip()
                    continue

                #explain
                pattern = r">解析</span>"
                match = re.search(pattern,str(dt))
                if match:
                    dd = dt.find_next("dd")
                    means.explain = cutHeadAndFoot("<dd>","</dd>",str(dd)).strip()
                    continue

                #notice
                pattern = r">注意</span>"
                match = re.search(pattern,str(dt))
                if match:
                    dd = dt.find_next("dd")
                    means.notice = cutHeadAndFoot("<dd>","</dd>",str(dd)).strip()
                    continue

                #mixup
                pattern = r">易混淆语法辨析</span>"
                match = re.search(pattern,str(dt))
                if match:
                    dd = dt.find_next("dd")
                    means.mixup = cutHeadAndFoot("<dd>","</dd>",str(dd)).strip()
                    continue
            means.save()




def cutHeadAndFoot(head,foot,string):
    newString = re.sub(head,"",string)
    return re.sub(foot,"",newString)

class Means:
    id = ""
    grammar_id = None
    format = None
    mean = None
    type = None
    example = None
    explain = None
    notice = None
    mixup = None
    
    def save(self):
        # エラー処理（例外処理）
        try:
            # CREATE
#            cursor.execute("DROP TABLE IF EXISTS means")
            cursor.execute(
                           "CREATE TABLE IF NOT EXISTS means (id INTEGER PRIMARY KEY,grammar_id INTEGER NOT NULL, format TEXT,mean TEXT,type TEXT,example TEXT,explain TEXT,notice TEXT,mixup TEXT)")
            # INSERT
            sql = "INSERT INTO means VALUES (" + self.id
            sql = addStrWith(self.grammar_id,sql)
            sql = addStrWith(self.format,sql)
            sql = addStrWith(self.mean,sql)
            sql = addStrWith(self.type,sql)
            sql = addStrWith(self.example,sql)
            sql = addStrWith(self.explain,sql)
            sql = addStrWith(self.notice,sql)
            sql = addStrWith(self.mixup,sql)
            sql = sql + ")"
            #print("sql = " + sql)
            cursor.execute(sql)
        except sqlite3.Error as e:
            print('sqlite3.Error occurred:', e.args[0])
        
        # 保存を実行（忘れると保存されないので注意）
        connection.commit()
        print("means save success.........")


class Grammar:
    id = ""
    title = None
    level = None
    like = None
    about = None
    def save(self):
        # エラー処理（例外処理）
        try:
            # CREATE
#            cursor.execute("DROP TABLE IF EXISTS grammar")
            cursor.execute(
                           "CREATE TABLE IF NOT EXISTS grammar (id INTEGER PRIMARY KEY, title TEXT,level TEXT,like TEXT,about TEXT)")
            # INSERT
            sql = "INSERT INTO grammar VALUES (" + self.id
            sql = addStrWith(self.title,sql)
            sql = addStrWith(self.level,sql)
            sql = addStrWith(self.like,sql)
            sql = addStrWith(self.about,sql)
            sql = sql + ")"
            #print("sql = " + sql)
            cursor.execute(sql)
        except sqlite3.Error as e:
            print('sqlite3.Error occurred:', e.args[0])

        # 保存を実行（忘れると保存されないので注意）
        connection.commit()
        print("grammar save success.........")

#安全でテキストを追加して
def addStrWith(value,string):
    if value:
        return string + ",'" + value + "'"
    else:
        return string + ",''"



if __name__ == "__main__":
    scraping()
