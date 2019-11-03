import json
import time
import requests
from selenium import webdriver
import configparser

# tool function
def string_sub(key,key_value):
    l = len(key) if len(key)<=len(key_value) else len(key_value)
    print(l)
    return key_value[l:].strip()


def store(data,path):
    data = str(data)
    with open(path, 'a', encoding='UTF-8' ) as fw:
        # 上面两句等同于下面这句
        json.dump(data,fw,ensure_ascii=False, indent=2)
        fw.write('\n')


def smart_wait(webdriver,method,element_path):
    for i in range(10):
        if i >= 9:
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


# specify the function of get product_info
def get_product_info(product_url):
    print("product_url:"+product_url+" begin spider")
    driver.get(product_url)
    driver.maximize_window()
    time.sleep(1)
    # the whole data structure
    data_dic = {}
    # the product name and score 
    print("----name and score")
    driver.refresh()
    smart_wait(driver,'xpath','//h1')
    time.sleep(2)
    product_name = driver.find_element_by_xpath('//h1').text
    smart_wait(driver,'xpath','//span[@class="score_s"]//em')
    time.sleep(2)
    product_score = driver.find_element_by_xpath('//span[@class="score_s"]//em').text
    data_dic['product_name'] = product_name
    data_dic['score'] = product_score
    # the time and value 
    # find the button control the month change
    # next_button_list = driver.find_element_by_xpath('//div[@class="arr_btn"]//i[@class="tag_arr"]')
    print("----time and value")
    smart_wait(driver,'xpath','//ul[@class="revision_side_function"]//a')
    other_bottum = driver.find_element_by_xpath('//ul[@class="revision_side_function"]//a')
    
    other_bottum.click()
    
    smart_wait(driver,'class_name','s_month')
    month = driver.find_elements_by_class_name('s_month')
    month = [m.text for m in month]
    time_value_list = []
    # get the rencent three month value change
    for i in range(month_num):
        smart_wait(driver,'xpath','//table[@class="d_calendar_table"]//td/div/a/span[@class="date basefix"]')
        day_list = driver.find_elements_by_xpath('//table[@class="d_calendar_table"]//td/div/a/span[@class="date basefix"]')
        # get all day
        day_list = [d.text for d in day_list]
        smart_wait(driver,'xpath','//table[@class="d_calendar_table"]//td/div/a/span[last()-1]')
        value_list = driver.find_elements_by_xpath('//table[@class="d_calendar_table"]//td/div/a/span[last()-1]')
        value_list = [value.text[1:-1] for value in value_list]
        # get all value 
        value_set = list(set(value_list))
        for v in value_set:
            time_value = {}
            # get the day according to the change value
            day = day_list[value_list.index(v)]
            value = v
            time_value['date'] = month[i]+day
            time_value['value'] = value
            time_value_list.append(time_value)
        # print(len(day_list),len(value_list))
        if(i != 2):
            smart_wait(driver,'xpath','//div[@class="arr_btn"]//i[@class="tag_arr"]')
            next_button_list = driver.find_element_by_xpath('//div[@class="arr_btn"]//i[@class="tag_arr"]')
            
            next_button_list.click()
        
        time.sleep(5)
    # the value_day_change
    data_dic['time_value'] = time_value_list
    # recover the web page
    driver.get(product_url)
    time.sleep(5)

    print("----schedule_intro_summary")
    # get the schedule_intro
    schedule_intro = {}
    summary = {}
    driver.refresh()
    smart_wait(driver,'xpath','//table[@class="route_item_table"]//tr//td')
    summary_info_list = driver.find_elements_by_xpath('//table[@class="route_item_table"]//tr//td')
    for s in summary_info_list:
        smart_wait(s,'tag_name','em')
        key = s.find_element_by_tag_name('em').text
        # print("key" + key)
        key_value = s.text
        # print("key_value" + key_value)
        value = string_sub(key, key_value)
        value = value.replace('\\n','  ')
        # print("value" + value)
        summary[key] = value
        # print(summary)
    schedule_intro['summary'] = summary

    print('----every_day_info')
    # get every day info 
    schedule_day_list = []
    driver.refresh()
    smart_wait(driver,'xpath','//div[@class="mult_route"]/div')
    schedule_day_info = driver.find_elements_by_xpath('//div[@class="mult_route"]/div')
    i=1
    while(len(schedule_day_info) == 0):
        schedule_day_info = driver.find_elements_by_xpath('//div[@class="mult_route"]/div')
    # process every one
    for day in schedule_day_info:
        print('--------the'+str(i)+'day')
        schedule_day_detail = {}
        print('----------title')
        smart_wait(day,'tag_name','h3')
        title = day.find_element_by_tag_name('h3').text
        schedule_day_detail["title"] = title[5:]
        print('----------event')
        event_list = []
        # it have two event tag
        smart_wait(day,'xpath','.//div[@class="mult_data_item J_scheduleSubItemGraphic data_type"]//h4')
        event_list_1_direct = day.find_elements_by_xpath('.//div[@class="mult_data_item J_scheduleSubItemGraphic data_type"]//h4') # 可以直接提取
        # print(len(event_list_1_direct))
        smart_wait(day,'xpath','.//div[@class="mult_specific_item J_scheduleSubItemGraphic"]//h4//a')
        event_list_2_mixture = day.find_elements_by_xpath('.//div[@class="mult_specific_item J_scheduleSubItemGraphic"]//h4//a') # 需要取属性再提取
        # print(len(event_list_2_mixture))
        for e in event_list_1_direct:
            event = {}
            smart_wait(e,'tag_name','a')
            location = e.find_element_by_tag_name('a').text
            smart_wait(e,'tag_name','em')
            try:
                score = e.find_element_by_tag_name('em').text
                event['location'] = location
                event['score'] = score
            except:
                event['location'] = location
                event['score'] = None
            event_list.append(event)
        for e in event_list_2_mixture:
            event = {}
            time.sleep(2)
            l = e.get_attribute('data-json')
            if(l!=None and 'Name' in json.loads(l).keys()):
                location = json.loads(l)['Name']
                # print("-------------------------")
                smart_wait(e,'xpath','..//em')
                try:
                    score = e.find_element_by_xpath('..//em').text
                    event['location'] = location
                    event['score'] = score
                except:
                    event['location'] = location
                    event['score'] = None
                event_list.append(event)
        schedule_day_detail['event'] = event_list
        # get hotel info
        print('----------hotel')
        smart_wait(day,'xpath','.//div[@class="mult_specific_item J_scheduleSubItemGraphic"]//h4//a')
        hotel_list = day.find_elements_by_xpath('.//div[@class="mult_specific_item J_scheduleSubItemGraphic"]//h4//a')
        hotel_list = [h.get_attribute('data-json') for h in hotel_list]
        hotel_list = [json.loads(h)['HotelName'] for h in hotel_list if 'HotelName' in json.loads(h).keys()]
        hotel = list(set(hotel_list))
        schedule_day_detail['hotel'] = hotel
        # add one day info in list
        schedule_day_list.append(schedule_day_detail)
        i += 1

    # add in the all data structure
    for i,s in enumerate(schedule_day_list):
        schedule_intro['schedule_day_'+str(i+1)] = s
    
    print('--------cost')
    # get the cost info
    cost = {}
    driver.refresh()
    smart_wait(driver,'xpath','//dl[@class="mod_info_box"][last()-1]//table[@class="tour_description_table"]//tbody//th')
    cost_name_list = driver.find_elements_by_xpath('//dl[@class="mod_info_box"][last()-1]//table[@class="tour_description_table"]//tbody//th')
    cost_name_list = [n.text for n in cost_name_list]
    smart_wait(driver,'xpath','//dl[@class="mod_info_box"][last()-1]//table[@class="tour_description_table"]//tbody//td')
    cost_detail_list = driver.find_elements_by_xpath('//dl[@class="mod_info_box"][last()-1]//table[@class="tour_description_table"]//tbody//td')
    cost_detail_list = [d.text for d in cost_detail_list]
    cost_detail_list = [d.replace('\\n',' ') for d in cost_detail_list]
    for n,d in zip(cost_name_list,cost_detail_list):
        cost[n] = d
    schedule_intro['cost'] = cost

    data_dic['schedule_intro'] = schedule_intro

    return data_dic


