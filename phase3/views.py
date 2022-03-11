# from django.contrib.auth.models import User
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect

from phase3.forms import CargoForm, ContainerForm, TrackerForm, TrackerCargoForm, TrackerContainerForm, UserForm, \
    AdminUserForm, RoleForm, RepositionForm, Cargo_Staff_Form, MoveCargoForm
from phase3.models import Container, Cargo, Tracker

# Create your views here.

User = get_user_model()


def cargo_to_json(qs):
    result_list = []
    for i in qs:
        if i.Container is not None:
            dic = {'cargo_id': i.id, 'sender_name': i.sender_name, 'recip_name': i.recip_name,
                   'recip_address': i.recip_address, 'container_id': i.Container.cid,
                   'cargo_state': i.state, 'owner': i.owner.username, 'container_type': i.Container.type,
                   'owner_id': i.owner.id, 'location_x': i.Container.location_x, 'location_y': i.Container.location_y}
        else:
            dic = {'cargo_id': i.id, 'sender_name': i.sender_name, 'recip_name': i.recip_name,
                   'recip_address': i.recip_address, 'container_id': None,
                   'cargo_state': i.state, 'owner': i.owner.username, 'owner_id': i.owner.id}
        result_list.append(dic)
    return result_list


def container_to_json(qs):
    result_list = []
    for i in qs:
        dic = {'cid': i.cid, 'description': i.description, 'type': i.type, 'location_x': i.location_x,
               'location_y': i.location_y, 'state': i.state}
        result_list.append(dic)
    return result_list


def tracker_to_json(qs):
    result_list = []
    for i in qs:
        dic = {'role': i.tracker_owner.role, 'tid': i.tid, 'tracker_description': i.tracker_description, 'top': i.top,
               'left': i.left, 'bottom': i.bottom, 'right': i.right, 'tracker_owner': i.tracker_owner.username}
        result_list.append(dic)
    return result_list


# entity_type = cargo container tracker etc
def update_group(role, entity_type, content):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(role, {
        'type': entity_type + '.notify',
        'content': content
    })


def update_user_view(uid, entity_type, content):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(uid, {
        'type': entity_type + '.notify',
        'content': content
    })


def inform_clients_cargo():
    clients = User.objects.filter(role="client")
    for i in clients:
        update_user_view(str(i.id), "cargo", cargo_to_json(Cargo.objects.filter(owner=i)))


def inform_clients_tracker(entity_type, content):
    clients = User.objects.filter(role="client")
    for i in clients:
        update_user_view(str(i.id), "tracker", tracker_to_json(Tracker.objects.filter(owner=i)))


def notify_user(uid, content):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(str(uid), {
        'type': 'user.notify',
        'content': content
    })


# def update_cargo_trackers(item):
#     for i in item.tracker_set.all():
#         uid = i.owner
#         notify_user(uid, "Tracked cargo (id = " + item.id + ") has been updated.")
#         update_user_view(uid,cargo)


def update_except_client(entity_type, content):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)("staff", {
        'type': entity_type + '.notify',
        'content': content
    })
    async_to_sync(layer.group_send)("carrier", {
        'type': entity_type + '.notify',
        'content': content
    })
    async_to_sync(layer.group_send)("admin", {
        'type': entity_type + '.notify',
        'content': content
    })


def update_all(entity_type, content):  # useful for container
    layer = get_channel_layer()
    async_to_sync(layer.group_send)("client", {
        'type': entity_type + '.notify',
        'content': content
    })
    async_to_sync(layer.group_send)("staff", {
        'type': entity_type + '.notify',
        'content': content
    })
    async_to_sync(layer.group_send)("carrier", {
        'type': entity_type + '.notify',
        'content': content
    })
    async_to_sync(layer.group_send)("admin", {
        'type': entity_type + '.notify',
        'content': content
    })


def alarm_cargo(request):
    layer = get_channel_layer()
    qs = Cargo.objects.all()
    result_list = cargo_to_json(qs)
    notify_user(request.user.id, "Hacım sana alarmım var")
    return HttpResponse('<p>Done</p>')


def home_page(request):
    return render(request, 'base.html')


############################## ADD FUNCTIONS ##############################


def create_user_form(request):
    form = UserForm()
    operation = 'insert'
    return render(request, 'registration.html', {'form': form, 'operation': operation})


def register(request):
    u = request.POST
    if 'insert' in request.POST:
        user = User.objects.create_user(username=u['username'],
                                        password=u['password'],
                                        role="client")
        login(request, user)
        return redirect("/")  # TODO fix this
    else:
        return render(request, "loginfailed.html")


@login_required
def update_role_form(request, id):
    form = RoleForm()
    operation = 'insert'
    return render(request, 'update_user_role.html', {'uid': id, 'form': form, 'operation': operation})


@login_required
def update_role(request, id):
    u = request.POST
    if 'insert' in request.POST:
        user = User.objects.get(id=id)
        user.role = u['role']
        user.save()
        return redirect("/user_list")  # TODO fix this
    else:
        return render(request, "loginfailed.html")


@login_required
def create_user_by_admin(request):
    form = AdminUserForm()
    operation = 'insert'
    return render(request, 'add_user_by_admin.html', {'form': form, 'operation': operation})


