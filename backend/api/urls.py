from django.urls import path
from .views import PredictView, FeedbackView, StatsView, HealthCheckView, ResetDataView, ModelInfoView, RecentMessagesView, DeleteMessageView, DeleteAllMessagesView
from .advanced_views import ThreatIntelligenceView, ModelPerformanceView, AdvancedStatsView, ExportDataView

urlpatterns = [
    path('predict/', PredictView.as_view(), name='predict'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
    path('stats/', StatsView.as_view(), name='stats'),
    path('health/', HealthCheckView.as_view(), name='health'),
    path('reset/', ResetDataView.as_view(), name='reset'),
    path('model-info/', ModelInfoView.as_view(), name='model-info'),
    path('recent-messages/', RecentMessagesView.as_view(), name='recent-messages'),
    path('messages/<int:message_id>/', DeleteMessageView.as_view(), name='delete-message'),
    path('messages/delete-all/', DeleteAllMessagesView.as_view(), name='delete-all-messages'),
    path('threat-intelligence/', ThreatIntelligenceView.as_view(), name='threat-intelligence'),
    path('model-performance/', ModelPerformanceView.as_view(), name='model-performance'),
    path('advanced-stats/', AdvancedStatsView.as_view(), name='advanced-stats'),
    path('export/', ExportDataView.as_view(), name='export'),
]
