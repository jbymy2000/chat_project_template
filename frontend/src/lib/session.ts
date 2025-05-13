import { getIronSession } from "iron-session";
import 'server-only';

// 定义会话类型
export interface SessionData {
    uid?: string;
}

// 定义会话配置
export const sessionOptions = {
    password: process.env.SESSION_PASSWORD || "complex_password_at_least_32_characters_long",
    cookieName: "user-session",
    cookieOptions: {
        secure: process.env.NODE_ENV === "production",
    },
};

// 旧版获取会话函数 - 用于传统API路由
export async function getSession(req: Request, res: Response) {
    const session = await getIronSession<SessionData>(req, res, sessionOptions);
    return session;
} 

export interface AppSession {
  uid: string;
  token?: string;
}

// 获取应用会话信息
export async function getAppSession(): Promise<AppSession> {
  try {
    // 在实际环境中，这里应该从cookie或请求头中获取会话信息
    // 在这个简化实现中，我们从localStorage中获取
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      const user = localStorage.getItem('user');
      
      if (token && user) {
        try {
          const userData = JSON.parse(user);
          return {
            uid: userData.username || '',
            token
          };
        } catch (e) {
          console.error('解析用户数据失败:', e);
        }
      }
    }
    
    // 如果无法获取会话信息，返回空会话
    return { uid: '' };
  } catch (error) {
    console.error('获取会话信息失败:', error);
    return { uid: '' };
  }
} 