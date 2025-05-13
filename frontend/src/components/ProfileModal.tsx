"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNotification } from "../contexts/NotificationContext";
import {
    UserProfile,
    calculateEquivalentRank,
    createUserProfile,
    getCurrentUserProfile,
    updateUserProfile,
} from "../lib/api";

interface ProfileModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
}

const provinces = [
    "北京",
    "上海",
    "广东",
    "江苏",
    "浙江",
    "山东",
    "河南",
    "四川",
    "湖北",
    "湖南",
    "安徽",
    "河北",
];

const batches = ["本科", "专科"];

const subjects = ["物理", "化学", "生物", "政治", "历史", "地理"];

export default function ProfileModal({
    isOpen,
    onClose,
    onSuccess,
}: ProfileModalProps) {
    const { user } = useAuth();
    const { showNotification } = useNotification();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [profile, setProfile] = useState<UserProfile>({
        gender: "other",
        province: "",
        exam_year: 2025,
        subject_choice: ["物理", "化学", "生物"],
        score: 500,
        rank: undefined,
        batch: undefined,
    });

    // 获取用户档案
    const fetchUserProfile = useCallback(async () => {
        if (!user) return;

        try {
            setLoading(true);
            setError("");
            try {
                const data = await getCurrentUserProfile();
                if (data) {
                    setProfile({
                        gender: data.gender || "other",
                        province: data.province || "",
                        exam_year: data.exam_year,
                        subject_choice: data.subject_choice || [],
                        score: data.score,
                        rank: data.rank,
                        batch: data.batch,
                    });
                } else {
                    // 如果获取用户档案返回null，表示档案不存在
                    console.log("用户档案不存在，设置默认值");
                    setProfile({
                        gender: "other",
                        province: "",
                        exam_year: 2025,
                        subject_choice: ["物理", "化学", "生物"],
                        score: 500,
                        rank: undefined,
                        batch: undefined,
                    });
                }
            } catch (err) {
                console.error("获取用户档案失败:", err);
                // 如果获取用户档案失败，可能是因为档案不存在
                // 设置默认值，保存时会自动创建新档案
                setProfile({
                    gender: "other",
                    province: "",
                    exam_year: 2025,
                    subject_choice: ["物理", "化学", "生物"],
                    score: 500,
                    rank: undefined,
                    batch: undefined,
                });
            }
        } finally {
            setLoading(false);
        }
    }, [user]);

    // 计算等效位次
    const calculateRank = useCallback(async () => {
        if (!profile.province || !profile.batch || !profile.score) {
            return;
        }

        try {
            const result = await calculateEquivalentRank({
                province_name: profile.province,
                batch: profile.batch,
                score: profile.score,
            });

            setProfile((prev) => ({
                ...prev,
                rank: result.rank,
            }));
        } catch (err) {
            console.error("计算等效位次失败:", err);
            showNotification("error", "计算等效位次失败，请稍后重试");
        }
    }, [profile.province, profile.batch, profile.score, showNotification]);

    // 当省份、批次或分数变化时，自动计算位次
    useEffect(() => {
        if (profile.province && profile.batch && profile.score) {
            calculateRank();
        }
    }, [profile.province, profile.batch, profile.score, calculateRank]);

    useEffect(() => {
        if (isOpen && user) {
            fetchUserProfile();
        }
    }, [isOpen, user, fetchUserProfile]);

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        const { name, value } = e.target;
        setProfile((prev) => ({
            ...prev,
            [name]:
                name === "score" || name === "exam_year"
                    ? value
                        ? Number(value)
                        : undefined
                    : value,
        }));
    };

    const handleSubjectChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { value, checked } = e.target;
        setProfile((prev) => {
            const subjects = prev.subject_choice || [];
            if (checked) {
                return { ...prev, subject_choice: [...subjects, value] };
            } else {
                return {
                    ...prev,
                    subject_choice: subjects.filter((s) => s !== value),
                };
            }
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!user) return;

        try {
            setLoading(true);
            setError("");
            setSuccess("");

            // 准备提交的数据
            const profileData = {
                ...profile,
                user_id: user.user_id,
                batch: profile.batch || null, // 确保 batch 字段被包含
                rank: profile.rank || null, // 确保 rank 字段被包含
            };

            let successMessage = "";

            // 尝试更新用户档案，如果失败则尝试创建
            try {
                await updateUserProfile(user.user_id, profileData);
                successMessage = "个人信息更新成功！";
            } catch (err) {
                console.error("更新用户档案失败，尝试创建新档案:", err);
                try {
                    await createUserProfile(user.user_id, profileData);
                    successMessage = "个人信息创建成功！";
                } catch (createErr) {
                    console.error("创建用户档案失败:", createErr);
                    setError("无法保存用户信息，请稍后再试");
                    return;
                }
            }

            // 立即调用成功回调并关闭modal
            if (onSuccess) {
                onSuccess();
            } else {
                onClose();
            }

            // 显示成功通知
            showNotification("success", successMessage);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold">用户信息设置</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-700"
                    >
                        ✕
                    </button>
                </div>

                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded mb-4">
                        {error}
                    </div>
                )}

                {success && (
                    <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded mb-4">
                        {success}
                    </div>
                )}

                {loading ? (
                    <div className="flex justify-center py-8">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit}>
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                性别
                            </label>
                            <select
                                name="gender"
                                value={profile.gender || "other"}
                                onChange={handleInputChange}
                                className="w-full border border-gray-300 rounded-md p-2"
                            >
                                <option value="male">男</option>
                                <option value="female">女</option>
                                <option value="other">其他</option>
                            </select>
                        </div>

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                高考年份
                            </label>
                            <input
                                type="number"
                                name="exam_year"
                                value={profile.exam_year || ""}
                                onChange={handleInputChange}
                                placeholder="请输入高考年份，例如：2024"
                                className="w-full border border-gray-300 rounded-md p-2"
                            />
                        </div>

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                省份
                            </label>
                            <select
                                name="province"
                                value={profile.province || ""}
                                onChange={handleInputChange}
                                className="w-full border border-gray-300 rounded-md p-2"
                            >
                                <option value="">请选择省份</option>
                                {provinces.map((province) => (
                                    <option key={province} value={province}>
                                        {province}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                批次
                            </label>
                            <select
                                name="batch"
                                value={profile.batch || ""}
                                onChange={handleInputChange}
                                className="w-full border border-gray-300 rounded-md p-2"
                            >
                                <option value="">请选择批次</option>
                                {batches.map((batch) => (
                                    <option key={batch} value={batch}>
                                        {batch}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                高考分数
                            </label>
                            <input
                                type="number"
                                name="score"
                                value={profile.score || ""}
                                onChange={handleInputChange}
                                placeholder="请输入高考分数"
                                className="w-full border border-gray-300 rounded-md p-2"
                            />
                        </div>

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                等效位次
                            </label>
                            <div className="flex gap-2">
                                <input
                                    type="number"
                                    name="rank"
                                    value={profile.rank || ""}
                                    onChange={handleInputChange}
                                    placeholder="请输入或等待自动计算"
                                    className="flex-1 border border-gray-300 rounded-md p-2"
                                />
                                <button
                                    type="button"
                                    onClick={calculateRank}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                                    disabled={
                                        !profile.province ||
                                        !profile.batch ||
                                        !profile.score
                                    }
                                >
                                    计算
                                </button>
                            </div>
                            <p className="text-sm text-gray-500 mt-1">
                                填写省份、批次和分数后会自动计算，也可以手动输入
                            </p>
                        </div>

                        <div className="mb-6">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                选考科目
                            </label>
                            <div className="grid grid-cols-2 gap-2">
                                {subjects.map((subject) => (
                                    <label
                                        key={subject}
                                        className="flex items-center"
                                    >
                                        <input
                                            type="checkbox"
                                            value={subject}
                                            checked={(
                                                profile.subject_choice || []
                                            ).includes(subject)}
                                            onChange={handleSubjectChange}
                                            className="mr-2"
                                        />
                                        {subject}
                                    </label>
                                ))}
                            </div>
                        </div>

                        <div className="flex justify-end space-x-2">
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                                disabled={loading}
                            >
                                取消
                            </button>
                            <button
                                type="submit"
                                className={`px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 ${
                                    loading
                                        ? "opacity-50 cursor-not-allowed"
                                        : ""
                                }`}
                                disabled={loading}
                            >
                                {loading ? "保存中..." : "保存"}
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
}
