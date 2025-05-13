import { Button } from "antd";

const MAJOR_CATEGORIES = [
    "哲学",
    "经济学",
    "法学",
    "教育学",
    "文学",
    "历史学",
    "理学",
    "工学",
    "农学",
    "医学",
    "管理学",
    "艺术学",
    "教育与体育学",
    "资源环境与安全大类",
    "生物与化工大类",
    "交通运输大类",
    "轻工纺织大类",
    "财经商贸大类",
    "新闻传播大类",
    "文化艺术大类",
    "装备制造大类",
    "能源动力与材料大类",
    "农林牧渔大类",
    "医药卫生大类",
    "旅游大类",
    "电子与信息大类",
    "土木建筑大类",
    "食品药品与粮食大类",
    "公安与司法大类",
    "水利大类",
    "公共管理与服务大类",
];

interface MajorCategoryFilterProps {
    selectedCategories: string[];
    onChange: (selected: string[]) => void;
}

export default function MajorCategoryFilter({
    selectedCategories,
    onChange,
}: MajorCategoryFilterProps) {
    const handleSelect = (value?: string) => {
        if (value === undefined) {
            onChange([]);
            return;
        }
        if (selectedCategories.includes(value)) {
            onChange(selectedCategories.filter((v) => v !== value));
        } else {
            onChange([
                ...selectedCategories.filter((v) => v !== undefined),
                value,
            ]);
        }
    };
    return (
        <div className="flex flex-wrap items-baseline mb-2">
            <span className="mr-2 text-gray-600 font-medium h-8 flex items-center text-sm">
                专业门类：
            </span>
            <Button
                type={selectedCategories.length === 0 ? "primary" : "text"}
                size="small"
                className="mr-2 mb-2 h-8"
                onClick={() => handleSelect(undefined)}
            >
                不限
            </Button>
            {MAJOR_CATEGORIES.map((c) => (
                <Button
                    key={c}
                    type={selectedCategories.includes(c) ? "primary" : "text"}
                    size="small"
                    className="mr-2 mb-2 h-8"
                    onClick={() => handleSelect(c)}
                >
                    {c}
                </Button>
            ))}
        </div>
    );
}
