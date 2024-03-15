from urllib.parse import urlparse, parse_qs, urlencode
import requests
from bs4 import BeautifulSoup


class Crawler:
    home_base_url = "https://jrecin.jst.go.jp"
    search_base_url = "https://jrecin.jst.go.jp/seek/SeekJorSearch?"

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
        'Connection': 'keep-alive',
        'Referer': 'https://jrecin.jst.go.jp',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    def __init__(self, url):
        self.original_url = url

    def get_search_request_url(self, url):
        parsed_url = urlparse(url if url else self.original_url)
        query_params = parse_qs(parsed_url.query)
        query_string = urlencode(query_params, doseq=True)
        return Crawler.search_base_url + query_string

    def do_request(self, url) -> (bool, str, str):
        response = requests.get(url, headers=Crawler.headers, timeout=20)

        success = True
        message = "Request {url} succeeded"

        if response.status_code != 200:
            success = False
            message = f'Request {url} failed，status_code：{response.status_code}'

        return success, message, response.text

    def parse_item_count_and_generate_search_page_url(self, html) -> list:
        soup = BeautifulSoup(html, 'html.parser')  # 'lxml'
        item_count = soup.find('span', class_="em_text me-2")
        count = int(item_count.text) if item_count else 0
        if count % 50 != 0:
            pages = int((count / 50) + 1)
        else:
            pages = int(count / 50)

        search_page_urls = [
            self.get_search_request_url(f'{self.original_url}&page={page + 1}&dispcount=50') for page in
            range(pages)]

        # for url in search_page_urls:
        #     print(url)
        return search_page_urls

    def parse_search_page_and_generte_item_detail_page_url(self, html) -> list:
        soup = BeautifulSoup(html, 'html.parser')
        a_tags = soup.find_all('a', class_='btn dtl_btn text-center mb-2')
        detail_page_urls = [f"{Crawler.home_base_url}{tag.get('href')}" for tag in a_tags]

        button_tags = soup.find_all('button', class_='btn dtl_btn text-center mb-2')
        outside_detail_page_urls = [tag.get('data-url') for tag in button_tags]

        # print(len(detail_page_urls), detail_page_urls)
        # print(len(outside_detail_page_urls), outside_detail_page_urls)

        detail_page_urls.extend(outside_detail_page_urls)
        return detail_page_urls

    def parse_detail_page_and_generate_job_description_item(self, html, flag=True) -> dict:

        item = {
            "university": None,
            "location": None,
            "research_field": None,
            "start_date": None,
            "end_date": None,
            "job_type": None,
            "salary": None,
            "qualification": None,
            "job_description": None,
            "work_time": None
        }

        if flag:
            soup = BeautifulSoup(html, 'html.parser')

            def clean_text(element):
                if element:
                    return element.get_text(strip=True).replace("\n", "").replace("\t", "")
                return ""

            university = clean_text(soup.find('p', class_='me-md-3'))
            location = clean_text(soup.find('p', string=lambda x: x and '勤務地' in x))
            research_field = clean_text(soup.find('p', string=lambda x: x and '研究分野' in x))
            start_date = clean_text(soup.find('p', string=lambda x: x and '公開開始日' in x))
            end_date = clean_text(soup.find('p', string=lambda x: x and '募集終了日' in x))

            salary = ""
            salaries = soup.find('p', string='給与')
            if salaries:
                salary_list = salaries.find_next_sibling('ul')
                if salary_list:
                    salary_details = salary_list.find_all('li')
                    salary = ''.join([clean_text(salary_detail) for salary_detail in salary_details])

            job_type = ""
            job_types = soup.find('p', string='職種')
            if job_types:
                job_type_list = job_types.find_next_sibling('ul')
                if job_type_list:
                    job_types = job_type_list.find_all('li')
                    job_type = ''.join([clean_text(type) for type in job_types])

            qualification = ""
            education_requirements = soup.find_all(string="応募に必要な学歴・学位")
            for item in education_requirements:
                parent = item.find_parent('li')
                if parent:
                    qualification += clean_text(parent)

            experience_requirements = soup.find_all(string="業務における経験")
            for item in experience_requirements:
                parent = item.find_parent('li')
                if parent:
                    qualification += clean_text(parent)

            job_descriptions = soup.find("div", class_="card_item border-0")
            job_description = ""
            if job_descriptions:
                texts = job_descriptions.find_all(string=True)
                job_description += "\n".join([text.strip() for text in texts if text.strip() != ""])

            work_times = soup.find("div", class_="card_item border-bottom border-secondary")
            work_time = ""
            if work_times:
                texts = work_times.find_all(string=True)
                work_time += "\n".join([text.strip() for text in texts if text.strip() != ""])

            # print(f'University: {university}')
            # print(f'Location: {location}')
            # print(f'Research Field: {research_field}')
            # print(f'Start Date: {start_date}')
            # print(f'End Date: {end_date}')
            # print(f'Job Type: {job_type}')
            # print(f'Salary: {salary}')
            # print(f'Qualification: {qualification}')
            # print(f'Job_description: {job_description}')
            # print(f'Work_time: {work_time}')

            item = {
                "university": university,
                "location": location,
                "research_field": research_field,
                "start_date": start_date,
                "end_date": end_date,
                "job_type": job_type,
                "salary": salary,
                "qualification": qualification,
                "job_description": job_description,
                "work_time": work_time
            }

        return item


# only for test
if __name__ == '__main__':
    page = 1
    dispcount = 50
    c = Crawler("http://127.0.0.1:3333/download?keyword_and=&keyword_or=&keyword_not=&_bgCode=1&bgCode=00289&_smCode"
                "=1&_orgtype=1&_area=1&_prefecture=1&_jobkind=1&jobkind=00011&jobkind=00022&jobkind=00014&jobkind"
                "=00016&jobkind=00018&jobkind=00020&jobkind=00024&jobkind=00026&jobkind=00028&jobkind=00030&jobkind"
                "=00033&employmentform=01&_employmentform=on&employmentform=02&_employmentform=on&_employmentform=on"
                "&_employmentform=on&_employmentform=on&_employmentform=on&_jobterm=on&_jobterm=on&_jobterm=on"
                "&_jobterm=on&wageValue=&_consideration=on&_consideration=on&_consideration=on&_entry=on&_entry=on"
                "&_entry=on&_duration=on&_duration=on&_duration=on&sort=0&fn=0")
    success, message, html = c.do_request(c.get_search_request_url(None))
    search_page_urls = c.parse_item_count_and_generate_search_page_url(html)

    detail_page_urls = []
    for search_url in search_page_urls:
        success, message, html = c.do_request(search_url)
        detail_page_urls.extend(c.parse_search_page_and_generte_item_detail_page_url(html))

    print(len(detail_page_urls))

    print(detail_page_urls[1])
    success, message, html = c.do_request(detail_page_urls[1])
    print(c.parse_detail_page_and_generate_job_description_item(html))
    print(c.parse_detail_page_and_generate_job_description_item(html, False))
