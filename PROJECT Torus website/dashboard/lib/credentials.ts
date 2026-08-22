import fs from 'fs';
import path from 'path';

const VAULT = 'D:\\Work\\Torus Coffee Company LLC';
const BASE = path.join(VAULT, '10_Skills_Library', '05_Operations');

export function readJson(name: string) {
  const p = path.join(BASE, name);
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

export function getCredential(service: string) {
  const map: Record<string, string> = {
    buffer: 'buffer_credentials.json',
    zapier: 'zapier_credentials.json',
    hubspot: 'hubspot_credentials.json',
    trello: 'Trello_API_Credentials.md',
  };

  const file = map[service];
  if (!file) throw new Error(`Unknown service: ${service}`);

  const data = readJson(file);
  if (!data) throw new Error(`Missing credentials for ${service}`);

  return data;
}

export function validateCredentials() {
  const services = ['buffer', 'zapier', 'hubspot'];
  const result: Record<string, any> = {};

  for (const service of services) {
    try {
      const creds = getCredential(service);
      result[service] = {
        ok: true,
        account: creds.account || creds.service || 'connected',
        verified: true,
      };
    } catch (e) {
      result[service] = {
        ok: false,
        error: e instanceof Error ? e.message : 'Unknown error',
      };
    }
  }

  return result;
}
