from datetime import date

from django.db import models


class ConcurrentUpdateError(Exception):
    pass


class AlertGroupCounterQuerySet(models.QuerySet):
    def get_value(self, organization):
        counter, _ = self.get_or_create(organization=organization)

        today = date.today()
        update_kwargs = {}
        if counter.current_month.month != today.month or counter.current_month.year != today.year:
            # if the previous alert group was created not in the current month, reset the monthly counter values
            update_kwargs["current_month"] = today
            update_kwargs["value_this_month"] = 1
        else:
            update_kwargs["value_this_month"] = counter.value_this_month + 1

        num_updated_rows = self.filter(organization=organization, value=counter.value).update(
            value=counter.value + 1, **update_kwargs
        )
        if num_updated_rows == 0:
            raise ConcurrentUpdateError()

        return counter.value


class AlertGroupCounter(models.Model):
    """
    This model is used to assign unique, increasing inside_organization_number's for alert groups.
    It uses optimistic locking to get values and raises ConcurrentUpdateError exception in case of concurrent updates.
    This is used on alert group creation in order to not block Celery workers with select_for_update and give space
    to other tasks to run in case of high load on alert group creation.
    """

    objects = models.Manager.from_queryset(AlertGroupCounterQuerySet)()

    organization = models.OneToOneField("user_management.Organization", on_delete=models.CASCADE)
    value = models.PositiveBigIntegerField(default=0)

    current_month = models.DateField(default=date.today)
    value_this_month = models.PositiveBigIntegerField(default=0)
