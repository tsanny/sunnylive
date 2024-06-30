import { NextRequest, NextResponse } from "next/server";
import { refreshToken } from "./refresh";

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
