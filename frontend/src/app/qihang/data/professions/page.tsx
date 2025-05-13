"use client";

import { getProfessionList } from "@/lib/api";
import { SearchOutlined } from "@ant-design/icons";
import { Breadcrumb, Card, Input, Table } from "antd";
import type { TablePaginationConfig, TableProps } from "antd/es/table";
import { useEffect, useState } from "react";

export default function ProfessionsPage() {
    const [loading, setLoading] = useState<boolean>(false);
    const [data, setData] = useState<any[]>([]);
    const [pagination, setPagination] = useState<TablePaginationConfig>({
        current: 1,
        pageSize: 10,
        total: 0,
        showSizeChanger: true,
        pageSizeOptions: ["10", "20", "50"],
    });
    const [searchText, setSearchText] = useState<string>("");

    // 专业列表表格列定义
    const columns = [
        {
            title: "专业代码/名称/属性",
            key: "profession_code_name_attrs",
            dataIndex: "profession_code_name_attrs",
            width: 480,
            render: (_: any, record: any) => (
                <div>
                    <div>
                        <span
                            style={{
                                color: "#999",
                                fontSize: 12,
                                marginRight: 8,
                            }}
                        >
                            {record.profession_code}
                        </span>
                        <span>{record.profession_name}</span>
                    </div>
                    <div style={{ fontSize: 12, color: "#888", marginTop: 2 }}>
                        <span style={{ color: "#bbb" }}>|</span>
                        {record.profession_type}
                        <span style={{ color: "#bbb" }}>|</span>
                        <span style={{ color: "#aaa", margin: "0 4px" }}>
                            {record.degree_category}
                        </span>
                        <span style={{ color: "#bbb" }}>|</span>
                        <span style={{ color: "#aaa", margin: "0 4px" }}>
                            {record.duration}
                        </span>
                        <span style={{ color: "#bbb" }}>|</span>
                        <span style={{ color: "#aaa", margin: "0 4px" }}>
                            {record.establishment_year}
                        </span>
                    </div>
                </div>
            ),
        },
    ];

    // 获取专业列表数据
    const fetchData = async (params: any = {}) => {
        setLoading(true);
        try {
            const page = params.current || 1;
            const pageSize = params.pageSize || 10;

            const queryParams: any = {
                page,
                page_size: pageSize,
            };

            if (searchText) {
                queryParams.profession_name = searchText;
            }

            const result = await getProfessionList(queryParams);

            if (result.code === 200 && result.data) {
                setData(
                    (result.data.items || []).map((item: any, idx: number) => ({
                        ...item,
                        key: idx,
                    }))
                );
                setPagination({
                    ...pagination,
                    current: result.data.page,
                    pageSize: result.data.page_size,
                    total: result.data.total,
                });
            }
        } catch (e) {
            console.error("获取专业列表失败:", e);
            setData([]);
            setPagination({ ...pagination, total: 0 });
        } finally {
            setLoading(false);
        }
    };

    // 处理表格变化
    const handleTableChange: TableProps<any>["onChange"] = (pag) => {
        fetchData({ current: pag.current, pageSize: pag.pageSize });
    };

    // 处理搜索
    const handleSearch = () => {
        fetchData({ current: 1, pageSize: pagination.pageSize });
    };

    // 初始加载数据
    useEffect(() => {
        fetchData();
    }, []);

    // 分组处理
    const groupedData: any[] = [];
    let lastCategory = null;
    data.forEach((item, idx) => {
        if (item.profession_category !== lastCategory) {
            groupedData.push({
                isGroup: true,
                groupKey: `group-${item.profession_category}-${idx}`,
                profession_category: item.profession_category,
            });
            lastCategory = item.profession_category;
        }
        groupedData.push(item);
    });

    // 自定义行渲染，插入分组标签
    const rowClassName = (record: any) => (record.isGroup ? "bg-gray-50" : "");

    return (
        <div className="p-4">
            <Breadcrumb
                className="mb-4 text-sm"
                items={[
                    { title: "首页", href: "/qihang/data/recommendation" },
                    { title: "专业列表" },
                ]}
            />
            <Card className="mb-4">
                <div className="flex items-center gap-4">
                    <Input
                        placeholder="请输入专业名称搜索"
                        value={searchText}
                        onChange={(e) => setSearchText(e.target.value)}
                        onPressEnter={handleSearch}
                        style={{ width: 300 }}
                        suffix={
                            <SearchOutlined
                                className="cursor-pointer"
                                onClick={handleSearch}
                            />
                        }
                    />
                </div>
            </Card>
            <Card>
                <Table
                    columns={columns}
                    dataSource={groupedData}
                    loading={loading}
                    pagination={pagination}
                    onChange={handleTableChange}
                    scroll={{ x: "max-content" }}
                    showHeader={false}
                    rowClassName={rowClassName}
                    rowKey={(record: any) =>
                        record.isGroup ? record.groupKey : record.key
                    }
                    // 自定义渲染分组行
                    components={{
                        body: {
                            row: (props: any) => {
                                const { className, children, ...restProps } =
                                    props;
                                console.log(children);
                                const record = props["data-row-key"]
                                    ? groupedData.find(
                                          (item) =>
                                              (item.key !== undefined &&
                                                  String(item.key) ===
                                                      props["data-row-key"]) ||
                                              (item.groupKey &&
                                                  item.groupKey ===
                                                      props["data-row-key"])
                                      )
                                    : null;
                                if (record && record.isGroup) {
                                    return (
                                        <tr
                                            {...restProps}
                                            className={className + " group-row"}
                                        >
                                            <td colSpan={columns.length}>
                                                {record.profession_category}
                                            </td>
                                        </tr>
                                    );
                                }
                                return <tr {...props} />;
                            },
                        },
                    }}
                />
            </Card>
        </div>
    );
}
