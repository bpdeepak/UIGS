'use client';

import { useState, useRef } from 'react';
import { X, Upload, FileJson, AlertCircle, CheckCircle } from 'lucide-react';
import { ingestCredential } from '@/lib/api-client';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function UploadModal({ isOpen, onClose, onSuccess }: UploadModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<Record<string, unknown> | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setError(null);
    setSuccess(false);

    try {
      const text = await selectedFile.text();
      const json = JSON.parse(text);
      setPreview(json);
    } catch {
      setError('Invalid JSON file');
      setPreview(null);
    }
  };

  const handleUpload = async () => {
    if (!preview) return;

    setIsUploading(true);
    setError(null);

    try {
      await ingestCredential({
        source_type: 'VC',
        payload: preview,
      });
      setSuccess(true);
      setTimeout(() => {
        onSuccess();
        handleClose();
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setPreview(null);
    setError(null);
    setSuccess(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            Upload Verifiable Credential
          </h2>
          <button
            onClick={handleClose}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* File Input */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              onChange={handleFileChange}
              className="hidden"
            />
            <FileJson className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-sm text-gray-600">
              {file ? file.name : 'Click to select a JSON file'}
            </p>
            <p className="text-xs text-gray-400 mt-1">
              W3C Verifiable Credential format
            </p>
          </div>

          {/* Preview */}
          {preview && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Preview</h3>
              <div className="space-y-2 text-sm">
                {'type' in preview && preview.type ? (
                  <div>
                    <span className="text-gray-500">Type:</span>{' '}
                    <span className="font-medium">
                      {Array.isArray(preview.type) ? (preview.type as string[]).join(', ') : String(preview.type)}
                    </span>
                  </div>
                ) : null}
                {'issuer' in preview && preview.issuer ? (
                  <div>
                    <span className="text-gray-500">Issuer:</span>{' '}
                    <span className="font-mono text-xs">
                      {typeof preview.issuer === 'object'
                        ? String((preview.issuer as Record<string, unknown>).id ?? JSON.stringify(preview.issuer))
                        : String(preview.issuer)}
                    </span>
                  </div>
                ) : null}
                {'credentialSubject' in preview && preview.credentialSubject ? (
                  <div>
                    <span className="text-gray-500">Claims:</span>
                    <ul className="ml-4 mt-1 space-y-1">
                      {Object.entries(preview.credentialSubject as Record<string, unknown>)
                        .filter(([key]) => key !== 'id')
                        .slice(0, 5)
                        .map(([key, value]) => (
                          <li key={key} className="text-xs">
                            <span className="text-gray-600">{key}:</span>{' '}
                            <span className="font-medium">
                              {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                            </span>
                          </li>
                        ))}
                    </ul>
                  </div>
                ) : null}
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="flex items-center gap-2 text-red-600 bg-red-50 p-3 rounded-lg">
              <AlertCircle size={20} />
              <span className="text-sm">{error}</span>
            </div>
          )}

          {/* Success */}
          {success && (
            <div className="flex items-center gap-2 text-green-600 bg-green-50 p-3 rounded-lg">
              <CheckCircle size={20} />
              <span className="text-sm">Credential uploaded successfully!</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t bg-gray-50">
          <button
            onClick={handleClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!preview || isUploading || success}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Upload size={16} />
            {isUploading ? 'Uploading...' : 'Upload Credential'}
          </button>
        </div>
      </div>
    </div>
  );
}
