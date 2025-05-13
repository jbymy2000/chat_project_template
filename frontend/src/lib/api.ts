/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-unused-vars */
import config from '../../config.json';

// API基础URL
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? config.production.apiBaseUrl 
  : config.development.apiBaseUrl;

// 默认请求超时时间（毫秒）
export const DEFAULT_TIMEOUT = 15000;

// 创建带有认证头的请求配置
export function createAuthenticatedRequestConfig(method: string = 'GET', body?: any, timeout: number = DEFAULT_TIMEOUT): RequestInit {
  const token = localStorage.getItem('auth_token');
  const headers: HeadersInit = {
    'Authorization': `Bearer ${token}`,
  };
  
  if (body && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  
  const config: RequestInit = {
    method,
    headers,
    signal: AbortSignal.timeout(timeout), // 添加超时信号
  };
  
  if (body) {
    if (body instanceof FormData) {
      config.body = body;
    } else {
      config.body = JSON.stringify(body);
    }
  }
  
  return config;
}

// 发送带认证的请求
export async function fetchWithAuth(endpoint: string, config: RequestInit) {
  try {
    const response: Response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    if (!response.ok) {
      // 如果是401错误，可以在这里处理登出逻辑
      if (response.status === 401) {
        localStorage.removeItem('auth_token');
        window.location.href = '/auth';
        throw new Error('认证失效，请重新登录');
      }
      
      // 特殊处理用户档案不存在的情况
      if (endpoint === '/profile/me' && (response.status === 404 || response.status === 422)) {
        console.warn('用户档案不存在，返回null');
        return null;
      }
      
      // 尝试解析错误响应
      try {
        const errorData = await response.json();
        throw new Error(errorData.detail || `错误: ${response.status}`);
      } catch (parseError) {
        // 如果无法解析JSON，则直接使用状态码
        throw new Error(`请求失败，状态码: ${response.status}`);
      }
    }
    
    return await response.json();
  } catch (error) {
    console.error('API请求错误:', error);
    throw error;
  }
}

// 用户注册
export async function registerUser(userData: {
  username: string;
  password: string;
  email: string;
  phone_number: string;
}) {
  try {
    const response: Response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '注册失败');
    }

    return await response.json();
  } catch (error) {
    console.error('注册错误:', error);
    throw error;
  }
}