@login_required
def register_by_admin(request):
    u = request.POST
    if 'insert' in request.POST:
        user = User.objects.create_user(username=u['username'],
                                        password=u['password'],
                                        role=u['role'])
        # login(request, user)
        return redirect("/user_list")  # TODO fix this
    else:
        return render(request, "loginfailed.html")


@login_required
def create_cargo(request):
    if request.user.role == "staff" or request.user.role == "admin":
        form = Cargo_Staff_Form()
        operation = 'insert'
    else:
        form = CargoForm()
        operation = 'insert'
    return render(request, 'add_cargo.html', {'form': form, 'operation': operation})


@login_required
def add_cargo(request):
    p = request.POST
    if 'id' not in p:
        if request.user.role != "client":
            cargo = Cargo.objects.create(sender_name=p['sender_name'],
                                         recip_name=p['recip_name'],
                                         recip_address=p['recip_address'],
                                         Container=Container.objects.get(cid=p['cont']),
                                         owner=User.objects.get(id=p['owner']),
                                         state=Container.objects.get(cid=p['cont']).state
                                         )
            notify_user(p['owner'], request.user.username + ", has added a cargo on your account.")  # notify client
            update_user_view(p['owner'], "cargo", cargo_to_json(Cargo.objects.filter(
                owner=User.objects.get(id=p['owner']))))  # update client
            update_except_client("cargo", cargo_to_json(Cargo.objects.all()))  # update all views except clients.
            update_all("contcargo", cargo_to_json(Cargo.objects.filter(
                Container=Container.objects.get(cid=p['cont']))))  # container_cargo tableri de güncelleniyor.
        else:
            cargo = Cargo.objects.create(sender_name=p['sender_name'],
                                         recip_name=p['recip_name'],
                                         recip_address=p['recip_address'],
                                         Container=Container.objects.get(cid=p['cont']),
                                         owner=request.user,
                                         state=Container.objects.get(cid=p['cont']).state
                                         )

            update_user_view(str(cargo.owner.id), "cargo", cargo_to_json(Cargo.objects.filter(owner=cargo.owner)))
            update_except_client("cargo", cargo_to_json(
                Cargo.objects.all()))  # TODO abi burada frontend guncellemesine mi birakacagiz
            update_all("contcargo", cargo_to_json(Cargo.objects.filter(
                Container=Container.objects.get(cid=p['cont']))))  # container_cargo tableri de güncelleniyor.
        item = {}
        item = {'container_type': cargo.Container.type, 'cargo_id': cargo.id, 'sender_name': cargo.sender_name,
                'recip_name': cargo.recip_name, 'recip_address': cargo.recip_address,
                'container_id': cargo.Container.cid, 'owner': cargo.owner.username, 'cargo_state': cargo.state}
        return JsonResponse({'data': [item]})
    else:
        if request.user.role != "client":
            cargo = Cargo.objects.filter(id=p['id']).update(sender_name=p['sender_name'],
                                                            recip_name=p['recip_name'],
                                                            recip_address=p['recip_address'],
                                                            Container=Container.objects.get(cid=p['cont']),
                                                            state=Container.objects.get(cid=p['cont']).state,
                                                            owner=p['owner']
                                                            )
            cargo = Cargo.objects.get(id=p['id'])
            print("owner: " + p['owner'])
            notify_user(p['owner'], request.user.username + ", has updated a cargo on your account.")  # notify client
            update_user_view(p['owner'], "cargo", cargo_to_json(Cargo.objects.filter(
                owner=User.objects.get(id=p['owner']))))  # update client
            update_except_client("cargo", cargo_to_json(Cargo.objects.all()))  # update all views except clients.
            update_all("contcargo", cargo_to_json(Cargo.objects.filter(
                Container=Container.objects.get(cid=p['cont']))))  # container_cargo tableri de güncelleniyor.
            trackers = cargo.tracker_set.all()
            for tracker in trackers:
                notify_user(str(tracker.tracker_owner.id), "Your tracked cargo with id: {} has been updated.".format(cargo.id))


        else:
            cargo = Cargo.objects.filter(id=p['id']).update(sender_name=p['sender_name'],
                                                            recip_name=p['recip_name'],
                                                            recip_address=p['recip_address'],
                                                            Container=Container.objects.get(cid=p['cont']),
                                                            state=Container.objects.get(cid=p['cont']).state,
                                                            owner=p['owner']
                                                            )
            cargo = Cargo.objects.get(id=p['id'])
            update_user_view(str(cargo.owner.id), "cargo", cargo_to_json(Cargo.objects.filter(owner=cargo.owner)))
            update_except_client("cargo", cargo_to_json(
                Cargo.objects.all()))
            for t in Tracker.objects.all():
                update_except_client("trackcargo", cargo_to_json(t.Cargo.all()))
            for t in Tracker.objects.filter(tracker_owner=cargo.owner):
                update_user_view(str(cargo.owner.id), "trackcargo", cargo_to_json(t.Cargo.all()))
            update_all("contcargo", cargo_to_json(Cargo.objects.filter(
                Container=Container.objects.get(cid=p['cont']))))  # container_cargo tableri de güncelleniyor.
            trackers = cargo.tracker_set.all()
            trackers = cargo.tracker_set.all()
            for tracker in trackers:
                notify_user(str(tracker.tracker_owner.id), "Your tracked cargo with id: {} has been updated.".format(cargo.id))
        data = []
        # item = {'container_type': cargo.Container.type, 'cargo_id': cargo.id, 'sender_name': cargo.sender_name,
        #         'recip_name': cargo.recip_name, 'recip_address': cargo.recip_address,
        #         'container_id': cargo.Container.cid, 'owner': cargo.owner.username, 'cargo_state': cargo.state}
        # return JsonResponse({'data': [item]})
        return JsonResponse({'data': data})


