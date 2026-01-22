'use client';

import { useState } from 'react';
import { Header } from '@/components/layout/Header';
import { UploadModal } from '@/components/upload/UploadModal';
import { useGraph } from '@/hooks/useGraph';
import { Upload, FileJson, CheckCircle } from 'lucide-react';

export default function UploadPage() {
  const { refetch, processEvents } = useGraph();
  const [showModal, setShowModal] = useState(false);
  const [recentUploads, setRecentUploads] = useState<string[]>([]);

  const handleSuccess = () => {
    setRecentUploads((prev) => [...prev, new Date().toISOString()]);
    processEvents(10);
    refetch();
  };

  return (
    <div className="h-screen flex flex-col">
      <Header title="Upload Credential" />

      <div className="flex-1 p-6">
        <div className="max-w-2xl mx-auto">
          {/* Upload Area */}
          <button
            onClick={() => setShowModal(true)}
            className="w-full bg-white rounded-xl shadow-lg p-12 border-2 border-dashed border-gray-300 hover:border-blue-500 hover:bg-blue-50 transition-all group"
          >
            <div className="text-center">
              <Upload className="mx-auto h-16 w-16 text-gray-400 group-hover:text-blue-500 transition-colors" />
              <h2 className="mt-4 text-xl font-semibold text-gray-900">
                Upload Verifiable Credential
              </h2>
              <p className="mt-2 text-gray-500">
                Click to select a JSON file containing a W3C Verifiable Credential
              </p>
            </div>
          </button>

          {/* Supported Formats */}
          <div className="mt-8 bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Supported Formats</h3>
            <div className="space-y-3">
              <FormatItem
                title="W3C Verifiable Credential"
                description="JSON-LD format with @context and credentialSubject"
              />
              <FormatItem
                title="University Credentials"
                description="Degrees, certificates, and academic records"
              />
              <FormatItem
                title="Employment Credentials"
                description="Work history and employment verification"
              />
              <FormatItem
                title="Government IDs"
                description="Identity documents and official records"
              />
            </div>
          </div>

          {/* Recent Uploads */}
          {recentUploads.length > 0 && (
            <div className="mt-8 bg-green-50 rounded-lg p-6">
              <h3 className="font-semibold text-green-800 flex items-center gap-2">
                <CheckCircle size={20} />
                Recent Uploads
              </h3>
              <ul className="mt-3 space-y-2">
                {recentUploads.map((timestamp, i) => (
                  <li key={i} className="text-sm text-green-700">
                    Credential uploaded at {new Date(timestamp).toLocaleTimeString()}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      <UploadModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSuccess={handleSuccess}
      />
    </div>
  );
}

function FormatItem({ title, description }: { title: string; description: string }) {
  return (
    <div className="flex items-start gap-3">
      <FileJson className="h-5 w-5 text-blue-500 mt-0.5" />
      <div>
        <p className="font-medium text-gray-900">{title}</p>
        <p className="text-sm text-gray-500">{description}</p>
      </div>
    </div>
  );
}
