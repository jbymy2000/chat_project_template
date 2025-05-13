"use client";

import { useState } from "react";
import { loginUser } from "../lib/api";

interface LoginFormProps {
    onLoginSuccess: (token: string) => void;
    onRegisterClick: () => void;
}

export default function LoginForm({
    onLoginSuccess,
    onRegisterClick,
}: LoginFormProps) {
    const [credentials, setCredentials] = useState({
        username: "",
        password: "",
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setCredentials((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const data = await loginUser(credentials);
            // 假设API返回包含token的数据
            if (data.access_token) {
                localStorage.setItem("auth_token", data.access_token);
                onLoginSuccess(data.access_token);
            }
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "登录失败，请检查用户名和密码"
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full max-w-md mx-auto">
            <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
                <h2 className="text-2xl font-bold mb-6 text-center">
                    用户登录
                </h2>

                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded mb-4">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label
                            className="block text-gray-700 text-sm font-bold mb-2"
                            htmlFor="username"
                        >
                            用户名
                        </label>
                        <input
                            id="username"
                            name="username"
                            type="text"
                            value={credentials.username}
                            onChange={handleChange}
                            required
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        />
                    </div>

                    <div className="mb-6">
                        <label
                            className="block text-gray-700 text-sm font-bold mb-2"
                            htmlFor="password"
                        >
                            密码
                        </label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            value={credentials.password}
                            onChange={handleChange}
                            required
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        />
                    </div>

                    <div className="flex items-center justify-between">
                        <button
                            type="submit"
                            disabled={loading}
                            className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ${
                                loading ? "opacity-50 cursor-not-allowed" : ""
                            }`}
                        >
                            {loading ? "登录中..." : "登录"}
                        </button>

                        <button
                            type="button"
                            onClick={onRegisterClick}
                            className="inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800"
                        >
                            没有账号？注册
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
