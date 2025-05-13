import { getIronSession } from "iron-session";
import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { SessionData, sessionOptions } from "./lib/session";

export async function middleware(request: NextRequest) {
    const res = NextResponse.next();
    const session = await getIronSession<SessionData>(request, res, sessionOptions);

    // // 如果没有 uid，生成一个新的
    // if (!session.uid) {
    //     session.uid = Math.random().toString(36).substring(2);
    // }

    // 保存会话
    await session.save();

    return res;
}

export const config = {
    matcher: [
        /*
         * 匹配所有路径除了:
         * 1. /_next (Next.js 内部路由)
         * 2. /static (静态文件)
         * 3. /_vercel (Vercel 内部路由)
         * 4. 所有文件扩展名 (例如 .jpg, .png, .ico)
         */
        "/((?!_next|static|_vercel|[\\w-]+\\.\\w+).*)",
    ],
}; 