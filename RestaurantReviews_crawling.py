class PoingReviews:
    def __init__(self):
        self.restaurant_names = None
        self.final = None
        self.restaurant_type = None
        self.restaurant_location = None
        self.dom = None
        self.links = None
        self.scores = None
        self.reviews = None
        self.df = None
        self.complete_infos = []
        self.columns = ["name", "type", "location", "link", "score", "review"]
        self.food_types = ["한식", "양식", "중식", "일식", "아시아식", "컨템퍼러리", "뷔페", "구이", "술집", '카페/베이커리']
        
    def make_url(self, page):
        url = "https://www.poing.co.kr/seoul/review?pg={}".format(page)
        response = requests.get(url)
        self.dom = BeautifulSoup(response.content, "html.parser")
        
    def get_name(self):
        self.restaurant_names = self.dom.select("div.review > a.place > p.name")
        self.restaurant_names = [name.text for name in self.restaurant_names]
        return self.restaurant_names

    def get_location_type(self):
        
        self.final = []
        loc_types_restaurants = self.dom.select("div.review > a.place > p.info")
        loc_types_restaurants = [res.text.split(" ") for res in loc_types_restaurants]

        for restaurant in loc_types_restaurants:
            restaurant_info = []
            for word in restaurant:
                try:
                    if word[0].isalpha():
                        restaurant_info.append(word)
                except:
                    if word.isalpha():
                        restaurant_info.append(word)
            self.final.append(restaurant_info)
        
        return self.final
        
    def get_type(self):
        self.restaurant_type = [item[-1] if item[-1] in food_types else " " for item in self.final]
        return self.restaurant_type

    def get_location(self):
        self.restaurant_location = []
        for restaurant in self.final:
            temp = []
            for item in restaurant: 
                if item not in self.food_types:
                    temp.append(item)
            self.restaurant_location.append(" ".join(temp))
        return self.restaurant_location
    
    def get_links(self):
        self.links = ["www.poing.co.kr" + a['href'] for a in self.dom.select("div.review > a.place")]
        return self.links
        
    def get_scores(self):
        self.scores = [float(score.text.split("/")[0]) for score in self.dom.select("div.review > div.body > div.grade span")]
        return self.scores
    
    def get_reviews(self):
        
        self.reviews = [re.sub("\\n|\\t+", " ", review.text) for review in self.dom.select("div.review > div.body > div.text")]
        return self.reviews
    
    def make_df(self, end_page, start_page=1):

        for p in range(start_page, end_page+1):
            print("crawling_page -- {}".format(p))
            self.make_url(p)
            self.restaurant_names = self.get_name()
            self.final = self.get_location_type()
            self.restaurant_type = self.get_type()
            self.restaurant_location = self.get_location()
            self.links = self.get_links()
            self.scores = self.get_scores()
            self.reviews = self.get_reviews()
            
            data = list(zip(self.restaurant_names, self.restaurant_type, self.restaurant_location, \
                                           self.links, self.scores, self.reviews))
            self.complete_infos.append(data)
            
            if p == start_page:
                self.df = pd.DataFrame(self.complete_infos[p-1], columns = self.columns)
            else:
                self.df = self.df.append(pd.DataFrame(self.complete_infos[p-1], columns = self.columns))
        print("crawling complete!")
        return self.df.reset_index(drop=True)