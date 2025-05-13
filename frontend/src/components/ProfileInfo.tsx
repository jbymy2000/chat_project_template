"use client";

import { useEffect, useState } from "react";
import { UserProfile, getCurrentUserProfile } from "../lib/api";

interface ProfileInfoProps {
    onClick?: () => void;
    refreshTrigger?: number; // 添加刷新触发器，可以从外部触发重新加载
}

export default function ProfileInfo({
    onClick,
    refreshTrigger = 0,
}: ProfileInfoProps) {
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchUserProfile();
    }, [refreshTrigger]); // 当refreshTrigger变化时重新获取数据

    const fetchUserProfile = async () => {
        try {
            setLoading(true);
            const data = await getCurrentUserProfile();
            setProfile(data); // 如果data为null，也正常设置
        } catch (err) {
            console.error("获取用户信息失败:", err);
            // 错误时设置profile为null，不再重试
            setProfile(null);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <span
                className="text-xs text-gray-500 border-b border-dashed border-gray-300 cursor-pointer mr-4"
                onClick={onClick}
            >
                加载中...
            </span>
        );
    }

    if (!profile) {
        return (
            <span
                className="text-xs text-gray-500 border-b border-dashed border-gray-300 cursor-pointer mr-4"
                onClick={onClick}
            >
                点击设置用户信息
            </span>
        );
    }

    const displayText = [
        profile.province || "未设置省份",
        profile.score ? `${profile.score}分` : "未设置分数",
        profile.subject_choice?.length
            ? profile.subject_choice.join(",")
            : "未选择科目",
    ].join(" | ");

    return (
        <span
            className="text-xs text-gray-500 border-b border-dashed border-gray-300 cursor-pointer mr-4"
            onClick={onClick}
        >
            {displayText}
        </span>
    );
}
