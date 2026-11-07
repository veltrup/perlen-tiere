#!/usr/bin/env node
// Kleiner Webserver für die Hochlandrind-App im Heimnetz.
// Start:  node app/server.js      (andere Ports: PORT=9000 HTTPS_PORT=9443 node app/server.js)
//
// http  (Port 8080): App ohne Offline-Funktion + Seite „einrichten.html“ mit dem Zertifikat fürs Handy
// https (Port 8443): App mit Offline-Funktion – braucht das Zertifikat auf dem Handy.
// Die Zertifikate erzeugt der Server beim ersten Start selbst mit openssl (Ordner app/certs).
'use strict';
const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execFileSync } = require('child_process');
const qrcode = require('./qrcode.js');

const PORT = +process.env.PORT || 8080;
const HTTPS_PORT = +process.env.HTTPS_PORT || 8443;
const ROOT = __dirname;
const CERTS = path.join(ROOT, 'certs');
const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.json': 'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json',
};
const HIDDEN = new Set(['server.js']);

// IPv4-Adressen im lokalen Netz, Heimnetz-Adressen (192.168.x.x) zuerst
function lanIPs() {
  const all = Object.values(os.networkInterfaces()).flat()
    .filter(i => i && i.family === 'IPv4' && !i.internal).map(i => i.address);
  const rank = ip => ip.startsWith('192.168.') ? 0 : ip.startsWith('10.') ? 1 : 2;
  return all.sort((a, b) => rank(a) - rank(b));
}

// ---------- Zertifikate ----------
// Eine eigene kleine Zertifizierungsstelle (CA) bleibt für immer gleich – die installierst du einmal auf dem Handy.
// Das Server-Zertifikat wird neu ausgestellt, wenn sich die Netzwerk-Adresse ändert.
function ensureCerts(ips) {
  const f = n => path.join(CERTS, n);
  const ssl = args => execFileSync('openssl', args, { stdio: 'pipe' });
  fs.mkdirSync(CERTS, { recursive: true });
  if (!fs.existsSync(f('ca.key')) || !fs.existsSync(f('ca.crt'))) {
    ssl(['req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-sha256', '-days', '3650',
      '-keyout', f('ca.key'), '-out', f('ca.crt'), '-subj', '/CN=Hochlandrind lokale CA',
      '-addext', 'basicConstraints=critical,CA:TRUE', '-addext', 'keyUsage=critical,keyCertSign,cRLSign']);
    fs.chmodSync(f('ca.key'), 0o600);
    console.log('  Neue Zertifizierungsstelle erzeugt (app/certs/ca.crt).');
  }
  const san = ['DNS:localhost', 'IP:127.0.0.1', ...ips.map(ip => 'IP:' + ip)].join(',');
  const old = fs.existsSync(f('server.san')) ? fs.readFileSync(f('server.san'), 'utf8') : '';
  if (old !== san || !fs.existsSync(f('server.crt')) || !fs.existsSync(f('server.key'))) {
    fs.writeFileSync(f('server.ext'), `subjectAltName=${san}\nbasicConstraints=CA:FALSE\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\n`);
    ssl(['req', '-newkey', 'rsa:2048', '-nodes', '-keyout', f('server.key'), '-out', f('server.csr'), '-subj', '/CN=Hochlandrind']);
    ssl(['x509', '-req', '-sha256', '-days', '397', '-in', f('server.csr'), '-CA', f('ca.crt'), '-CAkey', f('ca.key'),
      '-CAcreateserial', '-out', f('server.crt'), '-extfile', f('server.ext')]);
    fs.chmodSync(f('server.key'), 0o600);
    fs.writeFileSync(f('server.san'), san);
    console.log('  Server-Zertifikat für ' + ips.join(', ') + ' ausgestellt.');
  }
  return { key: fs.readFileSync(f('server.key')), cert: fs.readFileSync(f('server.crt')), ca: fs.readFileSync(f('ca.crt')) };
}

