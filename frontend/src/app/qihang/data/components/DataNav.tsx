"use client";
import {
    BankOutlined,
    BarChartOutlined,
    BookOutlined,
    FormOutlined,
} from "@ant-design/icons";
import { Button, Space } from "antd";
import { usePathname, useRouter } from "next/navigation";

const buttons = [
    {
        key: "recommendation",
        icon: <FormOutlined />,
        text: "志愿填报",
        path: "/qihang/data/recommendation",
    },
    {
        key: "universities",
        icon: <BankOutlined />,
        text: "查大学",
        path: "/qihang/data/universities",
    },
    {
        key: "majors",
        icon: <BookOutlined />,
        text: "查专业",
        path: "/qihang/data/professions",
    },
    {
        key: "score-rank",
        icon: <BarChartOutlined />,
        text: "一分一段",
        path: "/qihang/data/score-rank",
    },
];

export default function DataNav() {
    const router = useRouter();
    const pathname = usePathname();
    return (
        <div className="mb-4">
            <Space size="large" wrap>
                {buttons.map((button) => (
                    <Button
                        key={button.key}
                        type={pathname === button.path ? "primary" : "default"}
                        icon={<span>{button.icon}</span>}
                        size="small"
                        shape="round"
                        style={{ fontSize: 16 }}
                        onClick={() => router.push(button.path)}
                    >
                        {button.text}
                    </Button>
                ))}
            </Space>
        </div>
    );
}
