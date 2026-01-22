import Link from 'next/link';
import { Network, Shield, Zap, ArrowRight } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-4 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Unified Identity
            <span className="text-blue-400"> Graph System</span>
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-10">
            Manage your fragmented digital identities in one place. 
            Visualize, verify, and control your personal data across platforms.
          </p>
          
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors text-lg"
          >
            Go to Dashboard
            <ArrowRight size={20} />
          </Link>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <FeatureCard
            icon={<Network className="h-10 w-10 text-blue-400" />}
            title="Visual Graph"
            description="See your identity data as an interactive knowledge graph"
          />
          <FeatureCard
            icon={<Shield className="h-10 w-10 text-green-400" />}
            title="Conflict Detection"
            description="Automatically detect and resolve conflicting claims"
          />
          <FeatureCard
            icon={<Zap className="h-10 w-10 text-amber-400" />}
            title="Real-time Sync"
            description="Import credentials from multiple sources instantly"
          />
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center py-8 text-gray-500 text-sm">
        UIGS - Academic Project © 2024
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/10">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  );
}
