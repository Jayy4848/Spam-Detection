from django.urls import path
from .views import PredictView, FeedbackView, StatsView, HealthCheckView
from .advanced_views import ThreatIntelligenceView, ModelPerformanceView, AdvancedStatsView, ExportDataView

urlpatterns = [
    path('predict/', PredictView.as_view(), name='predict'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
    path('stats/', StatsView.as_view(), name='stats'),
    path('health/', HealthCheckView.as_view(), name='health'),
    path('threat-intelligence/', ThreatIntelligenceView.as_view(), name='threat-intelligence'),
    path('model-performance/', ModelPerformanceView.as_view(), name='model-performance'),
    path('advanced-stats/', AdvancedStatsView.as_view(), name='advanced-stats'),
    path('export/', ExportDataView.as_view(), name='export'),
]
