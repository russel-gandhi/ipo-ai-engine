"use client";

import React from "react";

interface TooltipProps {
  content: string;
  children?: React.ReactNode;
}

export default function Tooltip({ content, children }: TooltipProps) {
  return (
    <span className="relative inline-flex items-center group cursor-help ml-1">
      {children || (
        <span className="w-4 h-4 rounded-full bg-input-bg border border-input-border text-[10px] text-muted-text flex items-center justify-center font-mono font-medium hover:text-primary-text hover:border-secondary-text transition-colors">
          i
        </span>
      )}
      <span className="pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-max max-w-[240px] bg-white border border-card-border rounded-[8px] p-2.5 text-[11px] text-primary-text leading-tight shadow-lg z-50 font-normal normal-case">
        {content}
        <span className="absolute top-full left-1/2 -translate-x-1/2 -mt-px border-4 border-transparent border-t-white"></span>
      </span>
    </span>
  );
}
