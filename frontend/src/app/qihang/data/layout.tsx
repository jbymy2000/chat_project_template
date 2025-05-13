"use client";
import React from "react";
import DataNav from "./components/DataNav";

export default function DataLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="p-4 max-w-7xl mx-auto">
            <DataNav />
            {children}
        </div>
    );
}
