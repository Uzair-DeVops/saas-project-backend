"use client";

import { useEffect, useState } from "react";
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
  BarChart3,
  Video,
  Play,
  Eye,
  TrendingUp,
  Users,
  ArrowUpRight,
  ArrowDownRight,
  Plus,
  Upload,
  Zap,
} from "lucide-react";
import { DashboardOverview, Playlist, VideoAnalytics } from "@/types";
import { formatNumber, formatDate } from "@/lib/utils";
import toast from "react-hot-toast";
import Link from "next/link";

export default function DashboardPage() {
  const { user } = useAuth();
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [recentVideos, setRecentVideos] = useState<VideoAnalytics[]>([]);
  const [topPlaylists, setTopPlaylists] = useState<Playlist[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const [overviewData, videosData, playlistsData] = await Promise.all([
        apiClient.getDashboardOverview(),
        apiClient.getDashboardVideos(),
        apiClient.getDashboardPlaylists(),
      ]);

      setOverview(overviewData);
      setRecentVideos(videosData.slice(0, 5));
      setTopPlaylists(playlistsData.slice(0, 5));
    } catch (error) {
      console.error("Error loading dashboard data:", error);
      toast.error("Failed to load dashboard data");
    } finally {
      setIsLoading(false);
    }
  };

  const stats = [
    {
      name: "Total Videos",
      value: overview?.total_videos || 0,
      icon: Video,
      change: "+12%",
      changeType: "positive" as const,
    },
    {
      name: "Total Views",
      value: formatNumber(overview?.total_views || 0),
      icon: Eye,
      change: "+8%",
      changeType: "positive" as const,
    },
    {
      name: "Total Playlists",
      value: overview?.total_playlists || 0,
      icon: Play,
      change: "+5%",
      changeType: "positive" as const,
    },
    {
      name: "Total Likes",
      value: formatNumber(overview?.total_likes || 0),
      icon: TrendingUp,
      change: "+15%",
      changeType: "positive" as const,
    },
  ];

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="h-96 bg-gray-200 rounded"></div>
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
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600">Welcome back, {user?.full_name}!</p>
          </div>
          <div className="flex space-x-3">
            <Button
              onClick={() => (window.location.href = "/dashboard/upload")}
            >
              <Plus className="w-4 h-4 mr-2" />
              Upload Video
            </Button>
            <Button
              variant="outline"
              onClick={() => (window.location.href = "/dashboard/analytics")}
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              View Analytics
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat) => (
            <Card key={stat.name}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      {stat.name}
                    </p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stat.value}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <stat.icon className="w-6 h-6 text-primary-600" />
                  </div>
                </div>
                <div className="mt-4 flex items-center">
                  {stat.changeType === "positive" ? (
                    <ArrowUpRight className="w-4 h-4 text-green-500 mr-1" />
                  ) : (
                    <ArrowDownRight className="w-4 h-4 text-red-500 mr-1" />
                  )}
                  <span
                    className={`text-sm font-medium ${
                      stat.changeType === "positive"
                        ? "text-green-600"
                        : "text-red-600"
                    }`}
                  >
                    {stat.change}
                  </span>
                  <span className="text-sm text-gray-500 ml-1">
                    from last month
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts and Lists */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Videos */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Videos</CardTitle>
              <CardDescription>
                Your latest video uploads and their performance
              </CardDescription>
            </CardHeader>
            <CardContent>
              {recentVideos.length > 0 ? (
                <div className="space-y-4">
                  {recentVideos.map((video) => (
                    <div
                      key={video.video_id}
                      className="flex items-center space-x-4"
                    >
                      <div className="w-16 h-12 bg-gray-200 rounded-lg flex-shrink-0"></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {video.title}
                        </p>
                        <p className="text-sm text-gray-500">
                          {formatNumber(video.views || 0)} views •{" "}
                          {formatNumber(video.likes || 0)} likes
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">
                          {(video.engagement_rate || 0).toFixed(1)}%
                        </p>
                        <p className="text-xs text-gray-500">Engagement</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Video className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No videos uploaded yet</p>
                  <Button
                    variant="outline"
                    className="mt-4"
                    onClick={() => (window.location.href = "/dashboard/upload")}
                  >
                    Upload your first video
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Top Playlists */}
          <Card>
            <CardHeader>
              <CardTitle>Top Playlists</CardTitle>
              <CardDescription>Your best performing playlists</CardDescription>
            </CardHeader>
            <CardContent>
              {topPlaylists.length > 0 ? (
                <div className="space-y-4">
                  {topPlaylists.map((playlist) => (
                    <div
                      key={playlist.id}
                      className="flex items-center space-x-4"
                    >
                      <div className="w-16 h-12 bg-gray-200 rounded-lg flex-shrink-0"></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {playlist.title}
                        </p>
                        <p className="text-sm text-gray-500">
                          {playlist.total_videos || 0} videos •{" "}
                          {formatNumber(playlist.total_views || 0)} views
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">
                          {formatNumber(playlist.total_likes || 0)}
                        </p>
                        <p className="text-xs text-gray-500">Likes</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Play className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No playlists created yet</p>
                  <Button
                    variant="outline"
                    className="mt-4"
                    onClick={() =>
                      (window.location.href = "/dashboard/playlists")
                    }
                  >
                    Create your first playlist
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks to help you get started
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Link href="/dashboard/upload">
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-6 text-center">
                    <Upload className="w-8 h-8 text-primary-600 mx-auto mb-3" />
                    <h3 className="font-medium text-gray-900">Upload Video</h3>
                    <p className="text-sm text-gray-500">
                      Upload a new video to your channel
                    </p>
                  </CardContent>
                </Card>
              </Link>

              <Link href="/dashboard/ai-tools">
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-6 text-center">
                    <Zap className="w-8 h-8 text-primary-600 mx-auto mb-3" />
                    <h3 className="font-medium text-gray-900">AI Tools</h3>
                    <p className="text-sm text-gray-500">
                      Generate titles, descriptions & thumbnails
                    </p>
                  </CardContent>
                </Card>
              </Link>

              <Link href="/dashboard/analytics">
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-6 text-center">
                    <BarChart3 className="w-8 h-8 text-primary-600 mx-auto mb-3" />
                    <h3 className="font-medium text-gray-900">Analytics</h3>
                    <p className="text-sm text-gray-500">
                      View detailed performance metrics
                    </p>
                  </CardContent>
                </Card>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
