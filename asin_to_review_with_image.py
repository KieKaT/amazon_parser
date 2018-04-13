# 通过asin获取review的标题，星星数，内容，图片（如果有的话），留评日期，profile_url，等等
# 面向过程编程，只用到了函数，没有用类，结构简单，有时间再优化
# 有问题联系我：dg1245@qq.com
# 欢迎交流学习

from amazon_module import amazon_module
import re
import os
import csv
from datetime import datetime
import requests

asin_list = [
    # "B0131GM34U",
    "B01CKFMLYU",
    ]

# helpful, recent
top_or_recent = "helpful"

# all_reviews, avp_only_reviews
all_or_VP = "all_reviews"

# all, positive, negative, one_star, two_star, three_star, four_star, five_star
stars = "all"

# all_contents, media_reviews_only
all_or_media = "media_reviews_only"

# thumbnail, small, medium, large
img_size = "medium"

max_page = 5

csv_folder = "reviews"

# img_folder不用修改
img_folder = csv_folder + "/" + img_size + "_image/"

# csv_file_name 这个属性不填，默认按照日期来命名
# csv_file_name = ""


def dict_list_to_csv_file(dict_list, csv_folder, csv_file_name):
    try:
        headers = []
        for i in dict_list[0]:
            headers.append(i)
    except:
        print("FAIL to find csv header tags")

    csv_file_path = csv_folder + "/" + str(csv_file_name)

    if not os.path.exists(csv_folder):
        print("folder not exist, creating folder...")
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
        with open(csv_file_path, 'a+', encoding='utf8', newline='') as f:
            f_csv = csv.DictWriter(f, headers)
            f_csv.writerows(dict_list)
            print("SUCCESS to write csv content...")
    except:
        print("FAIL to write csv content!")

def download_picture_by_url(img_title, img_url, img_folder):
    if not os.path.exists(img_folder):
        print("image folder not exist, creating folder...")
        os.mkdir(img_folder)
        print("SUCCESS to create image folder")
    try:
        img_path = img_folder + img_title
        pic = requests.get(img_url, timeout=10)
        with open(img_path, 'wb') as fp:
            fp.write(pic.content)
        print("SUCCESS to download picture")
    except requests.exceptions.ConnectionError:
        print("FAIL to download picture!")
        
# main
start_datetime = datetime.now()
print("start_datetime:", start_datetime)
csv_file_name = str(start_datetime).replace(":", ";").strip().split(".")[0] + ".csv"

for asin in asin_list:
    listing_url = "https://www.amazon.com/dp/" + asin
    soup = amazon_module.download_soup_by_url(listing_url)
    start_review_url_part2 = soup.find(id="dp-summary-see-all-reviews")["href"]
    start_review_url = "https://www.amazon.com" + start_review_url_part2

    location = re.search("ref=", start_review_url)
    span = location.span()[0]
    start_review_url_part1 = start_review_url[:span]
    # https://www.amazon.com/Stainless-Steel-Personalized-Tags-Lines/product-reviews/B00BJLS55G/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&pageNumber=1&sortBy=helpful&filterByStar=five_star&mediaType=media_reviews_only
    review_base_url = start_review_url_part1 + "ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=" + all_or_VP  + "&sortBy=" + top_or_recent + "&filterByStar=" + stars + "&mediaType=" + all_or_media + "&pageNumber="
    first_review_url = review_base_url + str(1)

    for page in range(1, max_page + 1):
        review_url = review_base_url + str(page)
        try:
            dict_list = []
            soup = amazon_module.download_soup_by_url(review_url)
            review_list = soup.find(id="cm_cr-review_list").find_all("div", {"data-hook":"review"})

            for review_index, review in enumerate(review_list):
                page_rank = str(page) + "P" + str(review_index + 1)
                review_title = review.find("a", {"data-hook":"review-title"}).get_text()
                review_star_rating = review.find("i", {"data-hook": "review-star-rating"}).get_text()
                review_author = review.find("a", {"data-hook": "review-author"}).get_text()
                review_date = review.find("span", {"data-hook": "review-date"}).get_text()
                review_body = review.find("span", {"data-hook": "review-body"}).get_text()
                review_variation = review.find("a", {"data-hook": "format-strip"}).get_text()
                profile_url_part = review.find("a", {"data-hook": "review-author"})['href']
                profile_url = "https://www.amazon.com" + profile_url_part

                review_bage = ""
                try:
                    review_bage = review.find("span", {"data-hook": "avp-badge"}).get_text()
                except:
                    pass

                helpful_vote = ""
                try:
                    helpful_vote = review.find("span", {"data-hook": "helpful-vote-statement"}).get_text().strip()
                except:
                    pass

                try:
                    review_images = review.find("div", class_="review-image-tile-section").find_all("img")
                    for img_index, img in enumerate(review_images):
                        thumbnail_img_url = img['src']
                        small_img_url = thumbnail_img_url.replace("_SY88", "_SL256_")
                        medium_img_url = thumbnail_img_url.replace("_SY88", "_SY450_")
                        large_img_url = thumbnail_img_url.replace("_SY88", "_SL1500_")
                        img_url = eval(img_size + "_img_url")
                        img_title = asin + "-" + page_rank + "-" + str(img_index + 1) + ".jpg"
                        download_picture_by_url(img_title, img_url, img_folder)
                except:
                    pass


                print("page_rank:", page_rank)
                # print("review_title: ", review_title)
                # print("review_star_rating: ", review_star_rating)
                # print("review_author: ", review_author)
                # print("review_date: ", review_date)
                # print("review_body: ", review_body)
                # print("review_variation: ", review_variation)
                # print("review_bage: ", review_bage)
                # print("page_rank: ", page_rank)
                # print("review_title: ", review_title)
                # print("profile_url: ", profile_url)
                review_dict = {
                    "page_rank": page_rank,
                    "asin": asin,
                    "review_bage": review_bage,
                    "review_star_rating": review_star_rating,
                    "review_author": review_author,
                    "review_date": review_date,
                    "review_variation": review_variation,
                    "review_title": review_title,
                    "review_body": review_body,
                    "helpful_vote": helpful_vote,
                    "profile_url": profile_url,
                    }
                dict_list.append(review_dict)
        except:
            pass
        finally:
            dict_list_to_csv_file(dict_list, csv_folder, csv_file_name)
