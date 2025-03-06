# **Lens Faucet 领取脚本**
**更多脚本分享, 关注我的[X](https://x.com/0Xiaofan22921)**

## **功能说明**
该 Python 脚本用于自动领取 Lens 测试网的代币，主要功能包括：

1. **获取迷宫挑战**：从 `https://testnet.lenscan.io/api/trpc/faucet.getMaze` 获取挑战数据。
2. **解决迷宫挑战**：通过 BFS（广度优先搜索）算法找到最短路径。
3. **解决验证码**：使用 [`2Captcha`](https://2captcha.com/?from=22932323) API 自动处理 Turnstile 验证码。
4. **提交领取请求**：向 `https://testnet.lenscan.io/api/trpc/faucet.claim` 发送领取请求。
5. **支持代理**：可以使用 `socks5` 或 `http` 代理进行请求。

---
## **环境依赖**
请确保你的 Python 运行环境已经安装以下依赖库：

```bash
pip install requests twocaptcha
```

---
## **配置文件（config.json）格式**
在脚本目录下创建 `config.json`，内容示例如下：

```json
{
    "2_captcha_token": "your_2captcha_api_key",
    "wallets": [
        {
            "address": "0xYourWalletAddress1",
            "proxy": "socks5h://127.0.0.1:1080"
        },
        {
            "address": "0xYourWalletAddress2",
            "proxy": "http://127.0.0.1:8080"
        }
    ]
}
```

### **配置项说明**
- `2_captcha_token`：你的 [`2Captcha`](https://2captcha.com/?from=22932323) API 密钥。
- `wallets`：钱包地址列表，每个对象包含：
    - `address`：你的钱包地址。
    - `proxy`（可选）：代理地址（支持 `socks5h` 或 `http`）。

---
## **运行方式**
### **方式 1：运行所有钱包**
```bash
python main.py
```

### **方式 2：运行指定索引的钱包**
```bash
python main.py 0  # 领取 wallets[0] 的 Faucet 代币
python main.py 1  # 领取 wallets[1] 的 Faucet 代币
```

---
## **脚本执行逻辑**
### **1. 获取迷宫挑战**
```python
challenge_data = get_challenge()
walls_data = challenge_data["walls"]
start_position = (0, 0)
goal_position = (challenge_data["goalPos"]["row"], challenge_data["goalPos"]["col"])
sessionId = challenge_data["sessionId"]
```
从 API 获取迷宫数据，并解析 `walls`（墙壁位置）和 `goalPos`（终点位置）。

### **2. 解决迷宫挑战**
```python
path = solve_maze(walls_data, start_position, goal_position)
```
使用 BFS 算法找到从 `(0,0)` 到 `goalPos` 的路径。

### **3. 解决验证码**
```python
captcha_data = solve_captcha()
cfToken = captcha_data["code"]
```
调用 `2Captcha` API 解决 Turnstile 验证码，获取 `cfToken`。

### **4. 提交 Faucet 领取请求**
```python
claim_token(address, cfToken, sessionId, path, proxy)
```
发送 `POST` 请求到 `faucet.claim` 接口，成功后返回交易哈希。

---
## **常见问题**
### **1. 代理无法连接？**
- 确保代理服务器运行正常。
- 使用 `http` 代理时，请检查是否支持 `HTTPS`。
- 使用 `socks5h` 时，确保 `proxychains` 等工具配置正确。

### **2. 领取失败？**
- 确保 `2Captcha` API 余额充足。
- 检查 `config.json` 中 `wallets` 配置是否正确。

### **3. 迷宫无法解出？**
- 可能是 `walls_data` 解析错误，可 `print(walls_data)` 进行调试。
- 检查 `solve_maze` 逻辑是否符合 API 返回的数据格式。

---
## **参考资料**
- [Lenscan Faucet API](https://testnet.lenscan.io/)
- [2Captcha 官方文档](https://2captcha.com/)

