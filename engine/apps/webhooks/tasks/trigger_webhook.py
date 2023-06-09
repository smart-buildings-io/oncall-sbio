import json
import logging
from json import JSONDecodeError

from celery.utils.log import get_task_logger
from django.apps import apps
from django.conf import settings

from apps.alerts.models import AlertGroup
from apps.user_management.models import User
from apps.webhooks.models import Webhook, WebhookResponse
from apps.webhooks.utils import (
    InvalidWebhookData,
    InvalidWebhookHeaders,
    InvalidWebhookTrigger,
    InvalidWebhookUrl,
    serialize_event,
)
from common.custom_celery_tasks import shared_dedicated_queue_retry_task

logger = get_task_logger(__name__)
logger.setLevel(logging.DEBUG)


TRIGGER_TYPE_TO_LABEL = {
    Webhook.TRIGGER_NEW: "firing",
    Webhook.TRIGGER_ACKNOWLEDGE: "acknowledge",
    Webhook.TRIGGER_RESOLVE: "resolve",
    Webhook.TRIGGER_SILENCE: "silence",
    Webhook.TRIGGER_UNSILENCE: "unsilence",
    Webhook.TRIGGER_UNRESOLVE: "unresolve",
}


@shared_dedicated_queue_retry_task(
    autoretry_for=(Exception,), retry_backoff=True, max_retries=1 if settings.DEBUG else None
)
def send_webhook_event(trigger_type, alert_group_id, team_id=None, organization_id=None, user_id=None):
    Webhooks = apps.get_model("webhooks", "Webhook")
    webhooks_qs = Webhooks.objects.filter(trigger_type=trigger_type, organization_id=organization_id, team_id=team_id)

    for webhook in webhooks_qs:
        execute_webhook.apply_async((webhook.pk, alert_group_id, user_id))


def _isoformat_date(date_value):
    return date_value.isoformat() if date_value else None


def _build_payload(trigger_type, alert_group, user_id):
    user = None
    if user_id is not None:
        user = User.objects.filter(pk=user_id).first()

    event = {
        "type": TRIGGER_TYPE_TO_LABEL[trigger_type],
    }
    if trigger_type == Webhook.TRIGGER_NEW:
        event["time"] = _isoformat_date(alert_group.started_at)
    elif trigger_type == Webhook.TRIGGER_ACKNOWLEDGE:
        event["time"] = _isoformat_date(alert_group.acknowledged_at)
    elif trigger_type == Webhook.TRIGGER_RESOLVE:
        event["time"] = _isoformat_date(alert_group.resolved_at)
    elif trigger_type == Webhook.TRIGGER_SILENCE:
        event["time"] = _isoformat_date(alert_group.silenced_at)
        event["until"] = _isoformat_date(alert_group.silenced_until)

    # include latest response data per trigger in the event input data
    responses_data = {}
    responses = alert_group.webhook_responses.all().order_by("timestamp")
    for r in responses:
        try:
            response_data = r.json()
        except JSONDecodeError:
            response_data = r.content
        responses_data[TRIGGER_TYPE_TO_LABEL[r.trigger_type]] = response_data

    data = serialize_event(event, alert_group, user, responses_data)

    return data


@shared_dedicated_queue_retry_task(
    autoretry_for=(Exception,), retry_backoff=True, max_retries=1 if settings.DEBUG else None
)
def execute_webhook(webhook_pk, alert_group_id, user_id):
    Webhooks = apps.get_model("webhooks", "Webhook")
    try:
        webhook = Webhooks.objects.get(pk=webhook_pk)
    except Webhooks.DoesNotExist:
        logger.warn(f"Webhook {webhook_pk} does not exist")
        return

    try:
        alert_group = AlertGroup.unarchived_objects.get(pk=alert_group_id)
    except AlertGroup.DoesNotExist:
        return

    data = _build_payload(webhook.trigger_type, alert_group, user_id)
    status = {
        "url": None,
        "request_trigger": None,
        "request_headers": None,
        "request_data": data,
        "status_code": None,
        "content": None,
        "webhook": webhook,
    }

    exception = None
    try:
        triggered, status["request_trigger"] = webhook.check_trigger(data)
        if triggered:
            status["url"] = webhook.build_url(data)
            request_kwargs = webhook.build_request_kwargs(data, raise_data_errors=True)
            status["request_headers"] = json.dumps(request_kwargs.get("headers", {}))
            if "json" in request_kwargs:
                status["request_data"] = json.dumps(request_kwargs["json"])
            else:
                status["request_data"] = request_kwargs.get("data")
            response = webhook.make_request(status["url"], request_kwargs)
            status["status_code"] = response.status_code
            try:
                status["content"] = json.dumps(response.json())
            except JSONDecodeError:
                status["content"] = response.content.decode("utf-8")
        else:
            # do not add a log entry if the webhook is not triggered
            return
    except InvalidWebhookUrl as e:
        status["url"] = e.message
    except InvalidWebhookTrigger as e:
        status["request_trigger"] = e.message
    except InvalidWebhookHeaders as e:
        status["request_headers"] = e.message
    except InvalidWebhookData as e:
        status["request_data"] = e.message
    except Exception as e:
        status["content"] = str(e)
        exception = e

    # create response entry
    WebhookResponse.objects.create(
        alert_group=alert_group,
        trigger_type=webhook.trigger_type,
        **status,
    )

    if exception:
        raise exception
