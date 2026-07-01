from rest_framework.response import Response
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from django.contrib.auth.hashers  import make_password,check_password
from django.utils import timezone
from datetime import timedelta
from num2words import num2words

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken  # use to generate Token
from .isAuthanticated import tokenVerified # Custome Class to check Token
from .helpers import sendNotification, savePdf, sign_indicator # Function to send notification

import json
import logging

# Models Data here 
from .models import *
from django.db.models import Q
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

# Create your views here.

# status codes values
statusCode = {
    "0" : 'Pending',
    "1" : 'Approved',
    "2" : 'Rejected'
}

# GST counter Function
def calculate_sgst(total_amount, sgst_rate):
    sgst_amount = (total_amount * sgst_rate) / 100
    return sgst_amount

# funtion return the Product Data 
from bson.decimal128 import Decimal128

def to_float(value):
    """Safely convert Decimal128 to float, handle None values."""
    if value is None:
        return 0.00
    if isinstance(value, Decimal128):
        return float(value.to_decimal())  # More accurate conversion
    try:
        return float(value)
    except ValueError:
        return 0.00  # Fallback if conversion fails

def getProductData(product):
    """Extracts product details and converts Decimal128 fields properly."""
    return {
        "id": str(product.id),  # Convert ID to string
        "product_image": product.product_image.url if product.product_image else "",
        "product_name_eng": product.product_name_eng or "",
        "product_name_guj": product.product_name_guj or "",
        "product_name_hin": product.product_name_hin or "",
        "product_qty": product.product_qty or "",
        "product_unit": product.product_unit or "",
        "product_price_not_tax": to_float(product.product_price),
        "product_price": to_float(product.product_tax_price),
        "product_gst_rate": to_float(product.product_gst_rate),
        "product_discount_rate": to_float(product.product_discount_rate),
        "product_hsn_code": product.product_hsn_code or "",
        "is_delete": product.is_delete,
        "created_at": product.created_at.isoformat() if product.created_at else None,  # Convert datetime to string
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }


# def getProductData(product):
#     productObject = {
#         "id": product.id,
#         "product_image": product.product_image.url if product.product_image else "",
#         "product_name_eng": product.product_name_eng if product.product_name_eng else "" ,
#         "product_name_guj": product.product_name_guj if product.product_name_guj else "",
#         "product_name_hin": product.product_name_hin if product.product_name_hin else "",
#         "product_qty": product.product_qty if product.product_qty else "",
#         "product_unit": product.product_unit if product.product_unit else "",
#         "product_price_not_tax": product.product_price if f"₹ {product.product_price}" else "₹ 0.00",
#         "product_price": product.product_tax_price if f"₹ {product.product_tax_price}" else "₹ 0.00",
#         "product_gst_rate": product.product_gst_rate if f"{product.product_gst_rate}%" else "",
#         "product_discount_rate": product.product_discount_rate if f"{product.product_discount_rate}%" else "",
#         "product_hsn_code": product.product_hsn_code,
#         "is_delete": product.is_delete,
#         "created_at": product.created_at,
#         "updated_at": product.updated_at,
#     }
#     return productObject

# function return the User Data
def getUsersData(user):
    userObject = {
        'id' : user.id,
        "name" : user.name if user.name else "",
        "email" : user.email if user.email else "",
        "contact_no" : user.contact_no if user.contact_no else "",
        "is_approved" : user.is_approved if user.is_approved else "",
        "notificationToken" : user.expo_go_token if user.expo_go_token else "",
        "address" : user.address if user.address else "",
        "role" : user.role if user.role else "",
        'gst_no': user.gst_no if user.gst_no else "",
        "created_at" : user.created_at,
        "updated_at" : user.updated_at
    }
    return userObject

# this function is returns the amount based on the Number
def getInwordsUsingNumber(amount):
    integer_part = int(amount)
    decimal_part = int((amount - integer_part) * 100)
    integer_words = num2words(integer_part).casefold().replace("-", " ").replace("and", "")
    decimal_words = num2words(decimal_part).casefold().replace("-", " ").replace("and", "")
    return f"{integer_words} rupees"


