'''
Description: 
Autor: dulun
Date: 2023-07-16 09:36:33
LastEditors: dulun
LastEditTime: 2023-07-18 10:46:59
'''
import pandas as pd
import jieba
from wordcloud import WordCloud

jiehuan = {}
reader = pd.read_excel('data/读者信息.xlsx')
content = pd.read_excel('data/图书目录.xlsx')
for year in ['2014', '2015', '2016', '2017']:
    filename = 'data/图书借还{}.xlsx'.format(year)
    jiehuan[year] = pd.read_excel(filename)

all_df = pd.DataFrame()
for year in jiehuan:
    borrow_df = jiehuan[year]

    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')

    all_df = pd.concat([all_df, merge_df], ignore_index=True)
all_df = all_df[all_df['单位']=='经济管理学院']
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np

stopwords_files = ['data/停用词及敏感词库/baidu_stopwords.txt', 'data/停用词及敏感词库/cn_stopwords.txt',
                   'data/停用词及敏感词库/hit_stopwords.txt', 'data/停用词及敏感词库/scu_stopwords.txt',
                   'data/停用词及敏感词库/stop-words.txt']
stopwords = set()
for file in stopwords_files:
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            stopwords.add(line.strip())
stopwords.add('版')

words_list = []
for book_name in all_df['书名']:
    words = jieba.cut(str(book_name))
    words_filtered = [word for word in words if word not in stopwords and word.strip()!='']
    words_list.extend(words_filtered)

word_counts = {}
for word in words_list:
    if word in word_counts:
        word_counts[word] += 1
    else:
        word_counts[word] = 1


font_path = 'data/NotoSerifSC-Regular.otf' 

wordcloud = WordCloud(width=800, height=400, max_words=50, background_color='white', font_path=font_path)
wordcloud.generate_from_frequencies(word_counts)


plt.figure(figsize=(10, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()


top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
for word, count in top_words:
    print(f'{word}: {count}')