from django import forms
from phase3.models import Container, Cargo, MyUser


class CargoForm(forms.Form):
    sender_name = forms.CharField(label='Sender Name', max_length=100, required=True)
    recip_name = forms.CharField(label="Recipent Name", max_length=100, required=True)
    recip_address = forms.CharField(label="Recipent Address", max_length=1024, widget=forms.Textarea, required=False)
    # cont = forms.ChoiceField(label="Front-Office", choices=Container.objects.all())
    cont = forms.ModelChoiceField(label="Front-Office", queryset=Container.objects.filter(type="Front-Office"),
                                  empty_label="Select a Front-Office")
    owner = forms.ModelChoiceField(label="Owner", queryset=MyUser.objects.filter(role="client"),
                                   empty_label="Select a Client")
    def set(self, userid):
        self.fields['owner'].queryset = self.fields['owner'].queryset.filter(id=userid)
        return self

class Cargo_Staff_Form(forms.Form):
    sender_name = forms.CharField(label='Sender Name', max_length=100, required=True)
    recip_name = forms.CharField(label="Recipent Name", max_length=100, required=True)
    recip_address = forms.CharField(label="Recipent Address", max_length=1024, widget=forms.Textarea, required=False)
    cont = forms.ModelChoiceField(label="Front-Office", queryset=Container.objects.filter(type="Front-Office"),
                                  empty_label="Select a Front-Office")
    owner = forms.ModelChoiceField(label="Owner", queryset=MyUser.objects.filter(role="client"),
                                   empty_label="Select a Client")


class ContainerForm(forms.Form):
    description = forms.CharField(label="Description", max_length=100)
    type = forms.ChoiceField(label="Container Type",
                             choices=(("Front-Office", "Front-Office"), ("Cargo-Van", "Cargo-Van")))
    location_x = forms.IntegerField(label="X Coordinate")
    location_y = forms.IntegerField(label="Y Coordinate")


class TrackerForm(forms.Form):
    tracker_description = forms.CharField(label="Description", max_length=100)
    top = forms.IntegerField(label="Top")
    left = forms.IntegerField(label="Left")
    bottom = forms.IntegerField(label="Bottom")
    right = forms.IntegerField(label="Top")


class TrackerStaffForm(forms.Form):
    tracker_description = forms.CharField(label="Description", max_length=100)
    top = forms.IntegerField(label="Top")
    left = forms.IntegerField(label="Left")
    bottom = forms.IntegerField(label="Bottom")
    right = forms.IntegerField(label="Top")
    tracker_owner = forms.ModelChoiceField(label="Owner", queryset=MyUser.objects.filter(role="client"),
                                   empty_label="Select a Client")


class TrackerCargoForm(forms.Form):
    cargoID = forms.ModelChoiceField(label="Cargos", queryset=Cargo.objects.all(),
                                     empty_label="Select a Cargo")

    def set(self, userid):
        self.fields['cargoID'].queryset = self.fields['cargoID'].queryset.filter(owner=userid)
        return self

    def set2(self, userid):
        self.fields['cargoID'].queryset = self.fields['cargoID'].queryset.exclude(state="Delivered")
        return self


class TrackerContainerForm(forms.Form):
    cid = forms.ModelChoiceField(label="Containers", queryset=Container.objects.all(),
                                 empty_label="Select a Container")


class MoveCargoForm(forms.Form):
    move_cid = forms.ModelChoiceField(label="Containers", queryset=Container.objects.all(),
                                 empty_label="Select a Container")

    def set(self, userid):
        self.fields['move_cid'].queryset = self.fields['move_cid'].queryset.exclude(cid=userid)
        return self


class UserForm(forms.Form):
    username = forms.CharField(label="Username", max_length=20)
    password = forms.CharField(label="Password", max_length=20)


class RoleForm(forms.Form):
    role = forms.ChoiceField(label="Role", choices=(("admin", "Admin"),
                                                    ("client", "Client"),
                                                    ("staff", "Staff"),
                                                    ("carrier", "Carrier")))


class AdminUserForm(forms.Form):
    username = forms.CharField(label="Username", max_length=20)
    password = forms.CharField(label="Password", max_length=20)
    role = forms.ChoiceField(label="Role", choices=(("admin", "Admin"),
                                                    ("client", "Client"),
                                                    ("staff", "Staff"),
                                                    ("carrier", "Carrier")))


class RepositionForm(forms.Form):
    location_x = forms.IntegerField(label="X Coordinate")
    location_y = forms.IntegerField(label="Y Coordinate")
