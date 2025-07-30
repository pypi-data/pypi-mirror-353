from django.contrib import admin

from django_hls.models import DjangoHLSMedia, HLSMedia

admin.site.register(HLSMedia)
admin.site.register(DjangoHLSMedia)