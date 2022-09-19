import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import sqlalchemy as db
import pandas as pd

################### Enter Server Details and Login Details before hand. ###############################################

class LinkedIn:

    driver = webdriver.Firefox()
    driver2 = webdriver.Firefox()

    # Saving data to database (Enter Server details before using)
    def save(self, data, user_name='', password='', host='', server=''):
        if user_name=='':
            print('Enter Server Details in Function')
            exit(0)
        try:
            # Connecting to server
            CHECKSUM_DB_CONN_STRING=f'postgresql+psycopg2://{user_name}:{password}@{host}/{server}'
            print('connected')
            engine = db.create_engine(CHECKSUM_DB_CONN_STRING)      # Database Engine

            # Making Type1 table of Categories
            file = pd.DataFrame({'Category': self.job_category_list})
            file.to_sql(f'Type1', engine, if_exists='append', index=False)

            # Making tables from final dictionary
            for table in ['Job', 'Company', 'States']:
                file = pd.DataFrame(data[table])
                print(file)
                file.to_sql(f'{table}', engine, if_exists='append', index=False)
        except Exception as e:
            print('save', e)
    
    # Making Dictionary of all data    
    def list_to_dict(self):
        position_list = []
        State_list = []
        Company_list = []
        Description_list = []
        headquaters_list = []
        size_list = []
        for job in self.job_list:
            position_list.append(job[0].strip())
            State_list.append(job[2].strip())
            Company_list.append(job[1].strip())
            Description_list.append(job[3].strip())
            headquaters_list.append(job[4].strip())
            size_list.append(job[5].strip())

        dict_data = {'Job': {'Postion': position_list, 'State': State_list, 'Company': Company_list},
                     'Company': {'Name': Company_list, 'Description': Description_list, 'State': headquaters_list,
                                 'size': size_list},
                     'States':{'State':State_list}}
        self.save(dict_data)

    # Login on LinkedIn (Enter Login Details Before Using)
    def login(self, dri, email='', pwd=''):
        try:
            dri.implicitly_wait(4)

            url = 'https://in.linkedin.com/company/indigo-airlines?trk=public_jobs_topcard-org-name'
            dri.get(url)
            time.sleep(4)

            # SignIn button
            dri.find_element(By.XPATH, '/html/body/div/main/div/form/p/button').click()
            time.sleep(4)

            # Sending email and password
            dri.find_element(By.XPATH, '//*[@id="session_key"]').send_keys(email)
            dri.find_element(By.XPATH, '//*[@id="session_password"]').send_keys(pwd)
            time.sleep(1)

            # Press submit
            dri.find_element(By.XPATH, '/html/body/div/main/div/div/div/form/button').click()
            time.sleep(6)
        except:
            print('logIn skip')

    # Get categories
    def career_guide(self):
        job_url = 'https://www.careerguide.com/career-options'
        re = requests.get(job_url)
        soup = BeautifulSoup(re.content, 'html.parser')

        # List of job category elements
        job_names = soup.findAll('h2', {'class': "c-font-bold"})

        # All job category list
        self.job_category_list = [j.text for j in job_names]

    # Getting Company's Data
    def company_data(self, c_link):

        # Open Company page
        self.driver2.get(c_link)
        time.sleep(2)

        # Looking for pop up
        try:
            self.driver2.find_element(By.XPATH, '/html/body/div[2]/div/div/section/button').click()
            time.sleep(1)
        except:
            time.sleep(1)

        # Clicking about button
        try:
            self.driver2.find_element(By.XPATH,
                                '/html/body/div[5]/div[3]/div/div[2]/div/div[2]/main/div[1]/section/div/div[2]/div[2]/nav/ul/li[2]').click()
            time.sleep(2)
        except:
            time.sleep(1)

        # Description
        try:
            para = self.driver2.find_element(By.CSS_SELECTOR,
                                       'p[class="break-words white-space-pre-wrap mb5 text-body-small t-black--light"]').text.strip()
        except:
            para = ''

        # Headquarter Location
        try:
            headquarter = self.driver2.find_element(By.CSS_SELECTOR, 'div[class="inline-block"]') \
                .find_element(By.CSS_SELECTOR, 'div[class="org-top-card-summary-info-list__info-item"]').text.strip()
        except:
            headquarter = ''

        # Number of employees
        try:
            size = self.driver2.find_element(By.XPATH,
                                       '/html/body/div[5]/div[3]/div/div[2]/div/div[2]/main/div[2]/div/div/div[1]/section/dl/dd[3]').text.strip()
        except:
            size = ''

        # List of company data
        cd_list = [para, headquarter, size]
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

        # Login 2nd driver
        self.login(self.driver2)
        time.sleep(3)

        try:
            # open India job page
            url = 'https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0'
            self.driver.get(url)
            time.sleep(3)

            # Sending search term
            self.driver.find_element(By.XPATH,'/html/body/div[1]/header/nav/section/section[2]/form/section[1]/input').send_keys(search)

            # Click search
            time.sleep(1)
            self.driver.find_element(By.XPATH, '/html/body/div[1]/header/nav/section/section[2]/form/button').click()

            # Loop for job count and search
            time.sleep(2)
            self.job_list = []
            n = 1
            while len(self.job_list) < result_limit:

                # Scroller
                for c in range(0, 7):
                    time.sleep(3)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Scrape the entire page
                result_list = self.driver.find_element(By.CSS_SELECTOR,
                                                       'ul[class="jobs-search__results-list"]').find_elements(By.TAG_NAME, 'li')

                # iterate through jobs
                for job in result_list:
                    if n<=result_limit:

                        # Name
                        try:
                            name = job.find_element(By.CSS_SELECTOR, 'h3[class="base-search-card__title"]').text.strip()
                        except:
                            name = ''

                        # Comany name
                        try:
                            company = job.find_element(By.CSS_SELECTOR, 'h4[class="base-search-card__subtitle"]').text.strip()
                        except:
                            company = ''

                        # Location
                        try:
                            location = job.find_element(By.CSS_SELECTOR, 'span[class="job-search-card__location"]').text.strip()
                        except:
                            location = ''

                        # Company's linkedIn page link
                        try:
                            c_link = job.find_element(By.CSS_SELECTOR, 'h4[class="base-search-card__subtitle"]').find_element(By.TAG_NAME, 'a').get_attribute('href')
                        except:
                            c_link = ''

                        # Making list of all content related to this job
                        content = [name, company, location] + self.company_data(c_link)
                        n += 1

                        # Making list of lists containing job content
                        self.job_list.append(content)
                    else:
                        break

                # Click show more
                try:
                    self.driver.find_element(By.XPATH, '//*[@id="main-content"]/section[2]/button').click()
                    time.sleep(4)
                except Exception as e:
                    print('page button not here')
                    break
                
            # Printing results
            #self.make_me_pretty()
            # converting list to Dictionary
            self.list_to_dict()
        except:
            print('error')

    # Main
    def main(self, n):
        # Getting Job categories
        self.career_guide()
        # Scraping results for each category
        for cat in self.job_category_list:
            print(f'---->{cat}<-----')
            try:
                self.LinkedIn(cat, n)
            except:
                print('Next Category')

        # Closing Drivers
        self.driver.close()
        self.driver2.close()


l = LinkedIn()
l.main(2)          # Change Result Limit here





