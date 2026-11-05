import { NextResponse } from "next/server";
import { demoSessionCookieName } from "../../../lib/demo-auth";

export const runtime = "nodejs";
export async function POST() {
  const response = NextResponse.json({ ok: true });
  response.cookies.set(demoSessionCookieName, "", { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "strict", path: "/", maxAge: 0 });
  return response;
}
