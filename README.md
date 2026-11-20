# NezhaBeautify v1 —— KomariBeautify 的 Nezha v1 改编版

把 [KomariBeautify](https://github.com/EmersonLopez2005/KomariBeautify)（Komari v1.1.3 + PurCarte v1.2.5）的 5 个功能，重做到 **Nezha v1** 上。
原版是单文件自定义代码，本项目同样保持**单文件**（`NezhaBeautify.html`），直接粘贴进 Nezha 后台的自定义代码即可用。

> **适配目标：nezhahq/nezha v1.x，实测对照版本 v1.14.14（v1 线最新版）。**
> 注意：nezhahq/nezha 的 main 分支现在是 **v2.x**（v2.7.0），与 v1 的 API/前端结构不同。
> 本项目只针对 v1.x；如果你用的是 v2，请勿直接使用（见“已知限制”）。

## 功能

| # | 功能 | 说明 |
|---|------|------|
| 1 | 欢迎气泡 | 左下角弹出：位置（城市/地区/国家）、OS、浏览器、IP（点击剧透隐藏）、ISP、日期。IP 数据三源故障转移：api.ip.sb → ipwho.is → api.ipapi.is。站名从 `/api/v1/setting` 的 `site_name` 取。 |
| 2 | 资产统计 | 右上角悬浮球，点击展开：服务器总数、总价值、月均支出、剩余总价值、逐台明细。货币 CNY/USD/HKD/EUR/GBP/JPY，汇率走 exchangerate-api.com（失败用默认汇率）。排序默认按 Nezha 的 `display_index`，也可按价格排序；可排除“白嫖中”。 |
| 3 | 地球仪 | 右上角第二个悬浮球，点击打开全屏 3D 地球（Globe.GL）：按国家代码标国旗、画到访客位置的弧线、点击国旗看该国服务器列表；浅/暗色自动切换日间/夜间纹理。 |
| 4 | 保护 | 仅**未登录游客**触发：拦截右键/复制/拖拽/打印/F12/Ctrl+Shift+I 等、检测无头浏览器/开发者工具/可疑扩展/DOM 注入，触发后弹警告，3 秒后跳转（原版行为）。开关见 `CONFIG.protection`。 |
| 5 | 自定义警告弹窗 | 保护组件的弹窗，模糊背景 + 动画。 |

## 安装（Nezha v1）

1. 登录 Nezha v1 后台（`/dashboard/`）→ **设置** → 找到**自定义代码**（`custom_code`，用户前台用）。
2. 把 `NezhaBeautify.html` 的**全部内容**复制粘贴进去，保存。
3. 刷新用户前台首页即可看到欢迎气泡和右上角两个悬浮球。
4. （可选）按下面“配置”填价格表，否则资产统计会显示“未配置”。

> 注入机制：官方用户前端（nezha-dash-v2）在加载 `/api/v1/setting` 后，用
> `InjectContext(custom_code)` 按文档顺序注入这段 HTML：
> `<style>`/`<link>` 进 `<head>`，`<script>`（含外链 Globe.GL）按序执行，
> 其它节点进 `<body>`。所以本文件必须是“样式 + 节点 + 脚本”一体的单文件。

## 配置（只改文件顶部 `CONFIG`）

```js
var NezhaBeautifyConfig = {
  settingApi: '/api/v1/setting',
  wsServerUrl: '/api/v1/ws/server',
  serverApi: '/api/v1/server',      // 仅登录后可用，WS 失败时的备用
  profileApi: '/api/v1/profile',    // 登录状态检查
  siteNameFallback: 'Nezha',
  protection: { enabled: true, guestsOnly: true, redirectDelayMs: 3000, pollMs: 500 },
  globe: {
    cdnDay / cdnNight / cdnSky / cdnTopology: '…',  // 地球纹理 CDN
    localDay / localNight / localSky: '',           // 填自己的图床 URL 可覆盖 CDN
    flagUrl: code => 'https://flagcdn.com/w40/' + code.toLowerCase() + '.png',
  },
  finance: {
    defaultCurrency: 'CNY',
    excludeFreeDefault: true,   // 默认排除“白嫖中”
    freeTag: '白嫖中',
    longTermYears: 100,
    prices: { /* 见下 */ },
  },
};
```

也可以在页面里先定义 `window.NezhaBeautifyConfig` 再加载本文件，会与默认配置合并。

### 资产统计的价格从哪来（必读）

**Nezha v1 的 Server 模型没有 `price / billing_cycle / expired_at / tags / weight / currency` 字段**，
所以价格必须另行提供，二选一（优先级：价格表 > 公开备注）：

**方式 A：在 `CONFIG.finance.prices` 里按服务器名填：**

```js
prices: {
  'HK-小鸡': { price: 100, currency: 'CNY', cycleDays: 365, expireAt: '2027-01-01' },
  'JP-免费': { price: -1 },   // price = -1 表示免费鸡，按 0 计
}
```

字段：`price`（必填，数字；`-1` = 免费）、`currency`（CNY/USD/HKD/EUR/GBP/JPY 或 ￥/$/HK$/€/£，默认 CNY）、
`cycleDays`（计费周期天数，30=月付、365=年付，默认 30）、`expireAt`（到期日 `YYYY-MM-DD`，不填则剩余价值按 0 计）、
`free: true`（等同于“白嫖中”，受排除开关控制）。

**方式 B：在 Nezha 后台给服务器写公开备注（`public_note`），格式：**

```
price:100CNY/365d;expire:2027-01-01
price:5USD/30d;expire:2026-06-01;白嫖中
```

注意：公开备注是**公开可见**的，写价格等于把价格公开给所有访客；不想公开就用方式 A。
另外 WS 首包才带 `public_note`，本代码会缓存首包备注，后续包为空时不覆盖。

**剩余价值算法（与原版一致）：** 到期 > 100 年视为长期，按原价计；否则按
`价格 ×（剩余天数 / 计费周期天数）`；无到期日则剩余价值为 0。
未配置价格的服务器在明细里显示“未配置”，不计入总额，数量会标注在“服务器数量”后。

## Komari → Nezha v1 映射表

| 原版（Komari + PurCarte） | Nezha v1 改编 | 备注 |
|---|---|---|
| `GET /api/nodes`（公开）取服务器 | `WS /api/v1/ws/server`（公开，除非开 ForceAuth）+ `GET /api/v1/server` 备用（仅登录） | v1 的服务器列表 REST 接口不对游客开放；公开数据走 WS，每 2 秒一包 |
| 节点字段 `name / price / currency / billing_cycle / expired_at / tags / weight` | `StreamServer`：`{id, name, public_note（仅首包）, display_index, host, state, country_code, last_active}` | **无价格/周期/到期/标签/权重字段**，见上节 |
| 排序 `weight` 正序/倒序 | 排序 `display_index`（越大越靠前，Nezha 原生）+ 价格正序/倒序 | |
| 标签 `白嫖中`（tags） | 价格表 `free: true` 或公开备注含“白嫖中” | Nezha 无 tags |
| `GET /api/me` → `logged_in` 判断登录 | `GET /api/v1/profile`：200 + `success:true` = 已登录 | Komari 的 `/api/me` 在 Nezha 不存在 |
| 自定义代码放 Komari 设置 → 自定义头部/Body | Nezha 后台 → 设置 → 自定义代码（`custom_code`） | 见“安装” |
| `MutationObserver` 监视 `.radix-themes`，节点挂到该容器下 | 监视 `#root`，节点直接挂到 `document.body` | Nezha 前端无 `.radix-themes`；根节点是 `<div id="root">`（React 18） |
| 样式变量 `--accent-9 / --purcarte-card-color / --gray-a5` 等 | 映射到 Nezha 的 Tailwind/shadcn 变量 `--background / --card / --foreground / --primary / --muted-foreground / --border / --destructive`（HSL 三元组），并自带回退值 | 详见下节 |
| 主题检测 `localStorage.appearance` | `html.dark` class + `localStorage "vite-ui-theme"`（light/dark/system）+ `prefers-color-scheme` 回退 | |
| 地球国旗 `/assets/flags/{CODE}.svg`（Komari 自带） | `flagcdn.com/w40/{code}.png`（`CONFIG.globe.flagUrl` 可改），加载失败自动隐藏 | Nezha 前端不提供该路径 |
| 地球纹理 unpkg three-globe CDN | 同上 CDN 默认；本项目 `images/` 有本地副本，可自托管覆盖 | 见 `images/SOURCE.unpkg.txt` |

## Nezha v1 API 核实记录（来源：nezhahq/nezha v1.14.14 源码）

- 路由表：`cmd/dashboard/controller/controller.go`（`routers()`），`@BasePath /api/v1`。
- `GET /api/v1/setting`：`fallbackAuth` 组，可公开访问；返回
  `CommonResponse{success, data:{config:{site_name, custom_code, custom_code_dashboard, ...}}}`。
  字段定义：`model/config.go:27-28`（`custom_code` / `custom_code_dashboard`），
  `model/setting_api.go:11-12`。
- `GET /api/v1/ws/server`：`optionalAuth` 组（`ForceAuth=true` 时才强制登录）；
  `cmd/dashboard/controller/ws.go:106-196`（`serverStream` / `getServerStat`），
  每 2 秒推送一次，首包带 `public_note`。
  推送体：`model/server_api.go:5-21`（`StreamServer` / `StreamServerData{now, online, servers}`）。
  游客：`hide_for_guest` 的服务器被排除（`GetSortedListForGuest`），
  `host` 只保留 Platform/CPU/内存/磁盘等字段（`Host.Filter()`，`model/host.go:131`）。
- `GET /api/v1/server`：`auth` 组（`controller.go`），**必须登录**；返回
  `CommonResponse[[]Server]`。`Server` 模型见 `model/server.go`：
  `name / uuid / note（仅管理员） / public_note / display_index / hide_for_guest /
  host / state / geoip{ip, country_code} / last_active`——**无价格类字段**。
- `GET /api/v1/profile`：`auth` 组；`cmd/dashboard/controller/user.go:24`
  （`getProfile`），未登录返回 `unauthorized` 错误。登录用 JWT，cookie 名 `nz-jwt`
 （`cmd/dashboard/controller/jwt.go:23,34`）。
- 通用返回体：`model/api.go:21`（`CommonResponse{success, data, error}`）。
- 前端注入：官方用户前端 `hamster1963/nezha-dash-v2`（`frontend-templates.yaml` 中
  Official v2.7.0）：`src/App.tsx` 取 `settingData.data.config.custom_code`，
  经 `src/features/runtime-config/inject.ts`（`InjectContext`）注入；
  根节点 `<div id="root">`（`index.html` / `src/main.tsx`，`WebSocketProvider url="/api/v1/ws/server"`）；
  主题变量见 `src/index.css`（`:root` / `.dark`，HSL 三元组；主题键 `vite-ui-theme`）；
  登录检查用 `GET /api/v1/profile`（`src/lib/nezha-api.ts:fetchLoginUser`）。
- 注意：Nezha v1 官方前端自带一个 2D 世界地图（`src/components/GlobalMap.tsx`），
  本项目的 3D 地球仪是额外功能，与它不冲突。

## 已知限制

1. **资产统计依赖手动填价**：Nezha v1 没有价格/到期字段，不填 `prices` 或公开备注就只能看到服务器数量，金额全是“未配置”。这是 Nezha v1 数据模型本身的限制，不是 bug。
2. **公开备注的价格会被所有访客看到**（包括 WS 首包）。在意隐私请用方式 A（`CONFIG` 价格表）。
3. **WS 首包才有 `public_note`**：页面打开后如果错过首包（例如 WS 重连），备注解析可能暂时缺失；本代码会缓存已拿到的备注，重连后一般能恢复。
4. **ForceAuth 的站**：后台开启“强制要求认证”后，游客连 WS 都拿不到服务器列表，欢迎气泡以外的地球/资产功能对游客不可用（登录后正常）。
5. **保护组件是前端威慑，不是安全边界**：和原版一样，懂行的人仍可绕过；不要把它当成真正的访问控制。`CONFIG.protection.enabled=false` 可彻底关闭。
6. **仅适配 Nezha v1.x**：v2（main 分支，v2.7.0）的 API 与前端结构已变，本文件未经 v2 测试，很可能无法工作。
7. **Globe.GL 走 CDN**（`//unpkg.com/globe.gl`）：离线 / CDN 被墙的环境地球仪打不开，其余功能不受影响。

## 待验证 / Unknowns

以下是在源码里**未能完全核实**、需要你在真实 Nezha v1 实例上测试确认的：

- [ ] `custom_code` 在你所用的 v1.x 小版本里的注入时机：v1.14.14 的官方前端是在设置加载后注入；如果你用的是第三方主题（如 Nezha-Pixel / Nazhua 等），注入方式和根节点可能不同，需按该主题调整。
- [ ] `GET /api/v1/profile` 在**未登录**时的确切 HTTP 状态码（源码里是 gin-jwt 的 `unauthorized`，本代码按 `!res.ok || !json.success` 判断，已覆盖两种情况，但未在真站上实测）。
- [ ] WS 在反代 / 子路径部署下的表现：`wsServerUrl` 默认相对路径按当前 host 拼接；如果你的 Nezha 在子路径或 WS 被反代拦截，需要改成绝对 `wss://…` 地址。
- [ ] `public_note` 价格标记解析：格式是我方约定的（`price:…;expire:…`），Nezha 本身没有这个约定；只有你按本文档写了备注才会生效。
- [ ] 地球纹理 CDN（unpkg）在你访客网络下的可达性；如需自托管，把 `images/` 里的三张图放到你自己的图床，并在 `CONFIG.globe.localDay/localNight/localSky` 里填 URL。
- [ ] `flagcdn.com` 国旗 CDN 的可达性；不可达时国旗标记会自动隐藏（不报错），弧线和计数器不受影响。
- [ ] 汇率 API（exchangerate-api.com）的可达性；失败时自动用 `CONFIG.finance.defaultRates` 默认汇率，并在小部件底部注明。

## 文件清单

```
nezha-beautify-v1/
├── README.md              # 本文件
├── NezhaBeautify.html     # 单文件自定义代码（样式 + 节点 + 脚本），粘贴进 custom_code
└── images/
    ├── earth-day.jpg      # 地球日间纹理（three-globe 示例图本地副本）
    ├── earth-night.jpg    # 地球夜间纹理（本地副本）
    ├── night-sky.png      # 星空背景（本地副本）
    └── SOURCE.unpkg.txt   # 纹理来源 URL
```

纹理来源：`https://unpkg.com/three-globe/example/img/earth-day.jpg`、
`earth-night.jpg`、`night-sky.png`（three-globe 示例资源）。
本项目未修改这些图片；如需商用请自行确认 three-globe 示例资源的许可。
