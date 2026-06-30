from django.db import models

# Create your models here.


class User(models.Model):
    role = models.CharField(
        max_length=15, default="0", choices=[("0", "Customer"), ("1", "Admin")]
    )
    name = models.CharField(default="", max_length=255, null=True)
    shopname = models.CharField(default="", max_length=255, null=True)
    email = models.CharField(default="", max_length=255, null=True)
    contact_no = models.CharField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    register_by = models.CharField(max_length=255, default="self", null=True)
    is_approved = models.CharField(
        max_length=10,
        default="0",
        choices=[("0", "Pending"), ("1", "Approved"), ("2", "Rejected")],
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    expo_go_token = models.CharField(max_length=255, blank=True, null=True)
    gst_no = models.CharField(max_length=255, blank=True, null=True)
    bankname = models.CharField(max_length=255, blank=True, null=True)
    holderName = models.CharField(max_length=255, blank=True, null=True)
    branch_name = models.CharField(max_length=255, blank=True, null=True)
    ifsc_code = models.CharField(max_length=255, blank=True, null=True)
    account_num = models.CharField(max_length=255, blank=True, null=True)
    fassai = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.name if self.name else self.email


class Products(models.Model):
    product_name_eng = models.CharField(max_length=255, null=True)
    product_name_guj = models.CharField(max_length=255, null=True)
    product_name_hin = models.CharField(max_length=255, null=True)
    product_image = models.FileField(
        upload_to="Product_images/%Y%m%d/%H%M%S/", blank=True, null=True
    )
    product_qty = models.CharField(max_length=255, null=True)
    product_unit = models.CharField(max_length=255, null=True)
    product_gst_rate = models.IntegerField(default=0)
    product_discount_rate = models.IntegerField(default=0)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_gst = models.DecimalField(max_digits=10, decimal_places=2)
    product_tax_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_hsn_code = models.CharField(max_length=255, null=True)
    is_delete = models.CharField(
        max_length=10, default="0", choices=[("0", "No"), ("1", "Yes")]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Products"


class Order(models.Model):
    order_id = models.IntegerField(default=0)
    customer_id = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    name = models.CharField(default="", max_length=255, null=True)
    email = models.CharField(default="", max_length=255, null=True)
    contact_no = models.CharField(max_length=255, null=True)
    gst_no = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    round_off = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    round_type = models.CharField(default="less", max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    grand_total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    status = models.CharField(
        max_length=10, default="0", choices=[("0", "Pending"), ("1", "Approved")]
    )
    invoice_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Orders"


class Order_data(models.Model):
    order_id = models.ForeignKey(Order, blank=True, null=True, on_delete=models.CASCADE)
    product_id = models.ForeignKey(
        Products, blank=True, null=True, on_delete=models.CASCADE
    )
    qty = models.CharField(max_length=255, blank=True, null=True)
    cgst_rate = models.CharField(default="0", max_length=255, blank=True, null=True)
    sgst_rate = models.CharField(default="0", max_length=255, blank=True, null=True)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=10, default="0", choices=[("0", "Pending"), ("1", "Approved")]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Orders_list"


class order_taxes(models.Model):
    order_id = models.ForeignKey(Order, blank=True, null=True, on_delete=models.CASCADE)
    tax_rate = models.CharField(default="0", max_length=255, blank=True, null=True)
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )


class Esstimate(models.Model):
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_number = models.CharField(max_length=255, null=True, blank=True)
    invoice_date = models.DateField(blank=True, null=True)
    items_list = models.JSONField(blank=True, null=True)
    grand_total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
