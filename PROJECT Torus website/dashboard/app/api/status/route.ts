import { getCredential } from '@/lib/credentials';
import { NextResponse } from 'next/server';

export const runtime = 'nodejs';

export async function GET() {
  try {
    const services = ['buffer', 'zapier', 'hubspot', 'trello'];
    const status: Record<string, any> = {};

    for (const service of services) {
      try {
        const creds = getCredential(service);
        status[service] = {
          ok: true,
          account: creds.account || creds.service || 'connected',
          verified: creds.verified ?? true,
        };
      } catch (e) {
        status[service] = {
          ok: false,
          error: e instanceof Error ? e.message : 'Unknown error',
        };
      }
    }

    return NextResponse.json({
      timestamp: new Date().toISOString(),
      services: status,
    });
  } catch (error) {
    return NextResponse.json(
      {
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
