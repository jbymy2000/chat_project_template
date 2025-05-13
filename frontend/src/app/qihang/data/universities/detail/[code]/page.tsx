"use client";
import { SCHOOL_NATURES } from "@/constants/constants";
import { College, getCollegeDetail } from "@/lib/api";
import {
    EnvironmentOutlined,
    GlobalOutlined,
    HomeOutlined,
    MailOutlined,
    PhoneOutlined,
} from "@ant-design/icons";
import { Breadcrumb, Image, message, Spin, Tabs, Tag, Typography } from "antd";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

const { Title } = Typography;

const tagStyle = {
    background: "#10b981",
    color: "#fff",
    borderColor: "#fff",
    fontWeight: 500,
    fontSize: 12,
    marginRight: 8,
};

function getNatureLabel(value: string) {
    const found = SCHOOL_NATURES.find((item) => item.value === value);
    return found ? found.label : value;
}

export default function UniversityDetailPage() {
    const params = useParams();
    const code = params.code as string;
    const [loading, setLoading] = useState(false);
    const [college, setCollege] = useState<College | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!code) return;
        setLoading(true);
        setError(null);
        getCollegeDetail(code)
            .then((res) => {
                if (
                    res.college_address &&
                    typeof res.college_address === "string"
                ) {
                    try {
                        res.college_address = JSON.parse(res.college_address);
                    } catch (e) {
                        res.college_address = [];
                        console.error(e);
                    }
                }
                setCollege(res);
            })
            .catch((err) => {
                setError(err.message);
                message.error(err.message);
            })
            .finally(() => setLoading(false));
    }, [code]);

    let tabItems = [];
    if (college) {
        tabItems = [
            {
                key: "overview",
                label: "学校概况",
                children: <div>{college.introduction || "暂无简介"}</div>,
            },
            {
                key: "admission",
                label: "招生简章",
                children: <div>招生简章内容</div>,
            },
            {
                key: "score",
                label: "分数/计划",
                children: <div>分数/计划内容</div>,
            },
            {
                key: "majors",
                label: "开设专业",
                children: <div>开设专业内容</div>,
            },
        ];
    }

    return (
        <Spin spinning={loading}>
            <div className="p-4 max-w-7xl mx-auto">
                <Breadcrumb
                    className="mb-4 text-sm"
                    items={[
                        { title: "首页", href: "/qihang/data/recommendation" },
                        { title: "找大学", href: "/qihang/data/universities" },
                        { title: college?.cn_name || "院校详情" },
                    ]}
                />
                {error ? (
                    <div className="text-red-500 text-center py-8">{error}</div>
                ) : college ? (
                    <div>
                        <div className="bg-emerald-500 rounded-xl p-8 flex items-center mb-4 relative">
                            {college.logo_url && (
                                <div
                                    style={{
                                        minWidth: 140,
                                        display: "flex",
                                        justifyContent: "center",
                                        alignItems: "center",
                                        height: 140,
                                    }}
                                >
                                    <Image
                                        src={college.logo_url}
                                        alt={college.cn_name}
                                        width={120}
                                        height={120}
                                        preview={false}
                                        style={{
                                            objectFit: "contain",
                                            background: "#fff",
                                            borderRadius: 16,
                                            padding: 8,
                                        }}
                                    />
                                </div>
                            )}
                            <div
                                style={{ marginLeft: 64 }}
                                className="flex-1 min-w-0"
                            >
                                <div className="flex items-center mb-3">
                                    <Title
                                        level={3}
                                        className="!mb-0 !text-white !font-bold mr-4"
                                    >
                                        {college.cn_name}
                                    </Title>
                                </div>
                                <div className="flex items-center text-white text-sm mb-3">
                                    <EnvironmentOutlined className="mr-1" />
                                    <span className="truncate max-w-xs">
                                        {college.city_name ||
                                            college.province_name}
                                    </span>
                                    {college.college_address &&
                                    college.college_address.length > 0 &&
                                    college.college_address[0].address ? (
                                        <>
                                            <HomeOutlined className="ml-4 mr-1" />
                                            <span className="truncate max-w-xs">
                                                {
                                                    college.college_address[0]
                                                        .address
                                                }
                                            </span>
                                        </>
                                    ) : (
                                        college.address && (
                                            <>
                                                <HomeOutlined className="ml-4 mr-1" />
                                                <span className="truncate max-w-xs">
                                                    {college.address}
                                                </span>
                                            </>
                                        )
                                    )}
                                </div>
                                <div className="flex flex-wrap gap-1 mb-3">
                                    {college.categories &&
                                        college.categories.length > 0 &&
                                        college.categories.map((cat) => (
                                            <Tag key={cat} style={tagStyle}>
                                                {cat}
                                            </Tag>
                                        ))}
                                    {college.nature_type && (
                                        <Tag style={tagStyle}>
                                            {getNatureLabel(
                                                college.nature_type
                                            )}
                                        </Tag>
                                    )}
                                    {college.features &&
                                        college.features.length > 0 &&
                                        college.features.map((f) => (
                                            <Tag key={f} style={tagStyle}>
                                                {f}
                                            </Tag>
                                        ))}
                                </div>
                                <div className="flex flex-col text-white text-xs gap-2">
                                    {college.web_site && (
                                        <span>
                                            <GlobalOutlined className="mr-1" />
                                            <span className="mr-1">
                                                官网地址：
                                            </span>
                                            <a
                                                href={college.web_site}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="underline text-white"
                                            >
                                                {college.web_site}
                                            </a>
                                        </span>
                                    )}
                                    {college.zhao_ban_dh && (
                                        <span>
                                            <PhoneOutlined className="mr-1" />
                                            招生电话：{college.zhao_ban_dh}
                                        </span>
                                    )}
                                    {college.zhao_ban_email && (
                                        <span>
                                            <MailOutlined className="mr-1" />
                                            电子邮箱：{college.zhao_ban_email}
                                        </span>
                                    )}
                                </div>
                            </div>
                        </div>
                        {college && (
                            <Tabs
                                className="bg-white rounded-xl px-6 py-4 mt-6"
                                defaultActiveKey="overview"
                                items={tabItems}
                            />
                        )}
                    </div>
                ) : (
                    <div className="text-gray-400 text-center py-8">
                        暂无数据
                    </div>
                )}
            </div>
        </Spin>
    );
}
