import { getValidatedStrategies } from '@/lib/db'
import { getStatus } from '@/lib/registry'
import StrategyCard from '@/components/StrategyCard'

export const dynamic = 'force-dynamic'

export default function IndexPage() {
  const strategies = getValidatedStrategies(1.0)

  const validated = strategies.filter((s) => getStatus(s.sharpe) === 'validated')
  const promising = strategies.filter((s) => getStatus(s.sharpe) !== 'validated')

  return (
    <div className="px-8 py-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white tracking-tight">Strategy Lab</h1>
        <p className="text-gray-500 mt-1 text-sm">
          {strategies.length} validated edge{strategies.length !== 1 ? 's' : ''} — sorted by Sharpe
        </p>
      </div>

      {validated.length > 0 && (
        <section className="mb-10">
          <h2 className="text-xs font-semibold text-gray-600 uppercase tracking-widest mb-4">
            Verified Edges
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {validated.map((s) => (
              <StrategyCard key={s.slug} strategy={s} />
            ))}
          </div>
        </section>
      )}

      {promising.length > 0 && (
        <section>
          <h2 className="text-xs font-semibold text-gray-600 uppercase tracking-widest mb-4">
            Promising
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {promising.map((s) => (
              <StrategyCard key={s.slug} strategy={s} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
