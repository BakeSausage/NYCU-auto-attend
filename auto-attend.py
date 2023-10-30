from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
import numpy as np
from time import sleep
import datetime
import os
import configparser


class config:
    def __init__(self):
        self.account = ""
        self.password = ""
        # self.PATH = ""
        self.operateTimeInterval = ""
        
    def get_config(self):
        config = configparser.ConfigParser()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with open(".\config.ini", "a+") as f:
            config.read("config.ini")
            try:
                self.account = config["config"]["account"]
                self.password = config["config"]["password"]
                # self.PATH = config["config"]["PATH"]
                self.operateTimeInterval = config["config"]["operateTimeInterval"]
            except:
                print("Configuration file not found, please set it up.")
                try:
                    config.add_section("config")
                except:
                    pass
                self.account = input("Account:")
                self.password = input("Password:")
                # self.PATH = input("Complete Path of ChromeDriver:")
                self.operateTimeInterval = input("Operate Time Interval(default=0.5):")
                config.set("config", "account", self.account)
                config.set("config", "password", self.password)
                # config.set("config", "PATH", self.PATH)
                config.set("config", "operateTimeInterval", self.operateTimeInterval)
                config.write(f)
    


def connent_to_attendence():
    try:
        driver = webdriver.Chrome()
    except:
        cService = webdriver.ChromeService()
        driver = webdriver.Chrome(service = cService)
    return driver

def login(account, password):
    driver.find_element(By.NAME, "Account").send_keys(account)
    driver.find_element(By.NAME, "Password").send_keys(password)
    driver.find_element(By.NAME, "Password").send_keys(Keys.RETURN)

def get_main_elements():
    main1 = driver.find_element(By.ID, "main1")
    main2 = driver.find_element(By.ID, "main2")
    main3 = driver.find_element(By.ID, "main3")
    main4 = driver.find_element(By.ID, "main4")
    return main1, main2, main3, main4

def get_data(elements, elements_branch_class_name, rows_number=8):
    data=[]
    for element in elements:
        for a in element.find_elements(By.CLASS_NAME, elements_branch_class_name):
            data.append(a.text)
    return np.array(data, dtype=str).reshape(int(len(data)/rows_number), rows_number)

def check_for_attendance(date_today, date_check, attendance_date):
    #True  -> need attendance
    #False -> already attended
    date_today = int(date_today)
    date_check = int(date_check)
    if str(date_check) in attendance_date:
        return False
    if date_today//100 < date_check:
        return False
    return True
    
class laber_select_time:
    def __init__(self, timePicker):
        self.timePicker = main3.find_element(By.ID, timePicker)

    def set_time(self, day, time):
        self.timePicker.click()
        sleep(0.2)
        driver.find_element(By.ID, "ui-datepicker-div").find_element(By.XPATH, "//a[contains(text(),"+ str(day) +")]").click()
        self.slider = driver.find_element(By.ID, "ui-datepicker-div").find_element(By.CLASS_NAME, "ui_tpicker_hour_slider")
        move = ActionChains(driver)
        move.click_and_hold(self.slider).move_by_offset(time, 0).release().perform()
        sleep(0.2)
        driver.find_element(By.ID, "ui-datepicker-div").find_element(By.CLASS_NAME, "ui-datepicker-close").click()