@login_required
def create_container(request, cid=None):
    if request.user.role == "admin":
        try:
            container = Container.objects.get(cid=cid)
            form = ContainerForm({'description': container.description,
                                  'type': container.type,
                                  'location_x': container.location_x,
                                  'location_y': container.location_y})
            operation = 'update'
        except:
            form = ContainerForm()
            operation = 'insert'

        return render(request, 'add_container.html', {'cid': cid, 'form': form, 'operation': operation})
    else:
        return render(request, "loginfailed.html")


@login_required
def add_container(request):
    p = request.POST
    if 'cid' not in request.POST:
        if p['type'] == "Front-Office":
            stateX = "Waiting"
        else:
            stateX = "In-Transit"
        container = Container.objects.create(description=p['description'],
                                             type=p['type'],
                                             location_x=p['location_x'],
                                             location_y=p['location_y'],
                                             state=stateX,
                                             )
        update_all("container", container_to_json(Container.objects.all()))
        data = []
        # data.append({'description': container.description, 'type': container.type, 'location_x': container.location_x,
        #              'location_y': container.location_y, 'state': container.state, 'cid': container.cid})
        return JsonResponse({'data': data})
    else:
        if p['type'] == "Front-Office":
            stateX = "Waiting"
        else:
            stateX = "In-Transit"
        container = Container.objects.filter(cid=p['cid']).update(
            description=p['description'],
            type=p['type'],
            location_x=p['location_x'],
            location_y=p['location_y'],
            state=stateX, )
        container = Container.objects.get(cid=p['cid'])
        data = []
        update_all("container", container_to_json(Container.objects.all()))
        cargos = container.cargo_set.all()
        for t in Tracker.objects.all():
            update_except_client("trackcontainer", container_to_json(t.Container.all()))

        for tracker in container.tracker_set.all():
            notify_user(str(tracker.tracker_owner.id),
                        "Tracked Container {} with id: {} is now at {}-{}".format(container.description,container.cid, container.location_x,
                                                                                 container.location_y))
        for cargo in cargos:
            trackers = cargo.tracker_set.all()
            for tracker in trackers:
                notify_user(str(tracker.tracker_owner.id), "Tracked Cargo with id: {} is now at {}-{} in {}".format(cargo.id,container.location_x, container.location_y, container.description))

        # TODO abi buraya notif gerekebilir, container pozisyonu cargo pozisyonunun degismesine sebepse
        # TODO ona basit bir check yapilabilir pozisyon degisti mi diye.

        # data.append({'description': container.description, 'type': container.type, 'location_x': container.location_x,
        #              'location_y': container.location_y, 'state': container.state, 'cid': container.cid})
        return JsonResponse({'data': data})


@login_required
def create_tracker(request, tid=None):
    try:
        tracker = Tracker.objects.get(tid=tid)
        form = TrackerForm({'tracker_description': tracker.tracker_description,
                            'top': tracker.top,
                            'left': tracker.left,
                            'right': tracker.right,
                            'bottom': tracker.bottom,
                            'tracker_owner': tracker.tracker_owner})
        operation = 'update'
    except:
        form = TrackerForm()
        operation = 'insert'

    return render(request, 'add_tracker.html', {'form': form, 'operation': operation, 'tid': tid})


@login_required
def add_tracker(request):
    p = request.POST
    # if 'insert' in request.POST:
    if 'tid' not in request.POST:
        tracker = Tracker.objects.create(tracker_description=p['tracker_description'],
                                         top=p['top'],
                                         left=p['left'],
                                         right=p['right'],
                                         bottom=p['bottom'],
                                         tracker_owner=request.user,
                                         )
        update_except_client("tracker", tracker_to_json(Tracker.objects.all()))
        if request.user.role == "client":
            update_user_view(str(request.user.id), "tracker",
                             tracker_to_json(Tracker.objects.filter(tracker_owner=request.user)))
        item = {}
        # item = {'role': tracker.owner.role, 'tid': tracker.tid, 'tracker_description': tracker.tracker_description, 'top': tracker.top,
        #         'left': tracker.left, 'bottom': tracker.bottom, 'right': tracker.right, 'owner': tracker.owner.username}
        return JsonResponse({'data': item})
    else:
        tracker = Tracker.objects.filter(tid=p['tid']).update(
            tracker_description=p['tracker_description'],
            top=p['top'],
            left=p['left'],
            right=p['right'],
            bottom=p['bottom'])
        tracker = Tracker.objects.get(tid=p['tid'])
        update_except_client("tracker", tracker_to_json(Tracker.objects.all()))
        if tracker.tracker_owner.role == "client":
            update_user_view(str(tracker.tracker_owner.id), "tracker",
                             tracker_to_json(Tracker.objects.filter(tracker_owner=tracker.tracker_owner)))
        item = {}
        return JsonResponse({'data': item})


