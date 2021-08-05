# Create your views here.
"""
def createuser(request):
    if request.method == "POST":
        form = CmnUsersForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('listusers')
            except:
                pass
    else:
        form = CmnUsersForm()
    return render(request,'common/model_form.html', {'form':form})


def listusers(request):
    users = CmnUsers.objects.all()
    return render(request,"common/listusers.html", {'list':users, 'request':request})


def edituser(request, id):
    print('ID:'+str(id))
    users = CmnUsers.objects.get(user_id=id)
    return render(request,'common/model_form.html', {'form':users})


def updateuser(request, id):
    users = CmnUsers.objects.get(user_id=id)
    form = CmnUsersForm(request.POST, instance = users)
    if form.is_valid():
        form.save()
        return redirect("common/listusers")
    return render(request, 'common/editUser.html', {'form': users})


def deleteuser(request, id):
    users = CmnUsers.objects.get(user_id=id)
    users.delete()
    return redirect("common/listusers")

"""