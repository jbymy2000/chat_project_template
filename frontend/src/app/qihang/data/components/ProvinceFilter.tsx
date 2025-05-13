import { Button } from "antd";

const PROVINCES = [
    "北京",
    "天津",
    "河北",
    "山西",
    "内蒙古",
    "辽宁",
    "吉林",
    "黑龙江",
    "上海",
    "江苏",
    "浙江",
    "安徽",
    "福建",
    "江西",
    "山东",
    "河南",
    "湖北",
    "湖南",
    "广东",
    "广西",
    "海南",
    "重庆",
    "四川",
    "贵州",
    "云南",
    "西藏",
    "陕西",
    "甘肃",
    "青海",
    "宁夏",
    "新疆",
];

interface ProvinceFilterProps {
    selectedProvinces: string[];
    onChange: (selected: string[]) => void;
}

export default function ProvinceFilter({
    selectedProvinces,
    onChange,
}: ProvinceFilterProps) {
    const handleSelect = (value?: string) => {
        if (value === undefined) {
            onChange([]);
            return;
        }
        if (selectedProvinces.includes(value)) {
            onChange(selectedProvinces.filter((v) => v !== value));
        } else {
            onChange([
                ...selectedProvinces.filter((v) => v !== undefined),
                value,
            ]);
        }
    };
    return (
        <div className="flex flex-wrap items-baseline mb-2">
            <span className="mr-2 text-gray-600 font-medium h-8 flex items-center text-sm">
                院校地区：
            </span>
            <Button
                type={selectedProvinces.length === 0 ? "primary" : "text"}
                size="small"
                className="mr-2 mb-2 h-8"
                onClick={() => handleSelect(undefined)}
            >
                不限
            </Button>
            {PROVINCES.map((p) => (
                <Button
                    key={p}
                    type={selectedProvinces.includes(p) ? "primary" : "text"}
                    size="small"
                    className="mr-2 mb-2 h-8"
                    onClick={() => handleSelect(p)}
                >
                    {p}
                </Button>
            ))}
        </div>
    );
}
