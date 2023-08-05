'''
Description: 
Autor: dulun
Date: 2023-07-15 13:54:19
LastEditors: dulun
LastEditTime: 2023-07-18 11:00:04
'''
import pandas as pd

jiehuan = {}
reader = pd.read_excel('data/读者信息.xlsx')
content = pd.read_excel('data/图书目录.xlsx')
for year in ['2014', '2015', '2016', '2017']:
    filename = 'data/图书借还{}.xlsx'.format(year)
    jiehuan[year] = pd.read_excel(filename)

print(len(set(content['图书分类号'])))
print(len(content))

for year in jiehuan:
    borrow_df = jiehuan[year]

    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')

    teacher_df = merge_df[merge_df['读者类型'] == '教师']

    category_counts = teacher_df['图书分类号'].value_counts().head(10)

    print("教师{}年借阅的书籍类别占前10的类别为：".format(year))
    print(category_counts)

for year in jiehuan:
    borrow_df = jiehuan[year]
    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')

    teacher_df = merge_df[(merge_df['读者类型'] == '教师')]# & ('I207.4' in merge_df['图书分类号'])]

    category_counts = teacher_df['书名'].value_counts().head(1)

    print("教师{}年最喜欢看的小说为：".format(year))
    print(category_counts)

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

for year in jiehuan:
    borrow_df = jiehuan[year]

    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')

    teacher_df = merge_df[(merge_df['读者类型'] == '教师') & merge_df['图书分类号'].str.contains('|'.join(xiaoshuo), case=False)]

    category_counts = teacher_df['书名'].value_counts().head(1)

    print("教师{}年最喜欢看的小说为：".format(year))
    print(category_counts)


book_sum = 0
all_teacher_df = pd.DataFrame()
all_teacher_df = all_teacher_df[all_teacher_df['单位']=='经济管理学院']
for year in jiehuan:
    borrow_df = jiehuan[year]

    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')

    teacher_df = merge_df[(merge_df['读者类型'] == '教师')]
    all_teacher_df = pd.concat([all_teacher_df, teacher_df], ignore_index=True)
print("教师一共借阅：{}本书".format(len(all_teacher_df['操作类型']=='借')))


zhuanye_df = all_teacher_df[all_teacher_df['图书分类号'].str.startswith(('A', 'TB', 'S', 'R', 'C', 'F', 'G', 'K', 'I', 'N'))]
print("教师借阅专业书{}本".format(len(zhuanye_df)))


print(all_teacher_df.info())


borrowed_books = all_teacher_df[all_teacher_df['操作类型'] == '借']


returned_books = all_teacher_df[all_teacher_df['操作类型'] == '还']

books_not_returned = borrowed_books['图书ID'].value_counts() - returned_books['图书ID'].value_counts()

num_books_not_returned = len(books_not_returned[books_not_returned > 0])

print("没有归还的书籍数量：", num_books_not_returned)

def parse_classification_number(classification_number):

    parts = classification_number.split('.') if '.' in classification_number else classification_number.split('/')
    

    main_class_number = parts[0].strip()
    secondary_class_number = parts[1].strip() if len(parts) > 1 else ""
    main_class = None
    secondary_class = None
    if main_class_number in book_class:
        main_class = book_class[main_class_number]
    if secondary_class_number in book_class:
        secondary_class = book_class[secondary_class_number]
    return main_class, secondary_class



not_returned_categories = borrowed_books[borrowed_books['图书ID'].isin(books_not_returned[books_not_returned > 0].index)]['图书分类号']


category_counts = not_returned_categories.value_counts()

most_common_category = category_counts.idxmax()

print("没有归还的书籍中数量最多的图书分类号：", most_common_category,"类别：", parse_classification_number(most_common_category))



for year in jiehuan:
    borrow_df = jiehuan[year]

    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')
    student_condition = ((merge_df['读者类型'] == '博士研究生') | (merge_df['读者类型'] == '本科生') | (merge_df['读者类型'] == '研究生'))

    student_df = merge_df[student_condition]

    category_counts = student_df['图书分类号'].value_counts().head(10)

    print("\n学生{}年借阅的书籍类别占前10的类别为：".format(year))

    for idx, category in enumerate(category_counts.items()):
        print("第{}\t图书分类号:{}\t计数值:{}\t类别:{} ".format(idx+1, category[0], category[1], parse_classification_number(category[0])))

for year in jiehuan:
    borrow_df = jiehuan[year]

    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')
    student_condition = ((merge_df['读者类型'] == '博士研究生') | (merge_df['读者类型'] == '本科生') | (merge_df['读者类型'] == '研究生'))

    student_df = merge_df[student_condition & merge_df['图书分类号'].str.contains('|'.join(xiaoshuo), case=False)]# & ('I207.4' in merge_df['图书分类号'])]


    category_counts = student_df['书名'].value_counts().head(1)


    print("学生{}年最喜欢看的小说为：".format(year))
    print(category_counts)

book_sum = 0
all_student_df = pd.DataFrame()
for year in jiehuan:
    borrow_df = jiehuan[year]

    merge_df = pd.merge(borrow_df, content, on='图书ID')
    merge_df = pd.merge(merge_df, reader, on='读者ID')
    student_condition = ((merge_df['读者类型'] == '博士研究生') | (merge_df['读者类型'] == '本科生') | (merge_df['读者类型'] == '研究生'))

    student_df = merge_df[student_condition]
    all_student_df = pd.concat([all_student_df, student_df], ignore_index=True)
print("学生一共借阅：{}本书".format(len(all_student_df['操作类型']=='借')))


student_jieyue  = all_student_df[all_student_df['操作类型']=='借']
student_jieyue['图书分类号'] = student_jieyue['图书分类号'].fillna('')
student_zhuanye_df = student_jieyue[student_jieyue['图书分类号'].str.startswith(('A', 'TB', 'S', 'R', 'C', 'F', 'G', 'K', 'I', 'N'))]
print("学生借阅专业书{}本".format(len(student_zhuanye_df)))



student_borrowed_books = all_student_df[all_student_df['操作类型'] == '借']


student_returned_books = all_student_df[all_student_df['操作类型'] == '还']


student_books_not_returned = student_borrowed_books['图书ID'].value_counts() - student_returned_books['图书ID'].value_counts()


student_num_books_not_returned = len(student_books_not_returned[student_books_not_returned > 0])


print("学生没有归还的书籍数量：", student_num_books_not_returned)



studetn_not_returned_categories = student_borrowed_books[student_borrowed_books['图书ID'].isin(student_books_not_returned[student_books_not_returned > 0].index)]['图书分类号']


sutdent_category_counts = studetn_not_returned_categories.value_counts()


student_most_common_category = sutdent_category_counts.idxmax()


print("学生没有归还的书籍中数量最多的图书分类号：", student_most_common_category,"类别：", parse_classification_number(student_most_common_category))

