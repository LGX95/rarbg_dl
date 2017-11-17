# rarbg_dl

一个自用的脚本。

通过关键字搜索 rarbg.is 发布的资源，并获取第一个搜索结果的磁力链接，
再打开 Mac 上的 Transmission 添加到下载列表中。
如果没有搜索结果，一段时间后再请求搜索，直到添加下载后退出执行。
如果需要验证浏览器，读取图形验证码，并设置新的Cookies。

测试环境：
* macOS High Sierra
* Python 3.6.3
* Requests 2.18.4
* BeautifulSoup 4.6
* Selenium 3.7
* Pillow 4.2.1
* pytesseract 0.1.7
* Transmission 2.92

个人使用场景：

在美剧更新后，输入关键字进行搜索，如果搜索到内容，获取第一条结果的磁力链接，并打开 Transmission 下载。
如果没更新，保持脚本运行，直到资源发布后添加到下载列表自动退出。