# manage Notification Center function
def manageNotifications(tokenFor, expoToken ,title, message):
    if tokenFor == "User":
        sendNotification(expoToken,title, message)
    
    if tokenFor == "Admin":
        allUser = User.objects.filter(role='1',is_approved='1')
        for admin in allUser:
            if admin.expo_go_token:
                sendNotification(admin.expo_go_token,title, message)

# Get UserID based on the Token
def getUserIdBasedOnToken(refresh_token):
    try:
        token = refresh_token.split(' ')[1]
        authorization_header = AccessToken(token)
        user_id = authorization_header.payload['user_id']
        return user_id
    except Exception as e:
        # Handle exceptions like TokenError or KeyError
        return None
    

# User Register API
@api_view(["POST"])
def userRegister(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        name = data.get('name')
        email = data.get('email')
        contact_no = data.get('contact_no')
        password = data.get('password')
        address = data.get('address')
        firebase_token = data.get('firebase_token')
        if not name and not contact_no and not password and not firebase_token:
            return Response({'message':"Please provide valid name, contact_no, and password."},status=400)
        
        emailValidate = User.objects.filter(email=email)
        contactValidate = User.objects.filter(contact_no=contact_no)
        if len(emailValidate) > 0 or len(contactValidate) > 0:
            return Response({'message':"User Already Exists."},status=400)
        User.objects.create(
            role = '0',
            name = name,
            email = email,
            expo_go_token = firebase_token,
            contact_no = contact_no,
            password = make_password(password),
            address = address,
        )
        
        manageNotifications('Admin','',"New User Registration", f"A new user named {name} has registered. Please review their details in the admin panel.")
        return Response({'message':"User register successfully.Wait for Approval."},status=200)
    except json.JSONDecodeError:
        return Response({'message': "Invalid JSON data in the request body."}, status=400)
    except User.DoesNotExist:
        return Response({'message': "User not found."}, status=404)
    except Exception as e:
        logger.error(f"User Register Exception : {str(e)}")
        return Response({'message': str(e)}, status=500)

# User Login API
@api_view(['POST'])
def userLogin(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
        firebase_token = data.get('firebase_token')

        if not (username and password):
            return Response({'message': "Please provide a valid username and password."}, status=400)

        email_validate = User.objects.filter(email=username)
        contact_validate = User.objects.filter(contact_no=username)

        if email_validate.exists():
            user_data = email_validate[0]
        elif contact_validate.exists():
            user_data = contact_validate[0]
        else:
            return Response({'message': "User not registered."}, status=404)

        if user_data.is_approved in ('0', '2'):
            return Response({'message': "Access Denied."}, status=403)

        if check_password(password, user_data.password):
            user_data.expo_go_token = firebase_token
            user_data.save()
            refresh = RefreshToken.for_user(user_data)
            token = str(refresh.access_token)
            return Response({'message': "User logged in successfully", 'token': token, "userData": getUsersData(user_data)}, status=200)
        else:
            return Response({'message': "Invalid username or password."}, status=400)

    except json.JSONDecodeError:
        return Response({'message': "Invalid JSON data in the request body."}, status=400)
    except User.DoesNotExist:
        return Response({'message': "User not found."}, status=404)
    except Exception as e:
        logger.error(f"User Login Exception: {str(e)}")
        return Response({'message': "Internal server error."}, status=500)

# User Logout API
@api_view(['POST'])
@tokenVerified
def userLogout(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        userId = data.get('userId')
        if userId is None:
            return Response({'message': "Please provide valid userId."}, status=400)
        user_instance = get_object_or_404(User, id=userId)
        user_instance.expo_go_token = ''
        user_instance.save()
        return Response({'message': f"User Logout successfully"}, status=200)
    except json.JSONDecodeError:
        return Response({'message': "Invalid JSON data in the request body."}, status=400)
    except User.DoesNotExist:
        return Response({'message': "User not found."}, status=404)
    except Exception as e:
        return Response({'message': str(e)}, status=500)

# All Users API
@api_view(['GET'])
@tokenVerified
def getUserDataList(request,userId):
    try:
        if not userId:
            return Response({'message':"Please provide appropiat User id or all"},status=400)
        
        if userId == "all":
            userData = User.objects.filter(role=0)
        else:
            userData = User.objects.filter(id=userId,role=0).first()
            return Response({'message':"User Data fecthed",'data': getUsersData(userData)},status=200)
        
        userList = []
        for user in userData:
            userValue = getUsersData(user)
            userList.append(userValue)
        return Response({'message':"User Data fecthed",'data': userList},status=200)
    except Exception as e:
        logger.error(f"User Register Exception : {str(e)}")
        return Response({'message': str(e)}, status=500)

# Update User API 
@api_view(['POST'])
@tokenVerified
def userUpdate(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        userId = data.get('userId')
        name = data.get('name')
        email = data.get('email')
        contact_no = data.get('contact_no')
        address = data.get('address')
        gst_no = data.get('gst_no')
        
        userdata = get_object_or_404(User, id=userId)
        userdata.name = name if name else userdata.name
        userdata.email = email if email else userdata.email
        userdata.contact_no = contact_no if contact_no else userdata.contact_no
        userdata.address = address if address else userdata.address
        userdata.gst_no = gst_no if gst_no else userdata.gst_no
        userdata.save() 
        
        return Response({'message': f"Profile Updated successfully"}, status=200)
    except json.JSONDecodeError:
        return Response({'message': "Invalid JSON data in the request body."}, status=400)
    except User.DoesNotExist:
        return Response({'message': "User not found."}, status=404)
    except Exception as e:
        logger.error(f"User Register Exception : {str(e)}")
        return Response({'message': str(e)}, status=500)
        
# User Approval API
@api_view(['POST'])
@tokenVerified
def userApproval(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        userId = data.get('userId')
        approval_status = data.get('approvalStatus')

        if userId is None or approval_status is None:
            return Response({'message': "Please provide valid userId and approvalStatus."}, status=400)

        status_value = {
            "0": ' ',
            "1": ' Approved ',
            "2": ' Rejected ',
        }

        user_instance = get_object_or_404(User, id=userId)
        user_instance.is_approved = approval_status
        if approval_status == '1':
            manageNotifications('User',user_instance.expo_go_token, f"Approval Confirmation for {user_instance.name}", f"Congratulations, {user_instance.name}! Your registration has been approved by the admin. Welcome to Vardhaman!")
            # sendNotification(expoToken, f"Approval Confirmation for {user_instance.name}", f"Congratulations, {user_instance.name}! Your registration has been approved by the admin. Welcome to Vardhaman!")
        if approval_status == '2':
            # sendNotification(expoToken, f"Registration Rejection for {user_instance.name}", f"We regret to inform you that your registration has been rejected. If you have any questions or concerns, please don't hesitate to reach out to us.")
                manageNotifications('User',user_instance.expo_go_token, f"Registration Rejection for {user_instance.name}", f"We regret to inform you that your registration has been rejected. If you have any questions or concerns, please don't hesitate to reach out to us.")
            
        user_instance.save()
        return Response({'message': f"User{status_value[approval_status]}successfully"}, status=200)
    except json.JSONDecodeError:
        return Response({'message': "Invalid JSON data in the request body."}, status=400)
    except User.DoesNotExist:
        return Response({'message': "User not found."}, status=404)
    except Exception as e:
        return Response({'message': str(e)}, status=500)

# All Product API
@api_view(['GET'])
@tokenVerified
def getAllProductsList(request):
    try:
        productData = Products.objects.filter(is_delete='0')
        productList = []
        for product in productData:
            product_data = getProductData(product)
            productList.append(product_data)
        return Response({'message':"Product Data fecthed",'data': productList},status=200)
    except Exception as e:
        logger.error(f"User Register Exception : {str(e)}")
        return Response({'message': str(e)}, status=500)
    
# Product Search API
@api_view(['POST'])
@tokenVerified
def searchProducts(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        name = data.get('name')
        productList = []
        
        if not name:
            return Response({"message": "Product Data searched","data": productList},status=200)
            
        productData = Products.objects.filter(
            (Q(product_name_eng__icontains=name) | Q(product_name_guj__icontains=name) | Q(product_name_hin__icontains=name))
        ).exclude(is_delete='1')
        
        for product in productData:
            product_data = getProductData(product)
            productList.append(product_data)
        return Response({'message':"Product Data searched",'data': productList},status=200)
    except json.JSONDecodeError:
        return Response({'message': "Invalid JSON data in the request body."}, status=400)
    except Exception as e:
        logger.error(f"User Register Exception : {str(e)}")
        return Response({'message': str(e)}, status=500)

# Generate Order API
@api_view(["POST"])
@tokenVerified
def generateOrder(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        userId = data.get('userId')
        productList = data.get('productList')
        if not userId or not productList:
            return Response({"message": "Please provide userId or productList.",},status=400)
        
        try:
            userdata = get_object_or_404(User, id=userId)
        except:
            return Response({"message": "Please provide valid userId.",},status=400)
        
        if userdata.is_approved in ('0', '2'):
            return Response({'message': "Access Denied."}, status=403)
        
        if not userdata.name or not userdata.email or not userdata.contact_no or not userdata.address:
            return Response({'message': "Please Update Your Profile First"}, status=403)

        newOrder = Order.objects.create(
            customer_id = userdata,
            name = userdata.name,
            email = userdata.email,
            contact_no = userdata.contact_no,
            address = userdata.address,
            round_off = 0.00,
            total_amount = 0.00,
            grand_total_amount = 0.00,
            status = '0',
        )
        
        price = 0.00
        
        for i in productList:
            try:
                productdata = get_object_or_404(Products, id=i['product'])
                
                amount = float(productdata.product_price) * int(i['qty']) # count the total amount of product
                product_tax = (float(productdata.product_gst_rate) / 2) # count the tax for cgst and sgst
                gst_cal_amount = (float(productdata.product_gst) /2 ) * int(i['qty'])  # calculate_sgst(amount, product_tax) # count price with only cgst and sgst
                tax_amount= (float(gst_cal_amount)*2) + float(amount)
                price = float(price) + tax_amount
                
                listing_order = Order_data.objects.create(
                    order_id = newOrder,
                    product_id = productdata,
                    qty = i['qty'],
                    cgst_rate = product_tax,
                    sgst_rate = product_tax,
                    cgst_amount = gst_cal_amount,
                    sgst_amount = gst_cal_amount,
                    amount =amount,
                    tax_amount= tax_amount,
                    status = '0',
                )
            except:
                pass
        newOrder.total_amount = price
        newOrder.grand_total_amount = price
        newOrder.save() 
        
        manageNotifications('User',userdata.expo_go_token, f"Order Created by {userdata.name}", f"A new order has been created by {userdata.name}. Please review the details promptly.")
        # sendNotification(expoToken, f"Order Created by {userdata.name}", f"A new order has been created by {userdata.name}. Please review the details promptly.")
        return Response({'message':"Order Created"},status=200)
    except json.JSONDecodeError:
        return Response({'message': "Invalid JSON data in the request body."}, status=400)
    except Exception as e:
        logger.error(f"User Register Exception : {str(e)}")
        return Response({'message': str(e)}, status=500)

# Get Order's List by using UserId.
@api_view(['GET'])
@tokenVerified
def listOfOrders(request,userId):
    try:
        if not userId:
            return Response({'message':"Please provide appropiat User id"},status=400)
        
        dateRange = timezone.now() - timedelta(days=7)
        
        try:
            getUser = get_object_or_404(User,id=userId)
        except:
            return Response({'message':"Please provide appropiat User id"},status=400)
            
        if getUser.role == '1':
            orderData = Order.objects.filter(created_at__range=[dateRange, timezone.now()]).exclude(customer_id=userId).order_by('-created_at')
        else:
            orderData = Order.objects.filter(customer_id=userId,created_at__range=[dateRange, timezone.now()]).order_by('-created_at')
        
        orderId = [order.id for order in orderData]
        
        order_data_list = Order_data.objects.filter(order_id__in=orderId)
        
        ordersList = []
        for item in orderData:
            newData = {}
            listOfOrder = []
            for ls in order_data_list:
                itemObj = {}
                if (ls.order_id.id) == (item.id):
                    itemObj['id'] = ls.id
                    
                    itemObj['product_id'] = ls.product_id.id
                    itemObj['product_name_eng'] = f"{ls.product_id.product_name_eng}"
                    itemObj['product_name_guj'] = f"{ls.product_id.product_name_guj}"
                    itemObj['product_name_hin'] = f"{ls.product_id.product_name_hin}"
                    itemObj['product_qty'] = f"{ls.product_id.product_qty}"
                    itemObj['product_unit'] = f"{ls.product_id.product_unit}"
                    try: 
                        itemObj['product_image'] = ls.product_id.product_image.url if ls.product_id.product_image else ""
                    except:
                        itemObj['product_image'] = ''
                        
                    itemObj['product_price'] = ls.product_id.product_price
                    itemObj['product_tax_price'] = ls.product_id.product_tax_price
                    itemObj['qty'] = ls.qty
                    itemObj['amount'] = ls.amount
                    itemObj['cgst_amount'] = ls.cgst_amount
                    itemObj['sgst_amount'] = ls.sgst_amount
                    itemObj['grand_total'] = ls.tax_amount
                    itemObj['status'] = statusCode[ls.status]
                    listOfOrder.append(itemObj)
            newData['id'] = item.id
            newData['customer_name'] = item.customer_id.name
            newData['cgst_amount'] = item.cgst_amount
            newData['sgst_amount'] = item.sgst_amount
            newData['taxable_amount'] = item.taxable_amount
            newData['round_off'] = item.round_off
            newData['total_tax_amount'] = item.total_tax_amount
            newData['total_amount'] = item.grand_total_amount
            newData['created_at'] = item.created_at
            newData['status'] = statusCode[item.status] 
            newData['orderList'] = listOfOrder 
            ordersList.append(newData)
        return Response({'message':"Success","data":ordersList},status=200)
    
    except Exception as e:
        logger.error(f"User Register Exception : {str(e)}")
        return Response({'message': str(e)}, status=500)

# this function is return the single Values.
def process_tax_data(orderId,data):
    processed_data = {}
    orderVal = get_object_or_404(Order,id=orderId)
    for item in data:
        tax_rate = item['tax_rate']
        taxable_amount = float(item['taxable_amount']) + float(item['tax_amount'])
        if tax_rate in processed_data:
            processed_data[tax_rate] += taxable_amount
        else:
            processed_data[tax_rate] = taxable_amount
            
    newList = [{'tax_rate': tax_rate, 'taxable_amount': amount} for tax_rate, amount in processed_data.items()]

    taxable_amount =  0.00
    cgst_amount =  0.00
    sgst_amount =  0.00
    total_tax_amount =  0.00
    
    for i in newList:
        if i['tax_rate'] and i['taxable_amount']:
            orderTax = order_taxes.objects.filter(order_id=orderVal,tax_rate=i['tax_rate'])
            rateCount = product_tax = (float(i['tax_rate']) / 2) # count the tax for cgst and sgst
            gst_cal_amount = calculate_sgst(i['taxable_amount'], rateCount)
            newTaxAmount = float(i['taxable_amount']) - (float(gst_cal_amount) * 2)
            taxable_amount += newTaxAmount
            tax_total_count = float(gst_cal_amount) + float(gst_cal_amount)
            
            cgst_amount += float(gst_cal_amount)
            sgst_amount += float(gst_cal_amount)
            total_tax_amount += float(tax_total_count)
            if not len(orderTax) > 0:
                newo = order_taxes.objects.create(
                    order_id = orderVal,
                    tax_rate = i['tax_rate'],
                    taxable_amount = newTaxAmount,
                    cgst_amount = gst_cal_amount,
                    sgst_amount = gst_cal_amount,
                    total_tax_amount = tax_total_count,
                )
    responseData = {
        "taxable_amount":taxable_amount,
        "cgst_amount":cgst_amount,
        "sgst_amount":sgst_amount,
        "total_tax_amount":total_tax_amount
    }
    
    return responseData


# Download file API
# @api_view(['GET'])
# @tokenVerified
def generatePDF(orderId):
    try:
        try:
            orders = Order.objects.get(id=orderId)
        except:
            return Response({"message": "Order matching query does not exist."},status=400)
            
        ordersList = Order_data.objects.filter(order_id=orderId,status='1')
        taxes_order = order_taxes.objects.filter(order_id=orderId)
        
        totalAmountWithGST = float(orders.total_amount) + (calculate_sgst(float(orders.total_amount), 4) * 2)
        
        context = {
            'order': orders,
            'seller': User.objects.filter(role='1').first(),
            'totalAmountWords': getInwordsUsingNumber(orders.grand_total_amount),
            'orderList': ordersList,
            'taxes_order': taxes_order,
        }
        
        fileName,status = savePdf(context)
        print(fileName)
        print(status)
        if not status:
            return Response({status:200})
        return Response({status :400})
    except Exception as e:
        logger.error(f"Generate PDF Error : {str(e)}")
        return Response({status:400})
    
    
# Orders Approvel API
@api_view(['POST'])
# @tokenVerified
def updateOrders(request,orderId):
    try:
        data = json.loads(request.body.decode('utf-8'))
        orderList = data.get('orderList')
        taxList = []
        
        if not orderList:
            return Response({'message':"Please provide appropiat orderList"},status=400)
        
        try:
            orderVal = get_object_or_404(Order,id=orderId)
        except:
            return Response({'message':"Please select appropiat Order Id"},status=400)
        
        listOrders = [i for i in orderList]
        order_data_list = Order_data.objects.filter(id__in=listOrders)
        
        addition = 0
        for lis in order_data_list:
            taxObj = {}
            if(lis.order_id == orderVal):
                taxObj['tax_rate'] = lis.product_id.product_gst_rate
                taxObj['taxable_amount'] = float(lis.product_id.product_price) * float(lis.qty)
                taxObj['tax_amount'] = float(lis.product_id.product_gst) * float(lis.qty)
                taxList.append(taxObj)
                addition = float(addition) + float(lis.tax_amount)
                lis.status = '1'
                lis.save()
    
        taxProcessed = process_tax_data(orderId,taxList)
        totalAmount = float(addition)
        sumOrmin = sign_indicator(totalAmount - int(totalAmount))
        
        orderVal.round_type = "Less: Rounded Off (+)"
        if sumOrmin:
            orderVal.round_type = "Less: Rounded Off (-)"
        
        orderVal.taxable_amount = float(taxProcessed['taxable_amount'])
        orderVal.cgst_amount = float(taxProcessed['cgst_amount'])
        orderVal.sgst_amount = float(taxProcessed['sgst_amount'])
        orderVal.total_tax_amount = float(taxProcessed['total_tax_amount'])
        
        orderVal.total_amount = totalAmount
        orderVal.round_off = totalAmount - int(totalAmount)
        orderVal.grand_total_amount = round(totalAmount)
        orderVal.status = '1'
        # generatePDF(orderVal.id)
        orderVal.save()
        userName = orderVal.customer_id
        
        manageNotifications('User',userName.expo_go_token, f"Order Confirmation for {userName.name}", f"Your order has been confirmed by the admin. Thank you for your purchase!")
        return Response({'message':"Order Updated"},status=200)
    except json.JSONDecodeError:
        return Response({'message': "Invalid JSON data in the request body."}, status=400)
    except Exception as e:
        logger.error(f"User Register Exception : {str(e)}")
        return Response({'message': str(e)}, status=500)

# Download file API
@api_view(['GET'])
@tokenVerified
def downloadPdf(request,orderId):
    try:
        try:
            orders = Order.objects.get(id=orderId)
        except:
            return Response({"message": "Order matching query does not exist."},status=400)
            
        ordersList = Order_data.objects.filter(order_id=orderId,status='1')
        taxes_order = order_taxes.objects.filter(order_id=orderId)
        
        totalAmountWithGST = float(orders.total_amount) + (calculate_sgst(float(orders.total_amount), 4) * 2)
        
        context = {
            'order': orders,
            'seller': User.objects.filter(role='1').first(),
            'totalAmountWords': getInwordsUsingNumber(orders.grand_total_amount),
            'orderList': ordersList,
            'taxes_order': taxes_order,
        }
        return render(request,'pdf_template.html', context)
    except Exception as e:
        logger.error(f"User Register Exception : {str(e)}")
        return Response({'message': str(e)}, status=500)