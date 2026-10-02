// Liste de tâches partagée du groupe : lecture (GET) et mise à jour d'une tâche (POST).
// Chaque tâche est une clé séparée du store, pour que deux personnes qui cochent
// deux tâches différentes en même temps ne s'écrasent pas.
import { getStore } from "@netlify/blobs";

const TASKS = ["van", "ferries", "acropole", "myk", "parking", "vin", "delos", "tables", "caution"];
const NAMES = ["Antonin", "Nathan", "Xavier", "Simon", "Erwan", "Donovan", "Paul"];
const NO_STORE = { "cache-control": "no-store" };

async function readAll(store) {
  const entries = await Promise.all(TASKS.map(async (id) => [id, await store.get(id, { type: "json" })]));
  return Object.fromEntries(entries.filter(([, v]) => v));
}

export default async (req) => {
  const store = getStore({ name: "todo", consistency: "strong" });

  if (req.method === "GET") {
    return Response.json(await readAll(store), { headers: NO_STORE });
  }

  if (req.method !== "POST") {
    return new Response("Méthode non autorisée", { status: 405 });
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return new Response("JSON invalide", { status: 400 });
  }
  const { id, by } = body || {};
  if (!TASKS.includes(id)) return new Response("Tâche inconnue", { status: 400 });
  if (!NAMES.includes(by)) return new Response("Prénom inconnu", { status: 400 });

  const cur = (await store.get(id, { type: "json" })) || {};
  const now = new Date().toISOString();
  if ("who" in body) {
    if (body.who !== "" && !NAMES.includes(body.who)) return new Response("Prénom inconnu", { status: 400 });
    cur.who = body.who;
  }
  if ("done" in body) {
    cur.done = !!body.done;
    cur.doneBy = cur.done ? by : "";
    cur.doneAt = cur.done ? now : "";
  }
  cur.updatedBy = by;
  cur.updatedAt = now;
  await store.setJSON(id, cur);

  return Response.json(await readAll(store), { headers: NO_STORE });
};

export const config = { path: "/api/todo" };
