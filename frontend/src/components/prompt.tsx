/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable @typescript-eslint/no-unused-vars */
"use client";
// 移除axios导入
// import axios from "axios";
import { useEffect, useRef, useState } from "react";
import config from "../../config.json";

// 定义语音识别状态类型
enum RecognitionState {
    IDLE = "idle",
    LISTENING = "listening",
    PROCESSING = "processing",
    ERROR = "error",
}

// 声明SpeechRecognition类型
declare global {
    interface Window {
        SpeechRecognition: any;
        webkitSpeechRecognition: any;
    }
}

// API基础URL
const API_BASE_URL =
    process.env.NODE_ENV === "production"
        ? config.production.apiBaseUrl
        : config.development.apiBaseUrl;

export default function Prompt({
    onSubmit,
    disabled = false,
    isProcessing = false,
}: {
    onSubmit: (input: string) => void;
    disabled?: boolean;
    isProcessing?: boolean;
}) {
    const [promptInput, setPromptInput] = useState("");
    const [isListening, setIsListening] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [recognitionState, setRecognitionState] = useState<RecognitionState>(
        RecognitionState.IDLE
    );

    // 音频流和录音机引用
    const audioStreamRef = useRef<MediaStream | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);
    // 错误消息计时器引用
    const errorTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    // 设置错误消息并自动清除
    const setTemporaryError = (message: string) => {
        // 清除之前的计时器
        if (errorTimeoutRef.current) {
            clearTimeout(errorTimeoutRef.current);
        }

        // 设置错误消息
        setErrorMessage(message);

        // 设置5秒后自动清除
        errorTimeoutRef.current = setTimeout(() => {
            setErrorMessage("");
            errorTimeoutRef.current = null;
        }, 5000);
    };

    // 清除计时器
    useEffect(() => {
        return () => {
            if (errorTimeoutRef.current) {
                clearTimeout(errorTimeoutRef.current);
            }
        };
    }, []);

    // 启动录音
    const startRecording = async () => {
        try {
            setErrorMessage("");
            setRecognitionState(RecognitionState.LISTENING);

            // 请求麦克风访问权限
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: true,
            });
            audioStreamRef.current = stream;

            // 创建MediaRecorder实例
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;

            // 重置音频块
            audioChunksRef.current = [];

            // 设置数据可用时的处理函数
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            // 设置录音停止时的处理函数
            mediaRecorder.onstop = handleRecordingStop;

            // 开始录音
            mediaRecorder.start();
            setIsRecording(true);
            setIsListening(true);
        } catch (error: any) {
            console.error("启动录音失败:", error);
            let message = "无法启动麦克风录音。";

            if (
                error.name === "NotAllowedError" ||
                error.name === "PermissionDeniedError"
            ) {
                message = "麦克风访问被拒绝，请允许浏览器使用麦克风。";
            } else if (
                error.name === "NotFoundError" ||
                error.name === "DevicesNotFoundError"
            ) {
                message =
                    "未找到麦克风设备，请确保您的设备有麦克风并已正确连接。";
            } else if (
                error.name === "NotReadableError" ||
                error.name === "TrackStartError"
            ) {
                message =
                    "麦克风可能被其他应用程序占用，请关闭其他使用麦克风的应用。";
            }

            setTemporaryError(message);
            setRecognitionState(RecognitionState.ERROR);
            setIsListening(false);
            setIsRecording(false);
        }
    };

    // 停止录音
    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);

            // 停止所有音频轨道
            if (audioStreamRef.current) {
                audioStreamRef.current
                    .getTracks()
                    .forEach((track) => track.stop());
                audioStreamRef.current = null;
            }
        }
    };

    // 处理录音停止事件
    const handleRecordingStop = async () => {
        if (audioChunksRef.current.length === 0) {
            setTemporaryError("未捕获到任何音频");
            setRecognitionState(RecognitionState.ERROR);
            setIsListening(false);
            return;
        }

        try {
            setRecognitionState(RecognitionState.PROCESSING);

            // 合并音频块创建音频Blob
            const audioBlob = new Blob(audioChunksRef.current, {
                type: "audio/webm",
            });

            // 创建FormData对象用于发送文件
            const formData = new FormData();
            formData.append("file", audioBlob, "recording.webm");

            // 使用完整URL路径
            const apiUrl = `${API_BASE_URL}/speech/recognize-blob`;
            console.log("正在发送录音到:", apiUrl);

            // 使用fetch发送到后端进行识别
            const response = await fetch(apiUrl, {
                method: "POST",
                // 添加跨域支持
                credentials: "include",
                body: formData,
            });

            // 检查HTTP状态
            if (response.status === 404) {
                throw new Error(
                    "语音识别服务不可用(404)，请确认后端服务是否正常运行"
                );
            }

            // 处理其他错误状态
            if (!response.ok) {
                throw new Error(`服务器返回错误: ${response.status}`);
            }

            // 尝试解析JSON
            let result;
            try {
                result = await response.json();
            } catch (err) {
                console.error("解析响应JSON失败:", err);
                console.log("收到的响应:", await response.text());
                throw new Error("解析服务器响应失败，请检查后端返回格式");
            }

            // 处理识别结果
            if (result && result.success) {
                const recognizedText = result.text;

                // 将识别结果添加到输入框
                if (recognizedText) {
                    setPromptInput((currentInput) => {
                        return (
                            currentInput +
                            (currentInput ? " " : "") +
                            recognizedText
                        );
                    });
                } else {
                    setTemporaryError("未能识别到任何文本");
                }
            } else {
                setTemporaryError(
                    `语音识别失败: ${result?.error_msg || "未知错误"}`
                );
            }
        } catch (error: any) {
            console.error("发送录音到后端处理失败:", error);
            setTemporaryError(`发送录音失败: ${error.message || "网络错误"}`);
        } finally {
            setRecognitionState(RecognitionState.IDLE);
            setIsListening(false);
        }
    };

    // 切换录音状态
    const toggleListening = () => {
        if (isListening) {
            stopRecording();
        } else {
            startRecording();
        }
    };

    // 只在按钮和Enter键上应用禁用状态
    const isSendingDisabled = disabled || isProcessing;

    return (
        <div className="relative">
            <textarea
                value={promptInput}
                onChange={(e) => setPromptInput(e.target.value)}
                onKeyDown={(e) => {
                    if (
                        e.key === "Enter" &&
                        !e.nativeEvent.isComposing &&
                        !e.shiftKey &&
                        !isSendingDisabled
                    ) {
                        console.log("pressing Enter");
                        e.preventDefault();
                        onSubmit(promptInput);
                        setPromptInput("");
                    }
                }}
                rows={4}
                className={`w-full p-4 text-sm text-gray-900 bg-white rounded-2xl border ${
                    isListening ? "border-red-500" : "border-gray-200"
                } shadow-md hover:shadow-lg focus:shadow-xl focus:border-blue-300 
                transition-all duration-200 ease-in-out outline-none`}
                placeholder={
                    disabled
                        ? "请先选择或创建一个对话话题..."
                        : isListening
                        ? "正在聆听您的声音..."
                        : recognitionState === RecognitionState.PROCESSING
                        ? "正在处理语音..."
                        : "输入您的问题..."
                }
            />

            {/* 错误提示 */}
            {errorMessage && (
                <div className="absolute top-2 left-4 right-4 flex items-center text-red-500 text-xs bg-red-50 p-1 rounded">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-4 w-4 mr-1"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        />
                    </svg>
                    {errorMessage}
                </div>
            )}

            {/* 录音指示器 */}
            {isListening && (
                <div className="absolute top-2 right-2 flex items-center text-red-500 text-xs">
                    <span className="mr-1 h-2 w-2 rounded-full bg-red-500 animate-pulse"></span>
                    正在录音
                </div>
            )}

            {/* 处理中指示器 */}
            {recognitionState === RecognitionState.PROCESSING && (
                <div className="absolute top-2 right-2 flex items-center text-blue-500 text-xs">
                    <span className="mr-1 h-2 w-2 rounded-full bg-blue-500 animate-pulse"></span>
                    处理中...
                </div>
            )}

            <div className="absolute right-3 bottom-3 flex gap-2">
                {/* 麦克风按钮 */}
                <button
                    onClick={toggleListening}
                    disabled={
                        disabled ||
                        recognitionState === RecognitionState.PROCESSING
                    }
                    className={`p-2 rounded-full transition-colors duration-200 ${
                        disabled ||
                        recognitionState === RecognitionState.PROCESSING
                            ? "bg-gray-400 cursor-not-allowed"
                            : isListening
                            ? "bg-red-500 text-white hover:bg-red-600"
                            : "bg-blue-500 text-white hover:bg-blue-600"
                    }`}
                    title={isListening ? "停止语音输入" : "开始语音输入"}
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-5 w-5"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                    >
                        <path
                            fillRule="evenodd"
                            d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z"
                            clipRule="evenodd"
                        />
                    </svg>
                </button>

                {/* 发送按钮 */}
                {promptInput.trim() && (
                    <button
                        onClick={() => {
                            if (!isSendingDisabled) {
                                onSubmit(promptInput);
                                setPromptInput("");
                            }
                        }}
                        disabled={isSendingDisabled}
                        className={`p-2 rounded-full 
                        transition-colors duration-200 ${
                            isSendingDisabled
                                ? "bg-gray-400 cursor-not-allowed"
                                : "bg-blue-500 text-white hover:bg-blue-600 focus:bg-blue-700"
                        }`}
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                        >
                            <path
                                fillRule="evenodd"
                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z"
                                clipRule="evenodd"
                            />
                        </svg>
                    </button>
                )}
            </div>
        </div>
    );
}
