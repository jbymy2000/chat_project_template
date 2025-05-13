/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable react-hooks/exhaustive-deps */
"use client";

import {
    createContext,
    ReactNode,
    useContext,
    useEffect,
    useState,
} from "react";
import { checkAuthStatus, DEFAULT_TIMEOUT, getCurrentUser } from "../lib/api";

interface User {
    user_id: number;
    username: string;
    email?: string;
    phone_number?: string;
}

interface AuthContextType {
    isAuthenticated: boolean;
    loading: boolean;
    user: User | null;
    login: (token: string) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState<User | null>(null);

    // 检查认证状态并获取用户信息的函数
    const checkAuthAndFetchUser = async () => {
        try {
            setLoading(true);
            // 添加超时处理，防止在后端不可用时长时间等待
            const controller = new AbortController();
            const timeoutId = setTimeout(
                () => controller.abort(),
                DEFAULT_TIMEOUT
            );

            try {
                const { isAuthenticated } = await checkAuthStatus();
                clearTimeout(timeoutId);
                setIsAuthenticated(isAuthenticated);

                if (isAuthenticated) {
                    try {
                        const userData = await getCurrentUser();
                        setUser(userData);
                    } catch (error) {
                        console.error("获取用户数据失败:", error);
                        // 如果获取用户数据失败，我们可以选择登出用户
                        logout();
                    }
                } else {
                    setUser(null);
                }
            } catch (error: any) {
                clearTimeout(timeoutId);
                console.error("认证检查失败:", error);
                // 如果是AbortError，表示请求超时，可能是后端不可用
                if (error.name === "AbortError") {
                    console.warn("认证检查超时，后端可能不可用");
                }
                setIsAuthenticated(false);
                setUser(null);
            }
        } catch (error) {
            console.error("认证检查失败:", error);
            setIsAuthenticated(false);
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    // 组件挂载时进行认证检查
    useEffect(() => {
        checkAuthAndFetchUser();
    }, []);

    const login = (token: string) => {
        localStorage.setItem("auth_token", token);
        setIsAuthenticated(true);
        // 登录后立即获取用户信息
        checkAuthAndFetchUser();
    };

    const logout = () => {
        localStorage.removeItem("auth_token");
        setIsAuthenticated(false);
        setUser(null);
    };

    return (
        <AuthContext.Provider
            value={{ isAuthenticated, loading, user, login, logout }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth 必须在 AuthProvider 内部使用");
    }
    return context;
}
