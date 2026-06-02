import { type ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
}

export default function Card({ children, className = "" }: CardProps) {
  return (
    <div
      className={`bg-[var(--color-surface)] border-[3px] border-[var(--color-text)] rounded-[var(--radius-lg)] shadow-[4px_4px_0_rgba(26,26,46,0.10)] transition-all duration-150 ease-out hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0_rgba(26,26,46,0.10)] ${className}`}
    >
      {children}
    </div>
  );
}

function CardHeader({ children, className = "" }: CardProps) {
  return (
    <div
      className={`px-6 py-5 border-b-2 border-[var(--color-divider)] font-semibold text-[15px] ${className}`}
    >
      {children}
    </div>
  );
}

function CardBody({ children, className = "" }: CardProps) {
  return <div className={`px-6 py-6 ${className}`}>{children}</div>;
}

function CardFooter({ children, className = "" }: CardProps) {
  return (
    <div
      className={`px-6 py-4 border-t-2 border-[var(--color-divider)] ${className}`}
    >
      {children}
    </div>
  );
}

Card.Header = CardHeader;
Card.Body = CardBody;
Card.Footer = CardFooter;
