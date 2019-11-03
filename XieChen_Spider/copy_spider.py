#%%
import json
import requests
from selenium import webdriver
from configparser import ConfigParser
import time
#%%
def smart_wait(webdriver,method,element_path):
    for i in range(60):
        if i >= 60-1:
            print("timeout")
            break
        try:
            if(method=="xpath"):
                if webdriver.find_element_by_xpath(element_path):
                    break
            if(method=="class_name"):
                if webdriver.find_element_by_class_name(element_path):
                    break
            if(method=="tag_name"):
                if webdriver.find_element_by_tag_name(element_path):
                    break
        except:
            print("wait for find element")
        time.sleep(1)
#%%
# read config file
config_path = './XieChen_Spider/config.cfg'
conf = ConfigParser()
conf.read(config_path,encoding='utf-8')
city_name = conf.get("common","city_name")
root_url = conf.get("common","root_url")
product_url_part1 = conf.get("common","product_url_part1")
product_url_part2 = conf.get("common","product_url_part2")


#%%
# call the chrome webdriver
# print(root_url)
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}
driver = webdriver.Chrome('./XieChen_Spider/chromedriver_win32/chromedriver')
# print(root_url)
# root_url = "https://vacations.ctrip.com/"
# print(root_url)
driver.get(root_url)

#%%
# response = requests.get(root_url,params = headers)
smart_wait(driver,'class_name','search_txt')
driver.find_element_by_class_name("search_txt").send_keys(city_name)
driver.find_element_by_class_name("main_search_btn").click()
#%%
# get product-id for every page
product_id = []
for i in range(2):
    tmp = driver.find_elements_by_xpath('//div[@class="main_col"]/div[@class="list_product_box js_product_item"]')
    print(len(tmp))
    product_id_list = [p.get_attribute("data-track-product-id") for p in tmp]
    print(len(product_id_list))
    product_id.extend(product_id_list)
    print(len(product_id))
    driver.find_element_by_xpath('//a[@class="down"]').click()
    time.sleep(5)# this time should not too small
print(product_id)
#%%
# print(product_id)
product_url = [str(product_url_part1)+str(p)+str(product_url_part2) for p in product_id]
# %%
print(product_url)

# %%
url = product_url[0]
driver.get(url)

# %%
product_name = driver.find_element_by_xpath('//h1').text
product_score = driver.find_element_by_xpath('//span[@class="score_s"]//em').text
# print(product_name,product_score)

# %%
# schedule info
data_dic = {}
data_dic['product_name'] = product_name
data_dic['score'] = product_score

# %%
# 提取key对应的value
def string_sub(key,key_value):
    l = len(key) if len(key)<=len(key_value) else len(key_value)
    print(l)
    return key_value[l:].strip()

schedule_intro = {}
summary = {}
summary_info_list = driver.find_elements_by_xpath('//table[@class="route_item_table"]//tr//td')
s = summary_info_list[0]
for s in summary_info_list:
    key = s.find_element_by_tag_name('em').text
    print("key" + key)
    key_value = s.text
    print("key_value" + key_value)
    value = string_sub(key, key_value)
    # print("value" + value)
    summary[key] = value

# %%
print(summary)

# %%
# schedule_day info
schedule_day_list = []
schedule_day_info = driver.find_elements_by_xpath('//div[@class="mult_route"]/div')
# process every one
hotel = []
for day in schedule_day_info:
    schedule_day_detail = {}
    schedule_day_detail["title"] = day.find_element_by_tag_name('h3').text
    event_list = []
    event_score = []
    event_list_1_direct = day.find_elements_by_xpath('.//div[@class="mult_data_item J_scheduleSubItemGraphic data_type"]//h4') # 可以直接提取
    # print(len(event_list_1_direct))
    event_list_2_mixture = day.find_elements_by_xpath('.//div[@class="mult_specific_item J_scheduleSubItemGraphic"]//h4//a') # 需要取属性再提取
    # print(len(event_list_2_mixture))
    for e in event_list_1_direct:
        event = {}
        location = e.find_element_by_tag_name('a').text
        score = e.find_element_by_tag_name('em').text
        event[location] = score
        event_list.append(event)
    for e in event_list_2_mixture:
        event = {}
        l = e.get_attribute('data-json')
        print(l)
        if(l!=None and 'Name' in json.loads(l).keys()):
            location = json.loads(l)['Name']
            score = e.find_element_by_xpath('..//em').text
            event[location] = score
            print('---')
            event_list.append(event)
    schedule_day_detail['event'] = event_list

    hotel_list = day.find_elements_by_xpath('.//div[@class="mult_specific_item J_scheduleSubItemGraphic"]//h4//a')
    hotel_list = [h.get_attribute('data-json') for h in hotel_list]
    hotel_list = [json.loads(h)['HotelName'] for h in hotel_list if 'HotelName' in json.loads(h).keys()]
    hotel.extend(hotel_list)
    hotel = list(set(hotel))
    schedule_day_detail['hotel'] = hotel
    schedule_day_list.append(schedule_day_detail)

# %%
next_bottum_list = driver.find_element_by_xpath('//div[@class="arr_btn"]//i[@class="tag_arr"]')
other_bottum = driver.find_element_by_xpath('//ul[@class="revision_side_function"]//a')
other_bottum.click()
time.sleep(1)
month = driver.find_elements_by_class_name('s_month')
month = [m.text for m in month]
time_value_list = []
for i in range(3):
    day_list = driver.find_elements_by_xpath('//table[@class="d_calendar_table"]//td/div/a/span[@class="date basefix"]')
    day_list = [d.text for d in day_list]
    value_list = driver.find_elements_by_xpath('//table[@class="d_calendar_table"]//td/div/a/span[last()-1]')
    value_list = [value.text[1:-1] for value in value_list]
    value_set = list(set(value_list))
    for v in value_set:
        time_value = {}
        day = day_list[value_list.index(v)]
        value = v
        time_value['date'] = month[i]+day
        time_value['value'] = value
        time_value_list.append(time_value)
    # print(len(day_list),len(value_list))
    next_bottum_list.click()
    time.sleep(1)
data_dic['time_value'] = time_value_list
driver.get('https://vacations.ctrip.com/tour/detail/p9415175s28.html')
# %%
print(data_dict['time_value'])
    
# %%
print(time_value_list)
# %%
recode = ['123','456','789']
with open('./recode.txt','w') as f: 
    for p in recode:
        f.write(p)
        f.write('\n')


# %%
recode = []
with open('./recode.txt','r') as f:
    for p in f.readlines():
        recode.append(p[0:-1])
print(recode)

# %%
