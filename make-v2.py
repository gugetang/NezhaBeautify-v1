#!/usr/bin/env python3
"""Build NezhaBeautify-v2.html from NezhaBeautify.html (v1 source, untouched).

Applies the v1 -> v2 adaptations as text transforms, so the v1 file stays
the source of truth for the shared 5 features and the diff stays reviewable.
Run: python3 make-v2.py  (writes NezhaBeautify-v2.html next to this script)
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "NezhaBeautify.html"
DST = HERE / "NezhaBeautify-v2.html"

text = SRC.read_text(encoding="utf-8")

def sub(pattern, repl, count=0, flags=0):
    global text
    new, n = re.subn(pattern, repl, text, count=count, flags=flags)
    if n == 0:
        sys.exit(f"transform matched nothing: {pattern!r}")
    text = new

# --- 1. File header comment -----------------------------------------------
sub(
    r"<!--\n  NezhaBeautify v1.*?-->\n",
    """<!--
  NezhaBeautify v2 —— 为 Nezha v2（nezhahq/nezha v2.6.2，官方用户前端
  nezha-dash-v2 2.7.0 @ 1dd038b）改编的 KomariBeautify
  ============================================================================
  来源：KomariBeautify（Komari v1.1.3），按 Nezha v2 重做；由本项目 v1 版
  （NezhaBeautify.html，适配 v1.14.x）移植而来，5 个功能全部保留。
  使用方法（Nezha v2 Dashboard）：
    后台 → 设置 → 自定义代码（custom_code）→ 把本文件全部内容粘贴进去保存。
    custom_code 由官方用户前端（nezha-dash-v2）在加载设置后经
    InjectContext（src/features/runtime-config/inject.ts）按文档顺序注入：
    <style> 进 <head>，外链 <script> 按序等待加载（30 秒超时，失败会清掉
    全部已注入节点并报错），内联 <script> 和 HTML 节点进 <body>。
    所以本文件不再用外链 <script src> 加载 Globe.GL（见下），改由 JS 后台
    动态加载，避免 CDN 失败拖垮整段自定义代码。详见 README.md。
  配置：只改 <script> 开头的 CONFIG 对象即可，不用动其它代码。
  依赖：Globe.GL（CDN，见 CONFIG.globe，由 JS 动态加载，unpkg 失败自动换
  jsdelivr）；其余无外部库。
