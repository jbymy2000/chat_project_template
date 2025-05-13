import { Button } from "antd";

const SCHOOL_FEATURES = [
    "985",
    "211",
    "双一流",
    "强基院校",
    "101计划",
    "研究生院",
    "保研资格",
    "国重点",
    "省重点",
    "部委院校",
    "省属",
    "省部共建",
    "C9",
    "E9",
    "国防七子",
    "五院四系",
    "两电一邮",
    "八大美院",
    "双高计划",
    "高水平学校建设单位",
    "高水平专业群建设单位",
    "国家级示范",
    "国家级骨干",
    "现代学徒制试点学院",
    "香港高才通",
];

interface FeatureFilterProps {
    selectedFeatures: string[];
    onChange: (selected: string[]) => void;
}

export default function FeatureFilter({
    selectedFeatures,
    onChange,
}: FeatureFilterProps) {
    const handleSelect = (value?: string) => {
        if (value === undefined) {
            onChange([]);
            return;
        }
        if (selectedFeatures.includes(value)) {
            onChange(selectedFeatures.filter((v) => v !== value));
        } else {
            onChange([
                ...selectedFeatures.filter((v) => v !== undefined),
                value,
            ]);
        }
    };
    return (
        <div className="flex flex-wrap items-baseline mb-2">
            <span className="mr-2 text-gray-600 font-medium h-8 flex items-center text-sm">
                院校特色：
            </span>
            <Button
                type={selectedFeatures.length === 0 ? "primary" : "text"}
                size="small"
                className="mr-2 mb-2 h-8"
                onClick={() => handleSelect(undefined)}
            >
                不限
            </Button>
            {SCHOOL_FEATURES.map((f) => (
                <Button
                    key={f}
                    type={selectedFeatures.includes(f) ? "primary" : "text"}
                    size="small"
                    className="mr-2 mb-2 h-8"
                    onClick={() => handleSelect(f)}
                >
                    {f}
                </Button>
            ))}
        </div>
    );
}
