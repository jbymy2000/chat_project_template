import { CopyOutlined } from "@ant-design/icons";
import { message } from "antd";
import Image from "next/image";
import MarkdownRenderer from "./markdown-renderer";

export default function Message({
    text: initialText,
    avatar,
    author,
    reasoning,
    isTyping = false,
}: {
    idx: number;
    key: string;
    text: string;
    avatar: string;
    author: string;
    reasoning?: string;
    isTyping?: boolean;
}) {
    const isHuman = author === "human";
    const bgColorClass = isHuman ? "bg-blue-100" : "";
    const [messageApi, contextHolder] = message.useMessage();

    const handleCopy = () => {
        if (initialText) {
            navigator.clipboard
                .writeText(initialText)
                .then(() => {
                    messageApi.success("复制成功");
                })
                .catch((err) => {
                    messageApi.error("复制失败");
                    console.error("复制失败:", err);
                });
        }
    };

    return (
        <div
            className={`flex ${isHuman ? "justify-end" : "justify-start"} p-4`}
        >
            {contextHolder}
            <style jsx global>{`
                @keyframes blink {
                    0%,
                    100% {
                        opacity: 1;
                    }
                    50% {
                        opacity: 0;
                    }
                }
                .message-menu {
                    height: 28px;
                    margin-top: 4px;
                }
            `}</style>
            <div
                className={`flex ${
                    isHuman ? "flex-row-reverse" : "flex-row"
                } max-w-[100%] items-start`}
            >
                <div
                    className={`w-[30px] h-[30px] relative ${
                        isHuman ? "ml-3" : "mr-3"
                    } flex-shrink-0`}
                >
                    <Image src={avatar} fill alt="" className="rounded-full" />
                </div>

                <div
                    className={`message-container flex flex-col ${bgColorClass} rounded-lg p-3 relative`}
                >
                    {!isHuman && reasoning && (
                        <div className="text-gray-500 text-xs mb-2 pl-3 border-l-2 border-gray-300 font-['Microsoft YaHei']">
                            {reasoning}
                        </div>
                    )}
                    <div className="min-h-[30px]">
                        <MarkdownRenderer content={initialText} />
                        {!isHuman && isTyping && (
                            <span
                                className="inline-block w-2 h-4 ml-1 bg-black"
                                style={{
                                    animation: "blink 0.5s step-end infinite",
                                }}
                            ></span>
                        )}
                    </div>

                    {/* 只在AI消息上显示菜单栏，且不在输入状态时 */}
                    {!isHuman && !isTyping && initialText && (
                        <div className="message-menu flex items-center justify-start gap-3">
                            <CopyOutlined
                                className="text-gray-500 hover:text-blue-500 cursor-pointer text-base"
                                onClick={handleCopy}
                                title="复制内容"
                            />
                            {/* 未来可以在这里添加更多按钮 */}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
