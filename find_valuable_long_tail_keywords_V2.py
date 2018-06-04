import csv
import random
import re
import os
from datetime import datetime
import math

from amazon_module import amazon_module

def keyword_to_long_tail_keyword_list(keyword):
    try:
        # print("keyword:", keyword)
        # print("-" * (len("keyword: ") + len(keyword)))
        keyword = keyword.replace(" ", "%20")
        keyword = keyword.replace("'", "%27")
        if keyword[0] == "*":
            url_head = "https://completion.amazon.com/search/complete?method=completion&mkt=1&r=X8QW0QJV6AP2J4TJAZM4&s=140-5560419-0294343&c=&p=Gateway&l=en_US&b2b=0&fresh=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&ks=8&q=*&qs="
            url_tail = "&cf=1&fb=1&sc=1&"
        else:
            url_head = "https://completion.amazon.com/search/complete?method=completion&mkt=1&r=X8QW0QJV6AP2J4TJAZM4&s=140-5560419-0294343&c=&p=Gateway&l=en_US&b2b=0&fresh=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&ks=8&q="
            url_tail = "&cf=1&fb=1&sc=1&"

        url = url_head + keyword + url_tail
        soup = amazon_module.download_soup_by_url(url)

        soup_string = soup.get_text()
        soup_string = soup_string[13:-11]
        soup_list = eval(soup_string)

        long_tail_keyword_list = []
        for long_tail_keyword in soup_list[1]:
            # print(long_tail_keyword)
            long_tail_keyword_list.append(long_tail_keyword)
        return(long_tail_keyword_list)
    except:
        print("can't find long tail words")

def keyword_to_mw_rank(keyword):
    try:
        keyword = keyword.replace(" ", "%20")
        url = "https://www.merchantwords.com/search/us/" + keyword + "/sort-highest"
        soup = amazon_module.download_soup_by_url(url)

        trs = soup.find("table").find("tbody").find_all("tr")

        node_list = []
        for tr in trs:
            # print(tr.get_text())
            try:
                blurry_words = tr.find("span").get_text()
                # print(blurry_words)

                num = tr.find_all("td")[1].get_text()
                num = num.replace(",", "")
                # print(num)

                node = tr.find("small")
                node = str(node)
                node = node.replace("<br/>", "; ")
                node = node.replace("<small>", "")
                node = node.replace("</small>", "")
                node = node.replace("&amp;", "&")
                # print(node)

                node_tuple = (blurry_words, num, node)
                node_list.append(node_tuple)
            except:
                pass

        # print(node_list[0][1])
        return(node_list[0][1])
    except:
        print("fail to get merchantwords rank!")

def keyword_to_amz_rlt(keyword):
    try:
        # print("keyword:", keyword)
        url_head = "https://www.amazon.com/s/ref=nb_sb_noss/147-7192934-0083761?url=search-alias%3Daps&field-keywords="
        url = url_head + keyword

        soup = amazon_module.download_soup_by_url(url)

        results = soup.find(id="s-result-count").get_text()
        results_text = results.split(":")[0]
        # print(results_text)

        m = re.search(r"of (.*?) results", results)
        results = m.group()
        results = results.replace("of ", "").replace(" results", "").replace(",", "")
        # print(results)
        return(results)
    except:
        print("fail to find results")

def calc_star(mw_rank, amz_rlt, index):

    if int(mw_rank) > 0 and int(amz_rlt) > 0 and int(index) +1 > 0:
        # merchantwords 搜索量越大越好
        mw_weight = math.log(int(mw_rank)/1000, 10)
        # 搜索量与amazon商品数比值越大越好
        ratio_weight = math.log(int(mw_rank)/int(amz_rlt)/10, 2)
        # 长尾词顺序越靠前越好，注意：index是从0开始
        if int(index) + 1 <= 4:
            index_weight = 3
        elif int(index) + 1 <=7:
            index_weight = 1.5
        else:
            index_weight = 1
        # 先暂时简单的求积
        weight = mw_weight * ratio_weight * index_weight
        # 权重换算成星级，5最好，0最差
        star = weight/3.0
        star = round(star)
        star = min(star, 5)
        star = max(star, 0)
        # 返回字符串格式的星级
        return str(star)
    else:
        return "None"

