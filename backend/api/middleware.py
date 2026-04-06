"""
Custom middleware for request logging and performance monitoring
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

logger = logging.getLogger('api')


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log all API requests with relevant metadata"""
    
    def process_request(self, request):
        request.start_time = time.time()
        
        # Log request details
        logger.info(f"Request: {request.method} {request.path}")
        
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"Response: {request.method} {request.path} "
                f"Status: {response.status_code} "
                f"Duration: {duration:.3f}s"
            )
        
        return response


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Monitor API performance and track metrics"""
    
    def process_request(self, request):
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Track slow requests
            if duration > 1.0:  # More than 1 second
                logger.warning(
                    f"Slow request detected: {request.method} {request.path} "
                    f"took {duration:.3f}s"
                )
            
            # Store performance metrics in cache
            cache_key = f"perf_metrics_{request.path}"
            metrics = cache.get(cache_key, [])
            metrics.append(duration)
            
            # Keep only last 100 requests
            if len(metrics) > 100:
                metrics = metrics[-100:]
            
            cache.set(cache_key, metrics, timeout=3600)
        
        return response
