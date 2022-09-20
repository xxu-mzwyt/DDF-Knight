import tkinter,urllib,os
from win32com import client as wc
from bs4 import BeautifulSoup
from collections import Counter
from pyecharts import WordCloud

mypath = "C:\\Users\\windows\\Desktop\\高频单词\\dataset"

files = os.listdir(mypath)        ##将Word文档转换为txt
for f in files:
    new = mypath + '\\' + f
    print(new)
    if 'docx' in new:
        tmp = new[:-5]
        word = wc.Dispatch('Word.Application')
        docx = word.Documents.Open(new)
        docx.SaveAs(tmp + '.txt', 4)
    else:
        tmp = new[:-4]
        word = wc.Dispatch('Word.Application')
        docx = word.Documents.Open(new)
        docx.SaveAs(tmp + '.txt', 4)
    docx.Close()  

mypath2 = "dataset"
files = os.listdir(mypath)
 
for fileser in files:                ##将所有txt文档合并
    if 'txt' in fileser:    
        path = mypath2 + '\\' + fileser
        with open(path,'r') as f1:
            for line in f1:
#                line = f1.read()
                with open("C:\\Users\\windows\\Desktop\\高频单词\\dataset\\data_all.txt",'a',encoding = 'utf-8') as f2:
                    f2.write(line)

##将txt中的所有数据，存为列表words，便于后续操作
words = []
with open("dataset\\data_all.txt",'r',encoding = 'utf-8') as file:
    for line in file:
        words.append(line.split(' '))

##对数据进行处理，提取出单词，并存入列表corpous                     
corpous = []
for i in range(len(words)):
    for j in words[i]:
        if ('\n' in j) and len(j) > 2 :                                    #对每一行的最后一个单词进行处理，需去掉最后的'/n'换行符
            corpous.append(j[:-2])
        if j != '/n' and j.encode('utf-8').isalpha() and len(j) > 1 :      #对每一行除最后一个单词的其他词进行保存
            corpous.append(j.lower())                                      #统一为小写字母

##对数据进行进一步处理，去除汉字、阿拉伯数字、罗马数字、符号等非英文字符；存为列表word_result
words_result = []
for i in corpous:
    if i.encode('utf-8').isalpha() and len(i) > 2:
        words_result.append(i.lower())

##Counter对列表words_result中的所有单词进行词频统计，存为字典words_dict
words_dict = Counter(words_result)

#去除停用词，可根据需求调整
words_stop = []
for word in words_dict.most_common(200):   #寻找最高频的前200个词
    if len(word[0]) < 6:                   #将单词长度小于6的都视为停用词
        words_stop.append(word)
for word in words_dict.most_common(500):   #寻找最高频的前500个词
    if len(word[0]) < 5:                   #将单词长度小于5的都视为停用词
        words_stop.append(word)

for i in set(words_stop):                  #去除words_dict中的停用词
    words_dict.pop(i[0])

##获得去除停用词后的字典words_dict
words_dict_result =  words_dict.most_common(100)

def data_visual(words_dict_result):        #可视化函数，以词云的方式，直观得到高频词汇
    x = []
    y = []
    for i in range(len(words_dict_result)):
        x.append(words_dict_result[i][0])
        y.append(words_dict_result[i][1])
    wordcloud =WordCloud(width=1000, height=600)
    wordcloud.add("", x, y, word_size_range=[20, 100], shape='diamond')
    wordcloud.show_config()
    wordcloud.render(r'word_wordcloud.html')
    
    
def translate(word):                      #翻译函数，使用有道词典的接口，对高频词进行翻译，并使用爬虫爬取翻译结果
    url = 'http://dict.youdao.com/w/{}/'.format(word)
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
    page = urllib.request.Request(url, headers=headers)
    page_info = urllib.request.urlopen(page).read()
    page_info = page_info.decode('utf-8')
    
    soup = BeautifulSoup(page_info, 'html.parser')
    trans_container = soup.find(class_='trans-container')
    trans_li = trans_container.find_all('li')
    trans_data = [li.text.strip() for li in trans_li]
#    print(trans_data)
    return trans_data

##列表translate_word保存爬取得到的翻译结果
translate_word = []
for i in range(len(words_dict_result)):
#    translate_word.append(words_dict_result[i][0])
    translate_word.append(translate(words_dict_result[i][0]))

##列表translate_word_key按顺序保存翻译的单词
translate_word_key = []
for i in range(len(words_dict_result)):
    translate_word_key.append(words_dict_result[i][0])
    
##字典word_dict保存所翻译的单词及翻译结果
word_dict = dict(zip(translate_word_key,translate_word))
print(word_dict)

##将翻译结果保存为txt文件，便于学习查看
with open('./word_dict.txt','a',encoding = 'utf-8') as f:
    for i,j in word_dict.items():
        f.write(i+':  ')
        f.write(str(j)+'\n')

#进行可视化
data_visual(words_dict_result)

window = tkinter.Tk() 
window.title('单词提取')
window.geometry('300x200')

A=0

l = tkinter.Label(window,text='高频词汇提取',bg='white',font=('Arial',12),width=15,height=2)
l.pack()

def Open():
    with open('/Users/windows/Desktop/高频单词/word_wordcloud.html') as f:
    	s = f.read()
    print(s)

b = tkinter.Button(window,text=('一键打开词云及释义'),width=30,height=4,command=Open)
b.pack()

window.mainloop()

