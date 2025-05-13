import type { Components } from "react-markdown";
import Markdown from "react-markdown";
import SyntaxHighlighter from "react-syntax-highlighter";
import { darcula } from "react-syntax-highlighter/dist/esm/styles/hljs";
import remarkGfm from "remark-gfm";

interface CodeProps {
    inline?: boolean;
    className?: string;
    children?: React.ReactNode;
    [key: string]: unknown;
}

interface MarkdownRendererProps {
    content: string;
    className?: string;
}

export default function MarkdownRenderer({
    content,
    className = "",
}: MarkdownRendererProps) {
    const components: Components = {
        code: ({ inline, className, children, ...props }: CodeProps) => {
            const match = /language-(\w+)/.exec(className || "");
            if (
                !inline &&
                match &&
                match[1] &&
                !String(children).includes("|")
            ) {
                return (
                    <SyntaxHighlighter
                        style={darcula}
                        language={match[1]}
                        PreTag="div"
                        {...props}
                    >
                        {String(children).replace(/\n$/, "")}
                    </SyntaxHighlighter>
                );
            }
            return (
                <code className={className} {...props}>
                    {children}
                </code>
            );
        },
        p: ({ children }) => {
            return <p className="my-0">{children || "\u00A0"}</p>;
        },
        table: ({ children }) => {
            return (
                <div className="overflow-x-auto my-4">
                    <table className="min-w-full border border-gray-200">
                        {children}
                    </table>
                </div>
            );
        },
        thead: ({ children }) => {
            return <thead className="bg-gray-50">{children}</thead>;
        },
        tbody: ({ children }) => {
            return <tbody>{children}</tbody>;
        },
        tr: ({ children }) => {
            return <tr className="border-b border-gray-200">{children}</tr>;
        },
        th: ({ children }) => {
            return (
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-900 border border-gray-200">
                    {children}
                </th>
            );
        },
        td: ({ children }) => {
            return (
                <td className="px-4 py-2 text-sm text-gray-900 border border-gray-200">
                    {children}
                </td>
            );
        },
    };

    return (
        <div
            className={`prose prose-lg max-w-none dark:prose-invert ${className}`}
        >
            <Markdown remarkPlugins={[remarkGfm]} components={components}>
                {content}
            </Markdown>
        </div>
    );
}