-->
""",
    flags=re.S,
)

# --- 2. Theme CSS comment: v1 -> v2, drop PurCarte mentions -----------------
sub(r"Nezha v1 主题变量适配", "Nezha v2 主题变量适配")
sub(
    r"Nezha v1 官方用户前端（nezha-dash-v2）是 Tailwind \+ shadcn 风格：",
    "Nezha v2 官方用户前端（nezha-dash-v2）是 Tailwind v4 + shadcn 风格：",
)
sub(
    r"   （原版用的 PurCarte 变量 --accent-9 / --purcarte-card-color / --gray-a5\n   在 Nezha 里不存在，已全部替换。）",
    "   （旧版 Komari 主题的变量在 Nezha 里不存在，已全部替换；v2 的变量名与\n   v1 相同，见 nezha-dash-v2 src/index.css 的 :root / .dark，HSL 三元组。）",
)

# --- 3. CONFIG API comment block: replace v1 block with v2 block ----------
sub(
    r"/\* =+\n   NezhaBeautify v1 —— 配置区.*?={10,} \*/",
    """/* ==========================================================================
   NezhaBeautify v2 —— 配置区（只改这里）
   --------------------------------------------------------------------------
   Nezha v2 API（已按 nezhahq/nezha v2.6.2 与 hamster1963/nezha-dash-v2
   2.7.0 @ 1dd038b 源码核实；行号见 README 映射表）：
   - GET  /api/v1/setting    公开（fallbackAuth）。返回 {success,
     data:{config:{site_name, custom_code, ...}}}。本站名从这里取。
     注意：该接口不含 version 字段，版本号只能看后台/页脚。
   - GET  /api/v1/ws/server  公开（除非后台开启 ForceAuth）。WebSocket，
     每 2 秒推送 {now, online, servers:[StreamServer]}。StreamServer 字段：
     {id, name, public_note（仅首包有值）, display_index, host, state,
      country_code, last_active}。游客看不到 hide_for_guest 的服务器。
   - GET  /api/v1/service    公开。返回 ServiceResponse{services:
     map[id]ServiceResponseItem{service_name, current_up, current_down,
     total_up, total_down, delay[30], up[30], down[30]}}。
   - GET  /api/v1/service/:id/history  公开，?period=1d|7d|30d（默认 1d）；
     访客只能查 1d，7d/30d 需要登录。本项目不用它（延迟是 Latency 项目的事）。
   - GET  /api/v1/server     仅登录后可用，游客返回 HTTP 200 +
     {"error":"ApiErrorUnauthorized"}。不要把它当公开接口用。
   - GET  /api/v1/profile    仅登录后可用；200 + success:true = 已登录。
     访客同样返回 HTTP 200 + {"error":"ApiErrorUnauthorized"}（2026-11-20
     在 status.alicloud.ru 上实测），所以登录判断必须看 json.success，
     不能只看 HTTP 状态码。保护组件用它判断。
   - 通用返回体：{success: bool, data: ..., error: string}。
   - Komari 的旧取数接口在 Nezha v2 里根本不存在（路由表里没有），
     本文件已全部删掉，旧站内联代码用它们取数是 404，见 README 诊断。
   Nezha v2 的 Server 模型没有 price / billing_cycle / expired_at /
   tags / weight / currency 字段（见 README 映射表），所以资产统计的
   价格必须另行提供，见下面的 finance.prices。
   注入机制（nezha-dash-v2）：App.tsx 在设置加载后调用
   InjectContext(custom_code)，按文档顺序注入；外链脚本逐个等待加载，
   30 秒超时或加载失败会清掉全部已注入节点并在页顶报错；custom_code
   字符串一变（后台改了设置，或窗口获得焦点后重新拉取设置发现变了），
   旧节点会被 dispose 掉再重新注入。根节点仍是 <div id="root">，
   React 路由切换不会卸载 App，也不会动挂在 document.body 下的节点。
   ========================================================================== */""",
    flags=re.S,
)

sub(r"// ---- Nezha v1 接口（一般不用改；反代到子路径时改成绝对路径） ----",
    "// ---- Nezha v2 接口（一般不用改；反代到子路径时改成绝对路径） ----")
sub(r"// ---- 站点 ----", "// ---- 站点 ----")

# --- 4. CONFIG.globe: add jsdelivr fallback for Globe.GL -------------------
sub(
    r"    cdnDay: '//unpkg\.com/three-globe/example/img/earth-day\.jpg',",
    """    // Globe.GL 主库：JS 动态加载，unpkg 失败自动换 jsdelivr（已实测 200）。
    // 注意：不要在 custom_code 里再放外链脚本加载 Globe.GL，
    // InjectContext 会逐个等待外链加载，失败会清掉整段自定义代码。
    globeLib: '//unpkg.com/globe.gl',
    globeLibFallback: 'https://cdn.jsdelivr.net/npm/globe.gl@2.46.2/dist/globe.gl.min.js',
    cdnDay: '//unpkg.com/three-globe/example/img/earth-day.jpg',""",
)

# --- 5. Prices comment -------------------------------------------------------
sub(r"价格表：Nezha v1 没有价格字段", "价格表：Nezha v2 没有价格字段")

# --- 6. Section 2 (data layer) comment --------------------------------------
sub(
    r"/\* =+\n   2\. Nezha v1 数据层.*?={10,} \*/",
    """/* ==========================================================================
   2. Nezha v2 数据层
   - 服务器列表主通道是 WebSocket /api/v1/ws/server（公开，除非 ForceAuth），
     每 2 秒一包。首包的 public_note 有值，后续包为空——按 id 合并时保留
     已有的备注。来源：nezha v2.6.2 cmd/dashboard/controller/ws.go:109
     （serverStream，2 秒间隔见 ws.go:154,170），StreamServer 字段见
     model/server_api.go:5-21。
   - 备用通道是 REST /api/v1/server，仅登录后可用；WS 长时间无数据时才试。
     访客调用它会得到 HTTP 200 + {"error":"ApiErrorUnauthorized"}，
     本代码按 json.success 判断，不会误当成空列表。
   - 登录判断：GET /api/v1/profile，访客同样返回 HTTP 200 + 错误体，
     必须看 json.success（见 isLoggedIn）。
   ========================================================================== */""",
    flags=re.S,
)

# --- 7. isLoggedIn / fetchRestServers comments -------------------------------
sub(
    r"  // 登录状态：GET /api/v1/profile，200 \+ success:true = 已登录",
    "  // 登录状态：GET /api/v1/profile。v2 里访客返回 HTTP 200 +\n  // {\"error\":\"ApiErrorUnauthorized\"}，所以必须看 json.success，不能只看 res.ok。",
)
sub(r"var t = localStorage\.getItem\('vite-ui-theme'\); // Nezha v1 主题键",
    "var t = localStorage.getItem('vite-ui-theme'); // Nezha v2 主题键（与 v1 相同）")

# --- 8. Protection / welcome / finance / earth section comments -------------
sub(r"3\. 保护组件 \(Protection\) —— 与原版相同逻辑，仅登录检查接口换成 Nezha v1",
    "3. 保护组件 (Protection) —— 与原版相同逻辑，登录检查用 Nezha v2 的 /api/v1/profile")
sub(r"站名改成从 /api/v1/setting 取 site_name，取不到用 CONFIG\.siteNameFallback。",
    "站名改成从 /api/v1/setting 取 site_name，取不到用 CONFIG.siteNameFallback。")
sub(
    r"5\. 资产统计 \(Finance Widget\) —— Nezha v1 适配版\n   与 Komari 原版的关键区别（Nezha v1 Server 模型无价格字段）：\n   - 数据源：WebSocket /api/v1/ws/server 的 StreamServer（公开），不再是\n     Komari 的 GET /api/nodes；REST /api/v1/server 仅登录后可用作备用。",
    "5. 资产统计 (Finance Widget) —— Nezha v2 适配版\n   与 Komari 原版的关键区别（Nezha v2 Server 模型无价格字段）：\n   - 数据源：WebSocket /api/v1/ws/server 的 StreamServer（公开）；\n     REST /api/v1/server 仅登录后可用作备用。旧站内联代码用的\n     Komari 旧接口在 v2 上是 404，本文件不用它。",
)
sub(
    r"6\. 地球组件 \(Earth Globe\) —— Nezha v1 适配版",
    "6. 地球组件 (Earth Globe) —— Nezha v2 适配版",
)
sub(
    r"注意：Nezha v1 官方前端自带一个 2D 世界地图（GlobalMap 组件），本组件",
    "注意：Nezha v2 官方前端自带一个 2D 世界地图（GlobalMap 组件），本组件",
)

# --- 9. Remove the external Globe.GL script tag; JS loads it dynamically ---
sub(r"<script src=\"//unpkg\.com/globe\.gl\"></script>\n", "")

# --- 10. Protection / finance / earth double-init guards --------------------
sub(
    r"function initializeProtection\(\) \{\n  if \(!NB\.cfg\.protection\.enabled\) return;",
    """function initializeProtection() {
  if (!NB.cfg.protection.enabled) return;
  if (window.__nbProtectionStarted) return; // 守护者重挂节点时不重复绑 document 监听
  window.__nbProtectionStarted = true;""",
)
sub(
    r"function initializeFinanceWidget\(\) \{\n  var widget = document\.getElementById\('finance-widget'\);",
    """function initializeFinanceWidget() {
  if (window.__nbFinanceStarted) return; // 同上；节点重建时由守护者先清掉该标志
  window.__nbFinanceStarted = true;
  var widget = document.getElementById('finance-widget');""",
)
sub(
    r"function initializeEarth\(\) \{\n  var ball = document\.getElementById\('earth-ball'\);",
    """function initializeEarth() {
  if (window.__nbEarthStarted) return; // 同上
  window.__nbEarthStarted = true;
  var ball = document.getElementById('earth-ball');""",
)

# --- 11. Globe.GL dynamic loader (before initializeEarth) -------------------
sub(
    r"/\* =+\n   6\. 地球组件 \(Earth Globe\) —— Nezha v2 适配版",
    """/* ==========================================================================
   5b. Globe.GL 动态加载 —— v2 新增
   绝不能在 custom_code 里放外链脚本加载 Globe.GL：
   InjectContext 会逐个等待外链脚本加载，30 秒超时或加载失败会清掉整段
   自定义代码（包括欢迎气泡/资产统计的节点）。所以改由 JS 在后台动态
   加载：先 unpkg，失败自动换 jsdelivr；两个都失败时地球仪打不开，
   但其余功能不受影响。
   ========================================================================== */
function ensureGlobeLib(cb) {
  if (typeof Globe !== 'undefined') { if (cb) cb(true); return; }
  if (window.__nbGlobeLoading) { if (cb) { var t = setInterval(function () { if (typeof Globe !== 'undefined' || !window.__nbGlobeLoading) { clearInterval(t); cb(typeof Globe !== 'undefined'); } }, 300); } return; }
  window.__nbGlobeLoading = true;
  var urls = [NB.cfg.globe.globeLib, NB.cfg.globe.globeLibFallback].filter(Boolean);
  var i = 0;
  (function next() {
    if (typeof Globe !== 'undefined') { window.__nbGlobeLoading = false; if (cb) cb(true); return; }
    if (i >= urls.length) { window.__nbGlobeLoading = false; if (cb) cb(false); return; }
    var s = document.createElement('script');
    s.src = urls[i++];
    s.async = true;
    s.onload = function () { window.__nbGlobeLoading = false; if (cb) cb(typeof Globe !== 'undefined'); };
    s.onerror = function () { next(); };
    document.head.appendChild(s);
  })();
}

/* ==========================================================================
   6. 地球组件 (Earth Globe) —— Nezha v2 适配版""",
    flags=re.S,
)

# --- 12. Earth ball click: load Globe.GL on demand instead of giving up -----
sub(
    r"        if \(typeof Globe === 'undefined'\) \{\n          renderArea\.innerHTML = '<p style=\"padding:24px;color:var\(--nb-muted\)\">Globe\.GL 未加载成功，请检查网络后重试。</p>';\n          return;\n        \}",
    """        if (typeof Globe === 'undefined') {
          renderArea.innerHTML = '<p style="padding:24px;color:var(--nb-muted)">正在加载 Globe.GL，请稍候…</p>';
          ensureGlobeLib(function (ok) {
            if (!ok) { renderArea.innerHTML = '<p style="padding:24px;color:var(--nb-muted)">Globe.GL 未加载成功，请检查网络后重试。</p>'; return; }
            isGlobeInitialized = false; // 重新走下面的初始化分支
            ball.click();
          });
          return;
        }""",
)

# --- 13. Replace initializeApp (section 7) with the v2 guardian version -----
sub(
    r"/\* =+\n   7\. 初始化.*?if \(document\.readyState === 'loading'\) \{\n  document\.addEventListener\('DOMContentLoaded', initializeApp\);\n\} else \{\n  initializeApp\(\);\n\}\n</script>\n?$",
    """/* ==========================================================================
   7. 初始化 —— Nezha v2 守护者挂载
   v2 的 InjectContext（nezha-dash-v2 src/features/runtime-config/inject.ts）
   会在 custom_code 字符串变化时 dispose 掉上一次注入的全部节点再重新
   注入；App 本身不卸载，路由切换也不会动 document.body 下的节点。
   所以挂载策略是：
   - 节点直接挂 document.body（fixed 定位，不依赖任何前端容器；v2 前端
     里没有旧代码等的那类主题容器，等它是等不到的）。
   - 首次挂载后给 6 个节点拍 outerHTML 快照；body 的 MutationObserver
     + 3 秒轮询持续守护：节点被移走就挪回来，被删掉就用快照重建并重跑
     对应功能的初始化（重建前先清掉该功能的 started 标志）。
   - 每个功能初始化各自 try/catch：一个功能抛错不能拖垮其它功能，更
     不能让内联脚本顶层抛错——InjectContext 会捕获内联脚本执行期的
     window error 并清掉整段自定义代码。
   - Globe.GL 在后台预加载（不阻塞初始化）。
   登录检查（Nezha v2）：
   - GET /api/v1/profile：200 + success:true = 已登录 → 不启动保护；
     否则（未登录 / 请求失败）→ 按配置启动保护。
   ========================================================================== */
var NB_NODE_IDS = ['welcome-bubble-container', 'custom-alert-overlay', 'finance-widget', 'finance-ball', 'earth-ball', 'earth-modal-overlay'];
var NB_SNAPSHOTS = {};

function nbSnapshotNodes() {
  NB_NODE_IDS.forEach(function (id) {
    var el = document.getElementById(id);
    if (el && !NB_SNAPSHOTS[id]) NB_SNAPSHOTS[id] = el.outerHTML;
  });
}

function nbReinitFor(ids) {
  if (ids.indexOf('welcome-bubble-container') !== -1) {
    window.welcomeBubbleInitialized = false; window.ipInfoFetched = false;
    try { initializeWelcomeBubble(); } catch (e) { console.warn('[NezhaBeautify] welcome re-init failed', e); }
  }
  if (ids.indexOf('finance-widget') !== -1 || ids.indexOf('finance-ball') !== -1) {
    window.__nbFinanceStarted = false;
    try { initializeFinanceWidget(); } catch (e) { console.warn('[NezhaBeautify] finance re-init failed', e); }
  }
  if (ids.indexOf('earth-ball') !== -1 || ids.indexOf('earth-modal-overlay') !== -1) {
    window.__nbEarthStarted = false;
    try { initializeEarth(); } catch (e) { console.warn('[NezhaBeautify] earth re-init failed', e); }
  }
  if (ids.indexOf('custom-alert-overlay') !== -1) {
    window.__nbProtectionStarted = false;
    NB.isLoggedIn().then(function (loggedIn) {
      if (!loggedIn) { try { initializeProtection(); } catch (e) { console.warn('[NezhaBeautify] protection re-init failed', e); } }
    }).catch(function () {});
  }
}

// 守护：节点被移走就挪回 body，被删掉就用快照重建。返回重建的 id 列表。
function nbGuardNodes() {
  var restored = [];
  NB_NODE_IDS.forEach(function (id) {
    var el = document.getElementById(id);
    if (!el && NB_SNAPSHOTS[id]) {
      var tmp = document.createElement('div');
      tmp.innerHTML = NB_SNAPSHOTS[id];
      var node = tmp.firstChild;
      if (node) { document.body.appendChild(node); restored.push(id); }
    } else if (el && el.parentElement !== document.body) {
      document.body.appendChild(el);
    }
  });
  if (restored.length) nbReinitFor(restored);
  return restored;
}

function initializeApp() {
  nbSnapshotNodes();
  nbGuardNodes();

  try { initializeWelcomeBubble(); } catch (e) { console.warn('[NezhaBeautify] welcome init failed', e); }
  try { initializeFinanceWidget(); } catch (e) { console.warn('[NezhaBeautify] finance init failed', e); }
  try { initializeEarth(); } catch (e) { console.warn('[NezhaBeautify] earth init failed', e); }
  // Globe.GL 后台预加载，不阻塞其它功能；失败时点地球仪会再试一次
  try { ensureGlobeLib(function () {}); } catch (e) {}

  // 持久守护：v1 版只在启动时 attach 一次；v2 版持续观察 body，节点
  // 被 dispose/移走/删除都能恢复。只观察 body 的直接子节点，不盯 #root
  // 子树（React 每 2 秒推数据会频繁改 #root 子树，盯它又贵又吵）。
  try {
    var guardObserver = new MutationObserver(function () { nbGuardNodes(); });
    guardObserver.observe(document.body, { childList: true });
  } catch (e) {}
  setInterval(function () { nbGuardNodes(); }, 3000);

  NB.isLoggedIn().then(function (loggedIn) {
    if (!loggedIn && NB.cfg.protection.guestsOnly) {
      try { initializeProtection(); } catch (e) { console.warn('[NezhaBeautify] protection init failed', e); }
    } else if (!NB.cfg.protection.guestsOnly && NB.cfg.protection.enabled) {
      try { initializeProtection(); } catch (e) { console.warn('[NezhaBeautify] protection init failed', e); }
    }
  }).catch(function () {
    if (NB.cfg.protection.enabled) {
      try { initializeProtection(); } catch (e) {}
    }
  });
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeApp);
} else {
  initializeApp();
}
</script>
""",
    flags=re.S,
)

# --- 14. Global v1 -> v2 renames (text only, not /api/v1 paths) --------------
text = text.replace("NezhaBeautify v1", "NezhaBeautify v2")
text = text.replace("Nezha v1", "Nezha v2")
text = text.replace("v1.14.14", "v2.6.2")
text = text.replace("v1.14.x", "v2.6.x")
text = text.replace("v1.x", "v2.x")
# 上面把 v1 版自身的版本号也改了，改回来：v1 版适配的是 v1.14.x
text = text.replace("适配 v2.6.x）移植而来", "适配 v1.14.x）移植而来")
# Header line 2 still says v1 in the title area? handled above; fix leftovers:
text = text.replace("KomariBeautify（Komari v1.1.3 + PurCarte v1.2.5）", "KomariBeautify（Komari v1.1.3）")

# --- 15. Safety net: forbidden strings must be gone -------------------------
for bad in ["/api/nodes", "/api/me", ".radix-themes", "PurCarte", "purcarte"]:
    if bad in text:
        sys.exit(f"forbidden string still present: {bad}")
if '<script src="//unpkg.com/globe.gl">' in text:
    sys.exit("external globe script tag still present")

DST.write_text(text, encoding="utf-8")
print(f"wrote {DST} ({DST.stat().st_size} bytes)")
