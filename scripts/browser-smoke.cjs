// Optional loopback-only form check. Requires an existing Playwright installation.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const { spawnSync } = require('node:child_process');
const { chromium } = require(process.env.CAREER_PLAYWRIGHT_MODULE || 'playwright');

async function run() {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'career-browser-'));
  let server;
  let browser;
  try {
    const python = process.env.CAREER_PYTHON || 'python3';
    const setup = spawnSync(python, ['-c', [
      'import sys',
      'from pathlib import Path',
      'sys.path.insert(0, sys.argv[1])',
      'import career, demo',
      'root=Path(sys.argv[2]) / ".career"',
      'demo.populate(root)',
      'pdf=Path(sys.argv[2]) / "fictional.pdf"',
      'demo.fictional_pdf(pdf)',
      'career.register_resume(root,"Data Analytics","1.0",pdf,True)',
      'job=career.add_job(root,career.read(career.ROOT / "examples/job.json"))',
      'career.prepare(root,job["id"],"Data Analytics",career.ROOT / "examples/letter.json")',
      'print(job["id"])'
    ].join('\n'), __dirname, temp], { encoding: 'utf8' });
    if (setup.status !== 0) throw new Error(setup.stderr || 'Fixture setup failed');
    const id = setup.stdout.trim();
    const folder = path.join(temp, '.career', 'applications', id);
    const html = `<!doctype html><html lang="en"><title>Fictional application test</title>
      <h1>Fictional local application</h1><p>No employer or external service receives this test.</p>
      <form><label>Name <input name="name" required></label>
      <label>Resume <input name="resume" type="file" accept=".pdf" required></label>
      <label>Letter <input name="letter" type="file" accept=".docx" required></label>
      <label>Answer <textarea name="answer" required></textarea></label>
      <label><input name="reviewed" type="checkbox" required>Fictional review confirmed</label>
      <button>Simulate submission</button></form><output></output>
      <script>document.querySelector('form').addEventListener('submit',async e=>{
        e.preventDefault(); const form=e.target;
        const digest=async f=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await f.arrayBuffer()))).map(x=>x.toString(16).padStart(2,'0')).join('');
        const receipt={simulation:true,name:form.elements.name.value,
          resume:await digest(form.elements.resume.files[0]),letter:await digest(form.elements.letter.files[0])};
        document.querySelector('output').textContent=JSON.stringify(receipt);
      });</script></html>`;
    server = http.createServer((request, response) => {
      response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      response.end(html);
    });
    await new Promise((resolve, reject) => {
      server.once('error', reject);
      server.listen(0, '127.0.0.1', resolve);
    });
    browser = await chromium.launch({ headless: true, channel: process.env.CAREER_BROWSER_CHANNEL || 'chrome', chromiumSandbox: true });
    const page = await browser.newPage();
    const origin = `http://127.0.0.1:${server.address().port}`;
    await page.route('**/*', route => route.request().url().startsWith(origin + '/') ? route.continue() : route.abort());
    await page.goto(origin);
    await page.getByRole('textbox', { name: 'Name', exact: true }).fill('Alex Example');
    await page.getByLabel('Resume', { exact: true }).setInputFiles(path.join(folder, 'resume.pdf'));
    await page.getByLabel('Letter', { exact: true }).setInputFiles(path.join(folder, 'cover-letter.docx'));
    await page.getByRole('textbox', { name: 'Answer', exact: true }).fill('My fictional course project used SQL queries and spreadsheet checks.');
    await page.getByLabel('Fictional review confirmed').check();
    if ((await page.locator('output').textContent()).trim()) throw new Error('Form submitted before simulated manual action');
    await page.getByRole('button', { name: 'Simulate submission' }).click();
    await page.waitForFunction(() => document.querySelector('output').textContent.length > 0);
    const receipt = JSON.parse(await page.locator('output').textContent());
    for (const [key, filename] of [['resume', 'resume.pdf'], ['letter', 'cover-letter.docx']]) {
      const actual = crypto.createHash('sha256').update(fs.readFileSync(path.join(folder, filename))).digest('hex');
      if (receipt[key] !== actual) throw new Error('Uploaded file did not match prepared material: ' + key);
    }
    console.log(JSON.stringify({ fictional: true, headless: true, loopback_only: true, upload_hashes_match: true, simulated_submit: true, browser_version: browser.version() }, null, 2));
  } finally {
    if (browser) await browser.close();
    if (server) await new Promise(resolve => server.close(resolve));
    fs.rmSync(temp, { recursive: true, force: true });
  }
}
run().catch(error => { console.error(error.message); process.exitCode = 1; });
