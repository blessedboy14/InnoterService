from datetime import date

from celery import shared_task

from blog.models import Page


@shared_task
def unblock_pages_today():
    pages = Page.objects.filter(unblock_date__lte=date.today())
    for page in pages:
        page.unblock()
    return f"{len(pages)} pages unblocked."
