// MaBo Digital site worker.
// Serves the static site from ./site and handles the contact form at POST /api/contact,
// delivering each enquiry to the verified inbox through Cloudflare Email Routing.
import { EmailMessage } from "cloudflare:email";

const FROM = "web@mabodigital.dev";
const TO = "bocak.sk@gmail.com";
const TOPICS = { web: "New website", seo: "SEO", both: "Website and SEO", other: "Something else" };

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
  });
}

function b64(str) {
  const bytes = new TextEncoder().encode(str);
  let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}

const oneLine = (s) => String(s || "").replace(/[\r\n]+/g, " ").trim();
const encodeHeader = (s) => `=?UTF-8?B?${b64(s)}?=`;

function buildMime({ name, email, topic, message, lang, page }) {
  const subject = `New enquiry from mabodigital.dev: ${TOPICS[topic]} (${name})`;
  const text = [
    `Name: ${name}`,
    `Email: ${email}`,
    `Interested in: ${TOPICS[topic]}`,
    `Language: ${lang === "sk" ? "Slovak" : "English"}`,
    `Sent from: https://mabodigital.dev${page}`,
    "",
    message,
    "",
    "--",
    "Reply to this email to answer the sender directly.",
  ].join("\r\n");
  const body = b64(text).replace(/.{1,76}/g, "$&\r\n");
  return [
    `From: ${encodeHeader("MaBo Digital web")} <${FROM}>`,
    `To: <${TO}>`,
    `Reply-To: ${encodeHeader(name)} <${email}>`,
    `Subject: ${encodeHeader(subject)}`,
    `Date: ${new Date().toUTCString()}`,
    `Message-ID: <${crypto.randomUUID()}@mabodigital.dev>`,
    "MIME-Version: 1.0",
    "Content-Type: text/plain; charset=UTF-8",
    "Content-Transfer-Encoding: base64",
    "",
    body,
  ].join("\r\n");
}

async function handleContact(request, env) {
  if (request.method !== "POST") return json({ ok: false, error: "method" }, 405);
  let data;
  try {
    data = await request.json();
  } catch {
    return json({ ok: false, error: "invalid" }, 400);
  }
  // Bots fill the hidden field or submit instantly. Answer as if it worked and drop the message.
  if (data.website || Number(data.elapsed) < 3000) return json({ ok: true });

  const name = oneLine(data.name).slice(0, 100);
  const email = oneLine(data.email).slice(0, 200);
  const topic = Object.hasOwn(TOPICS, data.topic) ? data.topic : "other";
  const message = String(data.message || "").trim().slice(0, 5000);
  const lang = data.lang === "sk" ? "sk" : "en";
  const page = /^\/[\w\-\/]*$/.test(String(data.page || "")) ? data.page : "/";
  if (!name || !/^[^\s@<>"]+@[^\s@<>"]+\.[^\s@<>"]+$/.test(email) || message.length < 10) {
    return json({ ok: false, error: "invalid" }, 400);
  }

  // Keep a copy first, so the enquiry survives even if the email fails.
  let id = null;
  try {
    const row = await env.DB.prepare(
      "INSERT INTO enquiries (name, email, service, message, lang, page, country) VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id"
    ).bind(name, email, topic, message, lang, page, (request.cf && request.cf.country) || null).first();
    id = row && row.id;
  } catch (err) {
    console.error("contact save failed", err && err.message);
  }

  try {
    const raw = buildMime({ name, email, topic, message, lang, page });
    await env.CONTACT.send(new EmailMessage(FROM, TO, raw));
    if (id) await env.DB.prepare("UPDATE enquiries SET emailed = 1 WHERE id = ?").bind(id).run().catch(() => {});
    return json({ ok: true });
  } catch (err) {
    console.error("contact send failed", err && err.message);
    // Saved but not emailed: tell the visitor it arrived, it is waiting in the database.
    if (id) return json({ ok: true });
    return json({ ok: false, error: "send" }, 502);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/contact") return handleContact(request, env);
    return env.ASSETS.fetch(request);
  },
};
