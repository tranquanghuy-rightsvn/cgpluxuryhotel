// Minimal CDP driver for headless Chrome (no deps).
// Usage: node cdp.mjs <url> <width> <height> <outPrefix> [evalFile]
//   - waits for load + lazy content, scrolls through page
//   - writes <outPrefix>.png (full page, 1x DPR) and, if evalFile given, <outPrefix>.json with eval result
import { spawn } from "node:child_process";
import { readFileSync, writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [url, W = "1366", H = "900", out, evalFile] = process.argv.slice(2);
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const port = 9300 + Math.floor(Math.random() * 500);
const prof = mkdtempSync(join(tmpdir(), "cdp-"));
const proc = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, "--no-first-run", "--hide-scrollbars", "--disable-gpu", `--window-size=${W},${H}`, ...(process.env.NOSEC ? ["--disable-web-security", "--disable-site-isolation-trials", "--disable-features=IsolateOrigins,site-per-process"] : []), "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let ws, id = 0; const pend = new Map();
for (let i = 0; i < 50; i++) {
  try {
    const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
    const page = list.find((t) => t.type === "page");
    if (page) { ws = new WebSocket(page.webSocketDebuggerUrl); break; }
  } catch {}
  await sleep(200);
}
await new Promise((r) => (ws.onopen = r));
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } };
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (expr) => { const r = await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }); if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 500)); return r.result?.result?.value; };

await send("Page.enable"); await send("Runtime.enable");
const ERRS=[]; ws.addEventListener("message",(m)=>{const d=JSON.parse(m.data); if(d.method==="Runtime.exceptionThrown") ERRS.push(d.params.exceptionDetails.exception?.description?.slice(0,200)||d.params.exceptionDetails.text);});
await send("Emulation.setDeviceMetricsOverride", { width: +W, height: +H, deviceScaleFactor: 1, mobile: +W < 800 });
await send("Page.navigate", { url });
await sleep(4000);
// scroll sweep to trigger lazy content
await ev(`(async()=>{for(let y=0;y<document.documentElement.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,120));}scrollTo(0,0);await new Promise(r=>setTimeout(r,800));})()`);
// hide popups / animation noise
await ev(`(()=>{const s=document.createElement('style');s.textContent='*,*::before,*::after{transition:none!important;animation:none!important;caret-color:transparent!important}';document.head.appendChild(s);document.documentElement.style.scrollBehavior='auto'})()`);
if (process.env.PRE) await ev(readFileSync(process.env.PRE, "utf8"));
await sleep(600);
if (process.env.STEPS) {
  for (const st of JSON.parse(process.env.STEPS)) {
    if (st.scroll !== undefined) await ev(`scrollTo(0,${st.scroll})`);
    if (st.click) {
      for (const type of ["mouseMoved", "mousePressed", "mouseReleased"]) await send("Input.dispatchMouseEvent", { type, x: st.click[0], y: st.click[1], button: "left", clickCount: 1 });
    }
    if (st.js) await ev(st.js);
    if (st.wait) await sleep(st.wait);
    if (st.shot) { const s = await send("Page.captureScreenshot", { format: "png" }); writeFileSync(st.shot + ".png", Buffer.from(s.result.data, "base64")); }
  }
}
let result = null;
if (evalFile) result = await ev(readFileSync(evalFile, "utf8"));
const h = await ev("Math.ceil(document.documentElement.scrollHeight)");
await sleep(800);
if (out) {
  const shot = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip: { x: 0, y: 0, width: +W, height: h, scale: 1 } });
  writeFileSync(out + ".png", Buffer.from(shot.result.data, "base64"));
  if (result !== null) writeFileSync(out + ".json", typeof result === "string" ? result : JSON.stringify(result, null, 1));
}
console.log(JSON.stringify({ height: h, wrote: out, errors: ERRS }));
ws.close(); proc.kill();
