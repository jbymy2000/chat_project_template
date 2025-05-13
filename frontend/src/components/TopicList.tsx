"use client";

import { MenuFoldOutlined, PlusCircleOutlined } from "@ant-design/icons";
import { Button, List, Tooltip, Typography } from "antd";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { useNotification } from "../contexts/NotificationContext";
import { Topic, getUserTopics } from "../lib/api";

const { Text } = Typography;

interface TopicListProps {
    onSelectTopic: (topicId: number) => void;
    activeTopic?: number;
    onCollapse?: () => void;
}

// 定义时间分组类型
interface TimeGroup {
    title: string;
    topics: Topic[];
}

export default function TopicList({
    onSelectTopic,
    activeTopic,
    onCollapse = () => {},
}: TopicListProps) {
    const [topics, setTopics] = useState<Topic[]>([]);
    const [groupedTopics, setGroupedTopics] = useState<TimeGroup[]>([]);
    const { showNotification } = useNotification();
    const router = useRouter();

    const fetchTopics = useCallback(async () => {
        try {
            const data = await getUserTopics();
            setTopics(data);
        } catch (error) {
            console.error("获取话题列表失败:", error);
            showNotification("error", "获取话题列表失败");
        }
    }, [showNotification]);

    useEffect(() => {
        fetchTopics();
    }, []);

    // 根据话题更新时间对话题进行分组
    useEffect(() => {
        if (topics.length > 0) {
            // 获取当前日期
            const now = new Date();

            // 计算日期边界
            const today = new Date(
                now.getFullYear(),
                now.getMonth(),
                now.getDate()
            );
            const threeDaysAgo = new Date(today);
            threeDaysAgo.setDate(today.getDate() - 3);
            const sevenDaysAgo = new Date(today);
            sevenDaysAgo.setDate(today.getDate() - 7);
            const oneMonthAgo = new Date(today);
            oneMonthAgo.setMonth(today.getMonth() - 1);
            const sixMonthsAgo = new Date(today);
            sixMonthsAgo.setMonth(today.getMonth() - 6);

            // 初始化分组
            const groups: TimeGroup[] = [
                { title: "今天", topics: [] },
                { title: "最近三天", topics: [] },
                { title: "最近一周", topics: [] },
                { title: "最近一个月", topics: [] },
                { title: "最近半年", topics: [] },
                { title: "更早", topics: [] },
            ];

            // 对话题进行分组
            topics.forEach((topic) => {
                const topicDate = new Date(topic.updated_at);

                if (topicDate >= today) {
                    groups[0].topics.push(topic);
                } else if (topicDate >= threeDaysAgo) {
                    groups[1].topics.push(topic);
                } else if (topicDate >= sevenDaysAgo) {
                    groups[2].topics.push(topic);
                } else if (topicDate >= oneMonthAgo) {
                    groups[3].topics.push(topic);
                } else if (topicDate >= sixMonthsAgo) {
                    groups[4].topics.push(topic);
                } else {
                    groups[5].topics.push(topic);
                }
            });

            // 过滤掉没有话题的分组
            const filteredGroups = groups.filter(
                (group) => group.topics.length > 0
            );

            // 每个分组内部按照更新时间降序排序（最新的在前）
            filteredGroups.forEach((group) => {
                group.topics.sort(
                    (a, b) =>
                        new Date(b.updated_at).getTime() -
                        new Date(a.updated_at).getTime()
                );
            });

            setGroupedTopics(filteredGroups);
        } else {
            setGroupedTopics([]);
        }
    }, [topics]);

    const handleTopicClick = (topicId: number) => {
        onSelectTopic(topicId);
        router.push(`/qihang/ai/${topicId}`, { scroll: false });
    };

    return (
        <div className="bg-white border-r border-gray-200 w-64 h-full flex flex-col">
            <div className="p-1 border-b border-gray-200 flex justify-between items-center">
                <Tooltip title="收起侧边栏">
                    <Button
                        type="text"
                        icon={<MenuFoldOutlined />}
                        size="small"
                        onClick={onCollapse}
                    />
                </Tooltip>
                <Tooltip title="创建新聊天">
                    <Button
                        type="text"
                        icon={<PlusCircleOutlined />}
                        size="small"
                        onClick={() => {
                            router.push("/qihang/ai", { scroll: false });
                            window.dispatchEvent(
                                new CustomEvent("resetChatArea")
                            );
                        }}
                    />
                </Tooltip>
            </div>

            <div className="flex-1 overflow-y-auto">
                {groupedTopics.map((group, groupIndex) => (
                    <div key={groupIndex} className="mb-4">
                        <div className="px-4 py-2">
                            <Text type="secondary" className="text-sm">
                                {group.title}
                            </Text>
                        </div>
                        <List
                            dataSource={group.topics}
                            size="small"
                            split={false}
                            renderItem={(topic) => (
                                <List.Item
                                    key={topic.topic_id}
                                    onClick={() =>
                                        handleTopicClick(topic.topic_id)
                                    }
                                    className={`cursor-pointer px-4 py-2 ${
                                        activeTopic === topic.topic_id
                                            ? "bg-blue-50 border-l-2 border-blue-500"
                                            : "hover:bg-gray-50"
                                    }`}
                                >
                                    <List.Item.Meta
                                        title={
                                            <Text
                                                ellipsis
                                                className="text-sm"
                                                style={{ margin: 0 }}
                                            >
                                                {topic.topic}
                                            </Text>
                                        }
                                    />
                                </List.Item>
                            )}
                        />
                    </div>
                ))}
            </div>
        </div>
    );
}