if __name__ == "__main__":
    # read config file
    config_path = './config.cfg'
    # config_path = './XieChen_Spider/config.cfg' #debug
    conf = configparser.ConfigParser()
    conf.read(config_path, encoding='utf-8')
    city_name = conf.get("common","city_name")
    root_url = conf.get("common","root_url")
    product_url_part1 = conf.get("common","product_url_part1")
    product_url_part2 = conf.get("common","product_url_part2")
    page_num = conf.getint("common","page_num")
    month_num = conf.getint("common","month_num")
    path = conf.get("common","down_file_path")
    log_path = conf.get("common","log_path")

    # read the spidered record
    record = []
    with open(log_path,'r') as f: 
        for p in f.readlines():
            record.append(p[0:-1]) 

    # call the chrome driver
    driver = webdriver.Chrome('./chromedriver_win32/chromedriver') 
    # driver = webdriver.Chrome('./XieChen_Spider/chromedriver_win32/chromedriver') #debug 
    driver.get(root_url)
    driver.maximize_window()
    # input cityname and click search
    smart_wait(driver,'class_name',"search_txt")
    driver.find_element_by_class_name("search_txt").send_keys(city_name)
    smart_wait(driver,'class_name','main_search_btn')
    driver.find_element_by_class_name('main_search_btn').click()

    # get the product_id of specified pages
    product_id = []
    for i in range(page_num):
        smart_wait(driver,'xpath','//div[@class="main_col"]/div[@class="list_product_box js_product_item"]')
        driver.refresh()
        tmp = driver.find_elements_by_xpath('//div[@class="main_col"]/div[@class="list_product_box js_product_item"]')
        product_id_list = [p.get_attribute("data-track-product-id") for p in tmp]
        product_id.extend(product_id_list)
        smart_wait(driver,'xpath','//a[@class="down"]')
        driver.find_element_by_xpath('//a[@class="down"]').click()
        print("第"+str(i+1)+"页")
        # time.sleep(5)# this time should not too small
    # cat to the product_url
    product_url = [str(product_url_part1)+str(p)+str(product_url_part2) for p in product_id]

    # get data 
    product_spidered_id = []
    f = open(log_path,'a')
    for i,u in zip(product_id,product_url):
        count = 1
        data_struct = {}    
        if(str(i) not in record):
            while (count <= 10):
                try:
                    data_struct = get_product_info(u)
                    break
                except:
                    print(u+"occur exception! now try again the"+str(count))
                    count += 1
            if(count <= 10):
                store(data_struct,path)
                record.append(str(i))
                f.write(i)
                f.write('\n')
    f.close()
    print('--')
        

