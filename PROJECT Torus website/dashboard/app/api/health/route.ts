import { getCredential, validateCredentials } from '@/lib/credentials';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const summary = validateCredentials();
    const details: Record<string, any> = {};

    for (const [service, info] of Object.entries(summary)) {
      details[service] = {
        ok: info.ok,
        account: info.account,
        verified: info.verified,
        error: info.error,
      };
    }

    return NextResponse.json({
      timestamp: new Date().toISOString(),
      services: details,
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
