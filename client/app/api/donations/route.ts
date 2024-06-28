import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const API_URL = process.env.API_URL;
  const body = await request.json();

  let accessToken = request.cookies.get("sunnylive-auth-token")?.value;
  if (!accessToken) {
    return NextResponse.json(
      {
        error: "Not authenticated",
      },
      {
        status: 400,
      },
    );
  }

  try {
    const res = await fetch(`${API_URL}/api/donations/charge/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const data = await res.json();
      const errorMessage = data.non_field_errors
        ? data.non_field_errors[0]
        : "An error occurred";

      return NextResponse.json({ error: errorMessage }, { status: res.status });
    }

    const data = await res.json();

    return NextResponse.json({ ...data }, { status: res.status });
  } catch (error) {
    return NextResponse.json({ error: "An error occurred" }, { status: 500 });
  }
}
