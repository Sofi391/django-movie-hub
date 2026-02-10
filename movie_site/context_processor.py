from .models import Notification

def notification_count(request):
    """
    Context processor to add notification count to all templates.
    """
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        total_count = Notification.objects.filter(recipient=request.user).count()
        return {
            'unread_notification_count': unread_count,
            'total_notification_count': total_count,
            'has_notifications': total_count > 0
        }
    return {
        'unread_notification_count': 0,
        'total_notification_count': 0,
        'has_notifications': False
    }