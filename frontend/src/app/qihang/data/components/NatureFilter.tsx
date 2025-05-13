import { SCHOOL_NATURES } from "@/constants/constants";
import { Button } from "antd";

interface NatureFilterProps {
    selectedNatures: string[];
    onChange: (selected: string[]) => void;
}

export default function NatureFilter({
    selectedNatures,
    onChange,
}: NatureFilterProps) {
    const handleSelect = (value?: string) => {
        if (value === undefined) {
            onChange([]);
            return;
        }
        if (selectedNatures.includes(value)) {
            onChange(selectedNatures.filter((v) => v !== value));
        } else {
            onChange([
                ...selectedNatures.filter((v) => v !== undefined),
                value,
            ]);
        }
    };
    return (
        <div className="flex flex-wrap items-baseline mb-2">
            <span className="mr-2 text-gray-600 font-medium h-8 flex items-center text-sm">
                院校性质：
            </span>
            <Button
                type={selectedNatures.length === 0 ? "primary" : "text"}
                size="small"
                className="mr-2 mb-2 h-8"
                onClick={() => handleSelect(undefined)}
            >
                不限
            </Button>
            {SCHOOL_NATURES.map((n) => (
                <Button
                    key={n.value}
                    type={
                        selectedNatures.includes(n.value) ? "primary" : "text"
                    }
                    size="small"
                    className="mr-2 mb-2 h-8"
                    onClick={() => handleSelect(n.value)}
                >
                    {n.label}
                </Button>
            ))}
        </div>
    );
}
