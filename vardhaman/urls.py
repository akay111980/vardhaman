from django.urls import path
from . import views
from . import templateviews 

urlpatterns = [
    # Mobile APIs
    path('api/restore_from_excel', views.restoreFromExcel),
    path('api/user_register', views.userRegister),
    path('api/user_login', views.userLogin),
    path('api/user_logout', views.userLogout),
    path('api/fetch_user_data_list/<str:userId>', views.getUserDataList),
    path('api/user_approval_by_admin', views.userApproval),
    path('api/get_all_product_list', views.getAllProductsList),
    path('api/search_product_list', views.searchProducts),
    path('api/update_user_profile', views.userUpdate),
    path('api/generate_orders', views.generateOrder),
    path('api/update_orders/<str:orderId>', views.updateOrders),
    path('api/get_list_of_orders/<str:userId>', views.listOfOrders),
    path('api/get_order_invoice/<str:orderId>', views.downloadPdf),
    
    
    # Templates Path
    path('', templateviews.index, name='indexpage'),
    path('logout', templateviews.logout, name='logout'),
    path("login",  templateviews.login, name="login"),
    path('profilePage', templateviews.profilePage, name="profilePage"),
    path('profileupdate', templateviews.profileUpdate, name="profileUpdate"),
    path('adminlogin', templateviews.loginFunction, name='loginadmin'),
    path('users/all', templateviews.userPage, name='userPage'),
    path('products/all', templateviews.productsPage, name='productPage'),
    path('products/addPage', templateviews.addProductPage, name='addProductPage'),
    path('products/processing', templateviews.productAddUpdateFunctionality, name='productAddUpdateFunctionality'),
    path('products/<str:productId>/edit', templateviews.editProductPage, name='editProductPage'),
    path('products/<str:productId>/delete', templateviews.productDeleteFunctionality, name='deleteProductPage'),
    path('orders/all', templateviews.ordersPage, name='ordersPage'),
    path('orders/invoice', templateviews.invoicePage, name='invoicepage'),
    path('orders/billing', templateviews.billingPage, name='billingPage'),
    path('esstimate/all', templateviews.esstimatePage, name='esstimatePage'),
    path('esstimate/delete', templateviews.deleteEsstimate, name='deleteAllEsstimate'),
    path('esstimate/form', templateviews.esstimateForm, name='esstimateCreatepage'),
    path('esstimate/create', templateviews.createEsstimate, name='createEsstimate'),
    path('esstimate/invoice', templateviews.invoiceEsstimatePage, name='invoiceEsstimatePage'),

    path('orders/billing/generate', templateviews.createOrderFromAdmin, name='createOrderFromAdmin'),
    path('orders/<str:id>/delete', templateviews.orderDelete, name='orderDelete'),
    path('productsearching', templateviews.productSearchByName, name='productSearchByName'),
    path('customersearching', templateviews.customerSearchByName, name='customerSearchByName'),
    path('delete-all-orders', templateviews.deleteAllOrder, name='deleteAllOrder'),
]
