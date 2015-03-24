from django.db.models.query import QuerySet

from ...compat import metrics


class TimedQuerySet(QuerySet):

    def _get_metric_name(self, query_type):
        return 'database.query.%s.%s.%s.time' % (
            query_type,
            self.model._meta.app_label,
            self.model._meta.model_name,
        )

    def iterator(self, *args, **kwargs):
        with metrics.time(self._get_metric_name('iterator')):
            results = super(TimedQuerySet, self).iterator(*args, **kwargs)
        return results

    def aggregate(self, *args, **kwargs):
        with metrics.time(self._get_metric_name('aggregate')):
            results = super(TimedQuerySet, self).aggregate(*args, **kwargs)
        return results

    def count(self, *args, **kwargs):
        with metrics.time(self._get_metric_name('count')):
            results = super(TimedQuerySet, self).count(*args, **kwargs)
        return count

    def get(self, *args, **kwargs):
        with metrics.time(self._get_metric_name('get')):
            results = super(TimedQuerySet, self).get(*args, **kwargs)
        return results

    def create(self, *args, **kwargs):
        with metrics.time(self._get_metric_name('create')):
            results = super(TimedQuerySet, self).create(*args, **kwargs)
        return results

    def bulk_create(self, *args, **kwargs):
        with metrics.time(self._get_metric_name('bulk_create')):
            results = super(TimedQuerySet, self).bulk_create(*args, **kwargs)
        return results

    def update(self, *args, **kwargs):
        with metrics.time(self._get_metric_name('update')):
            results = super(TimedQuerySet, self).update(*args, **kwargs)
        return results

    def exists(self, *args, **kwargs):
        with metrics.time(self._get_metric_name('exists')):
            results = super(TimedQuerySet, self).exists(*args, **kwargs)
        return results
