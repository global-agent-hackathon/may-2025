import React from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";

interface TutorSelectProps {
  onSubjectChange: (subject: string) => void;
  onLanguageChange: (language: string) => void;
  showLanguageSelect: boolean;
}

const TutorSelect = ({ onSubjectChange, onLanguageChange, showLanguageSelect }: TutorSelectProps) => {
  const subjects = [
    { value: "physics", label: "Physics" },
    { value: "chemistry", label: "Chemistry" },
    { value: "mathematics", label: "Mathematics" },
    { value: "language", label: "Language Learning" },
  ];

  const languages = [
    { value: "en", label: "English" },
    { value: "fr", label: "French" },
    { value: "es", label: "Spanish" },
    { value: "de", label: "German" },
    { value: "it", label: "Italian" },
    { value: "ja", label: "Japanese" },
    { value: "zh", label: "Chinese" },
    { value: "dk", label: "Danish" },
  ];

  return (
    <div className="flex gap-4 items-center justify-center">
      <div className="w-64">
        <Select onValueChange={onSubjectChange}>
          <SelectTrigger>
            <SelectValue placeholder="Select a subject" />
          </SelectTrigger>
          <SelectContent>
            {subjects.map((subject) => (
              <SelectItem key={subject.value} value={subject.value}>
                {subject.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {showLanguageSelect && (
        <div className="w-64">
          <Select onValueChange={onLanguageChange} defaultValue="en">
            <SelectTrigger>
              <SelectValue placeholder="Select a language" />
            </SelectTrigger>
            <SelectContent>
              {languages.map((language) => (
                <SelectItem key={language.value} value={language.value}>
                  {language.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}
    </div>
  );
};

export default TutorSelect;
