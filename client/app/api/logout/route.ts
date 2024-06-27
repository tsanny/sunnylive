import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const API_URL = process.env.API_URL;
  const response = await fetch(`${API_URL}/api/logout/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const res = NextResponse.json(
    {},
    {
      status: response.status,
    },
  );
  await Promise.all([
    res.cookies.delete("sunnylive-auth-token"),
    res.cookies.delete("sunnylive-auth-refresh-token"),
  ]);
  return res;
}
