from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
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
        self.operateTimeInterval = ""
        
    def get_config(self):
        config = configparser.ConfigParser()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with open(".\config.ini", "a+") as f:
            config.read("config.ini")
            try:
                self.account = config["config"]["account"]
                self.password = config["config"]["password"]
                self.operateTimeInterval = config["config"]["operateTimeInterval"]
            except:
                print("Configuration file not found, please set it up.")
                try:
                    config.add_section("config")
                except:
                    pass
                self.account = input("Account:")
                self.password = input("Password:")
                self.operateTimeInterval = "0.5"
                config.set("config", "account", self.account)
                config.set("config", "password", self.password)
                config.set("config", "operateTimeInterval", self.operateTimeInterval)
                config.write(f)
    


def connent_to_attendence():
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    try:
        driver = webdriver.Chrome(options=options)
    except:
        try:
            driver = webdriver.Chrome(options=options)
        except:
            try:
                driver = webdriver.Chrome()
            except:
                pass
    return driver


def login(account, password):
    driver.find_element(By.NAME, "Account").send_keys(account)
    driver.find_element(By.NAME, "Password").send_keys(password)
    driver.find_element(By.NAME, "Password").send_keys(Keys.RETURN)

def get_main_elements():
    main2 = driver.find_element(By.ID, "main2")
    main3 = driver.find_element(By.ID, "main3")
    return main2, main3


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

def check_for_attendance2(date_today, date_check, attendance_date, attendance_reg):
    #True  -> need attendance
    #False -> already attended
    date_today = int(date_today)
    date_check = int(date_check)
    if date_today//100 < date_check:
        return False
    if attendance_reg[np.where(attendance_date==str(date_check))] != "未登錄":
        return False
    return True
    



class laber_select_time:
    def __init__(self, timePicker):
        self.timePicker = main3.find_element(By.ID, timePicker)

    def set_time(self, year_month, day, time):
        self.timePicker.click()
        year = driver.find_element(By.CLASS_NAME, "ui-datepicker-year").text
        month = driver.find_element(By.CLASS_NAME, "ui-datepicker-month").text
        while int(year + self.month_to_number(month)) != int(year_month):
            year = driver.find_element(By.CLASS_NAME, "ui-datepicker-year").text
            month = driver.find_element(By.CLASS_NAME, "ui-datepicker-month").text
            if int(year + self.month_to_number(month)) > int(year_month):
                driver.find_element(By.CLASS_NAME, "ui-datepicker-prev").click()
            elif int(year + self.month_to_number(month)) < int(year_month):
                driver.find_element(By.CLASS_NAME, "ui-datepicker-next").click()
                
        driver.find_element(By.ID, "ui-datepicker-div").find_element(By.XPATH, "//a[contains(text(),"+ str(day) +")]").click()
        self.slider = driver.find_element(By.ID, "ui-datepicker-div").find_element(By.CLASS_NAME, "ui_tpicker_hour_slider")
        move = ActionChains(driver)
        move.click_and_hold(self.slider).move_by_offset(time, 0).release().perform()
        driver.find_element(By.ID, "ui-datepicker-div").find_element(By.CLASS_NAME, "ui-datepicker-close").click()

    def month_to_number(self,o):
        M=["一月","二月","三月","四月","五月","六月","七月","八月","九月","十月","十一月","十二月"]
        m=["01","02","03","04","05","06","07","08","09","10","11","12"]
        return m[M.index(o)]

class schedule:
    def __init__(self):
        s = configparser.ConfigParser()
        with open(".\schedule.ini", "a+") as f:
            s.read("schedule.ini")
            self.schedule = s
    
    
    def has_class(self, date, morning):
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if self.schedule[weekdays[int(datetime.datetime.strptime(date, "%Y%m%d").weekday())]]["morning" if morning else "afternoon"] == "1":
            return True
        else:
            return False
        
    def all_class_time(self):
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        morning = ["morning", "afternoon"]
        t = 0
        for i in weekdays:
            for j in morning:
                t += int(self.schedule[i][j])
        return t

