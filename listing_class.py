import re
from pprint import pprint

from amazon_module import amazon_module

class Listing:

    def __init__(self, asin):
        self.soup = amazon_module.download_soup_by_url("https://www.amazon.com/dp/" + asin)

    @property
    def asin(self):
        return self._asin

    @asin.setter
    def asin(self, value):
        if len(value.strip()) != 10:
            raise ValueError('Invalid asin!')
        self._asin = value

    def get_title(self):
        title = ""
        try:
            if self.soup.find(id="productTitle"):
                title = self.soup.find(id="productTitle").get_text().strip()
        except:
            title = "fail"
        print(title)
        return title

    def get_brand(self):
        brand = ""
        try:
            if self.soup.find(id="bylineInfo"):
                brand = self.soup.find(id="bylineInfo").get_text().strip()
            if self.soup.find(id="brand"):
                brand = self.soup.find(id="brand").get_text().strip()
        except:
            brand = "fail"
        print(brand)
        return brand

    def get_price(self):
        price = ""
        try:
            price = self.soup.find(id="price").find("span").get_text().strip()
        except:
            price = self.soup.find(id="priceblock_ourprice").get_text().strip()
        print(price)
        return price

    def get_sold_by(self):
        sold_by = ""
        try:
            sold_by = " ".join(self.soup.find(id="merchant-info").get_text().strip().split())
        except:
            sold_by = "fail"
        print(sold_by)
        return sold_by

    def get_badge(self):
        badge = ""
        try:
            badge = " ".join(self.soup.find("a", class_="badge-link").get_text().strip().split())
        except:
            badge = "fail"
        print(badge)
        return badge

    def get_variation_name(self):
        variation_name = ""
        try:
            variation_name = self.soup.find(id="variation_pattern_name").find("span").get_text().strip()
        except:
            pass
        try:
            variation_name = self.soup.find(id="variation_color_name").find("span").get_text().strip()
        except:
            pass
        try:
            variation_name = self.soup.find(id="variation_size_name").find("span").get_text().strip()
        except:
            pass

        print(variation_name)
        return variation_name

    def get_how_many_sellers(self):
        how_many_sellers = ""
        try:
            how_many_sellers = self.soup.find(id="olp_feature_div").find("a").get_text().strip()
        except:
            how_many_sellers = "fail"
        print(how_many_sellers)
        return how_many_sellers

    def get_bullets(self):
        bullets = []
        try:
            bullets_contents = self.soup.find("div", id="feature-bullets").find_all("span", class_="a-list-item")
            for bullets_content in bullets_contents:
                print(bullets_content.get_text().strip())
                # toys
                if bullets_content.span:
                    continue
                bullets.append(bullets_content.get_text().strip())
        except:
            bullets = []
        return bullets

    def get_description(self):

        productDescription = ""
        try:
            if self.soup.find(id="productDescription"):
                productDescription = self.soup.find(id="productDescription").get_text()
        except:
            pass
        productDescription = re.sub(r"(Product Description.*; } )", "", productDescription)
        productDescription = productDescription.replace("Read more", "")
        productDescription = " ".join(productDescription.split())
        # print(productDescription)

        aplus = ""
        try:
            if self.soup.find(id="aplus"):
                aplus = self.soup.find(id="aplus").get_text()
            aplus = " ".join(aplus.split())
        except:
            pass
        aplus = re.sub(r"(From the manufacturer .aplus-v2 .*; } )", "", aplus)
        aplus = re.sub(r"(Product Description .aplus-v2 .*; } )", "", aplus)
        aplus = aplus.replace("Read more", "")
        aplus = " ".join(aplus.split())
        # print(aplus)

        description = productDescription + "\n" + aplus
        print(description)
        return description

    def get_salesrank(self):
        salesrank = ""
        try:
            if self.soup.find(id="SalesRank"):
                salesrank = self.soup.find(id="SalesRank")
                salesrank = salesrank.get_text().strip()
                salesrank = re.search('#(\d|,)+', salesrank)
                salesrank = salesrank.group()
                salesrank = salesrank.replace(',', '')
                salesrank = salesrank.replace('#', '')
            # toys
            if self.soup.find(id="productDetails_detailBullets_sections1"):
                trs = self.soup.find(id="productDetails_detailBullets_sections1").find_all("tr")
                for tr in trs:
                    if tr.find("th").get_text().strip():
                        if tr.find("th").get_text().strip() == "Best Sellers Rank":
                            salesrank = tr.find("td").get_text().strip()
                            salesrank = re.search('#(\d|,)+', salesrank)
                            salesrank = salesrank.group()
                            salesrank = salesrank.replace(',', '')
                            salesrank = salesrank.replace('#', '')
        except:
            pass
        print(salesrank)
        return salesrank

    def get_review_num(self):
        review_num = ""
        try:
            if self.soup.find(id="acrCustomerReviewText"):
                review_num = self.soup.find(id="acrCustomerReviewText").get_text().split()[0].strip()
        except:
            pass
        print(review_num)
        return review_num

    def get_review_value(self):
        review_value = ""
        try:
            if self.soup.find(class_="arp-rating-out-of-text"):
                review_value = self.soup.find(class_="arp-rating-out-of-text").get_text().strip()
                review_value = re.search('(.*?)\s', review_value)
                review_value = review_value.group()
                review_value = review_value.strip()
        except:
            pass
        print(review_value)
        return review_value

    def get_qa_num(self):
        qa_num = ""
        try:
            if self.soup.find(id="askATFLink"):
                qa_num = self.soup.find(id="askATFLink").get_text().split()[0].strip()
        except:
            pass
        print(qa_num)
        return qa_num

    def get_picture_url(self):
        picture_url = ""
        try:
            picture_urls_dict = dict()
            if self.soup.find("img", id="landingImage"):
                picture_urls = self.soup.find("img", id="landingImage")["data-a-dynamic-image"]
                picture_urls_dict = eval(picture_urls)
            picture_urls_list = []
            for key in picture_urls_dict.keys():
                picture_urls_list.append(key)
            picture_url = picture_urls_list[0]
        except:
            pass
        print(picture_url)
        return picture_url

    def get_listing(self):
        listing_dict = {
            "title": self.get_title(),
            "brand": self.get_brand(),
            "price": self.get_price(),
            "sold_by": self.get_sold_by(),
            "badge": self.get_badge(),
            "variation_name": self.get_variation_name(),
            "how_many_sellers": self.get_how_many_sellers(),
            "bullets": self.get_bullets(),
            "description": self.get_description(),
            "salesrank": self.get_salesrank(),
            "review_num": self.get_review_num(),
            "review_value": self.get_review_value(),
            "qa_num": self.get_qa_num(),
            "picture_url": self.get_picture_url(),
        }
        print(listing_dict)
        return listing_dict

listing = Listing("B00BJLS55G")
listing.get_listing()

# asin_list = ["B00BJLS55G", "B0075RW2KC", "B01J7KN23U"]
#
# for asin in asin_list:
#     listing = Listing(asin)
#     listing.get_listing()