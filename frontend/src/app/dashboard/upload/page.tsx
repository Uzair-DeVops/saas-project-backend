"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import { useAuth } from "@/hooks/useAuth";
import { apiClient } from "@/lib/api";
import DashboardLayout from "@/components/layout/DashboardLayout";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import {
  Upload,
  Video,
  Link as LinkIcon,
  FileVideo,
  X,
  CheckCircle,
  AlertCircle,
  Clock,
} from "lucide-react";
import { formatBytes, formatDuration } from "@/lib/utils";
import toast from "react-hot-toast";

interface UploadedFile {
  file: File;
  id: string;
  progress: number;
  status: "uploading" | "processing" | "completed" | "error";
  error?: string;
}

export default function UploadPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");
  const [isDownloading, setIsDownloading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file) => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      progress: 0,
      status: "uploading" as const,
    }));

    setUploadedFiles((prev) => [...prev, ...newFiles]);
    handleUpload(newFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "video/*": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"],
    },
    multiple: true,
  });

  const handleUpload = async (files: UploadedFile[]) => {
    setIsUploading(true);

    for (const fileData of files) {
      try {
        const formData = new FormData();
        formData.append("file", fileData.file);

        // Simulate upload progress
        const progressInterval = setInterval(() => {
          setUploadedFiles((prev) =>
            prev.map((f) =>
              f.id === fileData.id
                ? { ...f, progress: Math.min(f.progress + 10, 90) }
                : f
            )
          );
        }, 200);

        const response = await apiClient.uploadVideo(formData);

        clearInterval(progressInterval);

        setUploadedFiles((prev) =>
          prev.map((f) =>
            f.id === fileData.id
              ? { ...f, progress: 100, status: "completed" }
              : f
          )
        );

        toast.success(`${fileData.file.name} uploaded successfully!`);

        // Redirect to video details after successful upload
        setTimeout(() => {
          router.push(`/dashboard/videos/${response.id}`);
        }, 2000);
      } catch (error) {
        console.error("Upload error:", error);
        setUploadedFiles((prev) =>
          prev.map((f) =>
            f.id === fileData.id
              ? { ...f, status: "error", error: "Upload failed" }
              : f
          )
        );
        toast.error(`Failed to upload ${fileData.file.name}`);
      }
    }

    setIsUploading(false);
  };

  const handleDownloadFromUrl = async () => {
    if (!videoUrl.trim()) {
      toast.error("Please enter a valid video URL");
      return;
    }

    setIsDownloading(true);

    try {
      const response = await apiClient.downloadVideo(videoUrl);
      toast.success("Video downloaded successfully!");

      // Redirect to video details
      setTimeout(() => {
        router.push(`/dashboard/videos/${response.id}`);
      }, 2000);
    } catch (error) {
      console.error("Download error:", error);
      toast.error("Failed to download video from URL");
    } finally {
      setIsDownloading(false);
    }
  };

  const removeFile = (id: string) => {
    setUploadedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const getStatusIcon = (status: UploadedFile["status"]) => {
    switch (status) {
      case "uploading":
        return <Clock className="w-5 h-5 text-blue-500" />;
      case "processing":
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "error":
        return <AlertCircle className="w-5 h-5 text-red-500" />;
    }
  };

  const getStatusText = (status: UploadedFile["status"]) => {
    switch (status) {
      case "uploading":
        return "Uploading...";
      case "processing":
        return "Processing...";
      case "completed":
        return "Completed";
      case "error":
        return "Error";
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Upload Video</h1>
          <p className="text-gray-600">
            Upload videos to your channel or download from URLs
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* File Upload */}
          <Card>
            <CardHeader>
              <CardTitle>Upload Video Files</CardTitle>
              <CardDescription>
                Drag and drop video files or click to browse
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? "border-primary-500 bg-primary-50"
                    : "border-gray-300 hover:border-primary-400"
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                {isDragActive ? (
                  <p className="text-primary-600 font-medium">
                    Drop the files here...
                  </p>
                ) : (
                  <div>
                    <p className="text-gray-600 mb-2">
                      Drag & drop video files here, or click to select files
                    </p>
                    <p className="text-sm text-gray-500">
                      Supports MP4, AVI, MOV, MKV, WMV, FLV, WebM
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* URL Download */}
          <Card>
            <CardHeader>
              <CardTitle>Download from URL</CardTitle>
              <CardDescription>
                Download videos from YouTube, Vimeo, or other platforms
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <label
                    htmlFor="videoUrl"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Video URL
                  </label>
                  <div className="flex space-x-2">
                    <input
                      id="videoUrl"
                      type="url"
                      value={videoUrl}
                      onChange={(e) => setVideoUrl(e.target.value)}
                      placeholder="https://www.youtube.com/watch?v=..."
                      className="input-field flex-1"
                    />
                    <Button
                      onClick={handleDownloadFromUrl}
                      loading={isDownloading}
                      disabled={!videoUrl.trim()}
                    >
                      <LinkIcon className="w-4 h-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start">
                    <LinkIcon className="w-5 h-5 text-blue-500 mr-3 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-medium text-blue-900">
                        Supported Platforms
                      </h4>
                      <p className="text-sm text-blue-700 mt-1">
                        YouTube, Vimeo, Dailymotion, Facebook, Instagram,
                        TikTok, and more
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Upload Progress */}
        {uploadedFiles.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Upload Progress</CardTitle>
              <CardDescription>
                Track the progress of your video uploads
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {uploadedFiles.map((fileData) => (
                  <div
                    key={fileData.id}
                    className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg"
                  >
                    <div className="flex-shrink-0">
                      {getStatusIcon(fileData.status)}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {fileData.file.name}
                        </p>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(fileData.id)}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>

                      <div className="flex items-center justify-between mt-1">
                        <p className="text-sm text-gray-500">
                          {formatBytes(fileData.file.size)}
                        </p>
                        <p className="text-sm font-medium text-gray-900">
                          {getStatusText(fileData.status)}
                        </p>
                      </div>

                      {fileData.status === "uploading" && (
                        <div className="mt-2">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${fileData.progress}%` }}
                            />
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {fileData.progress}% complete
                          </p>
                        </div>
                      )}

                      {fileData.status === "error" && fileData.error && (
                        <p className="text-sm text-red-600 mt-1">
                          {fileData.error}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Tips */}
        <Card>
          <CardHeader>
            <CardTitle>Upload Tips</CardTitle>
            <CardDescription>
              Best practices for successful video uploads
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900">File Requirements</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Maximum file size: 2GB</li>
                  <li>
                    • Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM
                  </li>
                  <li>• Recommended resolution: 1080p or higher</li>
                  <li>• Recommended bitrate: 8-12 Mbps for 1080p</li>
                </ul>
              </div>

              <div className="space-y-3">
                <h4 className="font-medium text-gray-900">Best Practices</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Use descriptive filenames</li>
                  <li>• Ensure stable internet connection</li>
                  <li>• Don't close the browser during upload</li>
                  <li>• Check video quality before uploading</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
