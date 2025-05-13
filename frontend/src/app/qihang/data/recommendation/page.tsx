"use client";

import { useAuth } from "@/contexts/AuthContext";
import {
    getCurrentUserProfile,
    getProfessionGroups,
    // getProfessionVersions,
    UserProfile,
} from "@/lib/api";
import provinceConfig from "@/province_config.json";
import { Breadcrumb, Card, Table, Tag } from "antd";
import type { TablePaginationConfig, TableProps } from "antd/es/table";
import type { AlignType } from "rc-table/lib/interface";
import { useEffect, useState } from "react";
import FeatureExcludeFilter from "../components/FeatureExcludeFilter";
import FeatureFilter from "../components/FeatureFilter";
import MajorCategoryFilter from "../components/MajorCategoryFilter";
import NatureFilter from "../components/NatureFilter";
import ProvinceFilter from "../components/ProvinceFilter";
import TypeFilter from "../components/TypeFilter";

export default function RecommendationPage() {
    const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
    const [loadingProfile, setLoadingProfile] = useState<boolean>(true);
    console.log(loadingProfile);
    const { user } = useAuth();
    const [selectedProvinces, setSelectedProvinces] = useState<string[]>([]);
    const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
    const [selectedFeatures, setSelectedFeatures] = useState<string[]>([]);
    const [selectedNatures, setSelectedNatures] = useState<string[]>([]);
    const [selectedMajorCategories, setSelectedMajorCategories] = useState<
        string[]
    >([]);
    const [selectedMajorExcludes, setSelectedMajorExcludes] = useState<
        string[]
    >([]);
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [pagination, setPagination] = useState<TablePaginationConfig>({
        current: 1,
        pageSize: 10,
        total: 0,
        showSizeChanger: true,
        pageSizeOptions: ["10", "20", "50"],
    });

    // 获取用户档案
    const fetchUserProfile = async () => {
        if (!user) return;

        try {
            setLoadingProfile(true);
            const data = await getCurrentUserProfile();
            setUserProfile(data);
        } catch (err) {
            console.error("获取用户信息失败:", err);
            setUserProfile(null);
        } finally {
            setLoadingProfile(false);
        }
    };

    // 组件挂载时获取用户档案
    useEffect(() => {
        fetchUserProfile();
    }, [user]);

    // 当 userProfile 变化时，查询并打印省份政策
    useEffect(() => {
        if (userProfile && userProfile.province) {
            const policy = provinceConfig[userProfile.province];
            console.log("当前用户省份：", userProfile.province);
            console.log("该省高考政策：", policy);
        }
    }, [userProfile]);

    // 拉取专业组列表
    const fetchData = async (params: any = {}) => {
        setLoading(true);
        try {
            const page = params.current || 1;
            const pageSize = params.pageSize || 10;
            // 组装筛选参数
            const queryParams: any = {
                page,
                page_size: pageSize,
            };
            // 可根据筛选器补充参数
            // if (selectedProvinces.length > 0) queryParams.province = selectedProvinces[0];
            // if (selectedTypes.length > 0) queryParams.college_type = selectedTypes[0];
            // ...
            const result = await getProfessionGroups(queryParams);
            setData(
                (result?.data?.items || []).map((item: any, idx: number) => ({
                    ...item,
                    key: idx,
                }))
            );
            setPagination({
                ...pagination,
                current: result.page,
                pageSize: result.page_size,
                total: result.total,
            });
        } catch (e) {
            console.log(e);
            setData([]);
            setPagination({ ...pagination, total: 0 });
        } finally {
            setLoading(false);
        }
    };

    // 筛选项或分页变化时拉取数据
    useEffect(() => {
        fetchData({ current: 1, pageSize: pagination.pageSize });
        // eslint-disable-next-line
    }, [
        selectedProvinces,
        selectedTypes,
        selectedFeatures,
        selectedNatures,
        selectedMajorCategories,
    ]);

    const handleTableChange: TableProps<any>["onChange"] = (pag) => {
        fetchData({ current: pag.current, pageSize: pag.pageSize });
    };

    // 枚举专业组表格字段
    const professionGroupColumns = [
        {
            title: "院校信息",
            key: "college_info",
            dataIndex: "college_name",
            width: 220,
            render: (_: any, row: any) => {
                const tags = (row.college_tags || "")
                    .split("/")
                    .map((t: string) => t.trim())
                    .filter((t: string) => t);
                return (
                    <div style={{ lineHeight: 1.6 }}>
                        <div style={{ fontWeight: 600, fontSize: 16 }}>
                            {row.college_name}
                        </div>
                        <div style={{ margin: "4px 0" }}>
                            {tags.length > 0 &&
                                tags.map((tag: string, idx: number) => (
                                    <Tag
                                        color="blue"
                                        key={idx}
                                        style={{
                                            marginRight: 4,
                                            marginBottom: 2,
                                        }}
                                    >
                                        {tag}
                                    </Tag>
                                ))}
                        </div>
                        <div style={{ color: "#888", fontSize: 12 }}>
                            院校代码：{row.college_code}
                        </div>
                    </div>
                );
            },
        },
        {
            title: "专业组/选科要求",
            key: "group_and_subject",
            width: 160,
            render: (_: any, row: any) => (
                <div style={{ lineHeight: 1.6 }}>
                    <div style={{ fontWeight: 500 }}>
                        {row.profession_group_code}
                    </div>
                    <div style={{ color: "#888", fontSize: 13 }}>
                        {row.subject_requirements || "-"}
                    </div>
                </div>
            ),
        },
        {
            title: "专业组计划人数",
            dataIndex: "profession_group_plan_num",
            key: "profession_group_plan_num",
            width: 120,
        },
        {
            title: "近三年最低分/位次",
            key: "min_score_rank",
            width: 240,
            className: "no-padding-cell",
            render: (_: any, row: any) => (
                <table
                    style={{
                        width: "100%",
                        borderCollapse: "collapse",
                        background: "transparent",
                        tableLayout: "fixed",
                    }}
                >
                    <thead>
                        <tr style={{ background: "transparent" }}>
                            <th
                                style={{
                                    border: "1px solid #f0f0f0",
                                    padding: 0,
                                    fontWeight: 400,
                                    textAlign: "center",
                                }}
                            ></th>
                            <th
                                style={{
                                    border: "1px solid #f0f0f0",
                                    padding: 0,
                                    fontWeight: 400,
                                    textAlign: "center",
                                }}
                            >
                                2024
                            </th>
                            <th
                                style={{
                                    border: "1px solid #f0f0f0",
                                    padding: 0,
                                    fontWeight: 400,
                                    textAlign: "center",
                                }}
                            >
                                2023
                            </th>
                            <th
                                style={{
                                    border: "1px solid #f0f0f0",
                                    padding: 0,
                                    fontWeight: 400,
                                    textAlign: "center",
                                }}
                            >
                                2022
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td
                                style={{
                                    border: "1px solid #f0f0f0",
                                    padding: 0,
                                    textAlign: "center",
                                }}
                            >
                                最低分
                            </td>
                            <td
                                style={{
                                    border: "1px solid #f0f0f0",
                                    padding: 0,
                                    textAlign: "center",
                                }}
                            >
                                {row.last_1_year_min_score ?? "-"}
                            </td>
                            <td
                                style={{
                                    border: "1px solid #f0f0f0",
                                    padding: 0,
                                    textAlign: "center",
                                }}
                            >
                                {row.last_2_year_min_score ?? "-"}
                            </td>
                            <td
                                style={{
                                    border: "1px solid #f0f0f0",
                                    padding: 0,
                                    textAlign: "center",
                                }}
                            >
                                {row.last_3_year_min_score ?? "-"}
                            </td>
                        </tr>
                        <tr>
                            <td
                                style={{
                                    border: "1px solid #f0f0f0",
                                    padding: 0,
                                    textAlign: "center",
                                }}
                            >
                                最低位次
                            </td>
                            <td
                                style={{
                                    border: "1px solid #f0f0f0",
                                    padding: 0,
                                    textAlign: "center",
                                }}
                            >
                                {row.last_1_year_min_rank ?? "-"}
                            </td>
                            <td
                                style={{
                                    border: "1px solid #f0f0f0",
                                    padding: 0,
                                    textAlign: "center",
                                }}
                            >
                                {row.last_2_year_min_rank ?? "-"}
                            </td>
                            <td
                                style={{
                                    border: "1px solid #f0f0f0",
                                    padding: 0,
                                    textAlign: "center",
                                }}
                            >
                                {row.last_3_year_min_rank ?? "-"}
                            </td>
                        </tr>
                    </tbody>
                </table>
            ),
        },
        {
            title: "录取概率",
            key: "admission_rate",
            width: 100,
            align: "center" as AlignType,
            render: () => (
                <span style={{ fontWeight: 600, color: "#faad14" }}>42%</span>
            ),
        },
    ];

    return (
        <>
            <div className="p-4">
                <Breadcrumb
                    className="mb-4 text-sm"
                    items={[
                        { title: "首页", href: "/qihang/data/recommendation" },
                        { title: "志愿填报" },
                    ]}
                />
                <Card className="mb-4">
                    <ProvinceFilter
                        selectedProvinces={selectedProvinces}
                        onChange={setSelectedProvinces}
                    />
                    <TypeFilter
                        selectedTypes={selectedTypes}
                        onChange={setSelectedTypes}
                    />
                    <FeatureFilter
                        selectedFeatures={selectedFeatures}
                        onChange={setSelectedFeatures}
                    />
                    <NatureFilter
                        selectedNatures={selectedNatures}
                        onChange={setSelectedNatures}
                    />
                    <MajorCategoryFilter
                        selectedCategories={selectedMajorCategories}
                        onChange={setSelectedMajorCategories}
                    />
                    <FeatureExcludeFilter
                        selectedExcludes={selectedMajorExcludes}
                        onChange={setSelectedMajorExcludes}
                    />
                </Card>
                <Card>
                    <Table
                        columns={professionGroupColumns}
                        dataSource={data}
                        loading={loading}
                        pagination={pagination}
                        onChange={handleTableChange}
                        scroll={{ x: "max-content" }}
                    />
                </Card>
            </div>
        </>
    );
}
