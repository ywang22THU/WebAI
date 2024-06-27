# 浏览器交互

经过精简，目前与浏览器操作包括：打开页面、关闭页面、切换页面、输入操作与点击操作，其API规范为：

```json

{
    "type": "str",  // 操作类型
    "url": "str",  // 被操作的URL
    "time": "str", // 进行操作的时间戳
    "path": "list[str]", //从body开始找到标签的路径
    /* 
    每一项为"tag:id"的形式
    具体路径为从body开始，依次find_all(tag)[id]
    */
    "value": "Any", // 用户输入的值
    "urlTarget": "str" // 该操作引出的新url 
}
```


### 打开页面

```json
{
    "type": "tab_open",
    "url": "",
    "time": "2024-06-26 21:18:38", 
    "path": [], 
    "value": "", 
    "urlTarget": "www.google.com"
}
```

### 关闭页面

```json
{
    "type": "tab_close",
    "url": "www.google.com",
    "time": "2024-06-26 21:18:47", 
    "path": [], 
    "value": "", 
    "urlTarget": ""
}
```

### 切换页面

```json
{
    "type": "tab_change",
    "url": "www.google.com", // 从这个页面
    "time": "2024-06-26 21:18:47", 
    "path": [], 
    "value": "",
    "urlTarget": "www.baidu.com" // 切换到这
}
```

### 输入操作

```json
{
    "type": "input",
    "url": "www.google.com",
    "time": "2024-06-26 21:18:55", 
    "path": ["div:0", "div:2", "form:0", "div:0", "div:0", "div:0", "div:0", "div:1", "textarea:0"], 
    "value": "Tsinghua University",
    "urlTarget": ""
}
```

### 点击操作

```json
{
    "type": "input",
    "url": "www.google.com",
    "time": "2024-06-26 21:18:55", 
    "path": ["div:0", "div:2", "form:0", "div:0", "div:0", "div:1", "div:3", "div:5", "center:1", "input:1"], 
    "value": "", 
    "urlTarget": "https://www.google.com/search?q=Tsinghua+University&sca_esv=661b256b13fc34d5&source=hp&ei=R9x8ZpmuO6-7vr0PjsiIwA4&iflsig=AL9hbdgAAAAAZnzqV5j72UzDC6RSQhqvqbzNNsOm5QqL&ved=0ahUKEwjZ7eTB6_qGAxWvna8BHQ4kAugQ4dUDCA0&oq=Tsinghua+University&gs_lp=Egdnd3Mtd2l6IhNUc2luZ2h1YSBVbml2ZXJzaXR5MgUQLhiABDIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgAQyBRAAGIAEMgUQABiABEi3RlCXDVi0NHABeACQAQCYAeABoAHVGqoBBjAuMTguMbgBDMgBAPgBAZgCE6AC_BqoAgDCAgsQLhiABBjRAxjHAZgDAZIHBjAuMTguMaAHt5oB&sclient=gws-wiz"
}
```