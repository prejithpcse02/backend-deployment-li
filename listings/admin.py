from django.contrib import admin
from .models import Listing, ListingImage

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1  # Allows adding images inline in the admin panel

class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'status', 'created_at', 'updated_at')
    inlines = [ListingImageInline]  # Attach images inline in listing

# ✅ Register the Listing model correctly
admin.site.register(Listing, ListingAdmin)
admin.site.register(ListingImage)  # If not already registered
