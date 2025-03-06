import json
import sys
import urllib.parse

import requests
from collections import deque
from twocaptcha import TwoCaptcha


# 读取 config.json 文件
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,zh;q=0.8,zh-HK;q=0.7,zh-CN;q=0.6,zh-TW;q=0.5",
    "content-type": "application/json",
    "dnt": "1",
    "priority": "u=1, i",
    "referer": "https://testnet.lenscan.io/faucet",
    "sec-ch-ua": "\"Chromium\";v=\"133\", \"Not(A:Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "trpc-accept": "application/jsonl",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "x-trpc-source": "nextjs-react"
}


def solve_maze(walls, start, goal):
    rows, cols = len(walls), len(walls[0])

    # 定义墙壁的位掩码（1=上，2=右，4=下，8=左）
    DIRECTIONS = {
        "up": (-1, 0, 1),  # 上 (row-1, col) 受 1 影响
        "right": (0, 1, 2),  # 右 (row, col+1) 受 2 影响
        "down": (1, 0, 4),  # 下 (row+1, col) 受 4 影响
        "left": (0, -1, 8)  # 左 (row, col-1) 受 8 影响
    }

    queue = deque([(start, [])])
    visited = set([start])

    while queue:
        (r, c), current_path = queue.popleft()

        if (r, c) == goal:
            return current_path  # 找到路径

        for direction, (dr, dc, mask) in DIRECTIONS.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                if not (walls[r][c] & mask):  # 确保没有墙挡住
                    queue.append(((nr, nc), current_path + [direction]))
                    visited.add((nr, nc))

    return None  # 无解


def get_challenge(cf_token, page_token):
    data = {
        "0": {
            "json": {
                "difficulty": "hard",
                "cfToken": cf_token,
                "pageToken": page_token
            }
        }
    }
    json_str = json.dumps(data)  # 转换为 JSON 字符串
    encoded_json = urllib.parse.quote(json_str)  # URL 编码

    url = f"https://testnet.lenscan.io/api/trpc/faucet.getMaze?batch=1&input={encoded_json}"

    response = requests.get(url, headers=headers)
    print(response.text)
    last_line = response.text.strip().split("\n")[-1]

    last_json = json.loads(last_line)
    return last_json["json"][2][0][0]


def solve_captcha():
    api_key = config["2_captcha_token"]

    solver = TwoCaptcha(api_key)

    try:
        result = solver.turnstile(
            sitekey='0x4AAAAAAA1z6BHznYZc0TNL',
            url='https://testnet.lenscan.io/'
        )
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    else:
        return result


def claim_token(address, cf_token, session_id, path, proxy):
    url = "https://testnet.lenscan.io/api/trpc/faucet.claim?batch=1"
    data = {
        "0": {
            "json": {
                "address": address,
                "cfToken": cf_token,
                "gameChallenge": {
                    "sessionId": session_id,
                    "moves": path
                }
            }
        }
    }
    proxies = {
        "http": proxy,
        "https": proxy
    }

    if proxy:
        response = requests.post(url, data=json.dumps(data), headers=headers, proxies=proxies)
    else:
        response = requests.post(url, data=json.dumps(data), headers=headers)
    response_lines = response.text.strip().split("\n")
    line_nums = len(response_lines)
    if line_nums == 4:
        last_line_json = json.loads(response_lines[-1])
        print(f'Claim Grass Token Successfully for {address}, tx hash:{last_line_json["json"][2][0][0]["hash"]}')
    else:
        print(f"Claim failed: {response_lines[-1]}")

captcha_data = solve_captcha()
cf_token = captcha_data["code"]

#todo: ⚠️official faucet api is down with hint: Invalid page token. Waiting official faucet update
page_token = "1741241920913.cd87bd4e05252f2bbd44356afe06c6ef.5c57397631c65911fc7d155e3b18191bfd83602770e16cba5d3bc27de439d961"
# 迷宫墙壁数据
challenge_data = get_challenge(cf_token, page_token)
walls_data = challenge_data["walls"]

# 起点和终点
start_position = (0, 0)
goal_position = (challenge_data["goalPos"]["row"], challenge_data["goalPos"]["col"])
session_id = challenge_data["sessionId"]

# 计算路径
path = solve_maze(walls_data, start_position, goal_position)

accounts = config["wallets"]

if (len(sys.argv) > 1):
    index = int(sys.argv[1])
    account = accounts[index]
    address = account["address"]
    proxy = account["proxy"]
    claim_token(address, cf_token, session_id, path, proxy)
else:
    for account in accounts:
        address = account["address"]
        proxy = account["proxy"]
        claim_token(address, cf_token, session_id, path, proxy)
