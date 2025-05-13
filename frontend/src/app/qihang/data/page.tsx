"use client";

import {
    BankOutlined,
    BarChartOutlined,
    BookOutlined,
    FormOutlined,
} from "@ant-design/icons";
import { Button, Card, Space } from "antd";
import { useRouter } from "next/navigation";

export default function DataPage() {
    const router = useRouter();

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

    return (
        <div className="p-4 max-w-7xl mx-auto">
            <Card className="shadow-sm">
                <Space size="large" wrap>
                    {buttons.map((button) => (
                        <Button
                            key={button.key}
                            type="primary"
                            icon={
                                <span style={{ marginRight: 8 }}>
                                    {button.icon}
                                </span>
                            }
                            size="small"
                            shape="round"
                            style={{ fontSize: 16, padding: "0 20px" }}
                            onClick={() => router.push(button.path)}
                        >
                            {button.text}
                        </Button>
                    ))}
                </Space>
            </Card>
        </div>
    );
}
