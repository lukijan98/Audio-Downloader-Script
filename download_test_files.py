import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time

#requirements:
#selenium : pip install selenium
#requests : pip install requests
#BeautifulSoup : pip install bs4
#Also download the googleChrome driver from the link: https://chromedriver.chromium.org/downloads, the version of chrome you can see in the chrome browser: Help->About Google Chrome
#add chromedriver.exe to path

#Fill in these
path_chromedriver = r"";
path_dataset = r'' # put here where you want to save the data


words = []

#Keep in mind that a word may not have the desired number of recordings
limit_downloads = True  #if set false it will download all recordings for the word
max_downloads_per_word = 2


#fill in with your own data from the site https://forvo.com/
username = ""
password = ""
################################################################################
def splitter(string):
    s = string.split()
    pol = s[0]
    rec = ""
    if len(s) > 3:
        for i in range(2,len(s)):
            rec = rec + s[i] + " " 
    else:
        rec = s[2]    
    return [pol,rec.strip()]

chrome_options = Options()

#prefs = {'profile.default_content_setting_values.automatic_downloads': 1}
#chrome_options.add_experimental_option("prefs", prefs)
path_download = path_dataset +"\download_folder"

if not os.path.exists(path_download):
    os.makedirs(path_download)
chrome_options.add_argument('headless')
chrome_options.add_argument('window-size=1200x600')
chrome_options.add_argument("--silent")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument('--disable-gpu') 
prefs = {"profile.default_content_settings.popups": 0,
             "download.default_directory": 
                        path_download+"\\",
             "directory_upgrade": True,
             'profile.default_content_setting_values.automatic_downloads': 1}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(executable_path=path_chromedriver,chrome_options=chrome_options)

driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': path_download}}
command_result = driver.execute("send_command", params)

print("LOGIN ON: https://forvo.com/login/")
driver.get("https://forvo.com/login/")
print("ENTERING USERNAME")
driver.find_element_by_id("login").send_keys(username)
print("ENTERING PASSWORD")
driver.find_element_by_id("password").send_keys(password)

e = driver.find_element_by_class_name("button")
driver.execute_script("arguments[0].click();", e)



url_words = "https://forvo.com/languages-pronunciations/en/"
print("LOGGED IN")
print("GATHERING WORDS")
page_delimiter = "page-"
driver.get(url_words)
re = requests.get(url_words)
searchsoup = BeautifulSoup(re.text,"html.parser")
c = searchsoup.find_all("a", {"class": "word"})
for k in c:
    if " " not in k.text:
        words.append(k.text)
for i in range(2,21):     #change 21 to a higher value if you want to download from more pages.Check on site whats the limit
    url_tmp = url_words + page_delimiter + str(i)
    driver.get(url_tmp)
    re = requests.get(url_tmp)
    searchsoup = BeautifulSoup(re.text,"html.parser")
    c = searchsoup.find_all("a", {"class": "word"})
    for k in c:
        words.append(k.text)
print("GATHERING FINISHED")
print("DOWNLOADING WORDS")
for r in range(len(words)):

    url_word = words[r].strip().lower().replace(" ", "_")
    url = "https://forvo.com/word/" + url_word + "/"
    driver.get(url)
    title = "Download "+ words[r] + " MP3 pronunciation"
    element = driver.find_elements_by_xpath('//*[@title="Download '+ words[r] +  ' MP3 pronunciation"]')

    
    if not os.path.exists(path_dataset + "\\" + words[r]):
       os.makedirs(path_dataset + "\\" + words[r])

    re = requests.get("https://forvo.com/word/" + words[r])
    searchsoup = BeautifulSoup(re.text,"html.parser")
    c = searchsoup.find_all("span", {"class": "from"})
    
    if limit_downloads:
        number = max_downloads_per_word
    else:
        number = len(c)
        
    for k in range(number):
        
        a = c[k].text.strip("(").strip(")")
        if "Male" not in a and "Female" not in a:
            continue

        driver.execute_script("arguments[0].click();",element[k])
        time.sleep(5)         
        
        file_path = max([path_download + '\\' + f for f in os.listdir(path_download)],key=os.path.getctime)
        file_name = file_path.replace(path_download+"\\","")
        file_name = file_name.replace(".mp3","") + " " + str(k) + ".mp3"
        os.rename(file_path, path_download +"\\"+ file_name)
        
        info = splitter(str(a))
        gender = info[0]
        location = info[1]
        
        if not os.path.exists(path_dataset + "\\" + words[r] + "\\" + gender + "\\" + location):
           os.makedirs(path_dataset + "\\" + words[r] + "\\" + gender + "\\" + location)  
        
        os.replace(path_download  +"\\"+ file_name, path_dataset + "\\" + words[r] + "\\" + gender + "\\" + location + "\\" + file_name)

        print("--->CREATED " + path_dataset + "\\" + words[r] + "\\" + gender + "\\" + location + "\\" + file_name)

os.rmdir(path_download)
print("----->FINISHED<-----")
driver.quit()