############################## LIST FUNCTIONS ##############################

@login_required
def user_list(request, message=''):
    users = User.objects.all()
    return render(request, 'User.html', {'message': message, 'users': users})


def cargo_list(request, message=''):
    if request.user.is_authenticated:
        if request.user.role == "client":
            cargos = Cargo.objects.filter(owner=request.user)
        else:
            cargos = Cargo.objects.all()
        # return HttpResponse("Hello, this is a shop")
        return render(request, 'Cargo.html', {'message': message, 'cargos': cargos})
    else:
        cargos = None
        return render(request, 'Cargo.html', {'message': message, 'cargos': cargos})


@login_required
def tracker_list(request, message=''):
    if request.user.role == "client" or request.user.role == "carrier":
        trackers = Tracker.objects.filter(tracker_owner=request.user)
    elif request.user.role == "staff":
        trackersV2 = Tracker.objects.all()
        trackers = []
        for tracker in trackersV2:
            if tracker.tracker_owner.role != "admin" and tracker.tracker_owner.role != "carrier":
                trackers.append(tracker)
    else:
        trackers = Tracker.objects.all()
    # return HttpResponse("Hello, this is a shop")
    return render(request, 'Tracker.html', {'message': message, 'trackers': trackers})


@login_required
def container_list(request, message=''):
    if request.user.role == "admin" or request.user.role == "carrier":
        containers = Container.objects.all()
        # return HttpResponse("Hello, this is a shop")
        return render(request, 'Container.html', {'message': message, 'containers': containers})
    else:
        return render(request, "loginfailed.html")


@login_required
def delete_cargo(request, id):
    cargo = Cargo.objects.get(id=id)
    if request.user.role == "client" and cargo.owner == request.user:
        cont = cargo.Container
        trac = cargo.tracker_set.all()
        for t in trac:
            notify_user(str(t.tracker_owner.id), "Tracked Cargo with id: {} is deleted.".format(cargo.id))
        cargo.delete()

        update_except_client("cargo", cargo_to_json(Cargo.objects.all()))
        update_user_view(str(request.user.id), "cargo",
                         cargo_to_json(Cargo.objects.filter(owner=User.objects.get(id=request.user.id))))
        update_all("contcargo", cargo_to_json(Cargo.objects.filter(
            Container=Container.objects.get(cid=cont.cid))))

        # TODO aynısını tracker için yap yani trackerları ayıktır cargo gitti diye
    elif request.user.role == "client" and cargo.owner != request.user:
        return HttpResponse("You can't delete a cargo you do not own")  ##TODO BURAYA TOASTIFY
    else:
        oid = cargo.owner.id
        cont = cargo.Container
        trac = cargo.tracker_set.all()
        for t in trac:
            notify_user(str(t.tracker_owner.id), "Tracked Cargo with id: {} is deleted.".format(cargo.id))
        cargo.delete()

        update_user_view(str(oid), "cargo",
                         cargo_to_json(Cargo.objects.filter(owner=User.objects.get(id=oid))))
        update_except_client("cargo", cargo_to_json(Cargo.objects.all()))
        notify_user(cargo.owner.id, "Your cargo has been deleted.")

        update_all("contcargo", cargo_to_json(Cargo.objects.filter(
            Container=Container.objects.get(cid=cont.cid))))

        # TODO aynısını tracker için yap

    data = []
    # all = Cargo.objects.all()
    # for cargo in all:
    #     if cargo.Container != None:
    #         item = {'container_type': cargo.Container.type, 'cargo_id': cargo.id, 'sender_name': cargo.sender_name,
    #                 'recip_name': cargo.recip_name, 'recip_address': cargo.recip_address,
    #                 'container_id': cargo.Container.cid, 'owner': cargo.owner.username, 'cargo_state': cargo.state}
    #     else:
    #         item = {'container_type': "", 'cargo_id': cargo.id,
    #                 'sender_name': cargo.sender_name, 'recip_name': cargo.recip_name,
    #                 'recip_address': cargo.recip_address,
    #                 'container_id': "", 'owner': cargo.owner.username, 'cargo_state': cargo.state}
    #
    #     data.append(item)
    return JsonResponse({'data': data})


@login_required
def delete_container(request, cid):
    if request.user.role == "admin":
        container = Container.objects.get(cid=cid)
        cargos = container.cargo_set.all()
        affected = []
        for i in cargos:
            affected.append(i.owner.id)
        affected = set(affected)
        container.delete()

        update_all("container", container_to_json(Container.objects.all()))  # container tabloları guncellendi
        update_except_client("cargo",
                             cargo_to_json(Cargo.objects.all()))  # Kargolar da silindi cargo tablo güncellensin
        inform_clients_cargo()
        # TODO silinen container tab'ı gözüküyor
        for i in affected:
            notify_user(str(i), "Your cargo has been deleted due to Container Deletion")
        # TODO silinen kargolari bir de trackerlardan dusurmek gerek
        data = []
        # containers = Container.objects.all()
        # data = []
        # for container in containers:
        #     item = {
        #         'cid': container.cid,
        #         'description': container.description,
        #         'type': container.type,
        #         'location_x': container.location_x,
        #         'location_y': container.location_y,
        #         'state': container.state,
        #         'role': request.user.role
        #     }
        #     data.append(item)
        return JsonResponse({'data': data})
    else:
        return render(request, "loginfailed.html")


