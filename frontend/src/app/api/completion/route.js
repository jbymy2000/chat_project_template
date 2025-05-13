// app/api/completion/route.js
// 使用lib/api.ts中的函数处理流式聊天

import { processChatStream, streamChat } from '@/lib/api';

export async function POST(request) {
  try {
    const { prompt, topicId } = await request.json();
    
    // 从请求头获取认证token
    const authHeader = request.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return new Response(JSON.stringify({ message: "未授权，请先登录" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }
    
    // 获取token用于API请求
    const token = authHeader.split(' ')[1];
    
    // 检查是否提供了topicId
    if (!topicId) {
      return new Response(JSON.stringify({ message: "缺少话题ID" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    try {
      // 调用API发送流式对话请求，传入token
      const response = await streamChat(parseInt(topicId), prompt, token);
      
      // 处理流式响应
      const readableStream = await processChatStream(response);
      
      // 返回可读流
      return new Response(readableStream, {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    } catch (error) {
      return new Response(JSON.stringify({ 
        message: error.message || "服务器处理请求失败"
      }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }
  } catch (error) {
    console.error("API错误:", error);
    return new Response(JSON.stringify({ message: "Internal Server Error", error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}

export async function GET() {
  return new Response(JSON.stringify({ message: "GET method not supported" }), {
    status: 405,
    headers: { "Content-Type": "application/json" },
  });
}