// 用户登录
export async function loginUser(credentials: {
  username: string;
  password: string;
}) {
  try {
    // 创建表单数据
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response: Response = await fetch(`${API_BASE_URL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '登录失败');
    }

    return await response.json();
  } catch (error) {
    console.error('登录错误:', error);
    throw error;
  }
}

// 获取当前用户信息
export async function getCurrentUser() {
  const config = createAuthenticatedRequestConfig('GET');
  return fetchWithAuth('/auth/me', config);
}

// 验证令牌有效性
async function verifyToken(token: string): Promise<boolean> {
  try {
    // 尝试使用token发送一个请求来验证令牌有效性
    const response: Response = await fetch(`${API_BASE_URL}/auth/verify`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    return response.ok;
  } catch (error) {
    return false;
  }
}

// 检查用户是否已登录
export async function checkAuthStatus() {
  try {
    const token = localStorage.getItem('auth_token');
    
    if (!token) {
      return { isAuthenticated: false };
    }
    
    // 尝试解析JWT令牌，检查是否过期
    const tokenParts = token.split('.');
    if (tokenParts.length !== 3) {
      localStorage.removeItem('auth_token');
      return { isAuthenticated: false };
    }
    
    try {
      const payload = JSON.parse(atob(tokenParts[1]));
      const expiration = payload.exp * 1000; // 转换为毫秒
      
      if (Date.now() >= expiration) {
        // 令牌已过期
        localStorage.removeItem('auth_token');
        return { isAuthenticated: false };
      }
      
      // 只有在前端验证通过后，才尝试访问后端API进行验证
      try {
        // 设置超时
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);
        
        const response = await fetch(`${API_BASE_URL}/auth/verify`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          localStorage.removeItem('auth_token');
          return { isAuthenticated: false };
        }
        
        return { isAuthenticated: true };
      } catch (error) {
        console.warn('后端API验证失败，使用本地令牌验证:', error);
        // 如果后端API不可用，但令牌在前端验证有效，仍然允许用户登录
        // 这可以防止在后端不可用时用户被强制登出
        return { isAuthenticated: true };
      }
    } catch (e) {
      localStorage.removeItem('auth_token');
      return { isAuthenticated: false };
    }
  } catch (error) {
    console.error('认证检查错误:', error);
    return { isAuthenticated: false };
  }
}

// ---------- 用户档案相关API ----------

export interface UserProfile {
  user_id?: number;
  gender: string;
  province?: string;
  exam_year?: number;
  subject_choice?: string[];
  score?: number;
  rank?: number;
  batch?: string;
  requirement?: string;
  updated_at?: string;
}

// 获取当前用户档案
export async function getCurrentUserProfile() {
  const config = createAuthenticatedRequestConfig('GET');
  return fetchWithAuth('/profile/me', config);
}

// 获取指定用户档案
export async function getUserProfile(userId: number) {
  const config = createAuthenticatedRequestConfig('GET');
  return fetchWithAuth(`/profile/${userId}`, config);
}

// 创建用户档案
export async function createUserProfile(userId: number, profileData: UserProfile) {
  const config = createAuthenticatedRequestConfig('POST', profileData);
  return fetchWithAuth(`/profile/${userId}`, config);
}

// 更新用户档案
export async function updateUserProfile(userId: number, profileData: UserProfile) {
  const config = createAuthenticatedRequestConfig('PUT', profileData);
  return fetchWithAuth(`/profile/${userId}`, config);
}

// 更新用户需求
export async function updateUserRequirement(userId: number, requirement: string) {
  const config = createAuthenticatedRequestConfig('PUT', { requirement });
  return fetchWithAuth(`/profile/${userId}/requirement`, config);
}

// ---------- 话题相关API ----------

export interface Topic {
  topic_id: number;
  user_id: number;
  topic: string;
  started_at: string;
  updated_at: string;
}

export interface Message {
  message_id: number;
  topic_id: number;
  user_id: number;
  message_type: string;
  content: string;
  created_at: string;
}

// 创建新话题
export async function createTopic(topicName: string) {
  const config = createAuthenticatedRequestConfig('POST', { topic: topicName });
  return fetchWithAuth('/topics', config);
}

// 获取用户话题列表
export async function getUserTopics() {
  const config = createAuthenticatedRequestConfig('GET');
  return fetchWithAuth('/topics', config);
}

// 获取话题消息
export async function getTopicMessages(topicId: number) {
  const config = createAuthenticatedRequestConfig('GET');
  return fetchWithAuth(`/topics/${topicId}/messages`, config);
}

// 创建用户消息
export async function createMessage(topicId: number, content: string) {
  const config = createAuthenticatedRequestConfig('POST', { content });
  return fetchWithAuth(`/topics/${topicId}/messages`, config);
}

// 创建AI消息（通常由后端调用，但可能在某些情况下需要手动调用）
export async function createAIMessage(topicId: number, content: string) {
  const config = createAuthenticatedRequestConfig('POST', { content, message_type: 'ai' });
  return fetchWithAuth(`/topics/${topicId}/messages`, config);
}

// 发送流式对话请求
export async function streamChat(topicId: number, message: string, token?: string): Promise<Response> {
  // 如果提供了token参数则使用它，否则从localStorage获取
  const authToken = token || (typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null);
  
  if (!authToken) {
    throw new Error('认证令牌不存在，请先登录');
  }
  
  return fetch(`${API_BASE_URL}/topics/${topicId}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`,
    },
    body: JSON.stringify({ message }),
  });
}

// 处理流式聊天响应
export async function processChatStream(response: Response): Promise<ReadableStream> {
  if (!response.ok) {
    const error = await response.text();
    console.error(`后端服务响应错误: ${response.status}`, error);
    throw new Error(`服务器处理请求失败: ${error}`);
  }

  const { readable, writable } = new TransformStream();
  const reader = response.body!.getReader();
  
  (async () => {
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        // 将Uint8Array转换为字符串
        const chunk = new TextDecoder().decode(value);
        
        // 处理SSE格式的数据
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.trim() === '') continue;
          
          // 尝试解析数据行
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              // 发送到客户端
              const writer = writable.getWriter();
              await writer.write(new TextEncoder().encode(JSON.stringify({
                type: data.type,
                content: data.content
              }) + '\n'));
              writer.releaseLock();
            } catch (e) {
              console.error('解析SSE数据失败:', e);
            }
          }
        }
      }
      
      // 关闭流
      const writer = writable.getWriter();
      await writer.close();
    } catch (error) {
      console.error('处理流时出错:', error);
      const writer = writable.getWriter();
      await writer.abort(error);
    }
  })();
  
  return readable;
}

// ---------- 专家数据相关API ----------

export interface SpecialistResponse {
  data: any[];
  pagination: {
    total: number;
    page: number;
    page_size: number;
    pages: number;
  };
}

export interface SpecialistQueryParams {
  page?: number;
  page_size?: number;
  filters?: string;
  sort_by?: string;
  sort_order?: string;
  province_name?: string;
}

// 获取专家列表数据
export async function getSpecialists(params: SpecialistQueryParams = {}): Promise<SpecialistResponse> {
  const queryParams = new URLSearchParams();
  
  // 添加查询参数
  if (params.page) queryParams.append('page', params.page.toString());
  if (params.page_size) queryParams.append('page_size', params.page_size.toString());
  if (params.filters) queryParams.append('filters', params.filters);
  if (params.sort_by) queryParams.append('sort_by', params.sort_by);
  if (params.sort_order) queryParams.append('sort_order', params.sort_order);
  if (params.province_name) queryParams.append('province_name', params.province_name);
  
  const queryString = queryParams.toString();
  const endpoint = `/data/specialist${queryString ? `?${queryString}` : ''}`;
  
  const config = createAuthenticatedRequestConfig('GET');
  return fetchWithAuth(endpoint, config);
}

// 获取专家详情
export async function getSpecialistById(id: string) {
  const config = createAuthenticatedRequestConfig('GET');
  return fetchWithAuth(`/data/specialist/${id}`, config);
}

// ---------- 分数排名相关API ----------

export interface ScoreRankItem {
    minScore: number;
    maxScore: number;
    sameCount: number;
    lowestRank: number;
    highestRank: number;
}

export interface ScoreRankResponse {
    data: ScoreRankItem[];
    province_name: string;
    batch: string;
}

export interface EquivalentRankRequest {
    province_name: string;
    batch: string;
    score: number;
}

export interface EquivalentRankResponse {
    rank: number;
    score_range: {
        min: number;
        max: number;
    };
    same_count: number;
}

// 获取分数排名数据
export async function getScoreRank(params: {
    province_name: string;
    year: number;
    batch?: string;
}): Promise<ScoreRankResponse> {
    const queryParams = new URLSearchParams();
    queryParams.append('province_name', params.province_name);
    queryParams.append('year', params.year.toString());
    if (params.batch) {
        queryParams.append('batch', params.batch);
    }
    
    const queryString = queryParams.toString();
    const endpoint = `/data/specialist/score-rank?${queryString}`;
    
    const config = createAuthenticatedRequestConfig('GET');
    return fetchWithAuth(endpoint, config);
}

// 计算等效位次
export async function calculateEquivalentRank(params: EquivalentRankRequest): Promise<EquivalentRankResponse> {
    const config = createAuthenticatedRequestConfig('POST', params);
    return fetchWithAuth('/data/specialist/equivalent-rank', config);
}

export interface College {
    id: string;
    num_id: string;
    code: string;
    gb_code: string;
    cn_name: string;
    logo_url: string;
    province_name: string;
    city_name: string;
    nature_type: string;
    edu_level: string;
    categories: string[];
    features: string[];
    star: string;
    ranking_of_rk: number;
    ranking_of_xyh: number;
    web_site: string;
    address?: string;
    zhao_ban_dh?: string;
    zhao_ban_email?: string;
    college_address?: { name: string; address: string; coordinate: string }[];
    introduction?: string;
}

export interface CollegeListResponse {
    code: number;
    message: string;
    data: {
        total: number;
        items: College[];
    };
}

export async function getCollegeList(
    page: number = 1,
    pageSize: number = 10,
    cn_name?: string,
    province_name?: string[],
    categories?: string[],
    features?: string[],
    nature_type?: string[]
): Promise<CollegeListResponse> {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());
    if (cn_name) {
        params.append('cn_name', cn_name);
    }
    if (province_name && province_name.length > 0) {
        params.append('province_name', province_name.join(','));
    }
    if (categories && categories.length > 0) {
        params.append('categories', categories.join(','));
    }
    if (features && features.length > 0) {
        params.append('features', features.join(','));
    }
    if (nature_type && nature_type.length > 0) {
        params.append('nature_type', nature_type.join(','));
    }
    const response = await fetch(
        `${API_BASE_URL}/data/specialist/colleges?${params.toString()}`,
        {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
        }
    );

    if (!response.ok) {
        throw new Error("获取大学列表失败");
    }

    return response.json();
}

export async function getCollegeDetail(code: string): Promise<College> {
    const response = await fetch(`${API_BASE_URL}/data/specialist/colleges/${code}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
        credentials: "include",
    });
    if (!response.ok) {
        if (response.status === 404) {
            throw new Error("未找到该院校信息");
        }
        throw new Error("获取院校详情失败");
    }
    const res = await response.json();
    if (res.code !== 200 || !res.data) {
        throw new Error(res.message || "获取院校详情失败");
    }
    return res.data;
}

// 获取专业版本列表
export async function getProfessionVersions(params: Record<string, any>) {
    const query = new URLSearchParams(params).toString();
    const config = createAuthenticatedRequestConfig('GET');
    const res = await fetchWithAuth(`/data/specialist/profession-versions?${query}`, config);
    return res;
}

// 获取专业组聚合列表
export async function getProfessionGroups(params: Record<string, any>) {
    const query = new URLSearchParams(params).toString();
    const config = createAuthenticatedRequestConfig('GET');
    const res = await fetchWithAuth(`/data/specialist/profession-groups?${query}`, config);
    return res;
}

export async function getProfessionList(params: any) {
    const queryString = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
            if (Array.isArray(value)) {
                // 多选参数用逗号分隔
                queryString.append(key, value.join(','));
            } else {
                queryString.append(key, String(value));
            }
        }
    });
    const config = createAuthenticatedRequestConfig('GET');
    const response = await fetchWithAuth(
        `/data/specialist/professions?${queryString.toString()}`,
        config
    );
    return response;
} 