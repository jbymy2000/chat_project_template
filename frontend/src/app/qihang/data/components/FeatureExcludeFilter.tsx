import { Button } from "antd";

const MAJOR_EXCLUDES = [
    "排除中外合作专业",
    "排除校企合作专业",
    "排除少数民族专业",
];

interface FeatureExcludeFilterProps {
    selectedExcludes: string[];
    onChange: (selected: string[]) => void;
}

export default function FeatureExcludeFilter({
    selectedExcludes,
    onChange,
}: FeatureExcludeFilterProps) {
    const handleSelect = (value?: string) => {
        if (value === undefined) {
            onChange([]);
            return;
        }
        if (selectedExcludes.includes(value)) {
            onChange(selectedExcludes.filter((v) => v !== value));
        } else {
            onChange([
                ...selectedExcludes.filter((v) => v !== undefined),
                value,
            ]);
        }
    };
    return (
        <div className="flex flex-wrap items-baseline mb-2">
            <span className="mr-2 text-gray-600 font-medium h-8 flex items-center text-sm">
                是否排除：
            </span>
            <Button
                type={selectedExcludes.length === 0 ? "primary" : "text"}
                size="small"
                className="mr-2 mb-2 h-8"
                onClick={() => handleSelect(undefined)}
            >
                不限
            </Button>
            {MAJOR_EXCLUDES.map((e) => (
                <Button
                    key={e}
                    type={selectedExcludes.includes(e) ? "primary" : "text"}
                    size="small"
                    className="mr-2 mb-2 h-8"
                    onClick={() => handleSelect(e)}
                >
                    {e}
                </Button>
            ))}
        </div>
    );
}
