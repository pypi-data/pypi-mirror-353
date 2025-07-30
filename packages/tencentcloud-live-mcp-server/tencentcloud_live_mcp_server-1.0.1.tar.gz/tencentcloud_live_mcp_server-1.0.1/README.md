# 腾讯云直播服务
本服务基于Model Context Protocol（MCP）实现提供腾讯云直播API调用Tools的MCP Server，提供腾讯云直播域名管理、拉流转推、直播流管理和流管理等相关接口。
## 简介
本项目主要为大语言模型提供通过自然语言调用腾讯云直播API，管理腾讯云直播服务的能力。
## 依赖环境
- Python 1.12
- 腾讯云API密钥（ [腾讯云控制台申请](https://console.cloud.tencent.com/cam/capi) ）
    - TENCENTCLOUD_SECRET_ID
    - TENCENTCLOUD_SECRET_KEY
- 腾讯云SDK-Python

## 获取安装

### 本地运行Server
``` 
uv run src/server.py
```
### Cursor中使用
目前本项目已经部署在[Vedas](https://ai.woa.com/#/vedas/mcp-market/list) ，可以在平台上创建实例，获取生成的专属url以及token，通过下面的配置使用。

``` 
{
  "mcpServers": {
    "test1_1": {
      "disabled": false,
      "timeout": 60,
      "command": "npx",
      "args": [
        "-y",
        "@tencent/mcprouter"
      ],
      "env": {
        "VEDAS_MCP_URL": "------> 替换成你自己的 url <------",
        "VEDAS_TOKEN": "------> 替换成你自己的 token <------"
      },
      "transportType": "stdio"
    }
  }
}
```
需要注意的是，你需要提前安装好npx工具。

``` 
# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash

# in lieu of restarting the shell
\. "$HOME/.nvm/nvm.sh"

# Download and install Node.js:
nvm install 22

# Verify the Node.js version:
node -v # Should print "v22.14.0".
nvm current # Should print "v22.14.0".

# Verify npm version:
npm -v # Should print "10.9.2".

# 设置腾讯源
npm config set registry https://mirrors.tencent.com/npm/

# 安装npx
sudo npm install -g npx

# 验证npx
npx --version
```
完成后重启Cursor完成配置。
## 功能
- Tools
    - 域名管理
        - 添加域名
        - 删除域名
        - 启用域名
        - 禁用域名
        - 查询域名信息
        - 查询域名列表
    - 拉流转推
        - 删除直播拉流任务
        - 查询直播拉流任务
        - 创建直播拉流任务
        - 更新直播拉流任务
    - 直播流管理
        - 查询流状态
        - 查询直播中的流
    - 流管理
        - 断开直播流
        - 恢复直播流
        - 禁播直播流
        - 查询推断流事件
        - 设置延时直播
        - 取消直播延时
    - 转码模版
        - 创建转码模版
        - 删除转码模版
        - 创建转码规则
        - 删除转码规则

## 使用场景
