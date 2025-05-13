"use client";

import { getCollegeList } from "@/lib/api";
import {
    Breadcrumb,
    Card,
    Image,
    Input,
    Space,
    Table,
    Tag,
    Typography,
} from "antd";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import FeatureExcludeFilter from "../components/FeatureExcludeFilter";
import FeatureFilter from "../components/FeatureFilter";
import MajorCategoryFilter from "../components/MajorCategoryFilter";
import NatureFilter from "../components/NatureFilter";
import ProvinceFilter from "../components/ProvinceFilter";
import TypeFilter from "../components/TypeFilter";

const { Text } = Typography;

interface College {
    id: string;
    num_id: string;
    code: string;
    cn_name: string;
    logo_url: string;
    province_name: string;
    city_name: string;
    nature_type: string;
    edu_level: string;
    categories: string[];
    features: string[];
    star: string;
    ranking_of_rk: number;
    ranking_of_xyh: number;
    web_site: string;
    gb_code: string;
}

export default function UniversitiesPage() {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<College[]>([]);
    const [pagination, setPagination] = useState({
        current: 1,
        pageSize: 10,
        total: 0,
    });
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
    const [searchName, setSearchName] = useState("");
    const router = useRouter();

    const fetchData = async (page: number = 1, pageSize: number = 10) => {
        setLoading(true);
        try {
            const response = await getCollegeList(
                page,
                pageSize,
                searchName || undefined,
                selectedProvinces.length > 0 ? selectedProvinces : undefined,
                selectedTypes.length > 0 ? selectedTypes : undefined,
                selectedFeatures.length > 0 ? selectedFeatures : undefined,
                selectedNatures.length > 0 ? selectedNatures : undefined
            );
            if (response.code === 200) {
                setData(response.data.items);
                setPagination({
                    ...pagination,
                    current: page,
                    total: response.data.total,
                });
            }
        } catch (error) {
            console.error("获取大学列表失败:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData(1, pagination.pageSize);
    }, [selectedProvinces, selectedTypes, selectedFeatures, selectedNatures]);

    const columns = [
        {
            title: "学校信息",
            dataIndex: "cn_name",
            key: "cn_name",
            render: (text: string, record: College) => (
                <Space>
                    {record.logo_url && (
                        <Image
                            src={record.logo_url}
                            alt={text}
                            width={40}
                            height={40}
                            preview={false}
                            style={{ objectFit: "contain" }}
                        />
                    )}
                    <div>
                        <div
                            className="font-medium cursor-pointer hover:text-blue-600"
                            onClick={() =>
                                router.push(
                                    `/qihang/data/universities/detail/${record.code}`
                                )
                            }
                        >
                            {text}
                        </div>
                        <div className="text-gray-500 text-sm flex flex-wrap items-center">
                            {record.province_name} |
                            {record.nature_type && (
                                <span className="ml-1">
                                    {record.nature_type}
                                </span>
                            )}{" "}
                            |
                            {record.edu_level && (
                                <span className="ml-1">{record.edu_level}</span>
                            )}{" "}
                            |
                            {record.categories &&
                                record.categories.length > 0 && (
                                    <span className="ml-1">
                                        {record.categories.join(" ")}
                                    </span>
                                )}
                            {record.features && record.features.length > 0 && (
                                <span className="ml-1">
                                    {record.features.join(" ")}
                                </span>
                            )}
                        </div>
                    </div>
                </Space>
            ),
        },
        {
            title: "排名",
            key: "ranking",
            render: (record: College) => (
                <Space direction="vertical" size="small">
                    {record.ranking_of_rk && (
                        <Text>软科: {record.ranking_of_rk}</Text>
                    )}
                    {record.ranking_of_xyh && (
                        <Text>校友会: {record.ranking_of_xyh}</Text>
                    )}
                </Space>
            ),
        },
        {
            title: "星级",
            dataIndex: "star",
            key: "star",
            render: (text: string) => <Tag color="gold">{text}</Tag>,
        },
    ];

    const handleTableChange = (pagination: any) => {
        fetchData(pagination.current, pagination.pageSize);
    };

    const handleSearch = (v: string) => {
        setSearchName(v);
        fetchData(1, pagination.pageSize);
    };

    return (
        <div className="p-4 max-w-7xl mx-auto">
            <Breadcrumb
                className="mb-4 text-sm"
                items={[
                    { title: "首页", href: "/qihang/data/recommendation" },
                    { title: "找大学" },
                ]}
            />
            <Card className="mb-4">
                <div className="mb-2">
                    <div className="flex flex-wrap items-baseline mb-2">
                        <span className="mr-2 text-gray-600 font-medium h-8 flex items-center text-sm">
                            学校名称：
                        </span>
                        <Input.Search
                            allowClear
                            placeholder="请输入学校名称"
                            value={searchName}
                            onChange={(e) => setSearchName(e.target.value)}
                            style={{ width: 200, marginRight: 16 }}
                            onSearch={handleSearch}
                            size="small"
                        />
                    </div>
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
                </div>
            </Card>
            <Card>
                <Table
                    columns={columns}
                    dataSource={data}
                    rowKey="id"
                    pagination={pagination}
                    loading={loading}
                    onChange={handleTableChange}
                    scroll={{ x: 1200 }}
                    size="small"
                />
            </Card>
        </div>
    );
}
