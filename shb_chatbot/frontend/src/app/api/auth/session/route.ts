import { NextRequest, NextResponse } from "next/server";

export const runtime = 'edge';

export async function POST(request: NextRequest) {
  try {
    const { access_token, refresh_token } = await request.json();

    if (!access_token) {
      return NextResponse.json({ detail: "Missing tokens" }, { status: 400 });
    }

    const response = NextResponse.json({ message: "Session synced" });

    // Set access token cookie
    response.cookies.set("access_token", access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60, // 1 hour (Supabase default is 1h)
      path: "/",
    });

    if (refresh_token) {
      // Set refresh token cookie
      response.cookies.set("refresh_token", refresh_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        maxAge: 60 * 60 * 24 * 30, // 30 days
        path: "/",
      });
    }

    return response;
  } catch (error) {
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    );
  }
}
