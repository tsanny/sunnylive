import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const getUserAvatar = (username: string) => {
  const colors = [
    "EF4444",
    "3B82F6",
    "10B981",
    "F59E0B",
    "6366F1",
    "8B5CF6",
    "EC4899",
  ];
  const charCode = username.charCodeAt(0);
  const colorIndex = charCode % colors.length;
  const color = colors[colorIndex];
  return `https://ui-avatars.com/api/?rounded=true&name=${username}&background=${color}`;
};

export const getUsernameColor = (username: string) => {
  const colors = [
    "text-red-500",
    "text-blue-500",
    "text-green-500",
    "text-yellow-500",
    "text-indigo-500",
    "text-purple-500",
    "text-pink-500",
  ];
  const charCode = username.charCodeAt(0);
  const colorIndex = charCode % colors.length;
  return colors[colorIndex];
};
