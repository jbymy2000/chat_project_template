import { getAppSession } from "@/lib/session";

export async function PUT(request: Request) {
  try {
    const { uid } = await request.json();
    
    if (!uid) {
      return new Response(JSON.stringify({ message: "uid is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }
    
    // 在客户端环境下保存会话信息
    if (typeof window !== 'undefined') {
      // 保存当前用户ID到localStorage
      localStorage.setItem('current_uid', uid);
    }
    
    return new Response(JSON.stringify({ message: "Session updated successfully", uid }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("设置会话错误:", error);
    return new Response(JSON.stringify({ message: "Internal Server Error", error: (error as Error).message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}

export async function GET() {
  try {
    const session = await getAppSession();
    return new Response(JSON.stringify({ uid: session.uid }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("获取会话错误:", error);
    return new Response(JSON.stringify({ message: "Internal Server Error", error: (error as Error).message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
} 