"use client";
import Message from "@/components/message";
import Prompt from "@/components/prompt";
import TopicList from "@/components/TopicList";
import { useNotification } from "@/contexts/NotificationContext";
import {
    createAIMessage,
    createMessage,
    createTopic,
    getTopicMessages,
} from "@/lib/api";
import { MenuUnfoldOutlined } from "@ant-design/icons";
import { Button } from "antd";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";

// 消息类型定义
interface MessageType {
    id: string;
    author: string;
    avatar: string;
    text: string;
    reasoning?: string;
    isTyping?: boolean;
}

// 话题消息类型
interface TopicMessage {
    message_id: number;
    message_type: string;
    content: string;
}

export default function AiPage() {
    const [messages, setMessages] = useState<MessageType[]>([]);
    const [activeTopic, setActiveTopic] = useState<number | null>(null);
    const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
    const [isProcessing, setIsProcessing] = useState<boolean>(false);
    const { showNotification } = useNotification();
    const chatRef = useRef<HTMLDivElement>(null);
    const router = useRouter();
    const params = useParams();

    // 加载话题历史消息
    const loadTopicMessages = useCallback(
        async (topicId: number) => {
            try {
                const topicMessages = await getTopicMessages(topicId);

                // 将后端消息格式转换为前端显示格式
                const formattedMessages = topicMessages.map(
                    (msg: TopicMessage) => ({
                        id: `${msg.message_id}`,
                        author: msg.message_type === "user" ? "human" : "ai",
                        avatar:
                            msg.message_type === "user"
                                ? "/Avatar2.avif"
                                : "/logo-open-ai.png",
                        text: msg.content,
                        reasoning: msg.message_type === "ai" ? "" : undefined,
                        isTyping: false,
                    })
                );

                setMessages(formattedMessages);
            } catch (error) {
                console.error("加载话题消息失败:", error);
                showNotification("error", "加载对话历史失败");
            }
        },
        [showNotification]
    );

    const handleSelectTopic = (topicId: number) => {
        setActiveTopic(topicId);
    };

    const handleCollapseSidebar = () => {
        setSidebarCollapsed(!sidebarCollapsed);
    };

    // 提交消息处理函数
    const onSubmit = useCallback(
        async (prompt: string) => {
            if (prompt.trim().length === 0) {
                return;
            }

            // 设置处理状态为true，禁止连续发送
            setIsProcessing(true);

            try {
                // 如果没有选中话题，先创建一个新话题
                if (!activeTopic) {
                    try {
                        const topicName =
                            prompt.length > 200
                                ? prompt.substring(0, 200) + "..."
                                : prompt;
                        const newTopic = await createTopic(topicName);

                        // 修改：不使用localStorage存储消息，而是通过URL参数传递
                        const newUrl = `/qihang/ai/${
                            newTopic.topic_id
                        }?message=${encodeURIComponent(prompt)}`;
                        router.push(newUrl);
                        return;
                    } catch (error) {
                        console.error("创建话题失败:", error);
                        showNotification("error", "创建话题失败，请稍后再试");
                        setIsProcessing(false);
                        return;
                    }
                }
                console.log("activeTopic", activeTopic);
                // 使用时间戳加随机数生成唯一ID
                const generateUniqueId = () => {
                    return `${Date.now()}-${Math.random()
                        .toString(36)
                        .substr(2, 9)}`;
                };

                // 添加用户消息到UI
                const userMessageId = generateUniqueId();
                setMessages((messages) => [
                    ...messages,
                    {
                        id: userMessageId,
                        author: "human",
                        avatar: "/Avatar2.avif",
                        text: prompt,
                        isTyping: false,
                    },
                ]);

                // 创建一个新的AI消息占位符
                const aiMessageId = generateUniqueId();
                setMessages((messages) => [
                    ...messages,
                    {
                        id: aiMessageId,
                        author: "ai",
                        avatar: "/logo-open-ai.png",
                        text: "",
                        reasoning: "",
                        isTyping: true,
                    },
                ]);

                // 使用修改后的API接口
                const token = localStorage.getItem("auth_token");
                const response = await fetch("/api/completion", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify({
                        prompt,
                        topicId: activeTopic,
                    }),
                });

                if (!response.ok) {
                    try {
                        // 尝试解析错误响应
                        const errorData = await response.json();
                        console.error("API错误:", errorData);
                        showNotification(
                            "error",
                            errorData.message || "请求失败"
                        );
                    } catch (parseError) {
                        // 如果解析JSON失败，可能是空响应或格式错误
                        console.error("API错误: 无法解析错误响应", parseError);
                        showNotification(
                            "error",
                            "请求失败，服务器返回了无效的响应"
                        );
                    }

                    // 重置处理状态并提前返回
                    setIsProcessing(false);
                    return;
                }

                // 处理事件流响应
                const reader = response.body?.getReader();
                if (!reader) {
                    console.error("无法获取响应流");
                    return;
                }

                let aiResponse = "";
                let reasoningContent = "";

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) {
                        // 流结束，关闭输入状态
                        setMessages((messages) =>
                            messages.map((msg) =>
                                msg.id === aiMessageId
                                    ? {
                                          ...msg,
                                          isTyping: false,
                                      }
                                    : msg
                            )
                        );
                        break;
                    }

                    // 将Uint8Array转换为字符串
                    const chunk = new TextDecoder().decode(value);

                    // 处理SSE格式的数据
                    const lines = chunk.split("\n");
                    for (const line of lines) {
                        if (line.trim() === "") continue;

                        try {
                            const data = JSON.parse(line);

                            // 使用type区分不同类型的响应，这里的类型是由API路由转换后的格式
                            if (data.type === "reasoning") {
                                reasoningContent += data.content;
                                // 更新消息，同时包含思考过程和回答
                                setMessages((messages) =>
                                    messages.map((msg) =>
                                        msg.id === aiMessageId
                                            ? {
                                                  ...msg,
                                                  reasoning: reasoningContent,
                                                  text: aiResponse,
                                                  isTyping: true,
                                              }
                                            : msg
                                    )
                                );
                            } else if (data.type === "answer") {
                                aiResponse += data.content;
                                // 更新消息，同时包含思考过程和回答
                                setMessages((messages) =>
                                    messages.map((msg) =>
                                        msg.id === aiMessageId
                                            ? {
                                                  ...msg,
                                                  reasoning: reasoningContent,
                                                  text: aiResponse,
                                                  isTyping: true,
                                              }
                                            : msg
                                    )
                                );
                            }
                        } catch (error) {
                            console.error("解析响应数据失败:", error);
                        }
                    }
                }

                // 流结束后，先保存用户问题，再保存AI回复到后端
                try {
                    // 确保activeTopic现在有值
                    if (!activeTopic) {
                        throw new Error("话题ID不存在");
                    }

                    // 首先保存用户消息
                    await createMessage(activeTopic, prompt);

                    // 然后保存AI回复
                    if (aiResponse.trim()) {
                        await createAIMessage(activeTopic, aiResponse);
                    }
                } catch (error) {
                    console.error("保存对话消息失败:", error);
                    showNotification("error", "无法保存对话到历史记录");
                }
            } catch (error) {
                console.error("对话请求失败:", error);
                showNotification("error", "对话请求失败，请稍后再试");
            } finally {
                // 处理完成，设置状态为false，允许发送新消息
                setIsProcessing(false);
            }
        },
        [activeTopic, router, showNotification]
    );

    // 设置激活话题
    useEffect(() => {
        const topicIdParam = params?.topicId;
        if (topicIdParam) {
            const topicId = parseInt(topicIdParam as string);
            if (!isNaN(topicId)) {
                setActiveTopic(topicId);
            }
        }
        console.log("activeTopic input", activeTopic);
    }, [params, activeTopic]);

    // 聊天窗口滚动到底部
    useEffect(() => {
        if (chatRef.current) {
            chatRef.current.scrollTo(0, chatRef.current.scrollHeight);
        }
    }, [messages]);

    // 加载话题消息或处理待处理消息
    useEffect(() => {
        if (activeTopic) {
            loadTopicMessages(activeTopic);

            // 检查并处理localStorage中存储的待处理消息
            const pendingMessageStr = localStorage.getItem("pendingMessage");
            if (pendingMessageStr) {
                try {
                    const { prompt } = JSON.parse(pendingMessageStr);
                    if (prompt) {
                        // 调用onSubmit发送消息
                        onSubmit(prompt);
                        // 处理完成后移除localStorage中的数据
                        localStorage.removeItem("pendingMessage");
                    }
                } catch (error) {
                    console.error("解析待处理消息失败:", error);
                }
            }
        } else {
            setMessages([]);
        }
    }, [activeTopic, loadTopicMessages, onSubmit]);

    // 监听重置对话区域的自定义事件
    useEffect(() => {
        const handleResetChatArea = () => {
            // 重置状态
            setActiveTopic(null);
            setMessages([]);
            console.log("对话区域已重置");
        };

        window.addEventListener("resetChatArea", handleResetChatArea);
        return () => {
            window.removeEventListener("resetChatArea", handleResetChatArea);
        };
    }, []);

    // 添加一个处理URL参数的useEffect
    useEffect(() => {
        const processInitialMessage = async () => {
            const query = new URLSearchParams(window.location.search);
            const initialMessage = query.get("message");

            if (initialMessage && activeTopic) {
                await loadTopicMessages(activeTopic);
                const decodedMessage = decodeURIComponent(initialMessage);
                onSubmit(decodedMessage);
                window.history.replaceState(
                    {},
                    "",
                    `${window.location.pathname}`
                );
            }
        };

        processInitialMessage();
    }, [activeTopic]);

    return (
        <div className="flex h-full">
            {/* 左侧话题列表 */}
            {!sidebarCollapsed && (
                <div className="h-full flex-none">
                    <TopicList
                        onSelectTopic={handleSelectTopic}
                        activeTopic={activeTopic || undefined}
                        onCollapse={handleCollapseSidebar}
                    />
                </div>
            )}

            {/* 右侧聊天区域 */}
            <div className="flex flex-col flex-grow">
                {sidebarCollapsed && (
                    <div className="p-2">
                        <Button
                            type="text"
                            icon={<MenuUnfoldOutlined />}
                            onClick={handleCollapseSidebar}
                            size="small"
                        />
                    </div>
                )}

                <div ref={chatRef} className="flex-grow overflow-y-auto">
                    <div className="mx-auto max-w-5xl p-4 w-full">
                        {!activeTopic ? (
                            <div className="flex items-end justify-center min-h-[40vh]">
                                <p className="text-black-700 text-4xl font-bold mb-20">
                                    有什么可以帮忙的？
                                </p>
                            </div>
                        ) : messages.length === 0 ? (
                            <div className="flex items-center justify-center h-full min-h-[50vh]">
                                <p className="text-gray-500 text-lg">
                                    开始新的对话吧
                                </p>
                            </div>
                        ) : (
                            <div className="flex flex-col">
                                {messages.map((message, i) => (
                                    <Message
                                        idx={i}
                                        key={message.id}
                                        author={message.author}
                                        avatar={message.avatar}
                                        text={message.text}
                                        reasoning={message.reasoning}
                                        isTyping={message.isTyping}
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                <div className={`w-full ${!activeTopic ? "h-[80%]" : ""}`}>
                    <div className="mx-auto max-w-5xl p-4">
                        <Prompt
                            onSubmit={onSubmit}
                            disabled={false}
                            isProcessing={isProcessing}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
