from selenium.webdriver.remote.webelement import WebElement, By
# 最长公共子序列
def LCS(x, y):
    """
    最长公共子序列
    """
    xl = len(x)
    yl = len(y)
    dp = [[0] * (yl + 1) for _ in range(xl + 1)]
    for i in range(1, xl + 1):
        for j in range(1, yl + 1):
                dp[i][j] = dp[i - 1][j - 1] + 1 if x[i - 1] == y[j - 1] else max(dp[i - 1][j], dp[i][j - 1])
    return dp[xl][yl]

def get_parents(ele: WebElement) -> list:
    """
    获取一个节点的所有祖先节点
    """
    parents = [ele]
    while True:
        try:
            ele = ele.find_element(By.XPATH, "..")
            parents.append(ele)
        except:
            break
    return parents

# DOM树上两个节点的LCA
def LCA(x: WebElement, y: WebElement):
    """
    DOM树上两个节点的最近公共祖先
    """
    if x == y:
        return x
    x_path = get_parents(x)
    y_path = get_parents(y)
    if len(x_path) > len(y_path):
        x_path, y_path = y_path, x_path # 确保x是更浅的节点
    while len(y_path) > len(x_path):
        y_path.pop(0)
    while x_path[0] != y_path[0]:
        x_path.pop(0)
        y_path.pop(0)
    return x_path[0]