def can_work(work_time_list, date_day, morning):
    if work_time_list==[]:
        return True
    B = [eval(i) for i in np.array(work_time_list)[:,0]]
    
    T = 0
    for i in range(6):
        T += int(int(date_day)-i-1 in B)
    if T >= 5:
        return False
    
    T = 0
    for i in range(1):
        T += int(datetime.datetime.strptime(str(int(date_day)-i), "%Y%m%d").date().isoweekday() in [6,7] and datetime.datetime.strptime(str(int(date_day)-i-1), "%Y%m%d").date().isoweekday() in [6,7])
    if T >= 1:
        return False
    
    
    return True
    

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
                sleep(operateTimeInterval)
                
                day = start_date % 100
                morning = True
                time_unit = 0
                work_time_list = []
                
                select = Select(main3.find_element(By.NAME, "workP"))
                for op in select.options:
                    if op.text == "":
                        continue
                    if (int(op.text.split(" ")[1].split("~")[0].replace("-",""))//100-date) * (int(op.text.split(" ")[1].split("~")[1].replace("-",""))//100-date) > 0 or (op.text.split(":")[0] != project[0]):
                        continue
                    op_text = op.text
                    break
                days = (int(today)-int(op.text.split(" ")[1].split("~")[0].replace("-",""))+1) #default caculation only by date(dd), didnt consider project over 1 month
                if days//7*40 - ((days-5) % 7 * 8 if (days)%7==(0 or 6) else 0) + (days-days//7*7)*8 < int(project[5]) + 4*schedule.all_class_time():
                    print("fail : do not have enough time unit, need " + project[5] + " but " + str(days//7*40 - ((days-5) % 7 * 8 if (days)%7==(0 or 6) else 0) + (days-days//7*7)*8) + "\n")
                    break
                while time_unit < int(project[5]):
                    select = Select(main3.find_element(By.NAME, "workP"))
                    select.select_by_visible_text(op_text)
                    date_picker_start_time = laber_select_time("datetimepicker1")
                    date_picker_end_time = laber_select_time("datetimepicker2")
                    
                    
                    if schedule.has_class(str(date)+str(day), morning) == True:
                        day = day + 1 if not(morning) else day
                        morning = not morning
                        continue
                    if not(can_work(work_time_list, str(date)+str(day), morning)):
                        day = day + 1 if not(morning) else day
                        morning = not morning
                        continue
                        
                    if int(project[5]) - time_unit >= 4:
                        if morning:
                            start_time = -20
                            end_time = 4
                            date_picker_start_time.set_time(start_month, day, start_time)
                            date_picker_end_time.set_time(start_month, day, end_time)
                        else:
                            start_time = 9
                            end_time = 33
                            date_picker_start_time.set_time(start_month, day, start_time)
                            date_picker_end_time.set_time(start_month, day, end_time)
                    else:
                        if morning:
                            start_time = -20
                            end_time = -20 + 6* (int(project[5]) - time_unit)
                            date_picker_start_time.set_time(start_month, day, start_time)
                            date_picker_end_time.set_time(start_month, day, end_time)
                        else:
                            start_time = 9
                            end_time = 9 + 6 * (int(project[5]) - time_unit)
                            date_picker_start_time.set_time(start_month, day, start_time)
                            date_picker_end_time.set_time(start_month, day, end_time)
                    main3.find_element(By.ID, "btnSubmit").click()
                    work_time_list.append([str(date)+str(day), morning])
                    print("")
                    time_unit = time_unit + 4
                    
                    day = day + 1 if not(morning) else day
                    morning = not morning
                    
                    sleep(operateTimeInterval)
                    
                main2.find_element(By.ID, "node_level-1-2").click()
                sleep(operateTimeInterval)               
                for a in main3.find_elements(By.XPATH, "//div[@title='" + project[0] + "']/../.."):
                    a.find_element(By.CLASS_NAME, "w2ui-grid-select-check").click()
                main3.find_element(By.ID, "btnSubmit").click()
                WebDriverWait(driver, 10).until(EC.alert_is_present())
                driver.switch_to.alert.accept()
                print("successfully attend   " + project[0] + "    " + str(date)+"\n")
                
                
    elif project[2]=="獎助型":
        a = np.where(scholarship_history[:,4] == project[0])
        
        start_month = str(int(project[6].replace("-",""))//100)
        end_month = str(int(project[7].replace("-",""))//100)
        for i in range( 12*(int(end_month[0:4])-int(start_month[0:4])) + (int(end_month[4:6])-int(start_month[4:6])) + 1):
            date = int(start_month) + (int(start_month[4:6])+i-1)//12*88 + i
            
            if check_for_attendance2(today, date, scholarship_history[a,3], scholarship_history[a,6]):
                
                main2.find_element(By.ID, "node_level-2-1").click()
                print("try to attend  " + project[0] +"    " + str(date) + "...")
                sleep(operateTimeInterval)
                select = Select(main3.find_element(By.NAME, "workP"))
                for op in select.options:
                    if op.text == "":
                        continue
                    if ((int(op.text.split(" ")[1].split("-")[0])-date) * (int(op.text.split(" ")[1].split("-")[1])-date)) > 0 or (op.text.split(":")[0] != project[0]):
                        continue
                    break
                select.select_by_visible_text(op.text)
                WebDriverWait(main3, 10).until(EC.presence_of_element_located((By.TAG_NAME, "label")))
                sleep(operateTimeInterval)
                main3.find_element(By.ID, "ShowWorkDetail").find_element(By.XPATH, "//div[@title=" + str(date) + "]/../..").find_element(By.TAG_NAME, "input").click()
                main3.find_element(By.CSS_SELECTOR, "input[type='button']").click()
                sleep(operateTimeInterval)
                print("successfully attend   " + project[0] + "    " + str(date)+"\n")






if __name__ == '__main__':

    config = config()
    config.get_config()
    operateTimeInterval = float(config.operateTimeInterval)
    
    
    driver = connent_to_attendence()
    
    
    driver.get("https://pt-attendance.nycu.edu.tw/verify/userLogin.php")
    login(config.account, config.password)
    
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "modal-content")))
    sleep(operateTimeInterval)
    all_projects = get_data(driver.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr"), "align-middle")

    
    driver.find_element(By.ID, "showWorkLists").send_keys(Keys.ESCAPE)
    sleep(operateTimeInterval)
    
    
    main2, main3 = get_main_elements()


    driver.find_element(By.ID, "node_level-2-2").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "w2ui-grid-data")))
    sleep(operateTimeInterval)
    scholarship_history = get_data((main3.find_elements(By.CLASS_NAME, "w2ui-odd") + main3.find_elements(By.CLASS_NAME, "w2ui-even")), "w2ui-grid-data")
    
    try:
        driver.find_element(By.ID, "node_level-1-4").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "w2ui-grid-data")))
        sleep(operateTimeInterval)
        labor_history = get_data(main3.find_elements(By.CLASS_NAME, "w2ui-odd") + main3.find_elements(By.CLASS_NAME, "w2ui-even"), "w2ui-grid-data")
    except:
        pass
    
    ########################################################################
    
    today = str(datetime.date.today()).replace("-","")
    
    
    schedule = schedule()
    
    
    for project in all_projects:
        attendance(project)
    
    
    print("attend done.")

    driver.close()
    
