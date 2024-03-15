# jrecin-job-information-downloader
[![release_build](https://img.shields.io/github/actions/workflow/status/MGMCN/jrecin-job-information-downloader/release.yml?logo=github&label=release
)](https://github.com/MGMCN/jrecin-job-information-downloader/actions)
[![image](https://img.shields.io/github/v/release/MGMCN/jrecin-job-information-downloader?color=purple&label=version)](https://github.com/MGMCN/jrecin-job-information-downloader/releases)
[![image](https://img.shields.io/docker/pulls/godmountain/jrecin-job-information-downloader?logo=docker&logoColor=white)](https://hub.docker.com/r/godmountain/jrecin-job-information-downloader)
[![issue](https://img.shields.io/github/issues/MGMCN/jrecin-job-information-downloader?logo=github)](https://github.com/MGMCN/jrecin-job-information-downloader/issues?logo=github)
[![license](https://img.shields.io/github/license/MGMCN/jrecin-job-information-downloader)](https://github.com/MGMCN/jrecin-job-information-downloader/blob/main/LICENSE)
![last_commit](https://img.shields.io/github/last-commit/MGMCN/jrecin-job-information-downloader?color=red&logo=github)

 Download job postings in bulk from JREC-IN and save them as an Excel file.

 ## Usage
Pull our built image directly.
```bash
$ docker pull godmountain/jrecin-job-information-downloader:latest
$ docker run -d -p 3333:3333 -v your/local/path/directory:/APP/excels godmountain/jrecin-job-information-downloader:latest
```
Then visit http://127.0.0.1:3333 . 
The index.html page of this project is implemented to mimic the search page of [JREC-IN](https://jrecin.jst.go.jp/seek/SeekJorSearch).

## ⚠️ Warnings ⚠️
### This project is for learning purposes only and cannot be used for commercial use!
