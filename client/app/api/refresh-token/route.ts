import { NextRequest, NextResponse } from "next/server";

export const refreshToken = async (refreshToken: string) => {
  const API_URL = process.env.API_URL;

  const res = await fetch(`${API_URL}/api/token/refresh/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "cache-control": "no-cache",
    },
    body: JSON.stringify({ refresh: refreshToken }),
  });

  const data = await res.json();

  if (!res.ok) {
    return;
  }

  return data;
};

export async function GET(request: NextRequest) {
  if (
    !request.cookies.get("sunnylive-auth-token") ||
    !request.cookies.get("sunnylive-auth-refresh-token")
  ) {
    return NextResponse.json(
      {
        error: "Not authenticated",
      },
      {
        status: 400,
      },
    );
  }

  const refData = await refreshToken(
    request.cookies.get("sunnylive-auth-refresh-token")!.value,
  );

  const res = NextResponse.json(
    {
      data: refData,
    },
    {
      status: 200,
    },
  );

  await Promise.all([
    res.cookies.delete("sunnylive-auth-token"),
    res.cookies.set("sunnylive-auth-token", refData.access, {
      httpOnly: true,
      path: "/",
      sameSite: "lax",
      secure: true,
    }),
  ]);

  return res;
}
