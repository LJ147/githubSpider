# coding:utf-8

import datetime
import codecs
import requests
import os
import time
from pyquery import PyQuery as pq
import MySQLdb as mdb


def git_add_commit_push(date, filename):
    cmd_git_add = 'git add .'
    cmd_git_commit = 'git commit -m "{date}"'.format(date=date)
    cmd_git_push = 'git push -u origin master'

    os.system(cmd_git_add)
    os.system(cmd_git_commit)
    os.system(cmd_git_push)


def createMarkdown(date, filename):
    with open(filename, 'w') as f:
        f.write("###" + date + "\n")
def insertData(address):
    config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'passwd': 'root',
        'db': 'test',
        'charset': 'utf8'
    }
    conn = mdb.connect(**config)
    # 使用cursor()方法获取操作游标
    cursor = conn.cursor()
    # 因该模块底层其实是调用CAPI的，所以，需要先得到当前指向数据库的指针。

    try:
        # 创建数据库
        DB_NAME = 'test'
        cursor.execute('DROP DATABASE IF EXISTS %s' % DB_NAME)
        cursor.execute('CREATE DATABASE IF NOT EXISTS %s' % DB_NAME)
        conn.select_db(DB_NAME)

        # 创建表
        TABLE_NAME = 'user'
        cursor.execute('CREATE TABLE %s(id int primary key,name varchar(30))' % TABLE_NAME)

        # 插入单条数据
        sql = 'INSERT INTO user values("%d","%s")' % (1, address)

        # 不建议直接拼接sql，占位符方面可能会出问题，execute提供了直接传值
        value = [2, 'John']
        cursor.execute('INSERT INTO test values(%s,%s)', value)

        # 批量插入数据
        values = []
        for i in range(3, 20):
            values.append((i, 'kk' + str(i)))
        cursor.executemany('INSERT INTO user values(%s,%s)', values)

        # 查询数据条目
        count = cursor.execute('SELECT * FROM %s' % TABLE_NAME)
        print 'total records: %d' % count
        print 'total records:', cursor.rowcount

        # 获取表名信息
        desc = cursor.description
        print "%s %3s" % (desc[0][0], desc[1][0])

        # 查询一条记录
        print 'fetch one record:'
        result = cursor.fetchone()
        print result
        print 'id: %s,name: %s' % (result[0], result[1])

        # 查询多条记录
        print 'fetch five record:'
        results = cursor.fetchmany(5)
        for r in results:
            print r

        # 查询所有记录
        # 重置游标位置，偏移量:大于0向后移动;小于0向前移动，mode默认是relative
        # relative:表示从当前所在的行开始移动; absolute:表示从第一行开始移动
        cursor.scroll(0, mode='absolute')
        results = cursor.fetchall()
        for r in results:
            print r

        cursor.scroll(-2)
        results = cursor.fetchall()
        for r in results:
            print r

        # 更新记录
        cursor.execute('UPDATE %s SET name = "%s" WHERE id = %s' % (TABLE_NAME, 'Jack', 1))
        # 删除记录
        cursor.execute('DELETE FROM %s WHERE id = %s' % (TABLE_NAME, 2))

        # 如果没有设置自动提交事务，则这里需要手动提交一次
        conn.commit()
    except:
        import traceback
        traceback.print_exc()
        # 发生错误时会滚
        conn.rollback()
    finally:
        # 关闭游标连接
        cursor.close()
        # 关闭数据库连接
        conn.close()


def scrape(language, filename):

    HEADERS = {
        'User-Agent'		: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept'			: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding'	: 'gzip,deflate,sdch',
        'Accept-Language'	: 'zh-CN,zh;q=0.8'
    }

    url = 'https://github.com/trending/{language}'.format(language=language)
    r = requests.get(url, headers=HEADERS)
    assert r.status_code == 200

    # print(r.encoding)

    d = pq(r.content)
    items = d('ol.repo-list li')

    # codecs to solve the problem utf-8 codec like chinese
    with codecs.open(filename, "a", "utf-8") as f:
        f.write('\n####{language}\n'.format(language=language))

        for item in items:
            i = pq(item)
            title = i("h3 a").text()
            owner = i("span.prefix").text()
            description = i("p.col-9").text()
            url = i("h3 a").attr("href")
            url = "https://github.com" + url
            # ownerImg = i("p.repo-list-meta a img").attr("src")
            # print(ownerImg)
            f.write(u"* [{title}]({url}):{description}\n".format(title=title, url=url, description=description))


def printPage(address):

    HEADERS = {
        'User-Agent'		: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept'			: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding'	: 'gzip,deflate,sdch',
        'Accept-Language'	: 'zh-CN,zh;q=0.8'
    }

    url = 'https://github.com/{address}'.format(address=address)
    r = requests.get(url, headers=HEADERS)
    print r.status_code
    assert r.status_code == 200

    # print(r.encoding)
    # print r.content

    d = pq(r.content)
    items = d('col-12 d-block width-full py-4 border-bottom public source')

    print items[0]

    '''
    # codecs to solve the problem utf-8 codec like chinese
    with codecs.open(filename, "a", "utf-8") as f:
        f.write('\n####{language}\n'.format(language=language))

        for item in items:
            i = pq(item)
            title = i("h3 a").text()
            owner = i("span.prefix").text()
            description = i("p.col-9").text()
            url = i("h3 a").attr("href")
            url = "https://github.com" + url
            # ownerImg = i("p.repo-list-meta a img").attr("src")
            # print(ownerImg)
            f.write(u"* [{title}]({url}):{description}\n".format(title=title, url=url, description=description))
    '''

def job():

    strdate = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = '{date}.md'.format(date=strdate)

    # create markdown file
    createMarkdown(strdate, filename)

    # write markdown
    scrape('python', filename)
    scrape('swift', filename)
    scrape('javascript', filename)
    scrape('go', filename)
    scrape('Objective-C', filename)
    scrape('Java', filename)
    scrape('C++', filename)
    scrape('C#', filename)
    



    # git add commit push
    git_add_commit_push(strdate, filename)


if __name__ == '__main__':
    # while True:
        printPage("alibaba")
        # job()
        # time.sleep(6 * 60 * 60)