@login_required
def delete_user(request, id):
    u = User.objects.get(id=id)
    u.delete()
    return redirect("/user_list")


@login_required
def create_user(request):
    u = request.POST
    user = User.objects.create_user(username=u['username'], password=u['password'])
    return redirect("/login")  # TODO fix this


@login_required
def view_tracker(request, tid, message=''):
    tracker = Tracker.objects.get(tid=tid)
    tracker_cargo_list = list(tracker.Cargo.all())
    tracker_container_list = list(tracker.Container.all())
    tracker_container_listV2 = []
    tracker_cargo_listV2 = []
    for cargo in tracker_cargo_list:
        if ((tracker.right >= cargo.Container.location_x) and (cargo.Container.location_x >= tracker.left) and
                (tracker.top >= cargo.Container.location_y) and (cargo.Container.location_y >= tracker.bottom)):
            if request.user.role == "client":
                if cargo.owner == request.user:
                    tracker_cargo_listV2.append(cargo)
            else:
                tracker_cargo_listV2.append(cargo)
    for container in tracker_container_list:
        if ((tracker.right >= container.location_x) and (container.location_x >= tracker.left) and
                (tracker.top >= container.location_y) and (container.location_y >= tracker.bottom)):
            tracker_container_listV2.append(container)

    return render(request, 'View_Tracker.html',
                  {'message': message, 'containers': tracker_container_listV2, 'cargos': tracker_cargo_listV2,
                   'tid': tid, 'x_min': tracker.left, 'y_min': tracker.bottom, 'x_max': tracker.right,
                   'y_max': tracker.top, 'role': tracker.tracker_owner.role})


@login_required
def view_container(request, cid, message=''):
    container = Container.objects.get(cid=cid)
    container_cargo_list = list(container.cargo_set.exclude(state="Delivered"))
    # for cargo in tracker_cargo_list:
    #     if tracker.right >= cargo.Container.location_x >= tracker.
    return render(request, 'View_Container.html',
                  {'message': message, 'cargos': container_cargo_list, 'cid': cid})


@login_required
def delete_tracker_cargo(request, tid, id):
    tracker = Tracker.objects.get(tid=tid)
    cargo = tracker.Cargo.get(id=id)
    tracker.Cargo.remove(cargo)
    data = []
    cargos = tracker.Cargo.all()
    for t in Tracker.objects.all():
        update_except_client("trackcargo", cargo_to_json(t.Cargo.all()))
    for t in Tracker.objects.filter(tracker_owner=cargo.owner):
        update_user_view(str(cargo.owner.id),"trackcargo", cargo_to_json(t.Cargo.all()))
    for cargo in cargos:
        if cargo.Container != None:
            item = {'tid': tid, 'container_type': cargo.Container.type, 'cargo_id': cargo.id,
                    'sender_name': cargo.sender_name,
                    'recip_name': cargo.recip_name, 'recip_address': cargo.recip_address,
                    'container_id': cargo.Container.cid, 'owner': cargo.owner.username, 'cargo_state': cargo.state,
                    'location_x': cargo.Container.location_x, 'location_y': cargo.Container.location_y}
        else:
            item = {'tid': tid, 'container_type': "", 'cargo_id': cargo.id,
                    'sender_name': cargo.sender_name, 'recip_name': cargo.recip_name,
                    'recip_address': cargo.recip_address,
                    'container_id': "", 'owner': cargo.owner.username, 'cargo_state': cargo.state}
        data.append(item)
    return JsonResponse({'data': data})


@login_required
def delete_tracker_container(request, tid, cid):
    tracker = Tracker.objects.get(tid=tid)
    container = tracker.Container.get(cid=cid)
    tracker.Container.remove(container)
    data = []
    tracker_container_list = list(tracker.Container.all())
    for container in tracker_container_list:
        item = {'tid': tid, 'cid': container.cid, 'description': container.description, 'type': container.type,
                'location_x': container.location_x, 'location_y': container.location_y, 'state': container.state}
        data.append(item)
    return JsonResponse({'data': data})


@login_required
def add_tracker_cargo(request, tid):
    if request.user.role == "admin" or request.user.role == "staff":
        form = TrackerCargoForm()
        operation = 'insert'
        tracker = Tracker.objects.get(tid=tid)
        form = form.set(tracker.tracker_owner)
        form = form.set2(request.user)
        return render(request, 'add_tracker_cargo.html', {'form': form, 'operation': operation, 'tid': tid})
    elif request.user.role == "client":
        form = TrackerCargoForm()
        operation = 'insert'
        form = form.set(request.user)
        form = form.set2(request.user)
        return render(request, 'add_tracker_cargo.html', {'form': form, 'operation': operation, 'tid': tid})
    else:
        return HttpResponse(
            "You don't have the rights to view this page. Please contact system administrator for further details.")


