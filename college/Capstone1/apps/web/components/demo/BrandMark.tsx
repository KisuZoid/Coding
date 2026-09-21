interface BrandMarkProps {
  className?: string;
}

/** AutoInspect-X brand mark: an inspection shield carrying an amber X. */
export default function BrandMark({ className }: BrandMarkProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" className={className} aria-hidden="true">
      <path
        d="M12 2.5 19.5 6v5.6c0 4.3-2.9 8.2-7.5 9.9-4.6-1.7-7.5-5.6-7.5-9.9V6L12 2.5Z"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <path d="M9 9.2 15 15M15 9.2l-6 5.8" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}