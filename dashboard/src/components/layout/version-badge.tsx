import { cn } from '@/lib/utils'
interface VersionBadgeProps { currentVersion: string | null; className?: string }
export function VersionBadge({ currentVersion, className }: VersionBadgeProps) {
  return <a href="https://github.com/sabi-karami/SABI-RAY/releases" target="_blank" rel="noopener noreferrer" className={cn('text-[10px] text-amber-500', className)} title={`SABI-RAY alpha · upstream ${currentVersion || 'unknown'}`}>SABI-RAY α 0.2</a>
}
