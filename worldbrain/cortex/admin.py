from django.contrib import admin
from fsm_admin.mixins import FSMTransitionMixin

from .models import Source, AllUrl, SourceStates, Article


def move_sources_to_ready(source):
    if source.state == SourceStates.PENDING.value:
        source.ready()
        source.save()
        return 1
    else:
        return 0


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin, FSMTransitionMixin):
    fsm_field = ('state',)
    readonly_fields = ('state', 'last_time_crawled', 'last_error_message')
    list_display = ('domain_name', 'state', 'trusted_source',)
    list_filter = ('state', 'trusted_source',)
    actions = ['make_ready', 'make_trusted']

    def make_ready(self, request, queryset):
        count_updated = 0
        for source in queryset:
            count_updated += move_sources_to_ready(source)
        self.message_user(request,
                          '%s of %s successfully marked as ready for '
                          'crawling.'
                          % (count_updated, queryset.all().count()))

    make_ready.short_description = 'Mark sources as ready for ' \
                                   'crawling'

    def make_trusted(self, request, queryset):
        sources_updated = queryset.update(trusted_source=True)
        if sources_updated == 1:
            message_bit = "1 source was"
        else:
            message_bit = "%s sources were" % sources_updated
        self.message_user(request,
                          "%s successfully marked as Trusted sources." %
                          message_bit)

    make_trusted.short_description = 'Mark sources as trusted'


@admin.register(AllUrl)
class AllUrlAdmin(admin.ModelAdmin, FSMTransitionMixin):
    list_display = ('url', 'state', )
    fsm_field = ('state',)
    readonly_fields = ('state',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin, FSMTransitionMixin):
    fsm_field = ('state',)
    readonly_fields = ('title', 'url', 'text', 'publish_date', 'authors',
                       'tags', 'summary', 'state', 'parse_time', 'links',
                       'keywords')
