"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
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
  Video,
  Play,
  Upload,
  Eye,
  Heart,
  MessageCircle,
  MoreVertical,
  Search,
  Filter,
} from "lucide-react";
import { Video as VideoType } from "@/types";
import { formatBytes, formatDuration, formatDate } from "@/lib/utils";
import toast from "react-hot-toast";

export default function VideosPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [videos, setVideos] = useState<VideoType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    try {
      setIsLoading(true);
      const videosData = await apiClient.getMyVideos();
      setVideos(videosData);
    } catch (error) {
      console.error("Error loading videos:", error);
      toast.error("Failed to load videos");
    } finally {
      setIsLoading(false);
    }
  };

  const filteredVideos = videos.filter((video) => {
    const matchesSearch =
      (video.original_filename &&
        video.original_filename
          .toLowerCase()
          .includes(searchTerm.toLowerCase())) ||
      (video.title &&
        video.title.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesFilter =
      filterStatus === "all" || video.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ready":
        return "text-green-600 bg-green-100";
      case "processing":
        return "text-yellow-600 bg-yellow-100";
      case "uploading":
        return "text-blue-600 bg-blue-100";
      case "error":
        return "text-red-600 bg-red-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "ready":
        return <Play className="w-4 h-4" />;
      case "processing":
        return <Video className="w-4 h-4" />;
      case "uploading":
        return <Upload className="w-4 h-4" />;
      case "error":
        return <Video className="w-4 h-4" />;
      default:
        return <Video className="w-4 h-4" />;
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-64 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">My Videos</h1>
            <p className="text-gray-600">
              Manage and organize your video content
            </p>
          </div>
          <Button onClick={() => router.push("/dashboard/upload")}>
            <Upload className="w-4 h-4 mr-2" />
            Upload Video
          </Button>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search videos..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="input-field pl-10"
                  />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Filter className="w-4 h-4 text-gray-400" />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="input-field"
                >
                  <option value="all">All Status</option>
                  <option value="ready">Ready</option>
                  <option value="processing">Processing</option>
                  <option value="uploading">Uploading</option>
                  <option value="error">Error</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Videos Grid */}
        {filteredVideos.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredVideos.map((video) => (
              <Card
                key={video.id}
                className="hover:shadow-lg transition-shadow cursor-pointer"
              >
                <div className="relative">
                  <div className="w-full h-48 bg-gray-200 rounded-t-lg flex items-center justify-center">
                    <Video className="w-12 h-12 text-gray-400" />
                  </div>
                  <div
                    className={`absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1 ${getStatusColor(
                      video.status
                    )}`}
                  >
                    {getStatusIcon(video.status)}
                    <span className="capitalize">{video.status}</span>
                  </div>
                </div>

                <CardContent className="p-4">
                  <div className="space-y-3">
                    <div>
                      <h3 className="font-medium text-gray-900 truncate">
                        {video.title || video.original_filename}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {formatDate(video.created_at)}
                      </p>
                    </div>

                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span>{formatBytes(video.file_size || 0)}</span>
                      <span>{formatDuration(video.duration || 0)}</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center space-x-1">
                          <Eye className="w-4 h-4" />
                          <span>0</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Heart className="w-4 h-4" />
                          <span>0</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <MessageCircle className="w-4 h-4" />
                          <span>0</span>
                        </div>
                      </div>

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/dashboard/videos/${video.id}`);
                        }}
                      >
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="p-12 text-center">
              <Video className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {searchTerm || filterStatus !== "all"
                  ? "No videos found"
                  : "No videos uploaded yet"}
              </h3>
              <p className="text-gray-500 mb-6">
                {searchTerm || filterStatus !== "all"
                  ? "Try adjusting your search or filter criteria"
                  : "Upload your first video to get started"}
              </p>
              <Button onClick={() => router.push("/dashboard/upload")}>
                <Upload className="w-4 h-4 mr-2" />
                Upload Video
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Stats */}
        <Card>
          <CardHeader>
            <CardTitle>Video Statistics</CardTitle>
            <CardDescription>Overview of your video content</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {videos.length}
                </div>
                <div className="text-sm text-gray-500">Total Videos</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {videos.filter((v) => v.status === "ready").length}
                </div>
                <div className="text-sm text-gray-500">Ready</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  {videos.filter((v) => v.status === "processing").length}
                </div>
                <div className="text-sm text-gray-500">Processing</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {videos.filter((v) => v.status === "uploading").length}
                </div>
                <div className="text-sm text-gray-500">Uploading</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
