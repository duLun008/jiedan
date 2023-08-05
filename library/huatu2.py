'''
Description: 
Autor: dulun
Date: 2023-07-16 09:11:01
LastEditors: dulun
LastEditTime: 2023-07-19 11:18:16
'''
import pandas as pd


jiehuan = {}
reader = pd.read_excel('data/读者信息.xlsx')
content = pd.read_excel('data/图书目录.xlsx')
for year in ['2014', '2015', '2016', '2017']:
    filename = 'data/图书借还{}.xlsx'.format(year)
    jiehuan[year] = pd.read_excel(filename)

book_sum = 0
all_teacher_df = pd.DataFrame()
# all_teacher_df = all_teacher_df[all_teacher_df['单位']=='经济管理学院']
for year in jiehuan:
    borrow_df = jiehuan[year]

    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')

    teacher_df = merge_df[(merge_df['读者类型'] == '教师')]
    all_teacher_df = pd.concat([all_teacher_df, teacher_df], ignore_index=True)


book_sum = 0
all_student_df = pd.DataFrame()
for year in jiehuan:
    borrow_df = jiehuan[year]

    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')
    student_condition = ((merge_df['读者类型'] == '博士研究生') | (merge_df['读者类型'] == '本科生') | (merge_df['读者类型'] == '研究生'))

    student_df = merge_df[student_condition]
    all_student_df = pd.concat([all_student_df, student_df], ignore_index=True)

teacher_top_10 = all_teacher_df[(all_teacher_df['操作类型']=='借')]['图书分类号'].value_counts().head(10)
student_top_10 = all_student_df[(all_student_df['操作类型']=='借')]['图书分类号'].value_counts().head(10)
print(teacher_top_10, student_top_10)


teacher_points = {}

for year in jiehuan:
    borrow_df = jiehuan[year]
    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')
    merge_df = merge_df[(merge_df['操作类型']=='借') & (merge_df['读者类型'] == '教师')]
    
    for bid, bnum in teacher_top_10.items():
        if bid not in teacher_points:
            teacher_points[bid]=[]
        teacher_points[bid].append(len(merge_df[merge_df['图书分类号']==bid]))
print(teacher_points)


student_points = {}

for year in jiehuan:
    borrow_df = jiehuan[year]
    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')
    student_condition = ((merge_df['读者类型'] == '博士研究生') | (merge_df['读者类型'] == '本科生') | (merge_df['读者类型'] == '研究生'))
    merge_df = merge_df[(merge_df['操作类型']=='借') & student_condition]
    
    for bid, bnum in student_top_10.items():
        if bid not in student_points:
            student_points[bid]=[]
        student_points[bid].append(len(merge_df[merge_df['图书分类号']==bid]))
print(student_points)

import matplotlib.pyplot as plt
import numpy as np

plt.figure(figsize=(10, 6))
font_path = 'data/NotoSerifSC-Regular.otf' 
plt.rcParams['font.family'] = 'sans-serif'  # 设置默认字体为无衬线字体
plt.rcParams['font.sans-serif'] = ['SimHei']    
years = [2014, 2015, 2016, 2017]
labels = ["中国民族器乐", "经济学理论", "管理学", "市场营销", "金融学", "创业与创新", "战略规划", "领导学", "组织行为学", "国际商务"]
np.array(years, dtype=int)
for key,l in zip(teacher_points,labels):
    plt.plot(years, teacher_points[key], marker='o', label=l)

plt.title(f"老师书籍前十类趋势图 (2014-2017)")
plt.xlabel("Year")
plt.ylabel("Count")
plt.xticks(years)

plt.legend(title="Book Categories")
plt.xticks(years)

plt.show()