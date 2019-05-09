import pandas as pd
import time
from selenium import webdriver
from fake_useragent import UserAgent

class Whoscored: 
    def __init__(self, url='https://www.whoscored.com/Regions/206/Tournaments/63/Spain-Segunda-Divisi%C3%B3n', headless=False):         
        self.url = url
        self.urls = []
        self.league_table_df = None
        self.team_infos_df = None
        self.final_df = None   
        
        self.options = webdriver.ChromeOptions() 
        self.options.add_argument("user-agent={}".format(UserAgent().chrome))
        if headless:
            self.options.add_argument('headless')
        self.driver = webdriver.Chrome(options=self.options)
   
    def get_league_table(self):         
        
        self.driver.get(self.url)
        columns_league = self.driver.find_elements_by_css_selector("#standings-16547-grid > thead > tr:first-child > th")
        columns_league = [column.text for column in columns_league][:-1]
        
        self.league_table_df = pd.DataFrame(columns = columns_league)


        teams = self.driver.find_elements_by_css_selector("#standings-16547-content tr") # Check
        
        for (index,team) in enumerate(teams):
            league_info = {
                "R" : team.find_element_by_css_selector(".o").text,
                "Team" : team.find_element_by_css_selector(".team").text,
                "P" : team.find_element_by_css_selector(".p").text,
                "W" : team.find_element_by_css_selector(".w").text,
                "D" : team.find_element_by_css_selector(".d").text,
                "L" : team.find_element_by_css_selector(".l").text,
                "GF" : team.find_element_by_css_selector(".gf").text,
                "GA" : team.find_element_by_css_selector(".ga").text,
                "GD" : team.find_element_by_css_selector(".gd").text,
                "Pts" : team.find_element_by_css_selector(".pts").text,
            }
            self.league_table_df.loc[index] = league_info
            self.url = team.find_element_by_css_selector("a").get_attribute("href")
            self.urls.append(self.url)
          
        return self.league_table_df

    
    def get_team_information(self):
        
        self.driver.get(self.urls[0])
        team_infos = self.driver.find_elements_by_css_selector("div.stats-container > dl > dt")
        team_infos = team_infos[2:8]
        columns_team_infos = [team_info.text for team_info in team_infos]
        columns_team_infos.insert(0, "Team")
        columns_team_infos.append("yellow_card")
        columns_team_infos.append("red_card")
        
        self.team_infos_df = pd.DataFrame(columns = columns_team_infos)
        

        for (index, url) in enumerate(self.urls):
            self.driver.get(url)
            
            try:
                self.driver.find_element_by_css_selector(".team-profile-side-box div.team-name > a").text
                
            except:
                print("{} data not available".format(self.driver.find_element_by_css_selector("h2.team-header > span.team-header-name").text))
            
            else:  
                team_info = [
                    self.driver.find_element_by_css_selector(".team-profile-side-box div.team-name > a").text,
                    self.driver.find_element_by_css_selector("dl.stats > dd:nth-child(6)").text,
                    self.driver.find_element_by_css_selector("dl.stats > dd:nth-child(8)").text,
                    self.driver.find_element_by_css_selector("dl.stats > dd:nth-child(10)").text,
                    self.driver.find_element_by_css_selector("dl.stats > dd:nth-child(12)").text,
                    self.driver.find_element_by_css_selector("dl.stats > dd:nth-child(14)").text,
                    self.driver.find_element_by_css_selector("dl.stats > dd:nth-child(16)").text,
                    self.driver.find_element_by_css_selector("dl.stats > dd:nth-child(18) > .yellow-card-box").text,
                    self.driver.find_element_by_css_selector("dl.stats > dd:nth-child(18) > .red-card-box").text,
                ]
                self.team_infos_df.loc[index] = team_info 
                
            
            time.sleep(8) 
                          
        
        self.driver.quit()
        print("Crawling Completed")
        return self.team_infos_df    
    
    def making_df(self):
        self.final_df = self.league_table_df.merge(self.team_infos_df, how='outer', left_on='Team', right_on='Team')
        return self.final_df
    
    def df_columns_to_num(self, df):
        temp_cols = list(df.columns)
        del temp_cols[1]
        for column in temp_cols:
            try:
                df[column] = df[column].apply(pd.to_numeric)
            except ValueError:
                df[column] = df[column].apply(lambda x: float((str(x).strip('%')))) 
            else:
                df[column] = df[column].apply(pd.to_numeric)
        return df.copy().drop(columns = ['Team'])

    def crawling(self):
        self.league_table_df = self.get_league_table()
        self.team_infos_df = self.get_team_information()
        self.final_df = self.making_df()
        
if __name__ == '__main__':
    whoscored = Whoscored()
    df = whoscored.crawling()
    df.tail()