@login_required
def create_tracker_cargo(request, tid):
    p = request.POST
    cargo = Cargo.objects.get(id=p['cargoID'])
    tracker = Tracker.objects.get(tid=tid).Cargo.add(cargo)
    tracker = Tracker.objects.get(tid=tid)
    data = []
    if cargo.Container != None:
        if ((tracker.right >= cargo.Container.location_x) and (cargo.Container.location_x >= tracker.left) and
                (tracker.top >= cargo.Container.location_y) and (cargo.Container.location_y >= tracker.bottom)):
            item = {'tid': tid, 'container_type': cargo.Container.type, 'cargo_id': cargo.id,
                    'sender_name': cargo.sender_name,
                    'recip_name': cargo.recip_name, 'recip_address': cargo.recip_address,
                    'container_id': cargo.Container.cid, 'owner': cargo.owner.username, 'cargo_state': cargo.state,
                    'location_x': cargo.Container.location_x, 'location_y': cargo.Container.location_y}
            data.append(item)
    else:
        item = {'tid': tid, 'container_type': "", 'cargo_id': cargo.id,
                'sender_name': cargo.sender_name, 'recip_name': cargo.recip_name,
                'recip_address': cargo.recip_address,
                'container_id': "", 'owner': cargo.owner.username, 'cargo_state': cargo.state}
        data.append(item)
    update_all("trackcargo", cargo_to_json(Tracker.objects.get(tid=tid).Cargo.all()))
    return JsonResponse({'data': data})


@login_required
def add_tracker_container(request, tid):
    if request.user.role == "admin" or request.user.role == "carrier":
        form = TrackerContainerForm()
        operation = 'insert'
        return render(request, 'add_tracker_container.html', {'form': form, 'operation': operation, 'tid': tid})
    else:
        return HttpResponse(
            "You don't have the rights to view this page. Please contact system administrator for further details.")


@login_required
def create_tracker_container(request, tid):
    p = request.POST
    data = []
    container = Container.objects.get(cid=p['cid'])
    tracker = Tracker.objects.get(tid=tid).Container.add(container)
    item = {'tid': tid, 'cid': container.cid, 'description': container.description, 'type': container.type,
            'location_x': container.location_x, 'location_y': container.location_y, 'state': container.state}
    data.append(item)
    update_all("trackcontainer", container_to_json(Tracker.objects.get(tid=tid).Container.all()))
    return JsonResponse({'data': data})


@login_required
def delete_tracker(request, tid):
    tracker = Tracker.objects.get(tid=tid)

    if request.user.role == "client" and tracker.tracker_owner == request.user:
        tracker.delete()
        data = []
        all = Tracker.objects.all()

        if request.user.role == "client":
            all = Tracker.objects.filter(tracker_owner=request.user)
        for tracker in all:
            item = {'tracker_description': tracker.tracker_description, 'tid': tracker.tid, 'top': tracker.top,
                    'left': tracker.left,
                    'bottom': tracker.bottom, 'right': tracker.right, 'tracker_owner': tracker.tracker_owner.username,
                    'role': tracker.tracker_owner.role}

            data.append(item)
        return JsonResponse({'data': data})
    elif request.user.role == "client" and tracker.tracker_owner != request.user:
        return HttpResponse("You can't delete a tracker you do not own")
    elif request.user.role == "carrier" and tracker.tracker_owner.role == request.user.role:
        tracker.delete()
        data = []
        all = Tracker.objects.all()
        for tracker in all:
            item = {'tracker_description': tracker.tracker_description, 'tid': tracker.tid, 'top': tracker.top,
                    'left': tracker.left,
                    'bottom': tracker.bottom, 'right': tracker.right, 'tracker_owner': tracker.tracker_owner.username,
                    'role': tracker.tracker_owner.role}

            data.append(item)
        return JsonResponse({'data': data})
    elif request.user.role == "carrier" and tracker.tracker_owner.role != request.user.role:
        return HttpResponse("You can't delete a " + str(tracker.tracker_owner.role) + "'s tracker")
    else:
        tracker.delete()
        data = []
        all = Tracker.objects.all()
        for tracker in all:
            item = {'tracker_description': tracker.tracker_description, 'tid': tracker.tid, 'top': tracker.top,
                    'left': tracker.left,
                    'bottom': tracker.bottom, 'right': tracker.right, 'tracker_owner': tracker.tracker_owner.username,
                    'role': tracker.tracker_owner.role}

            data.append(item)
        return JsonResponse({'data': data})


@login_required
def reposition_form(request, cid):
    container = Container.objects.get(cid=cid)
    form = RepositionForm({'location_x': container.location_x, 'location_y': container.location_y})
    operation = 'insert'
    return render(request, 'reposition.html', {'cid': cid, 'form': form, 'operation': operation})


@login_required
def reposition(request):
    u = request.POST
    if 'insert' in request.POST:
        container = Container.objects.filter(cid=u['cid']).update(location_x=u['location_x'],
                                                                  location_y=u['location_y'])
        return redirect("/container_list")
    else:
        return render(request, "loginfailed.html")


