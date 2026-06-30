from django.shortcuts import render



# Create your views here.



def error_404(request, exception):

    return render(request, 'err.html')



def error_500(request, *args, **argv):

    return render(request,'500.html')