def attendance(project):

    if project[2]=="勞動型":
        a = np.where(labor_history[:,3] == project[0])
        start_date = int(project[6].replace("-",""))
        end_date = int(project[7].replace("-",""))
        start_month = str(int(project[6].replace("-",""))//100)
        end_month = str(int(project[7].replace("-",""))//100)
        for i in range( 12*(int(end_month[0:4])-int(start_month[0:4])) + (int(end_month[4:6])-int(start_month[4:6])) + 1):
            date = int(start_month) + (int(start_month[4:6])+i-1)//12*88 + i
            if check_for_attendance(today, date, labor_history[a,2]):
                main2.find_element(By.ID, "node_level-1-1").click()
                print("try to attend  " + project[0] + "    " + str(date) + "...")
                sleep(0.2)
                
                day = start_date % 100
                weekly_work_day = 1
                morning = True
                time_unit = 0
                

                select = Select(main3.find_element(By.NAME, "workP"))
                for op in select.options:
                    if op.text == "":
                        continue
                    if (int(op.text.split(" ")[1].split("~")[0].replace("-",""))//100-date) * (int(op.text.split(" ")[1].split("~")[1].replace("-",""))//100-date) > 0 or (op.text.split(":")[0] != project[0]):
                        continue
                    op_text = op.text
                    break
                days = (int(today)-int(op.text.split(" ")[1].split("~")[0].replace("-",""))+1) #default caculation only by date(dd), maybe it was wrong
                if days//7*40 - ((days-5) % 7 * 8 if (days)%7==(0 or 6) else 0) + (days-days//7*7)*8 < int(project[5]):
                    print("fail : do not have enough time unit, need " + project[5] + " but " + str(days//7*40 - ((days-5) % 7 * 8 if (days)%7==(0 or 6) else 0) + (days-days//7*7)*8))
                    break
                
                for i in range((int(project[5])+3)//4):
                    select = Select(main3.find_element(By.NAME, "workP"))
                    select.select_by_visible_text(op_text)
                    
                      #8.->-20   12.->4   13.->9   17->33
                    
                    date_picker_start_time = laber_select_time("datetimepicker1")
                    date_picker_end_time = laber_select_time("datetimepicker2")
                    if int(project[5]) - time_unit >= 4:
                        if morning:
                            start_time = -60
                            end_time = -36
                            date_picker_start_time.set_time(day, start_time)
                            date_picker_end_time.set_time(day, end_time)
                        else:
                            start_time = 45
                            end_time = 69
                            date_picker_start_time.set_time(day, start_time)
                            date_picker_end_time.set_time(day, end_time)
                    else:
                        if morning:
                            start_time = -60
                            end_time = -60 + 6* (int(project[5]) - time_unit)
                            date_picker_start_time.set_time(day, start_time)
                            date_picker_end_time.set_time(day, end_time)
                        else:
                            start_time = 45
                            end_time = 45 + 6 * (int(project[5]) - time_unit)
                            date_picker_start_time.set_time(day, start_time)
                            date_picker_end_time.set_time(day, end_time)
                    main3.find_element(By.ID, "btnSubmit").click()
                    day = day + 1 if not(morning) else day
                    weekly_work_day = weekly_work_day + 1 if not(morning) else weekly_work_day
                    if weekly_work_day > 5:
                        weekly_work_day = 1
                        day = day + 2
                    time_unit = time_unit + 4
                    morning = not morning
                    if time_unit >= int(project[5]):
                        break
                    sleep(operateTimeInterval)
                main2.find_element(By.ID, "node_level-1-2").click()
                sleep(operateTimeInterval)
                                    
                for a in main3.find_elements(By.XPATH, "//div[@title='" + project[0] + "']/../.."):
                    a.find_element(By.CLASS_NAME, "w2ui-grid-select-check").click()
                main3.find_element(By.ID, "btnSubmit").click()
                print("attend  " + project[0] + "    " + str(date) + "success")
                
                
    elif project[2]=="獎助型":
        a = np.where(scholarship_history[:,4] == project[0])
        start_month = str(int(project[6].replace("-",""))//100)
        end_month = str(int(project[7].replace("-",""))//100)
        for i in range( 12*(int(end_month[0:4])-int(start_month[0:4])) + (int(end_month[4:6])-int(start_month[4:6])) + 1):
            date = int(start_month) + (int(start_month[4:6])+i-1)//12*88 + i
            if check_for_attendance(today, date, scholarship_history[a,3]):
                main2.find_element(By.ID, "node_level-2-1").click()
                print("try to attend  " + project[0] +"    " + str(date) + "...")
                sleep(0.2)
                select = Select(main3.find_element(By.NAME, "workP"))
                for op in select.options:
                    if op.text == "":
                        continue
                    if ((int(op.text.split(" ")[1].split("-")[0])-date) * (int(op.text.split(" ")[1].split("-")[1])-date)) > 0 or (op.text.split(":")[0] != project[0]):
                        continue
                    select.select_by_visible_text(op.text)
                    sleep(0.2)
                    check_box_list = get_data(main3.find_elements(By.CLASS_NAME, "w2ui-odd") + main3.find_elements(By.CLASS_NAME, "w2ui-even"), "w2ui-grid-data", 4)

                    main3.find_element(By.ID, "ShowWorkDetail").find_element(By.XPATH, "//div[@title=" + str(check_box_list[(np.where(check_box_list[:,1]==str(date))),1][0,0]) + "]/../..").find_element(By.TAG_NAME, "input").click

                    main3.find_element(By.CSS_SELECTOR, "input[type='button']").click()
                    print("attend  " + project[0] + "    " + str(date) + "success")



if __name__ == '__main__':
    
    config = config()
    config.get_config()
    

    operateTimeInterval = float(config.operateTimeInterval)
    
    
    driver = connent_to_attendence()
    
    driver.get("https://pt-attendance.nctu.edu.tw/verify/userLogin.php")
    login(config.account, config.password)
    
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "modal-content")))
    sleep(operateTimeInterval)
    all_projects = get_data(driver.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr"), "align-middle")
    
    
    driver.find_element(By.ID, "showWorkLists").send_keys(Keys.ESCAPE)
    sleep(operateTimeInterval)
    
    
    main1, main2, main3, main4 = get_main_elements()

    driver.find_element(By.ID, "node_level-2-2").click() #獎助型申請紀錄
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "w2ui-grid-data")))
    sleep(operateTimeInterval)
    scholarship_history = get_data((main3.find_elements(By.CLASS_NAME, "w2ui-odd") + main3.find_elements(By.CLASS_NAME, "w2ui-even")), "w2ui-grid-data")
    
    
    driver.find_element(By.ID, "node_level-1-4").click() #勞動型申請紀錄
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "w2ui-grid-data")))
    sleep(operateTimeInterval)
    labor_history = get_data(main3.find_elements(By.CLASS_NAME, "w2ui-odd") + main3.find_elements(By.CLASS_NAME, "w2ui-even"), "w2ui-grid-data")
    
    
    ########################################################################
    
    today = str(datetime.date.today()).replace("-","")
    
    for project in all_projects:
        attendance(project)
    
    
    print("attend done.")

    driver.close()