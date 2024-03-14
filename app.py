import json
import time
import pandas as pd
import re

from flask import Flask, request, Response, render_template, stream_with_context

from crawler import Crawler


class App:
    def __init__(self):
        self.app = Flask(__name__)
        self.set_app_routes()
        self.tasks = {}
        self.path = "./excels/"

    def set_app_routes(self):
        def save_data_to_excel(task_id):
            df = pd.DataFrame(self.tasks[task_id]['job_descriptions'])

            invalid_chars = r'\/:*?"<>|'
            filename = f'jobs_{task_id}.xlsx'
            cleaned_filename = re.sub(f"[{re.escape(invalid_chars)}]", '_', filename)

            df.to_excel(self.path + cleaned_filename, index=False, engine='openpyxl')

        def generate_download_stream(task_id):
            print(f"Starting download for task ID: {task_id}")
            crawler = Crawler(self.tasks[task_id]['url'])

            success, message, html = crawler.do_request(crawler.get_search_request_url(None))
            if success:
                search_page_urls = crawler.parse_item_count_and_generate_search_page_url(html)

                detail_page_urls = []
                for search_url in search_page_urls:
                    success, message, html = crawler.do_request(search_url)
                    if success:
                        detail_page_urls.extend(crawler.parse_search_page_and_generte_item_detail_page_url(html))

                if len(detail_page_urls) != 0:
                    progress_bar_increment = 100 / len(detail_page_urls)

                    data = {'message': "init_done"}  # Not graceful
                    js_data = json.dumps(data)
                    yield f"data: {js_data}\n\n"

                    for detail_page_url in detail_page_urls:
                        data = {'message': "", 'increment': progress_bar_increment}

                        if "jrecin" in detail_page_url:
                            success, message, html = crawler.do_request(detail_page_url)
                            if success:
                                job_description = crawler.parse_detail_page_and_generate_job_description_item(html)
                                job_description['url'] = detail_page_url
                                self.tasks[task_id]['job_descriptions'].append(job_description)
                                data['message'] = f"Crawled {detail_page_url}"
                            else:
                                data['message'] = f"{message}"
                        else:
                            job_description = crawler.parse_detail_page_and_generate_job_description_item(html, False)
                            job_description['url'] = detail_page_url
                            self.tasks[task_id]['job_descriptions'].append(job_description)
                            data['message'] = f"Pages not from jrec cannot be parsed {detail_page_url}"

                        js_data = json.dumps(data)
                        yield f"data: {js_data}\n\n"

                    save_data_to_excel(task_id)
                else:
                    data = {'message': "no_matching", "alert_message": "No matching jobs found!"}  # Not graceful
                    js_data = json.dumps(data)
                    yield f"data: {js_data}\n\n"

            data = {'message': "done"}  # Not graceful
            js_data = json.dumps(data)
            self.tasks.pop(task_id, None)
            yield f"data: {js_data}\n\n"

        @self.app.route("/", methods=["GET"])
        def fake_it():
            return render_template("html/index.html")

        @self.app.route("/download", methods=["GET"])
        def download():
            task_id = hash(request.url.__str__() + time.time().__str__()).__str__()
            self.tasks[task_id] = {'url': request.url.__str__()}
            self.tasks[task_id]['job_descriptions'] = []
            return render_template('html/download.html', task_id=task_id)

        @self.app.route('/start_download')
        def start_download():
            task_id = request.args.get('task_id', None)
            return Response(stream_with_context(generate_download_stream(task_id)), content_type='text/event-stream')

    def run(self):
        self.app.run(host='0.0.0.0', port=3333)