@login_required
def unload_cargo(request, id):
    cargo = Cargo.objects.get(id=id)
    cargo_owner = cargo.owner
    cargo.state = "Delivered"
    cargo_cont_cid = cargo.Container.cid
    cargo.Container = None
    cargo.save()
    trackerSet = cargo.tracker_set.all()
    is_tracker_deleted = False
    for tracker in trackerSet:
        notify_user(str(tracker.tracker_owner.id), "Cargo with id: {} is unloaded.".format(cargo.id))
        tracker.Cargo.remove(cargo)
        if not tracker.Cargo.all():
            is_tracker_deleted = True
            notify_user(str(tracker.tracker_owner.id), "Your tracker has been deleted due to lack of tracked cargos.")
            tracker.delete()
    data = []
    if request.user != cargo.owner:
        notify_user(str(cargo.owner.id), "Your cargo has been unloaded.")

    all = Cargo.objects.all()
    update_except_client("cargo", cargo_to_json(all))
    if is_tracker_deleted:
        update_user_view(str(cargo_owner.id), "tracker",tracker_to_json(Tracker.objects.filter(tracker_owner=cargo_owner)))
        update_except_client("tracker", tracker_to_json(Tracker.objects.all()))
    for t in Tracker.objects.all():
        update_except_client("trackcargo", cargo_to_json(t.Cargo.all()))

    update_user_view(str(cargo_owner.id),"cargo", cargo_to_json(Cargo.objects.filter(owner=cargo_owner)))
    for t in Tracker.objects.filter(tracker_owner=cargo_owner):
        update_user_view(str(cargo_owner.id),"trackcargo", cargo_to_json(t.Cargo.all()))

    update_all("contcargo", cargo_to_json(Cargo.objects.filter(
        Container=Container.objects.get(cid=cargo_cont_cid))))
    for cargo in all:
        if cargo.Container != None:
            item = {'container_type': cargo.Container.type, 'cargo_id': cargo.id, 'sender_name': cargo.sender_name,
                    'recip_name': cargo.recip_name, 'recip_address': cargo.recip_address,
                    'container_id': cargo.Container.cid, 'owner': cargo.owner.username, 'cargo_state': cargo.state}
        else:
            item = {'container_type': "", 'cargo_id': cargo.id,
                    'sender_name': cargo.sender_name, 'recip_name': cargo.recip_name,
                    'recip_address': cargo.recip_address,
                    'container_id': "", 'owner': cargo.owner.username, 'cargo_state': cargo.state}

        data.append(item)
    return JsonResponse({'data': data})


@login_required
def move_cargo(request, id):
    cargo = Cargo.objects.get(id=id)
    containerold = cargo.Container
    containerold.cargo_set.remove(cargo)
    p = request.POST
    containernew = Container.objects.get(cid=p['cid'])
    cargo.Container = containernew
    containernew.cargo_set.add(cargo)
    cargo.state = cargo.Container.state
    cargo.save()
    containernew.save()
    containerold.save()
    return redirect("/view_cargo/" + str(containerold.cid))


@login_required
def add_move_cargo(request, cid, id):
    form = MoveCargoForm()
    form.set(cid)
    operation = 'insert'
    return render(request, 'move_cargo.html', {'form': form, 'operation': operation, 'id': id})


@login_required
def dashboardFunction(request):
    if request.user.is_authenticated:
        if request.user.role == "client":
            cargo_form = CargoForm()
            cargo_form.set(request.user.id)
            tracker_form = TrackerForm()
            tracker_cargo_form = TrackerCargoForm()
            tracker_cargo_form.set(request.user)
            tracker_cargo_form.set2(request.user)
            tracker_container_form = TrackerContainerForm()
            container_form = ContainerForm()
            move_cargo_form = MoveCargoForm()
        else:
            cargo_form = Cargo_Staff_Form()
            container_form = ContainerForm()
            tracker_form = TrackerForm()
            tracker_cargo_form = TrackerCargoForm()
            tracker_cargo_form.set2(request.user)
            tracker_container_form = TrackerContainerForm()
            move_cargo_form = MoveCargoForm()
        return render(request, 'dashboard.html',
                      {'cargo_form': cargo_form, 'tracker_form': tracker_form, 'tracker_cargo_form': tracker_cargo_form,
                       'tracker_container_form': tracker_container_form, 'container_form': container_form,
                       'move_cargo_form': move_cargo_form})
    else:
        cargos = None
        return render(request, 'dashboard.html', {'cargos': cargos})


@login_required
def new_deneme(request):
    data = []
    all = Cargo.objects.all()
    if request.user.role == "client":
        all = all.filter(owner=request.user)
    for cargo in all:
        if cargo.Container != None:
            item = {'container_type': cargo.Container.type, 'cargo_id': cargo.id, 'sender_name': cargo.sender_name,
                    'recip_name': cargo.recip_name, 'recip_address': cargo.recip_address,
                    'container_id': cargo.Container.cid, 'owner': cargo.owner.username, 'cargo_state': cargo.state,
                    'role': request.user.role, 'owner_id': cargo.owner.id}
        else:
            item = {'container_type': "", 'cargo_id': cargo.id,
                    'sender_name': cargo.sender_name, 'recip_name': cargo.recip_name,
                    'recip_address': cargo.recip_address,
                    'container_id': "", 'owner': cargo.owner.username, 'cargo_state': cargo.state,
                    'role': request.user.role, 'owner_id': cargo.owner.id}

        data.append(item)
    return JsonResponse({'data': data})


