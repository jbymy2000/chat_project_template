import { Button } from "antd";

const SCHOOL_TYPES = [
    "综合",
    "理工",
    "农林",
    "医药",
    "师范",
    "语言",
    "财经",
    "政法",
    "体育",
    "艺术",
    "民族",
    "军事",
    "其他",
];

interface TypeFilterProps {
    selectedTypes: string[];
    onChange: (selected: string[]) => void;
}

export default function TypeFilter({
    selectedTypes,
    onChange,
}: TypeFilterProps) {
    const handleSelect = (value?: string) => {
        if (value === undefined) {
            onChange([]);
            return;
        }
        if (selectedTypes.includes(value)) {
            onChange(selectedTypes.filter((v) => v !== value));
        } else {
            onChange([...selectedTypes.filter((v) => v !== undefined), value]);
        }
    };
    return (
        <div className="flex flex-wrap items-baseline mb-2">
            <span className="mr-2 text-gray-600 font-medium h-8 flex items-center text-sm">
                院校类型：
            </span>
            <Button
                type={selectedTypes.length === 0 ? "primary" : "text"}
                size="small"
                className="mr-2 mb-2 h-8"
                onClick={() => handleSelect(undefined)}
            >
                不限
            </Button>
            {SCHOOL_TYPES.map((t) => (
                <Button
                    key={t}
                    type={selectedTypes.includes(t) ? "primary" : "text"}
                    size="small"
                    className="mr-2 mb-2 h-8"
                    onClick={() => handleSelect(t)}
                >
                    {t}
                </Button>
            ))}
        </div>
    );
}