def dict_list_to_csv_file(dict_list, csv_file_name, csv_folder):
    try:
        headers = []
        for i in dict_list[0]:
            headers.append(i)
    except:
        print("FAIL to find csv header tags")

    try:
        csv_file_path = csv_folder + "/" + csv_file_name

        if not os.path.exists(csv_folder):
            os.mkdir(csv_folder)
            print("SUCCESS to create folder")

        if not os.path.isfile(csv_file_path):
            try:
                with open(csv_file_path, 'w', encoding='utf8', newline='') as f:
                    f_csv = csv.DictWriter(f, headers)
                    f_csv.writeheader()
                    print("SUCCESS to write csv header...")
            except:
                print("FAIL to write csv header!")

        try:
            with open(csv_file_path, 'a', encoding='utf8', newline='') as f:
                f_csv = csv.DictWriter(f, headers)
                f_csv.writerows(dict_list)
                print("SUCCESS to write csv content...")
        except:
            print("FAIL to write csv content!")
    except:
        pass

# 注意：关键词头部加*号，或者尾部加空格，amazon搜索框下拉菜单显示的词不一样
keyword_list = [
    "dog toy",
    "dog toy ",
    "*dog toy",
]

csv_folder = "long_tail_keyword_folder"

# 手动指定csv文件名，每次生成的数据都写入到同一个csv文件
csv_file_name = "long_tail_keyword.csv"

# 用日期命名csv文件，每次都会创建一个新的csv文件
# csv_file_name = str(datetime.now()[:19]).replace(":", ";").strip().split(".")[0]

start_time = str(datetime.now())[:19]
print("start_time:", start_time)

print("根据给定的关键词，获取亚马逊搜索框的提示词做为长尾词；")
# 没有登录merchantwords付费账号，默认抓取第一条记录的数字作为搜索量
print("获取长尾词的merchantwords搜索量(mw_rank)，亚马逊搜索框下显示的商品数(amz_rlt)，以及两者的比值(ratio)；")
print("星级star是根据mw_rank, amz_rlt, 搜索词中的排序index综合得出，仅供参考；")
print("")

for keyword in keyword_list:
    long_tail_keyword_dict_list = []
    try:
        first_col_width = len(keyword)
        try:
            long_tail_keyword_list = keyword_to_long_tail_keyword_list(keyword)

            second_col_width = len(max(long_tail_keyword_list, key = len))
            second_col_width = max(second_col_width, len("long_tail_keyword"))

            print('{:>{first_col_width}} | {:>{second_col_width}} | {:>8} | {:>7} | {:>7} | {:>4}'.format("keyword", "long_tail_keyword", "mw_rank", "amz_rlt", "ratio", "star", first_col_width=first_col_width, second_col_width=second_col_width))
            # print('-' * (first_col_width + second_col_width + 8 + 7 + 7 + 4 + 3 * 5))
            print('{:>{first_col_width}} | {:>{second_col_width}} | {:>8} | {:>7} | {:>7} | {:>4}'.format("-" * first_col_width, "-" * second_col_width, "-" * 8, "-" * 7, "-" * 7, "-" * 4, first_col_width=first_col_width, second_col_width=second_col_width))

            for index, long_tail_keyword in enumerate(long_tail_keyword_list):
                try:
                    # merchantwords rank
                    mw_rank = keyword_to_mw_rank(long_tail_keyword)
                except:
                    mw_rank = "None"

                try:
                    # amazon search results
                    amz_rlt = keyword_to_amz_rlt(long_tail_keyword)
                    amz_rlt = amz_rlt.replace("over ", "").strip()
                except:
                    amz_rlt = "None"

                try:
                    ratio = int(mw_rank)/int(amz_rlt)
                    ratio = (ratio*100)
                    ratio = str(ratio).split(".")[0]
                    ratio = str(int(ratio)/100)
                except:
                    ratio = "None"

                try:
                    # star = random.randint(0, 5)
                    star = calc_star(mw_rank, amz_rlt, index)
                except:
                    star = "None"

                print('{:>{first_col_width}} | {:>{second_col_width}} | {:>8} | {:>7} | {:>7} | {:>4}'.format(keyword, long_tail_keyword, mw_rank, amz_rlt, ratio, star, first_col_width=first_col_width, second_col_width=second_col_width))

                long_tail_keyword_dict = {
                    "datetime": str(datetime.now())[:19],
                    "keyword": keyword,
                    "long_tail_keyword": long_tail_keyword,
                    "mw_rank": mw_rank,
                    "amz_rlt": amz_rlt,
                    "ratio": ratio,
                    "star": star,

                }
                long_tail_keyword_dict_list.append(long_tail_keyword_dict)
        except:
            pass

        print("")
    except:
        pass

    try:
        dict_list_to_csv_file(long_tail_keyword_dict_list, csv_file_name, csv_folder)
    except:
        pass




