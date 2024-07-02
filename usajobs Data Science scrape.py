#Code to parse USAJobs.gov for 
import regex as re
import time
from selenium import webdriver
import pandas as pd

#Declare variables, uninterested variables contain different terms in job descriptions that I would not want to do
num_pages = range(1, 100)
uninterested_title = 'cybercrime|Financial|loan|Dispatcher|Dispatch|Maintenance|Laborer|MVO|Motor Vehicle Operator|Firefighter|Deckhand|Civil Engineer|Captain|Boss|Repairer|Counselor|Engine|Drill Rig|Custodial|Masonry|Operator|Carpenter|Mechanic|Teacher|Automotive|Paramedic|Human Resources|Architect|Airtanker|Mason|Social Services|Legal|Security|EMT|Cook|Auditor|Leader|Gardener|Writer|Chief|Archeologist|Lifeguard|Realty|Pest|Administrative|Attorney|Aviation|Budget|Contract|Construction|Enrollment|Manager|Law|Horse|Rigger|Tree Worker|Tree Faller|Fisheries|Animal Packer|Police'
uninterested_location = 'New Mexico|Washington|Washington, District of Columbia|Alabama|Alaska|California|Arizona|Idaho|Nevada|Wyoming|Oregon|Arkansas|Utah|Montana|Colorado|Mississippi|Missouri|Georgia|Florida|Texas'
min_salary = 50000
max_salary = 100000
driver = webdriver.Firefox(executable_path='C:\\Users\\anekl\\AppData\\Local\\Programs\\Python\\geckodriver.exe')
URL_base  = 'https://www.usajobs.gov/Search/Results?jt=Data%20Analyst&hp=public&p='

#metrics and lists to build df at the end
total_count = 0
matching_count = 0
titles, locations, salaries, grades, dates, links = [], [], [], [] ,[], []

for i in num_pages:
    #There are normally around 30 pages so this is to loop through them
    URL = URL_base + str(i)
    driver.get(URL)
    time.sleep(1)
    #a small delay to ensure the webpage fully loads
    list_of_jobs = driver.find_elements_by_class_name('usajobs-search-result--core')
    if list_of_jobs == []:
        #happens if page is empty, we know there's no more jobs to look for
        break
    for index, job in enumerate(list_of_jobs):
        #if there are jobs posted we look through them
        total_count += 1
        title = job.find_elements_by_id('usajobs-search-result-' + str(index))[0].text
        location = job.find_elements_by_class_name('usajobs-search-result--core__location')[0].text
        salary_desc = job.find_elements_by_class_name("usajobs-search-result--core__item")[0].text
        salary = re.search('\$[\d\.\,]+', salary_desc)[0]
        salary_numeric = float(salary[1:].replace(",", ""))
        if location != "Multiple Locations":
            location = location[:round(len(location)/2)].strip()
        if re.search(uninterested_title, title, re.IGNORECASE):
            continue
        elif re.search(uninterested_location, location, re.IGNORECASE):
            continue
        elif salary_numeric > max_salary or salary_numeric < min_salary:
            continue
        else:
            #when it finds a job that I'm interested in, append it to the running lists
            matching_count += 1
            link = job.find_elements_by_id('usajobs-search-result-' + str(index))[0].get_attribute('href')
            grade = re.search('(?<=\()(.*?)(?=\))', salary_desc)[0]
            date = job.find_elements_by_class_name("usajobs-search-result--core__footer")[0].text
            date = re.findall('\d{2}\/\d{2}\/\d{4}', date)[1]
            titles.append(title)
            locations.append(location)
            salaries.append(salary)
            grades.append(grade)
            dates.append(date)
            links.append(link)            

#Create the dataframe to be written
table = pd.DataFrame(list(zip(titles, locations, salaries, grades, dates, links)), columns=['title', 'location', 'salary', 'grade', 'date', 'link'])

#Print summary stats and write the table
print("Total jobs: %d" % total_count)
print("Matches: %d" % matching_count)
sort = table.sort_values('date')
sort.to_csv("Data Science Jobs.csv", index = False, header = False)
driver.close()