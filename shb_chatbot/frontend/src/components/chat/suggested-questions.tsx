"use client";

import { Button } from "@/components/ui";

interface SuggestedQuestionsProps {
  questions: string[];
  onSelect: (question: string) => void;
}

export function SuggestedQuestions({ questions, onSelect }: SuggestedQuestionsProps) {
  if (questions.length === 0) return null;

  return (
    <div className="flex flex-col gap-2 w-full">
      <p className="text-[10px] font-bold text-brand uppercase tracking-widest mb-1 opacity-70 px-1">
        Gợi ý tìm hiểu
      </p>
      <div className="flex flex-wrap gap-2">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onSelect(question)}
            className="text-left px-4 py-2 rounded-xl border border-brand/20 bg-card hover:border-brand/50 hover:bg-brand/5 transition-all text-xs sm:text-sm shadow-sm active:scale-95"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
