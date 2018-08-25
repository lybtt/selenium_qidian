
1. selenium 自带的解析比较慢， 可以导入scrapy.selector 下的 Selector 来解析

```py
t_selector = Selector(text=browser.page_source)
```

2. 滑到最下面

```
browser.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage")
```