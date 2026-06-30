from django.contrib import admin
from .models import *

# Custom admin Table design
class UserAdmin(admin.ModelAdmin):
    list_per_page = 15 # No of records per page 
    list_display = ("id","role","name","shopname","email","contact_no","is_approved","created_at","updated_at")
    list_display_links = ("id","role","name","shopname","email","contact_no","is_approved","created_at","updated_at")
    ordering = ("-id"),
    list_filter = ("role",)
    search_fields = ("name",)
    

class ProductsAdmin(admin.ModelAdmin):
    # model = Categories
    list_per_page = 15 # No of records per page 
    list_display = ("id","product_name_eng","product_name_guj","product_name_hin","product_image","product_qty","product_unit","product_gst_rate","product_discount_rate","product_price","product_tax_price","product_hsn_code","is_delete","created_at")
    list_display_links = ("id","product_name_eng","product_name_guj","product_name_hin","product_image","product_qty","product_unit","product_gst_rate","product_discount_rate","product_price","product_tax_price","product_hsn_code","is_delete","created_at")
    ordering = ("-id"),
    list_filter = ("product_gst_rate",)
    search_fields = ("product_name_eng","product_name_guj","product_name_hin",)


class OrderListAdmin(admin.ModelAdmin):
    list_per_page = 15 # No of records per page 
    list_display = ("id","order_id","product_id","qty","cgst_rate","sgst_rate","cgst_amount","sgst_amount","amount","tax_amount","status","created_at")
    list_display_links = ("id","order_id","product_id","qty","cgst_rate","sgst_rate","cgst_amount","sgst_amount","amount","tax_amount","status","created_at")
    search_fields = ("order_id",)
    
    
# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Products, ProductsAdmin)
admin.site.register(Order)
admin.site.register(Order_data, OrderListAdmin)
admin.site.register(order_taxes)