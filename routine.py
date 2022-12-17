from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import *
class connexion:
    def clickx(self, s):
        e = self.driver.find_element(By.XPATH, s)
        e.click()

    def connexionprocedure(self, password):
        selectemail = self.driver.find_element(By.XPATH, '//*[@id="pc-login-password"]')
        selectemail.click()
        selectemail.send_keys(password)
        self.clickx('//*[@id="pc-login-btn"]') #connect
        self.clickx('/html/body/div[1]/div[1]/div/div[1]/ul/li[3]/span[2]') #avancé
        # loginmode = self.driver.find_element(By.CLASS_NAME, 'login-switch-btn')
        # loginmode.find_element(By.TAG_NAME, 'span').click()

        # selectiframe = self.driver.find_element(By.XPATH, '//*[@id="cloud-login"]')
        # self.driver.switch_to.frame(selectiframe)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="conn_status_internet"]'))) #wait the loading
        interneticon = self.driver.find_element(By.XPATH, '//*[@id="conn_status_internet"]')
        classesicon = interneticon.get_attribute("class").split(' ')[-1]
        while(classesicon != "conn-internet-connected"):
            print(classesicon)
            classesicon = interneticon.get_attribute("class").split(' ')[-1] #tourne tant que la connexion est pas nette

        self.clickx('/html/body/div[1]/div[2]/div[1]/div[1]/div[2]/div/ul/li[4]/a') #sms
        self.clickx('/html/body/div[1]/div[2]/div[1]/div[1]/div[2]/div/ul/li[4]/ul/li[1]/a') #boite de reception
        self.state = False
    def __init__(self, password):
        self.password = password
        self.driver = webdriver.Firefox()
        self.driver.get("http://192.168.1.1")
        self.driver.implicitly_wait(30)
        assert "TL-MR6400" in self.driver.title

        self.connexionprocedure(password)
    def switch(self):
        if(not(self.state)):
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="tableSmsInbox"]'))) #la truc de reception a bien fini de charger ?
            self.clickx('/html/body/div[1]/div[2]/div[1]/div[1]/div[2]/div/ul/li[4]/ul/li[2]/a')
            self.state = not(self.state)
        else:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="inputContent"]'))) #la truc d'envoi a bien fini de charger ?
            self.clickx('/html/body/div[1]/div[2]/div[1]/div[1]/div[2]/div/ul/li[4]/ul/li[1]/a')
            self.state = not(self.state)

    def actualise(self):
        self.clickx('/html/body/div[1]/div[4]/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/label')
    
    def getmessagesDIC(self):
        if(self.state):
            self.switch()
        else:
            self.actualise()
        n_elems = [e.get_attribute('innerHTML') for e in self.driver.find_elements(By.CSS_SELECTOR, "td.table-content:nth-child(3)")]
        m_elems = [e.get_attribute('innerHTML') for e in self.driver.find_elements(By.CSS_SELECTOR, "td.table-content:nth-child(4)")]
        messages = list(map(lambda i,j : (i,j) , n_elems,m_elems)) #dico de list meilleur idée ?
        return messages #pas de gestion des pages, trop peu d'utilisateurs de toute manière

    def get_last(self):
        if(self.state):
            self.switch()
        else:
            self.actualise()
        WebDriverWait(self.driver, 20).until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, "td.table-content")))

        # Failed session handler, induce instablility
        # try :
        #     WebDriverWait(self.driver, 20).until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, "td.table-content")))
        # except Exception as e:
        #     try:
        #         self.driver.refresh()
        #         self.connexionprocedure(self, self.password)
        #     except Exception as e:
        #         print("cannot reconnect")
        number = self.driver.find_elements(By.CSS_SELECTOR, "tr:first-child td.table-content:nth-child(3)")[0].get_attribute('innerHTML')
        mes = self.driver.find_elements(By.CSS_SELECTOR, "tr:first-child td.table-content:nth-child(4)")[0].get_attribute('innerHTML')
        if(mes[-1] == '.' and mes[-2] == '.' and mes[-3] == '.'): #plante pour n<3, check avant stp
            self.clickx('/html/body/div[1]/div[4]/div[2]/div[1]/div[2]/form/table/tbody/tr[1]/td[6]/span[1]')
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, 'msgContent')))
            mes = self.driver.find_element(By.XPATH, '//*[@id="msgContent"]').get_attribute('innerHTML')
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, 'back')))
            self.clickx('//*[@id="back"]')
        return (number,mes)
        
    def send(self, number, text):
        if(not(self.state)):
            self.switch()
        ne = self.driver.find_element(By.XPATH, '//*[@id="toNumber"]')
        me = self.driver.find_element(By.XPATH, '//*[@id="inputContent"]')
        ne.send_keys(number)
        me.send_keys(text)
        self.clickx('//*[@id="send"]')
        WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located((By.ID, 'mask')))

    def listen(self):
        lastmes = self.get_last()
        while(self.get_last() == lastmes):
            pass
        return self.get_last()

c = connexion(password)

while(True):
    m = c.listen()
    c.send(m[0], m[1]+' echo')
