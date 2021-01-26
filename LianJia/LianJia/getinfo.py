import urllib.request
import ssl
from lxml import etree
import re
import threading
import os

# 全局取消证书验证
ssl._create_default_https_context = ssl._create_unverified_context


# 获取页面
def get_page(url):
    page = urllib.request.urlopen(url)
    html = page.read().decode('utf-8')
    return html


# 获取当前的总页数
def get_page_num(url):
    try:
        html = get_page(url)
        pagenum = re.findall(r'"totalPage":(.+?),"curPage"', html)[0]
    except:
        pagenum = 0
    pagenum = int(pagenum)
    return pagenum


# 获取当前页所有房子的url
def get_house_url_current_page(url):
    flag = ''
    list_house_url_current_page = []
    try:
        html = get_page(url)
        selector = etree.HTML(html)
        # 获取成交时间
        deal_date = selector.xpath('/html/body/div[5]/div[1]/ul/li[last()]/div/div[2]/div[2]/text()')[0]
        # print(deal_date)
        # 获取年份
        deal_year = deal_date[:4]
        if deal_year == '近30天':
            pass
        elif deal_year == '2020':
            house_url_list_li = selector.xpath('/html/body/div[5]/div[1]/ul/li')
            for li in house_url_list_li:
                house_url = li.xpath('div/div[1]/a/@href')[0]
                # print(house_url)
                list_house_url_current_page.append(house_url)
        else:
            flag = 'yearError'
    except:
        pass
    # print(list_house_url_current_page)
    return list_house_url_current_page, flag


# 获取某个区所有的房屋url
def get_house_url_current_district(district_url_list):
    list_house_url = []
    for district_url in district_url_list:
        # print(district_url)
        pagenum = get_page_num(district_url)
        if pagenum == 0:
            print('-------')
            pagenum = get_page_num(district_url)
            print(pagenum)
            print(district_url)
            print('+++')
        for i in range(1, pagenum+1):
            url = district_url + 'pg' + str(i)
            print(url)
            list_house_url_current_page, flag = get_house_url_current_page(url)
            if flag == 'yearError':
                break
            list_house_url.append(list_house_url_current_page)
    # print(list_house_url)

    # 把所有的url拼接成字符串，便于写入本地
    str_url = ''
    for row in list_house_url:
        for url in row:
            str_url += url + '\n'
    return str_url


# 把url写到本地
def write_house_url(write_str, district):
    local_path = './data_url'
    data_path = './data_url/house'
    # path_file = local_path + district + ".txt"
    if not os.path.exists(local_path):
        try:
            os.mkdir(local_path)
            print('Successfully created folder %s' % local_path)
            try:
                os.mkdir(data_path)
                print('Successfully created folder %s' % data_path)
            except:
                pass
        except OSError:
            print("Could not create directory")
            # sys.exit(1)
    path_file = data_path + district + ".txt"
    with open(path_file, 'w') as file:
        file.write(write_str)


# 组合所有区的搜索条件url
def get_search_url_all_district():
    # 各地区url
    district_url = [
        'https://bj.lianjia.com/chengjiao/changping/',
        'https://bj.lianjia.com/chengjiao/chaoyang/',
        'https://bj.lianjia.com/chengjiao/fengtai/',
        'https://bj.lianjia.com/chengjiao/haidian/',
        'https://bj.lianjia.com/chengjiao/xicheng/'
    ]

    # 组合搜索
    # 面积(50以下，50-70，70-90，90-110，110-130，130-150，150-200，200以上)
    search_area = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8']
    # 价格
    search_price = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8']

    # 组合搜索条件url
    search_url = []
    for url in district_url:
        url_list = []
        for area in search_area:
            for price in search_price:
                url_ = url + area + price + '/'
                url_list.append(url_)
        search_url.append(url_list)
    return search_url


def main(index):
    list_district = ['changping', 'chaoyang', 'fengtai', 'haidian', 'xicheng']
    # 切换不同的区 0，1，2，3，4代表不同的区--'changping', 'chaoyang', 'fengtai', 'haidian', 'xicheng
    district = list_district[index]
    search_url = get_search_url_all_district()
    district_url_list = search_url[index]
    write_str = get_house_url_current_district(district_url_list)
    write_house_url(write_str, district)


if __name__ == '__main__':
    # 这里根据需求调节线程数
    for index in range(0, 5):
        thread = threading.Thread(target=main, args=(index,))
        thread.start()

