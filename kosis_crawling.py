from selenium import webdriver
import time
from fake_useragent import UserAgent

class Kosis:
    def __init__(self, start_date=None, end_date=None, headless=True, url="http://kosis.kr/statHtml/statHtml.do?orgId=301&tblId=DT_041Y013&conn_path=I2"):
        options = webdriver.ChromeOptions()
        options.add_argument("user-agent={}".format(UserAgent().chrome))
        if headless:
            options.add_argument('headless')
        self.driver = webdriver.Chrome(options=options)
        self.start_date = start_date
        self.end_date = end_date
        self.url = url
        self.rows = None
        self.columns = None
        self.values = None
        self.result_df = None
        
    
    def __loading(self, term=1, maximum=10):
        print("loading.", end="")
        while True:
            style = self.driver.find_element_by_css_selector("#disPlayBox").get_attribute("style")
            time.sleep(term)
            
            # check whether loading is finished
            if style == "display: none;":
                print("done!")
                break
                
            # check maximum waiting time
            maximum -=1
            if not maximum:
                break
                
            print(".", end="")
    
    def __select_date(self):
            self.driver.find_element_by_css_selector("#tabTimeText").click()
            self.driver.find_element_by_css_selector(\
                "#timeM > h2.top > select:first-child > option[value='{}']".format(self.start_date)).click()
            self.driver.find_element_by_css_selector(\
                "#timeM > h2.top > select:nth-child(2) > option[value='{}']".format(self.end_date)).click()
            self.driver.execute_script("fn_search();") 
    
    def __rows(self): # get row elements
        return self.driver.find_elements_by_css_selector("#mainTable > tbody > tr")
    
    def __columns(self):
        columns = self.driver.find_elements_by_css_selector("#mainTableT > thead > tr:first-child > th")[2:] 
        return [column.text for column in columns]
    
    def __indexs(self):
        indexs, tmp_index = [], ""
        rows_count = len(self.rows)
        for count, row in enumerate(self.rows):
            
            if count != (rows_count - 1):
                row_indexs = row.find_elements_by_css_selector(".first")
            else:
                row_indexs = row.find_elements_by_css_selector(".first-end")
        
            if len(row_indexs) > 1:
                tmp_index = row_indexs[0].text
                indexs.append("{}:{}".format(tmp_index, row_indexs[1].text))
            else:
                indexs.append("{}:{}".format(tmp_index, row_indexs[0].text))
    
        return indexs

    def __values(self):
        values = []
        for count, row in enumerate(self.rows):
            row_values = row.find_elements_by_css_selector(".value > .val")
            row_values = [value.text for value in row_values]
            values.append(row_values)
        return values
    
    def crawling(self):
        self.driver.get(self.url)
        self.__loading()
 
        if self.start_date and self.end_date:
            print("set date...")
            self.__select_date()
        
        self.__loading()
        
        print("crawling...", end="")    
        self.rows = self.__rows()
        self.columns = self.__columns()
        self.indexs = self.__indexs()
        self.values = self.__values()
        print("done!")
        
        self.result_df = pd.DataFrame(self.values, columns = self.columns, index = self.indexs)
        return self.result_df
        
    def set_date(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
    
    def close(self):
        self.driver.quit()
    

# test code
kosis = Kosis("201803", "201807")
df = kosis.crawling()
df.tail()