// QR-Code im Terminal: zwei Modul-Zeilen pro Textzeile, feste Farben (schwarz auf weiß)
function terminalQR(text) {
  const qr = qrcode(0, 'M');
  qr.addData(text);
  qr.make();
  const n = qr.getModuleCount(), q = 4;
  const dark = (r, c) => r >= 0 && c >= 0 && r < n && c < n && qr.isDark(r, c);
  let out = '';
  for (let r = -q; r < n + q; r += 2) {
    let line = '';
    for (let c = -q; c < n + q; c++) {
      const top = dark(r, c) ? 30 : 37, bottom = dark(r + 1, c) ? 40 : 47;
      line += `\x1b[${top};${bottom}m▀`;
    }
    out += '  ' + line + '\x1b[0m\n';
  }
  return out;
}

// ---------- Anfragen ----------
let certs = null, httpsOn = false;
const ips = lanIPs();
const httpUrls = ips.map(ip => `http://${ip}:${PORT}/`);
const httpsUrls = () => httpsOn ? ips.map(ip => `https://${ip}:${HTTPS_PORT}/`) : [];
const setupUrls = () => httpsOn ? httpUrls.map(u => u + 'einrichten.html') : httpUrls;

function notFound(res) {
  res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end('Nicht gefunden');
}

function handle(req, res) {
  const url = new URL(req.url, 'http://x');
  if (url.pathname === '/info.json') {
    res.writeHead(200, { 'Content-Type': TYPES['.json'], 'Cache-Control': 'no-store' });
    return res.end(JSON.stringify({ urls: setupUrls(), httpUrls, httpsUrls: httpsUrls() }));
  }
  if (url.pathname === '/hochlandrind-ca.crt' && certs) {
    res.writeHead(200, { 'Content-Type': 'application/x-x509-ca-cert', 'Content-Disposition': 'attachment; filename="hochlandrind-ca.crt"' });
    return res.end(certs.ca);
  }
  let rel;
  try { rel = decodeURIComponent(url.pathname); } catch (e) { return notFound(res); }
  if (rel.endsWith('/')) rel += 'index.html';
  const file = path.normalize(path.join(ROOT, rel));
  const name = path.basename(file);
  if (!file.startsWith(ROOT + path.sep) || file.startsWith(CERTS + path.sep) || name.startsWith('.') ||
      HIDDEN.has(name) || !TYPES[path.extname(file)]) return notFound(res);
  fs.readFile(file, (err, data) => {
    if (err) return notFound(res);
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)], 'Cache-Control': 'no-cache' });
    res.end(data);
  });
}

function listen(server, port, label, done) {
  server.on('error', err => {
    if (err.code === 'EADDRINUSE') console.error(`  Port ${port} (${label}) ist schon belegt – läuft der Server schon in einem anderen Fenster?`);
    else console.error('  ' + err.message);
    process.exit(1);
  });
  server.listen(port, '0.0.0.0', done);
}

try {
  certs = ensureCerts(ips);
} catch (e) {
  console.error('  Konnte keine Zertifikate erzeugen (ist openssl installiert?). Die App läuft dann ohne Offline-Funktion.');
}

listen(http.createServer(handle), PORT, 'http', () => {
  const start = () => {
    console.log('\n  🐮 Hochlandrind-App läuft!\n');
    console.log(`  Auf diesem Computer:     http://localhost:${PORT}/`);
    if (!ips.length) { console.log('\n  Keine Netzwerk-Adresse gefunden – ist der Computer im WLAN?\n'); return; }
    if (httpsOn) {
      console.log(`  Handy einrichten:        ${setupUrls()[0]}`);
      console.log(`  App (offline-fähig):     ${httpsUrls()[0]}`);
      console.log('\n  Mit dem Handy scannen (gleiches WLAN) – führt zur Einrichtungs-Seite:\n');
    } else {
      console.log(`  Im Heimnetz:             ${httpUrls[0]}`);
      console.log('\n  Mit dem Handy scannen (gleiches WLAN):\n');
    }
    console.log(terminalQR(setupUrls()[0]));
    console.log('  Beenden mit Strg+C\n');
  };
  if (!certs) return start();
  listen(https.createServer({ key: certs.key, cert: certs.cert }, handle), HTTPS_PORT, 'https', () => { httpsOn = true; start(); });
});
