# XAU Quant

XAU Quant 是面向黄金交易者的 MT5 自动交易 EA 与 XAUUSD 策略资料站，主站地址为 <https://03xau.com>。

本仓库主要托管 03xau.com 的静态页面、多语言入口、免费 EA 下载页、安装教程、回测截图页、策略说明文档和搜索引擎抓取配置。网站内容用于说明 MT5 Expert Advisor 的功能、安装方式、回测材料、风险边界和开发者联系方式。

## 主要入口

- 官网首页：<https://03xau.com/>
- 免费 EA 下载：<https://03xau.com/free-ea.html>
- EA 安装教程：<https://03xau.com/ea-install.html>
- 回测与面板截图：<https://03xau.com/huice.html>
- AI/LLM 摘要入口：<https://03xau.com/llms.txt>

## 内容范围

- MT5 `.ex5` EA 下载入口与 GitHub Release 链接。
- XAUUSD / 黄金后缀品种的 M1 策略说明。
- 安装、回测、模拟盘验证和风险提示。
- 多语言页面：简体中文、繁体中文、英文、日文、韩文、德文、法文。
- `robots.txt`、`sitemap.xml`、canonical、hreflang、Open Graph、Twitter Card 和 JSON-LD 结构化数据。

## 免费 EA 说明

免费 EA 页面提供多个编译版 MT5 Expert Advisor 文件。每个 EA 应先在 Strategy Tester 和模拟账户验证，再考虑实盘环境。不同 Broker 的黄金报价后缀、点差、滑点、合约规格和交易时段可能导致实际结果与回测不同。

## 风险声明

自动交易不保证盈利。网格、马丁、定时间隔加仓和高频短周期策略可能快速放大持仓、保证金占用和账户回撤。历史回测、截图和下载量只用于参考，不构成投资建议、收益承诺或代客交易服务。

## 联系方式

- 微信：thRO03
- Telegram：aws2333
- 官网：<https://03xau.com>

## 维护提示

- 修改页面后同步检查 `sitemap.xml` 的 `lastmod`。
- 新增语言页面时同步维护 canonical、hreflang 和语言切换器。
- 新增下载项时保持页面卡片、说明弹窗、风险提示和 Release 资产名称一致。
- 新增 EA 说明时优先提供功能、关键参数、入场、出场、回测条件和风险说明。
