import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup


class LinkedIn:

    driver = webdriver.Firefox()
    driver2 = webdriver.Firefox()

    # Login on LinkedIn
    def login(self, dri, email = 'tist1.tist2.tist3@gmail.com', pwd = 'tE5uMchf7MYJdLv'):
        try:
            dri.implicitly_wait(4)

            url = 'https://in.linkedin.com/company/indigo-airlines?trk=public_jobs_topcard-org-name'
            dri.get(url)
            time.sleep(4)

            dri.find_element(By.XPATH, '/html/body/div/main/div/form/p/button').click()
            time.sleep(4)

            dri.find_element(By.XPATH, '//*[@id="session_key"]').send_keys(email)
            dri.find_element(By.XPATH, '//*[@id="session_password"]').send_keys(pwd)
            time.sleep(1)
            dri.find_element(By.XPATH, '/html/body/div/main/div/div/div/form/button').click()
            time.sleep(6)
            print('login SUCESSFUL')
        except:
            print('logIn skip')

    # Get categories
    def career_guide(self):
        job_url = 'https://www.careerguide.com/career-options'
        re = requests.get(job_url)
        soup = BeautifulSoup(re.content, 'html.parser')
        job_names = soup.findAll('h2', {'class': "c-font-bold"})
        self.job_category_list = [j.text for j in job_names]

    # Getting Company's Data
    def company_data(self, c_link):
        self.driver2.get(c_link)
        time.sleep(2)

        try:
            self.driver2.find_element(By.XPATH, '/html/body/div[2]/div/div/section/button').click()
            time.sleep(1)
        except:
            time.sleep(1)


        try:
            self.driver2.find_element(By.XPATH,
                                '/html/body/div[5]/div[3]/div/div[2]/div/div[2]/main/div[1]/section/div/div[2]/div[2]/nav/ul/li[2]').click()
            time.sleep(2)
        except:
            time.sleep(1)

        try:
            para = self.driver2.find_element(By.CSS_SELECTOR,
                                       'p[class="break-words white-space-pre-wrap mb5 text-body-small t-black--light"]').text.strip()
        except:
            para = ''

        try:
            headquater = self.driver2.find_element(By.CSS_SELECTOR, 'div[class="inline-block"]') \
                .find_element(By.CSS_SELECTOR, 'div[class="org-top-card-summary-info-list__info-item"]').text.strip()
        except:
            headquater = ''

        try:
            size = self.driver2.find_element(By.XPATH,
                                       '/html/body/div[5]/div[3]/div/div[2]/div/div[2]/main/div[2]/div/div/div[1]/section/dl/dd[3]').text.strip()
        except:
            size = ''

        cd_list = [para, headquater, size]
        return cd_list

    # Preaenting scraped data
    def make_me_pretty(self):
        for job in self.job_list:
            print(f'''
                    Position: {job[0].strip()}
                    Company: {job[1].strip()}
                    location: {job[2].strip()}
                    
                Company Details:-
                    Description:{job[3].strip()}
                    headquater: {job[4].strip()}
                    size: {job[5].strip()}


''')

    # LinkedIn Scraper
    def LinkedIn(self,search,result_limit):
        self.login(self.driver2)
        #self.login(self.driver)
        time.sleep(3)

        try:
            url = 'https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0'
            self.driver.get(url)
            time.sleep(3)

            self.driver.find_element(By.XPATH,'/html/body/div[1]/header/nav/section/section[2]/form/section[1]/input').send_keys(search)

            time.sleep(2)
            self.driver.find_element(By.XPATH, '/html/body/div[1]/header/nav/section/section[2]/form/button').click()

            time.sleep(2)
            self.job_list = []
            n = 1
            while len(self.job_list) < result_limit:
                for c in range(0, 7):
                    time.sleep(3)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                result_list = self.driver.find_element(By.CSS_SELECTOR,
                                                       'ul[class="jobs-search__results-list"]').find_elements(By.TAG_NAME, 'li')

                for job in result_list:
                    if n<=result_limit:
                        try:
                            name = job.find_element(By.CSS_SELECTOR, 'h3[class="base-search-card__title"]').text.strip()
                        except:
                            name = ''

                        try:
                            company = job.find_element(By.CSS_SELECTOR, 'h4[class="base-search-card__subtitle"]').text.strip()
                        except:
                            company = ''

                        try:
                            location = job.find_element(By.CSS_SELECTOR, 'span[class="job-search-card__location"]').text.strip()
                        except:
                            location = ''

                        try:
                            c_link = job.find_element(By.CSS_SELECTOR, 'h4[class="base-search-card__subtitle"]').find_element(By.TAG_NAME, 'a').get_attribute('href')
                        except:
                            c_link = ''
                        content = [name, company, location] + self.company_data(c_link)
                        n += 1

                        self.job_list.append(content)
                    else:
                        break

                try:
                    self.driver.find_element(By.XPATH, '//*[@id="main-content"]/section[2]/button').click()
                    time.sleep(4)
                except Exception as e:
                    print('page button not here')
                    break

            self.make_me_pretty()
        except:
            print('error')

    # Main
    def main(self,n):
        self.career_guide()
        for cat in self.job_category_list:
            print(f'---->{cat}<-----')
            try:
                self.LinkedIn(cat, n)
            except:
                print('Next Category')

        self.driver.close()
        self.driver2.close()


l = LinkedIn()
l.main(2)