@login_required
def get_trackers(request):
    data = []
    all = Tracker.objects.all()

    if request.user.role == "client":
        all = Tracker.objects.filter(tracker_owner=request.user)
    for tracker in all:
        item = {'tracker_description': tracker.tracker_description, 'tid': tracker.tid, 'top': tracker.top,
                'left': tracker.left,
                'bottom': tracker.bottom, 'right': tracker.right, 'tracker_owner': tracker.tracker_owner.username,
                'role': tracker.tracker_owner.role}

        data.append(item)
    return JsonResponse({'data': data})


@login_required
def get_tracker_cargos(request, tid):
    data = []
    tracker = Tracker.objects.get(tid=tid)
    tracker_cargo_list = list(tracker.Cargo.all())
    for cargo in tracker_cargo_list:
        if cargo.Container != None:
            if ((tracker.right >= cargo.Container.location_x) and (cargo.Container.location_x >= tracker.left) and
                    (tracker.top >= cargo.Container.location_y) and (cargo.Container.location_y >= tracker.bottom)):
                item = {'container_type': cargo.Container.type, 'cargo_id': cargo.id, 'sender_name': cargo.sender_name,
                        'recip_name': cargo.recip_name, 'recip_address': cargo.recip_address,
                        'container_id': cargo.Container.cid, 'owner': cargo.owner.username, 'cargo_state': cargo.state,
                        'location_x': cargo.Container.location_x, 'location_y': cargo.Container.location_y, 'tid': tid}
                data.append(item)
        else:
            item = {'container_type': "", 'cargo_id': cargo.id,
                    'sender_name': cargo.sender_name, 'recip_name': cargo.recip_name,
                    'recip_address': cargo.recip_address,
                    'container_id': "", 'owner': cargo.owner.username, 'cargo_state': cargo.state, 'tid': tid}
            data.append(item)
    return JsonResponse({'data': data})


@login_required
def get_tracker_containers(request, tid):
    data = []
    tracker = Tracker.objects.get(tid=tid)
    tracker_container_list = list(tracker.Container.all())
    for container in tracker_container_list:
        if ((tracker.right >= container.location_x) and (container.location_x >= tracker.left) and
                (tracker.top >= container.location_y) and (container.location_y >= tracker.bottom)):
            item = {'tid': tid, 'cid': container.cid, 'description': container.description, 'type': container.type,
                    'location_x': container.location_x, 'location_y': container.location_y, 'state': container.state}
            data.append(item)
    return JsonResponse({'data': data})


@login_required
def get_updated_cargo_form(request):
    if request.user.role == "client":
        cargos = Cargo.objects.filter(owner=request.user).exclude(state="Delivered")
    else:
        cargos = Cargo.objects.exclude(state="Delivered")
    return render(request, 'add_tracker_cargo_form.html', {'cargos': cargos})


@login_required
def get_updated_container_form(request):
    containers = Container.objects.all()
    return render(request, 'add_tracker_container_form.html', {'containers': containers})


@login_required
def get_containers(request):
    containers = Container.objects.all()
    data = []
    for container in containers:
        item = {
            'cid': container.cid,
            'description': container.description,
            'type': container.type,
            'location_x': container.location_x,
            'location_y': container.location_y,
            'state': container.state,
            'role': request.user.role
        }
        data.append(item)
    return JsonResponse({'data': data})


@login_required()
def contained_cargos(request, cid):
    cargos = Cargo.objects.filter(Container=Container.objects.get(cid=cid))
    data = []
    for cargo in cargos:
        if cargo.Container != None:
            item = {'container_type': cargo.Container.type, 'cargo_id': cargo.id, 'sender_name': cargo.sender_name,
                    'recip_name': cargo.recip_name, 'recip_address': cargo.recip_address,
                    'container_id': cargo.Container.cid, 'owner': cargo.owner.username, 'cargo_state': cargo.state,
                    'location_x': cargo.Container.location_x, 'location_y': cargo.Container.location_y, 'cid': cid}
        else:
            item = {'container_type': "", 'cargo_id': cargo.id,
                    'sender_name': cargo.sender_name, 'recip_name': cargo.recip_name,
                    'recip_address': cargo.recip_address,
                    'container_id': "", 'owner': cargo.owner.username, 'cargo_state': cargo.state, 'cid': cid}
        data.append(item)
    return JsonResponse({'data': data})


@login_required()
def move_cargo_new(request, id):
    cargo = Cargo.objects.get(id=id)
    container = Container.objects.get(cid=request.POST['move_cid'])
    containerold = cargo.Container
    containerold.cargo_set.remove(cargo)
    cargo.Container = container
    container.cargo_set.add(cargo)
    cargo.state = container.state
    update_all("contcargo", cargo_to_json(Cargo.objects.filter(
        Container=Container.objects.get(cid=request.POST['move_cid']))))
    for tracker in cargo.tracker_set.all():
        notify_user(str(tracker.tracker_owner.id), "Cargo with id: {} is moved from {} to {}".format(cargo.id, containerold.description,cargo.Container.description))
    for tracker in containerold.tracker_set.all():
        notify_user(str(tracker.tracker_owner.id), "Cargo with id: {} is moved from {} to {}".format(cargo.id, containerold.description,cargo.Container.description))
    for tracker in container.tracker_set.all():
        notify_user(str(tracker.tracker_owner.id), "Cargo with id: {} is moved from {} to {}".format(cargo.id, containerold.description,cargo.Container.description))

    return JsonResponse({'data': []})
