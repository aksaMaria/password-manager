
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import SavedPassword
from cryptography.fernet import Fernet
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q

def encrypt_password(password):
    key = settings.PASSWORD_ENCRYPTION_KEY

    if not key:
        raise ValueError("Encryption key is missing!")

    cipher = Fernet(key.encode())
    encrypted = cipher.encrypt(password.encode())

    return encrypted.decode()


def decrypt_password(encrypted_password):
    key = settings.PASSWORD_ENCRYPTION_KEY

    if not key:
        raise ValueError("Encryption key is missing!")

    cipher = Fernet(key.encode())
    decrypted = cipher.decrypt(encrypted_password.encode())

    return decrypted.decode()

def home(request):
    return render(request, "home.html")


def register_view(request):
    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Check empty fields
        if not username or not password or not confirm_password:
            messages.error(request, "All fields are required!")
            return redirect("register")

        # Check password length
        if len(password) < 8:
            messages.error(request, "Password must contain at least 8 characters!")
            return redirect("register")

        # Check password confirmation
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        # Check duplicate username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")

        # Create account
        User.objects.create_user(
            username=username,
            password=password
        )

        messages.success(request, "Account created! Please log in.")
        return redirect("login")

    return render(request, "register.html")

def login_view(request):
    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # Check empty fields
        if not username or not password:
            messages.error(request, "Please enter both username and password!")
            return render(request, "login.html")

        # Authenticate user
        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("vault")

        messages.error(request, "Invalid username or password!")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required(login_url="login")
def vault_view(request):

    if request.method == "POST":

        website = request.POST.get("website")
        username = request.POST.get("username")
        password = request.POST.get("password")
        category = request.POST.get("category") or "Other"
        notes = request.POST.get("notes")

        SavedPassword.objects.create(
            user=request.user,
            website=website,
            username=username,
            encrypted_password=encrypt_password(password),
            category=category,
            notes=notes
        )

        messages.success(request, "Account saved successfully!")
        return redirect("vault")

    passwords = SavedPassword.objects.filter(user=request.user)

    search_query = request.GET.get("q", "")

    if search_query:
        passwords = passwords.filter(
            Q(website__icontains=search_query) |
            Q(username__icontains=search_query)
        )

    selected_category = request.GET.get("category", "")

    if selected_category:
        passwords = passwords.filter(category=selected_category)

    return render(request, "vault.html", {
        "passwords": passwords,
        "search_query": search_query,
        "selected_category": selected_category
    })


@login_required(login_url="login")
def reveal_password(request, password_id):

    if request.method != "POST":
        return redirect("vault")

    saved_password = get_object_or_404(
        SavedPassword,
        id=password_id,
        user=request.user
    )

    decrypted_password = decrypt_password(
        saved_password.encrypted_password
    )

    passwords = SavedPassword.objects.filter(
        user=request.user
    )

    return render(request, "vault.html", {
        "passwords": passwords,
        "revealed_password": decrypted_password,
        "revealed_id": saved_password.id
    })

@login_required(login_url="login")
def delete_password(request, password_id):

    if request.method != "POST":
        return redirect("vault")

    saved_password = get_object_or_404(
        SavedPassword,
        id=password_id,
        user=request.user
    )

    saved_password.delete()

    messages.success(request, "Account deleted successfully!")

    return redirect("vault")  

@login_required(login_url="login")
def edit_password(request, password_id):

    if request.method not in ["GET", "POST"]:
        return redirect("vault")

    saved_password = get_object_or_404(
        SavedPassword,
        id=password_id,
        user=request.user
    )

    if request.method == "POST":

        saved_password.website = request.POST.get("website")
        saved_password.username = request.POST.get("username")
        saved_password.category = request.POST.get("category") or "Other"
        saved_password.notes = request.POST.get("notes")

        new_password = request.POST.get("password")

        if new_password:
            saved_password.encrypted_password = encrypt_password(new_password)

        saved_password.save()

        messages.success(request, "Account updated successfully!")
        return redirect("vault")

    return render(request, "edit_password.html", {
        "saved_password": saved_password
    })        

@login_required(login_url="login")
def toggle_favorite(request, password_id):

    if request.method != "POST":
        return redirect("vault")

    saved_password = get_object_or_404(
        SavedPassword,
        id=password_id,
        user=request.user
    )

    saved_password.is_favorite = not saved_password.is_favorite

    saved_password.save()

    return redirect("vault")    