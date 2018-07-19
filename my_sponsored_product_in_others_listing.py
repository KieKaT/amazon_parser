# coding: utf-8
# email: dg1245@qq.com
# your asin may display in other sellers listings sponsored products section, now you can find it easily
# amazon.com only

from amazon_module import amazon_module

class My_asin_in_others_listing():

    def __init__(self):
        # change to yours
        self.my_asin = "B0075RW2KC"
        # change to yours, find other sellers listings according self.keyword on amazon.com page 1
        self.keyword = "personalized dog collar"

        # do not change
        self.asin_list = []
        self.others_asin = ""
        self.sponsored_asin_list_dict = {}

    def asin_to_sponsored_asins(self):
        url = "https://www.amazon.com/dp/" + self.others_asin
        lis = amazon_module.download_soup_by_url(url).find(id="sp_detail").find("ol").find_all("li")
        sponsored_asin_list = []
        for li in lis:
            sponsored_asin = li.find("div")["data-asin"]
            sponsored_asin_list.append(sponsored_asin)
        return sponsored_asin_list

    def keyword_to_asin_list(self):
        try:
            print("Start running, may take a few minutes")
            base_url = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords="
            keyword_with_plus = "+".join(self.keyword.split())
            first_page_url = base_url + keyword_with_plus
            soup = amazon_module.download_soup_by_url(first_page_url)

            temp_others_asin_list = []
            try:
                lis = soup.find_all("li", class_="s-result-item")
                for li in lis:
                    try:
                        asin = li["data-asin"]
                        temp_others_asin_list.append(asin)
                    except:
                        pass

                # remove duplicate asin
                no_repeat_others_asin_list = []
                for asin in temp_others_asin_list:
                    if asin not in no_repeat_others_asin_list:
                        no_repeat_others_asin_list.append(asin)
                return no_repeat_others_asin_list
            except:
                pass
        except:
            pass

    def start(self):
        try:
            others_asin_list = self.keyword_to_asin_list()
            print("")
            print("My asin:", self.my_asin)
            print("Searching: " + self.keyword)
            print(str(len(others_asin_list)), "non-repeating asins in page 1")
            print("")

            for index, others_asin in enumerate(others_asin_list):
                self.others_asin = others_asin
                sponsored_asin_list = []
                sponsored_asin_list = self.asin_to_sponsored_asins()
                self.sponsored_asin_list_dict[self.others_asin] = sponsored_asin_list
                find_or_not = ""
                if self.my_asin in sponsored_asin_list:
                    find_or_not = "and find my asin"
                print(str(index+1), others_asin, "parse complete", find_or_not)

            my_count = 0
            total_count = 0

            print("")
            print("Others asin and sponsored asins in it:")
            for key, value in self.sponsored_asin_list_dict.items():
                print(key, value)
                if self.my_asin in value:
                    my_count += 1
                total_count += 1

            ratio = "unknown"
            if total_count != 0:
                ratio = str(my_count*100//total_count) + "%"

            print("")
            print("My asin in others listing sponsored products section: " + str(my_count) + "/" + str(total_count) + " (" + ratio + ")")

        except:
            pass

#main function
my_asin_in_others_listing = My_asin_in_others_listing()
my_asin_in_others_listing.start()
