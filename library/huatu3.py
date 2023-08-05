'''
Description: 
Autor: dulun
Date: 2023-07-16 09:11:01
LastEditors: dulun
LastEditTime: 2023-07-19 10:47:53
'''
import pandas as pd

def get_class():
    bc = {}
    with open("data/《中国图书馆图书分类法》简表.txt", 'r', encoding='utf8') as rf:
        for line in rf:
            if line[0] >='A' and line[0] <='Z':
                res = line.split()
                if len(res)> 1:
                    bc[res[0]]=res[1]
                else:
                    for i in range(len(line)-1, -1, -1):
                        if line[i]>='0' and line[i]<='9':
                            bc[line[:i+1]] = line[i+1:]
                            break
    return bc
book_class = get_class()

xiaoshuo = []
for key in book_class:
    if "小说" in book_class[key]:
        xiaoshuo.append(key)
print(xiaoshuo)

jiehuan = {}
reader = pd.read_excel('data/读者信息.xlsx')
content = pd.read_excel('data/图书目录.xlsx')
for year in ['2014', '2015', '2016', '2017']:
    filename = 'data/图书借还{}.xlsx'.format(year)
    jiehuan[year] = pd.read_excel(filename)

book_sum = 0
all_teacher_df = pd.DataFrame()
for year in jiehuan:
    borrow_df = jiehuan[year]

    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')

    teacher_df = merge_df[(merge_df['读者类型'] == '教师')]
    all_teacher_df = pd.concat([all_teacher_df, teacher_df], ignore_index=True)


book_sum = 0
all_student_df = pd.DataFrame()
# all_teacher_df = all_teacher_df[all_teacher_df['单位']=='经济管理学院']
for year in jiehuan:
    borrow_df = jiehuan[year]

    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')
    student_condition = ((merge_df['读者类型'] == '博士研究生') | (merge_df['读者类型'] == '本科生') | (merge_df['读者类型'] == '研究生'))

    student_df = merge_df[student_condition]
    all_student_df = pd.concat([all_student_df, student_df], ignore_index=True)


xs_teacher_top_10 = all_teacher_df[(all_teacher_df['操作类型']=='借') & all_teacher_df['图书分类号'].str.contains('|'.join(xiaoshuo), case=False) ]['图书分类号'].value_counts().head(10)
xs_student_top_10 = all_student_df[(all_student_df['操作类型']=='借') & all_student_df['图书分类号'].str.contains('|'.join(xiaoshuo), case=False) ]['图书分类号'].value_counts().head(10)
print(xs_teacher_top_10, xs_student_top_10)


xs_teacher_points = {}

for year in jiehuan:
    borrow_df = jiehuan[year]
    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')
    merge_df = merge_df[(merge_df['操作类型']=='借') & (merge_df['读者类型'] == '教师')]
    
    for bid, bnum in xs_teacher_top_10.items():
        if bid not in xs_teacher_points:
            xs_teacher_points[bid]=[]
        xs_teacher_points[bid].append(len(merge_df[merge_df['图书分类号']==bid]))
print(xs_teacher_points)

xs_student_points = {}

for year in jiehuan:
    borrow_df = jiehuan[year]
    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')
    student_condition = ((merge_df['读者类型'] == '博士研究生') | (merge_df['读者类型'] == '本科生') | (merge_df['读者类型'] == '研究生'))
    merge_df = merge_df[(merge_df['操作类型']=='借') & student_condition]
    
    for bid, bnum in xs_student_top_10.items():
        if bid not in xs_student_points:
            xs_student_points[bid]=[]
        xs_student_points[bid].append(len(merge_df[merge_df['图书分类号']==bid]))
print(xs_student_points)

import matplotlib.pyplot as plt
import numpy as np

plt.figure(figsize=(10, 6))
font_path = 'data/NotoSerifSC-Regular.otf' 
plt.rcParams['font.family'] = 'sans-serif'  # 设置默认字体为无衬线字体
plt.rcParams['font.sans-serif'] = ['SimHei']
years = [2014, 2015, 2016, 2017]
np.array(years, dtype=int)
labels = ["各体文学评论和研究", "当代作品", "悬疑推理","心理小说", "科幻小说", "传记小说","青春文学", "冒险小说", "社会现实",  "爱情故事"]
for key,l in zip(xs_student_points, labels):
    plt.plot(years, xs_student_points[key], marker='o', label=l)

plt.title(f"学生小说前十类趋势图 (2014-2017)")
plt.xlabel("Year")
plt.ylabel("Count")


plt.legend(title="novel Book Categories")
plt.xticks(years)

plt.show()