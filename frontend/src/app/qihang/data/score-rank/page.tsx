"use client";

import { useAuth } from "@/contexts/AuthContext";
import {
    getCurrentUserProfile,
    getScoreRank,
    ScoreRankItem,
    UserProfile,
} from "@/lib/api";
import { Breadcrumb, Card, Form, Select, Spin, Table } from "antd";
import ReactECharts from "echarts-for-react";
import { useEffect, useState } from "react";

const { Option } = Select;

export default function ScoreRankPage() {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<ScoreRankItem[]>([]);
    const [form] = Form.useForm();
    const { user } = useAuth();
    const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
    const [loadingProfile, setLoadingProfile] = useState(true);

    const fetchUserProfile = async () => {
        if (!user) return;
        try {
            setLoadingProfile(true);
            const profile = await getCurrentUserProfile();
            setUserProfile(profile);
        } catch (error) {
            console.error("获取用户档案失败:", error);
        } finally {
            setLoadingProfile(false);
        }
    };

    useEffect(() => {
        fetchUserProfile();
    }, [user]);

    const columns = [
        {
            title: "分数段",
            dataIndex: "score_range",
            key: "score_range",
            render: (_: any, record: ScoreRankItem) =>
                `${record.minScore}-${record.maxScore}`,
        },
        {
            title: "同分人数",
            dataIndex: "sameCount",
            key: "sameCount",
        },
        {
            title: "最低排名",
            dataIndex: "lowestRank",
            key: "lowestRank",
        },
        {
            title: "最高排名",
            dataIndex: "highestRank",
            key: "highestRank",
        },
    ];

    const fetchData = async (values: any) => {
        try {
            setLoading(true);
            const response = await getScoreRank({
                province_name: values.province_name,
                year: values.year,
                batch: values.batch,
            });
            setData(response.data);
        } catch (error) {
            console.error("获取分数排名数据失败:", error);
            setData([]);
        } finally {
            setLoading(false);
        }
    };

    // 处理下拉列表变化
    const handleSelectChange = () => {
        form.submit();
    };

    useEffect(() => {
        if (user && !loadingProfile) {
            form.setFieldsValue({
                province_name: userProfile?.province || "北京",
                year: 2024,
                batch: "本科",
            });
            form.submit();
        }
    }, [user, userProfile, loadingProfile, form]);

    // 添加图表配置
    const getChartOption = () => {
        const xAxisData = data.map(
            (item) => `${item.minScore}-${item.maxScore}`
        );
        const seriesData = data.map((item) => item.sameCount);

        return {
            title: {
                text: "分数段分布",
                left: "center",
            },
            tooltip: {
                trigger: "axis",
                axisPointer: {
                    type: "shadow",
                },
            },
            grid: {
                left: "3%",
                right: "4%",
                bottom: "15%",
                containLabel: true,
            },
            xAxis: {
                type: "category",
                data: xAxisData,
                axisLabel: {
                    interval: Math.floor(xAxisData.length / 10), // 每10个显示一个
                    rotate: 45,
                    fontSize: 12,
                    margin: 15,
                },
                axisTick: {
                    alignWithLabel: true,
                },
            },
            yAxis: {
                type: "value",
                name: "人数",
                nameTextStyle: {
                    padding: [0, 0, 0, 40],
                },
            },
            series: [
                {
                    name: "同分人数",
                    type: "bar",
                    data: seriesData,
                    itemStyle: {
                        color: "#1890ff",
                    },
                    barWidth: "60%",
                },
            ],
            dataZoom: [
                {
                    type: "slider",
                    show: true,
                    xAxisIndex: [0],
                    start: 0,
                    end: 100,
                },
            ],
        };
    };

    return (
        <div className="p-4">
            <Breadcrumb
                className="mb-4 text-sm"
                items={[
                    { title: "首页", href: "/qihang/data/recommendation" },
                    { title: "一分一段表" },
                ]}
            />

            <Card className="mb-6">
                <Form
                    form={form}
                    layout="inline"
                    onFinish={fetchData}
                    initialValues={{
                        province_name: "北京",
                        year: 2024,
                        batch: "本科",
                    }}
                >
                    <Form.Item
                        name="province_name"
                        label="省份"
                        rules={[{ required: true, message: "请选择省份" }]}
                    >
                        <Select
                            style={{ width: 120 }}
                            onChange={handleSelectChange}
                        >
                            <Option value="北京">北京</Option>
                            <Option value="上海">上海</Option>
                            <Option value="广东">广东</Option>
                            {/* 可以添加更多省份 */}
                        </Select>
                    </Form.Item>

                    <Form.Item
                        name="year"
                        label="年份"
                        rules={[{ required: true, message: "请选择年份" }]}
                    >
                        <Select
                            style={{ width: 120 }}
                            onChange={handleSelectChange}
                        >
                            {Array.from({ length: 5 }, (_, i) => 2024 - i).map(
                                (year) => (
                                    <Option key={year} value={year}>
                                        {year}
                                    </Option>
                                )
                            )}
                        </Select>
                    </Form.Item>

                    <Form.Item
                        name="batch"
                        label="批次"
                        rules={[{ required: true, message: "请选择批次" }]}
                    >
                        <Select
                            style={{ width: 120 }}
                            onChange={handleSelectChange}
                        >
                            <Option value="本科">本科</Option>
                            <Option value="专科">专科</Option>
                        </Select>
                    </Form.Item>
                </Form>
            </Card>

            <Card className="mb-6">
                <Spin spinning={loading}>
                    <ReactECharts
                        option={getChartOption()}
                        style={{ height: "400px" }}
                        notMerge={true}
                    />
                </Spin>
            </Card>

            <Card>
                <Spin spinning={loading}>
                    <Table
                        columns={columns}
                        dataSource={data}
                        rowKey={(record) =>
                            `${record.minScore}-${record.maxScore}`
                        }
                        pagination={false}
                        bordered
                        size="small"
                        scroll={{ y: 400 }}
                    />
                </Spin>
            </Card>
        </div>
    );
}
