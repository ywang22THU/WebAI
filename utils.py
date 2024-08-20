import json

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {filename}.")
    
def save_to_txt(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(data)
        
def save_to_html(data, filename):
    if type(data) != str:
        data = str(data)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(data)
        
def read_from_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# 最长公共子序列
def LCS(x, y):
    xl = len(x)
    yl = len(y)
    dp = [[0] * (yl + 1) for _ in range(xl + 1)]
    for i in range(1, xl + 1):
        for j in range(1, yl + 1):
            if x[i - 1] == y[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[xl][yl]