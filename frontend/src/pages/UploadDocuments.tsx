import { useState, FormEvent } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';

export default function UploadDocuments() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [files, setFiles] = useState<{
        resume: File | null;
        roleDescription: File | null;
        jobOffering: File | null;
    }>({
        resume: null,
        roleDescription: null,
        jobOffering: null,
    });

    const handleFileChange = (field: 'resume' | 'roleDescription' | 'jobOffering') => (
        e: React.ChangeEvent<HTMLInputElement>
    ) => {
        const file = e.target.files?.[0] || null;
        setFiles((prev) => ({ ...prev, [field]: file }));
    };

    const handleUpload = async (e: FormEvent) => {
        e.preventDefault();

        if (!files.resume || !files.roleDescription || !files.jobOffering) {
            setError('Please select all required files');
            return;
        }

        if (!id) {
            setError('No interview ID found');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const interview = await apiClient.uploadDocuments(
                parseInt(id),
                files.resume,
                files.roleDescription,
                files.jobOffering
            );

            // Navigate to interview details page
            navigate(`/admin/interviews/${interview.id}`);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to upload documents');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
            <div className="max-w-2xl mx-auto">
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20">
                    <h1 className="text-3xl font-bold text-white mb-2">Upload Documents</h1>
                    <p className="text-purple-200 mb-8">
                        Upload the required documents for Interview #{id}
                    </p>

                    {error && (
                        <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg mb-6">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleUpload} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-purple-200 mb-2">
                                Candidate Resume (PDF)
                            </label>
                            <input
                                type="file"
                                accept=".pdf"
                                onChange={handleFileChange('resume')}
                                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-purple-500 file:text-white hover:file:bg-purple-600"
                                required
                            />
                            {files.resume && (
                                <p className="mt-1 text-sm text-green-300">✓ {files.resume.name}</p>
                            )}
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-purple-200 mb-2">
                                Role Description (PDF)
                            </label>
                            <input
                                type="file"
                                accept=".pdf"
                                onChange={handleFileChange('roleDescription')}
                                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-purple-500 file:text-white hover:file:bg-purple-600"
                                required
                            />
                            {files.roleDescription && (
                                <p className="mt-1 text-sm text-green-300">✓ {files.roleDescription.name}</p>
                            )}
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-purple-200 mb-2">
                                Job Offering (PDF)
                            </label>
                            <input
                                type="file"
                                accept=".pdf"
                                onChange={handleFileChange('jobOffering')}
                                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-purple-500 file:text-white hover:file:bg-purple-600"
                                required
                            />
                            {files.jobOffering && (
                                <p className="mt-1 text-sm text-green-300">✓ {files.jobOffering.name}</p>
                            )}
                        </div>

                        <div className="flex gap-4">
                            <button
                                type="submit"
                                disabled={loading}
                                className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold py-3 px-6 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Uploading & Analyzing...' : 'Upload & Analyze'}
                            </button>
                            <button
                                type="button"
                                onClick={() => navigate(`/admin/interviews/${id}`)}
                                className="px-6 py-3 bg-white/10 border border-white/20 text-white font-semibold rounded-lg hover:bg-white/20 transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </form>

                    {loading && (
                        <div className="mt-6 text-center">
                            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-purple-500 border-t-transparent mb-2"></div>
                            <p className="text-purple-200">
                                Analyzing documents... This may take a moment.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
